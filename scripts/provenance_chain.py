#!/usr/bin/env python3
"""
provenance_chain.py -- repo-wide provenance chain. Stdlib only.

  python3 scripts/provenance_chain.py build        # backfill / append steps
  python3 scripts/provenance_chain.py trace <id>   # assumption id, source id or step id
  python3 scripts/provenance_chain.py stale        # recompute hashes, flag changed inputs
  python3 scripts/provenance_chain.py dups         # near-duplicate source candidates
  python3 scripts/provenance_chain.py --selftest

Rules are declared in registry/DECLARED.json (with its amendments), committed
before this file existed. This script never deletes and never edits a stored step: a revision
appends a new step whose `supersedes` names the prior one.

Not the same thing as validation/provenance.py, which is a hand-written
lineage table for concepts and carries no hashes.
"""

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
METHOD = {"name": "manual_entry", "version": "1"}
VOID_STATES = ("REJECTED", "UNMAPPED", "LEXICAL_VOID", "VOID")
SNAPSHOT_CLASSES = ("CONTEXT_FREE_EXACT", "STABLE_LOSSY", "CHAOTIC_REFRESH", "SUMMARY_ONLY")
CLAIM_STATES = ("SUPPORTED", "UNVERIFIED")
STEP_KEYS = ("id", "inputs", "method", "params", "value", "assumptions", "scope",
             "status", "status_note", "supersedes", "declared_pre_run", "claim", "void",
             "snapshot_class")
ATTR_STATUS_NOTE = "not assessed in this vocabulary"
COORD_FIELDS = ("carrier", "signal", "record", "closure", "trust_basis",
                "energy_cost", "loop_topology", "assumption_trace")
GATE_FIELDS = ("limit_sensed", "early_signal", "response", "lead_time")
CAPS = ("adapts", "signals", "responds_to_other", "changes_environment", "co_adapts")


# ------------------------------------------------------------------ hashing
def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def step_id(step):
    """Fixes v2: the id covers entity id, field path, value hash, inputs, method,
    params without the entity file hash, assumptions, scope and status. The
    entity file hash stays in params as context only."""
    params = {k: v for k, v in step["params"].items() if k != "entity_file_sha256"}
    return sha(canon({"entity_id": step["params"].get("entity"),
                      "field_path": step["params"].get("field"),
                      "value_sha256": sha(canon(step["value"])),
                      "inputs": step["inputs"], "method": step["method"], "params": params,
                      "assumptions": step["assumptions"], "scope": step["scope"],
                      "status": step["status"]}))


def source_id(text):
    return sha(text)


def assumption_id(statement):
    return "A-" + sha(statement)[:12]


def make_step(inputs, params, value, assumptions=(), scope=None, status=None,
              supersedes=None, declared=None, claim=None, void=None,
              snapshot_class=None, method=None, status_note=None):
    st = {"inputs": list(inputs), "method": dict(method or METHOD), "params": params,
          "value": value,
          "assumptions": None if assumptions is None else list(assumptions), "scope": scope,
          "status": status, "status_note": status_note,
          "supersedes": supersedes, "declared_pre_run": declared,
          "claim": claim, "void": void, "snapshot_class": snapshot_class}
    st["id"] = step_id(st)
    return {k: st[k] for k in STEP_KEYS}


# ---------------------------------------------------------------- file I/O
def load(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def dump(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def declared_commit(root):
    """Latest commit that changed registry/DECLARED.json, or None when git cannot say."""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "log", "-1", "--format=%H", "--",
             "registry/DECLARED.json"], capture_output=True, text=True, timeout=30).stdout.split()
        return out[0] if out else None
    except Exception:
        return None


# ------------------------------------------------------- reading entities
_READ = re.compile(r"\[(abstract) read via NCBI efetch (\d{4}-\d{2}-\d{2})")


def source_entry(s):
    """Registry entry for one exact source string. `opened` and `fetched` are
    read from the string's own bracket note; absent a note, false and null."""
    m = _READ.search(s)
    return {"id": source_id(s), "string": s, "same_as": None,
            "opened": m.group(1) if m else False, "fetched": m.group(2) if m else None}


_KEY = re.compile(r"^\W*([^\W\d_]+)[^()]*?\(?((?:1[5-9]|20)\d{2})\b")


def near_duplicates(sources):
    """Groups of distinct strings sharing first word + first year. Candidates
    only: nothing is merged and same_as is not set."""
    groups = {}
    for e in sources:
        m = _KEY.search(e["string"])
        if m:
            groups.setdefault((m.group(1).lower(), m.group(2)), []).append(e)
    return {k: v for k, v in sorted(groups.items()) if len(v) > 1}


def _void(value, has_source, reason, label_slot=False):
    """Map an LID field to a void state (mapping declared PROPOSED, fixes v2).
    VOID = null, reason kept when the record gives one. LEXICAL_VOID = an open
    label slot only. REJECTED needs a declared gate; none exists, none is made."""
    if value is None:
        if label_slot:
            return {"state": "LEXICAL_VOID", "reason": reason or "open label slot: no term recorded"}
        return {"state": "VOID", "reason": reason or None}
    if not has_source:
        return {"state": "UNMAPPED", "reason": "value present, no source recorded"}
    return None


def entity_fields(d):
    """Yield (field, value, sources, status, scope, extra_params, void_reason, assumptions)."""
    eid = d.get("id")
    ctx = d.get("observation_context") if isinstance(d.get("observation_context"), dict) else {}

    def scope_for(key):
        return {"observation_context": ctx[key]} if ctx.get(key) is not None else None

    at = d.get("attributes")
    if isinstance(at, dict):
        for name, v in at.items():
            if isinstance(v, dict) and "scope" in v:
                sc = v["scope"] if isinstance(v["scope"], dict) else {}
                ev = sc.get("evidence") or {}
                src = [ev["source"]] if isinstance(ev.get("source"), str) and ev["source"] else []
                extra = {"evidence_type": ev.get("evidence_type"),
                         "reproducibility": ev.get("reproducibility")}
                cond = sc.get("condition")
                yield ("attributes." + name, v.get("value"), src, None,
                       {"condition": cond} if cond is not None else None, extra, None, None)
            else:
                yield ("attributes." + name, v, [], None, None, {}, None, None)

    c = d.get("coordination")
    if isinstance(c, dict):
        srcs, stat, notes = c.get("sources") or {}, c.get("status") or {}, c.get("notes") or {}
        for f in COORD_FIELDS:
            v = c.get(f)
            reason = None
            if f == "energy_cost" and isinstance(v, dict) and v.get("joules") is None:
                reason, v = v.get("note"), None
            elif v is None:
                reason = notes.get(f)
            ass = [assumption_id(s) for s in v] if f == "assumption_trace" and isinstance(v, list) else []
            yield ("coordination." + f, v, list(srcs.get(f) or []), stat.get(f),
                   scope_for("coordination." + f), {}, reason, ass)

    g = d.get("gate_sensing")
    if isinstance(g, dict):
        srcs, stat, notes = g.get("sources") or {}, g.get("status") or {}, g.get("notes") or {}
        for f in GATE_FIELDS:
            v = g.get(f)
            reason = None
            if f == "lead_time" and isinstance(v, dict) and v.get("value") is None:
                reason, v = v.get("note"), None
            elif v is None:
                reason = notes.get(f)
            yield ("gate_sensing." + f, v, list(srcs.get(f) or []), stat.get(f),
                   scope_for("gate_sensing." + f), {}, reason, [])

    fi = d.get("functional_intelligence")
    if isinstance(fi, dict):
        notes = fi.get("notes") or {}
        for f in CAPS:
            cap = fi.get(f)
            key = "functional_intelligence." + f
            if isinstance(cap, dict):
                v = cap.get("value")
                if v == "unmeasured":
                    yield (key, None, list(cap.get("source") or []), cap.get("status"),
                           scope_for(key), {}, cap.get("note") or "unmeasured", [])
                else:
                    yield (key, v, list(cap.get("source") or []), cap.get("status"),
                           scope_for(key), {}, None, [])
            else:
                yield (key, None, [], None, scope_for(key), {}, notes.get(f) or notes.get("_scope"), [])
        for i, cl in enumerate(fi.get("contested_label") or []):
            src = list(cl.get("claimed_by") or []) + list(cl.get("disputed_by") or [])
            yield ("functional_intelligence.contested_label[%d]" % i, cl.get("label"), src, None, None,
                   {"claimed_by": [source_id(s) for s in cl.get("claimed_by") or []],
                    "disputed_by": [source_id(s) for s in cl.get("disputed_by") or []]}, None, [])
    _ = eid


def compute_steps(d, declared, file_sha=None):
    """One step per field of one entity. Returns (steps, sources, assumptions).
    file_sha (sha256 of the entity file's bytes) goes into params as context; it is not in the id."""
    steps, sources, assumptions = [], {}, {}
    eid = d.get("id")
    for field, value, srcs, status, scope, extra, reason, ass in entity_fields(d):
        for s in srcs:
            sources[source_id(s)] = s
        if field == "coordination.assumption_trace" and isinstance(value, list):
            for s in value:
                assumptions[assumption_id(s)] = (s, status)
        params = {"entity": eid, "field": field, "entity_file_sha256": file_sha}
        params.update(extra)
        note = ATTR_STATUS_NOTE if field.startswith("attributes.") else None
        steps.append(make_step([source_id(s) for s in srcs], params, value, ass, scope, status,
                               None, declared, None,
                               _void(value, bool(srcs), reason,
                                     field.startswith("functional_intelligence.contested_label[")),
                               None,
                               status_note=note))
    return steps, sources, assumptions


def entity_files(root):
    for p in sorted((root / "ontology").glob("*/*.json")):
        try:
            raw = p.read_bytes()
            d = json.loads(raw.decode("utf-8"))
        except Exception:
            continue
        if isinstance(d, dict) and isinstance(d.get("id"), str):
            yield p, d, hashlib.sha256(raw).hexdigest()


# -------------------------------------------------------------- the chain
def heads(steps):
    """Latest step per field: a step nobody supersedes."""
    superseded = {s["supersedes"] for s in steps if s.get("supersedes")}
    out = {}
    for s in steps:
        if s["id"] not in superseded:
            out[s["params"].get("field")] = s
    return out


def append_step(steps, step):
    """Append, never replace. Refuses an id already present."""
    if any(s["id"] == step["id"] for s in steps):
        raise ValueError("step id already present: %s" % step["id"])
    steps.append(step)
    return step


def revise_assumption(registry, old_id, statement, **kw):
    """Append a new assumption entry that supersedes old_id. The old entry stays."""
    entry = {"id": assumption_id(statement), "statement": statement, "domain": kw.get("domain"),
             "status": kw.get("status"), "sources": kw.get("sources", []), "supersedes": old_id}
    if any(e["id"] == entry["id"] for e in registry):
        raise ValueError("assumption id already present: %s" % entry["id"])
    registry.append(entry)
    return entry


def build(root=ROOT, quiet=False):
    declared = declared_commit(root)
    pdir = root / "provenance"
    src_reg = {e["id"]: e for e in load(root / "registry" / "sources.json", {"sources": []})["sources"]}
    ass_file = load(root / "registry" / "assumptions.json", {"assumptions": []})
    ass_reg = ass_file["assumptions"]
    ass_ids = {e["id"] for e in ass_reg}
    counts = {"entities": 0, "steps_total": 0, "appended": 0, "superseding": 0}
    index = []
    for p, d, fsha in entity_files(root):
        rel = str(p.relative_to(root))
        steps, sources, assumptions = compute_steps(d, declared, fsha)
        for sid, text in sources.items():
            src_reg.setdefault(sid, source_entry(text))
        for aid, (statement, status) in assumptions.items():
            if aid not in ass_ids:
                ass_reg.append({"id": aid, "statement": statement, "domain": "coordination",
                                "status": status, "sources": [], "supersedes": None})
                ass_ids.add(aid)
            entry = next(e for e in ass_reg if e["id"] == aid)
            if rel not in entry["sources"]:
                entry["sources"].append(rel)
        fpath = pdir / ("%s.json" % d["id"])
        doc = load(fpath, {"entity": d["id"], "path": rel, "snapshot_class": None, "steps": []})
        head = heads(doc["steps"])
        present = {s["id"] for s in doc["steps"]}
        for st in steps:
            prior = head.get(st["params"]["field"])
            if prior is not None and prior["id"] == st["id"]:
                continue
            if st["id"] in present:      # an older version of this field came back
                continue
            if prior is not None:
                st["supersedes"] = prior["id"]
                counts["superseding"] += 1
            append_step(doc["steps"], st)
            present.add(st["id"])
            counts["appended"] += 1
        if doc["steps"]:
            dump(fpath, doc)
            counts["entities"] += 1
            counts["steps_total"] += len(doc["steps"])
            index.append({"entity": d["id"], "path": rel, "steps": len(doc["steps"]),
                          "head_steps": len(heads(doc["steps"]))})
    dump(root / "registry" / "sources.json",
         {"note": "One entry per exact source string. id = sha256 of the string as UTF-8. "
                  "Two spellings of one work are two entries; nothing is merged and same_as is null. "
                  "opened and fetched are read from the string's own bracket note.",
          "sources": sorted(src_reg.values(), key=lambda e: e["id"])})
    ass_file["note"] = ("One entry per assumption. id = 'A-' + first 12 hex of sha256(statement). "
                        "A revision is a new entry with supersedes; old entries stay.")
    dump(root / "registry" / "assumptions.json", {"note": ass_file["note"], "assumptions": ass_reg})
    dump(pdir / "INDEX.json",
         {"snapshot_class": "SUMMARY_ONLY",
          "note": "Per-entity counts. The steps cannot be rebuilt from this file.",
          "declared_pre_run": declared, "entities": index})
    counts["sources"] = len(src_reg)
    counts["assumptions"] = len(ass_reg)
    if not quiet:
        print("declared_pre_run: %s" % declared)
        for k in ("entities", "steps_total", "appended", "superseding", "sources", "assumptions"):
            print("%-13s %d" % (k, counts[k]))
    return counts


def load_chain(root=ROOT):
    """All stored steps as {id: (entity, step)}, plus registries."""
    steps = {}
    for p in sorted((root / "provenance").glob("*.json")):
        if p.name == "INDEX.json":
            continue
        doc = json.loads(p.read_text(encoding="utf-8"))
        for s in doc["steps"]:
            steps[s["id"]] = (doc["entity"], s)
    srcs = load(root / "registry" / "sources.json", {"sources": []})["sources"]
    ass = load(root / "registry" / "assumptions.json", {"assumptions": []})["assumptions"]
    return steps, srcs, ass


def downstream(steps, seeds):
    """Every step reachable from seeds through inputs (seeds included)."""
    found, frontier = set(seeds), set(seeds)
    while frontier:
        nxt = {sid for sid, (_, s) in steps.items()
               if sid not in found and frontier & set(s["inputs"])}
        found |= nxt
        frontier = nxt
    return found


def trace(steps, ident):
    """Steps that use ident (assumption, source or step id), then everything downstream."""
    direct = {sid for sid, (_, s) in steps.items()
              if ident in s["inputs"] or ident in (s["assumptions"] or []) or sid == ident}
    allof = downstream(steps, direct)
    return [(sid, steps[sid][0], steps[sid][1]["params"].get("field"),
             "direct" if sid in direct else "downstream") for sid in sorted(
                 allof, key=lambda i: (i not in direct, steps[i][0], str(steps[i][1]["params"].get("field"))))]


def stale(steps, srcs, ass, current=None):
    """Return {step_id: [reasons]}. `current` = {(entity, field): id computed now}."""
    flags = {}

    def flag(sid, why):
        flags.setdefault(sid, [])
        if why not in flags[sid]:
            flags[sid].append(why)

    src_ok = {e["id"] for e in srcs if source_id(e["string"]) == e["id"]}
    ass_ok = {e["id"] for e in ass if assumption_id(e["statement"]) == e["id"]}
    ass_superseded = {e.get("supersedes") for e in ass if e.get("supersedes")}
    superseded = {s["supersedes"] for _, s in steps.values() if s.get("supersedes")}
    for sid, (ent, s) in steps.items():
        if step_id(s) != sid:
            flag(sid, "HASH_MISMATCH")
        for i in s["inputs"]:
            if i not in steps and i not in src_ok:   # not a parent step: must be a good source
                flag(sid, "SOURCE_CHANGED")
        for a in s["assumptions"] or []:
            if a not in ass_ok or a in ass_superseded:
                flag(sid, "ASSUMPTION_CHANGED")
        if current is not None and sid not in superseded:
            now = current.get((ent, s["params"].get("field")))
            if now is not None and now != sid:
                flag(sid, "FIELD_CHANGED")
    seeds = set(flags) | (superseded & set(steps))
    for sid in downstream(steps, seeds) - seeds:
        flag(sid, "INPUT_CHANGED")
    for sid in seeds:   # a flagged or superseded parent also marks its direct children
        for cid, (_, s) in steps.items():
            if sid in s["inputs"] and cid != sid:
                flag(cid, "INPUT_CHANGED")
    return flags


def current_ids(root=ROOT):
    declared = declared_commit(root)
    out = {}
    for _, d, fsha in entity_files(root):
        for st in compute_steps(d, declared, fsha)[0]:
            out[(d["id"], st["params"]["field"])] = st["id"]
    return out


def check_shape(steps):
    """Stdlib shape check of stored steps. Returns failure strings."""
    out = []
    for sid, (ent, s) in steps.items():
        if tuple(s) != STEP_KEYS:
            out.append("%s %s: keys differ from the step schema" % (ent, sid[:12]))
            continue
        if s["void"] is not None and s["void"].get("state") not in VOID_STATES:
            out.append("%s %s: void state %r" % (ent, sid[:12], s["void"].get("state")))
        if s["void"] is not None and s["void"]["state"] in ("VOID", "LEXICAL_VOID") and s["value"] is not None:
            out.append("%s %s: void state on a field with a value" % (ent, sid[:12]))
        if s["snapshot_class"] is not None and s["snapshot_class"] not in SNAPSHOT_CLASSES:
            out.append("%s %s: snapshot_class %r" % (ent, sid[:12], s["snapshot_class"]))
        if s["claim"] is not None and s["claim"].get("state") not in CLAIM_STATES:
            out.append("%s %s: claim state %r" % (ent, sid[:12], s["claim"].get("state")))
    return out


# ---------------------------------------------------------------- selftest
def selftest():
    cases = []

    def case(name, ok):
        cases.append((name, bool(ok)))

    a1 = "coordination requires money"
    ass = [{"id": assumption_id(a1), "statement": a1, "domain": "t", "status": "PROPOSED",
            "sources": [], "supersedes": None}]
    src_text = "Planted source (0000)"
    srcs = [source_entry(src_text)]
    A = make_step([source_id(src_text)], {"entity": "T", "field": "a"}, 1, [assumption_id(a1)])
    B = make_step([A["id"]], {"entity": "T", "field": "b"}, 2)
    C = make_step([B["id"]], {"entity": "T", "field": "c"}, 3)
    D = make_step([], {"entity": "T", "field": "d"}, 4)
    chain = [A, B, C, D]
    steps = {s["id"]: ("T", s) for s in chain}

    case("ids are 64 hex and distinct", len({s["id"] for s in chain}) == 4 and all(len(s["id"]) == 64 for s in chain))
    case("id does not depend on key order", step_id(dict(reversed(list(A.items())))) == A["id"])
    case("clean chain: nothing stale", stale(steps, srcs, ass) == {})
    t = trace(steps, assumption_id(a1))
    case("trace(assumption) finds A, B, C", {x[0] for x in t} == {A["id"], B["id"], C["id"]})
    case("trace(assumption) leaves D out", D["id"] not in {x[0] for x in t})
    case("trace(source) finds A, B, C", {x[0] for x in trace(steps, source_id(src_text))} == {A["id"], B["id"], C["id"]})
    case("trace marks A direct, B and C downstream",
         {x[0]: x[3] for x in t} == {A["id"]: "direct", B["id"]: "downstream", C["id"]: "downstream"})

    # change A's assumption: append a superseding registry entry
    before = [dict(e) for e in ass]
    revise_assumption(ass, assumption_id(a1), "coordination requires a shared record", domain="t", status="PROPOSED")
    case("revised assumption appended, old entry unchanged", len(ass) == 2 and ass[0] == before[0])
    fl = stale(steps, srcs, ass)
    case("stale flags A as ASSUMPTION_CHANGED", fl.get(A["id"]) == ["ASSUMPTION_CHANGED"])
    case("stale flags B and C as INPUT_CHANGED",
         fl.get(B["id"]) == ["INPUT_CHANGED"] and fl.get(C["id"]) == ["INPUT_CHANGED"])
    case("stale leaves D alone", D["id"] not in fl)
    case("trace still finds B, C after the change",
         {B["id"], C["id"]} <= {x[0] for x in trace(steps, assumption_id(a1))})

    # revise A: append, never replace
    A2 = make_step(A["inputs"], {"entity": "T", "field": "a", "revision": "assumption revised"}, 1,
                   [ass[1]["id"]], supersedes=A["id"])
    append_step(chain, A2)
    steps = {s["id"]: ("T", s) for s in chain}
    case("old steps still present after revision", all(s in chain for s in (A, B, C, D)) and len(chain) == 5)
    case("head of field a is the new step", heads(chain)["a"]["id"] == A2["id"])
    case("B, C still flagged while they point at superseded A",
         {B["id"], C["id"]} <= set(stale(steps, srcs, ass)))
    try:
        append_step(chain, dict(A2))
        dup = False
    except ValueError:
        dup = True
    case("appending an id already present is refused", dup)

    # planted corruption
    bad = dict(B)
    bad["value"] = 99
    case("edited step value fires HASH_MISMATCH",
         "HASH_MISMATCH" in stale({B["id"]: ("T", bad)}, srcs, ass).get(B["id"], []))
    case("edited source text fires SOURCE_CHANGED",
         "SOURCE_CHANGED" in stale({A["id"]: ("T", A)}, [dict(srcs[0], string="edited")], before).get(A["id"], []))
    case("missing source fires SOURCE_CHANGED",
         "SOURCE_CHANGED" in stale({A["id"]: ("T", A)}, [], before).get(A["id"], []))
    case("field drift fires FIELD_CHANGED",
         "FIELD_CHANGED" in stale({D["id"]: ("T", D)}, srcs, before, {("T", "d"): "0" * 64}).get(D["id"], []))
    case("void mapping: null + reason -> VOID, reason kept",
         _void(None, False, "unmeasured") == {"state": "VOID", "reason": "unmeasured"})
    case("void mapping: null, no reason -> VOID", _void(None, False, None) == {"state": "VOID", "reason": None})
    case("void mapping: open label slot -> LEXICAL_VOID", _void(None, False, None, True)["state"] == "LEXICAL_VOID")
    case("void mapping: nothing maps to REJECTED",
         all((_void(v, h, r, l) or {}).get("state") != "REJECTED"
             for v in (None, 1) for h in (False, True) for r in (None, "x") for l in (False, True)))
    ls = compute_steps({"id": "T", "functional_intelligence": {"contested_label": [
        {"label": None, "claimed_by": ["Planted (0000)"]}, {"label": "learning"}]}}, None, "0" * 64)[0]
    lv = {s["params"]["field"]: (s["void"] or {}).get("state") for s in ls}
    case("backfill: null contested label -> LEXICAL_VOID, null capability -> VOID",
         lv["functional_intelligence.contested_label[0]"] == "LEXICAL_VOID"
         and lv["functional_intelligence.contested_label[1]"] == "UNMAPPED"
         and lv["functional_intelligence.adapts"] == "VOID")
    case("void mapping: value, no source -> UNMAPPED", _void(1, False, None)["state"] == "UNMAPPED")
    case("void mapping: value + source -> null", _void(1, True, None) is None)
    attr = compute_steps({"id": "T", "attributes": {"k": 1}}, None, "0" * 64)[0][0]
    case("attribute step: assumptions null, status null with a note",
         attr["assumptions"] is None and attr["status"] is None and attr["status_note"] == ATTR_STATUS_NOTE)
    attr2 = compute_steps({"id": "T", "attributes": {"k": 1}}, None, "1" * 64)[0][0]
    case("id does not cover the entity file hash; the hash stays in params",
         attr2["id"] == attr["id"] and attr2["params"]["entity_file_sha256"] == "1" * 64
         and attr["params"]["entity_file_sha256"] == "0" * 64)
    base = make_step([], {"entity": "T", "field": "s"}, 1, [], None, "PROPOSED")
    variants = [make_step([], {"entity": "T", "field": "s"}, 1, [], None, "OBSERVED"),
                make_step([], {"entity": "T", "field": "s"}, 1, ["A-000000000000"], None, "PROPOSED"),
                make_step([], {"entity": "T", "field": "s"}, 1, [], {"condition": "c"}, "PROPOSED"),
                make_step([], {"entity": "T", "field": "s"}, 1, None, None, "PROPOSED"),
                make_step([], {"entity": "T", "field": "s2"}, 1, [], None, "PROPOSED"),
                make_step([], {"entity": "T2", "field": "s"}, 1, [], None, "PROPOSED")]
    case("id covers status, assumptions, scope, field path and entity id",
         len({base["id"]} | {v["id"] for v in variants}) == 7)
    case("id does not cover status_note, claim, void, snapshot_class, supersedes, declared_pre_run",
         step_id(dict(base, status_note="n", void={"state": "VOID", "reason": None}, supersedes="0" * 64,
                      snapshot_class="SUMMARY_ONLY", declared_pre_run="x",
                      claim={"statement": "s", "evidence": "e", "refuter": "r", "state": "UNVERIFIED"})) == base["id"])
    case("source id is the full sha256 of the exact string",
         srcs[0]["id"] == hashlib.sha256(src_text.encode("utf-8")).hexdigest() and len(srcs[0]["id"]) == 64)
    se = source_entry("X Y (2016) T. PMID 1 [abstract read via NCBI efetch 2026-11-24; full text not read]")
    case("source entry reads opened and fetched from the string",
         se["opened"] == "abstract" and se["fetched"] == "2026-11-24" and se["same_as"] is None
         and srcs[0]["opened"] is False and srcs[0]["fetched"] is None)
    nd = near_duplicates([source_entry("Smith A (2001) One."), source_entry("Smith, A. 2001. One, again."),
                          source_entry("Jones B (2001) Two.")])
    case("near-duplicate candidates: same first word + year, nothing merged",
         list(nd) == [("smith", "2001")] and len(nd[("smith", "2001")]) == 2)
    case("bad void state fails the shape check",
         check_shape({"x": ("T", dict(D, void={"state": "EMPTY", "reason": None}))}))
    case("bad snapshot_class fails the shape check",
         check_shape({"x": ("T", dict(D, snapshot_class="FUZZY"))}))
    case("bad claim state fails the shape check",
         check_shape({"x": ("T", dict(D, claim={"statement": "s", "evidence": "e", "refuter": "r", "state": "TRUE"}))}))

    # build twice on a planted repo: second build appends nothing; an edit appends and keeps
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "ontology" / "x").mkdir(parents=True)
        ent = {"id": "T1", "name": "t", "ontology": "x",
               "attributes": {"k": {"value": 1, "scope": {"evidence": {"source": "Planted (0000)"}}}, "u": 5},
               "gate_sensing": {"limit_sensed": "x", "early_signal": "y", "response": "z", "lead_time": None,
                                "sources": {"limit_sensed": ["Planted (0000)"]},
                                "status": {"limit_sensed": "PROPOSED"}}}
        (root / "ontology" / "x" / "t1.json").write_text(json.dumps(ent), encoding="utf-8")
        c1 = build(root, quiet=True)
        c2 = build(root, quiet=True)
        case("build: one step per field", c1["appended"] == 6 and c1["steps_total"] == 6)
        case("build twice: nothing appended", c2["appended"] == 0 and c2["steps_total"] == 6)
        case("build leaves the entity file untouched",
             json.loads((root / "ontology" / "x" / "t1.json").read_text(encoding="utf-8")) == ent)
        ent["attributes"]["k"]["value"] = 2
        (root / "ontology" / "x" / "t1.json").write_text(json.dumps(ent), encoding="utf-8")
        st, sr, asr = load_chain(root)
        fl = stale(st, sr, asr, current_ids(root))
        case("change one field: only that field's step is FIELD_CHANGED",
             [st[i][1]["params"]["field"] for i in fl] == ["attributes.k"]
             and list(fl.values()) == [["FIELD_CHANGED"]])
        c3 = build(root, quiet=True)
        doc = json.loads((root / "provenance" / "T1.json").read_text(encoding="utf-8"))
        case("rebuild appends one superseding step for that field, keeps the old",
             c3["appended"] == 1 and c3["superseding"] == 1 and len(doc["steps"]) == 7
             and doc["steps"][6]["supersedes"] == doc["steps"][0]["id"]
             and doc["steps"][6]["params"]["field"] == "attributes.k")
        case("unchanged fields keep the file hash they were written under",
             doc["steps"][1]["params"]["entity_file_sha256"] != doc["steps"][6]["params"]["entity_file_sha256"])
        st, sr, asr = load_chain(root)
        case("after rebuild nothing is stale", stale(st, sr, asr, current_ids(root)) == {})
        # status-only revision: new step, supersedes old, old kept
        ent["gate_sensing"]["status"]["limit_sensed"] = "OBSERVED"
        (root / "ontology" / "x" / "t1.json").write_text(json.dumps(ent), encoding="utf-8")
        st, sr, asr = load_chain(root)
        fl = stale(st, sr, asr, current_ids(root))
        case("status-only change: only that field's step is FIELD_CHANGED",
             [st[i][1]["params"]["field"] for i in fl] == ["gate_sensing.limit_sensed"])
        c4 = build(root, quiet=True)
        doc = json.loads((root / "provenance" / "T1.json").read_text(encoding="utf-8"))
        old = [s for s in doc["steps"] if s["params"]["field"] == "gate_sensing.limit_sensed"]
        case("status-only revision: new step supersedes the old, old kept, value unchanged",
             c4["appended"] == 1 and len(old) == 2 and old[1]["supersedes"] == old[0]["id"]
             and old[0]["status"] == "PROPOSED" and old[1]["status"] == "OBSERVED"
             and old[0]["value"] == old[1]["value"])
        # scope-only revision
        ent["attributes"]["k"]["scope"]["condition"] = "at 20 C"
        (root / "ontology" / "x" / "t1.json").write_text(json.dumps(ent), encoding="utf-8")
        c5 = build(root, quiet=True)
        doc = json.loads((root / "provenance" / "T1.json").read_text(encoding="utf-8"))
        ks = [s for s in doc["steps"] if s["params"]["field"] == "attributes.k"]
        case("scope-only revision: new step supersedes the old, old kept",
             c5["appended"] == 1 and len(ks) == 3 and ks[2]["supersedes"] == ks[1]["id"]
             and ks[1]["scope"] is None and ks[2]["scope"] == {"condition": "at 20 C"})
        st, sr, asr = load_chain(root)
        case("unsourced value carries UNMAPPED",
             {s["void"]["state"] for _, s in st.values() if s["params"]["field"] == "attributes.u"} == {"UNMAPPED"})
        case("stored steps pass the shape check", check_shape(st) == [])

    failed = 0
    for name, ok in cases:
        failed += not ok
        print("  %s  %s" % ("ok  " if ok else "FAIL", name))
    print("selftest checks: %d   failed: %d" % (len(cases), failed))
    return 1 if failed else 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if not argv or argv[0] not in ("build", "trace", "stale", "dups"):
        print(__doc__.strip())
        return 2
    if argv[0] == "build":
        build()
        return 0
    steps, srcs, ass = load_chain()
    if argv[0] == "dups":
        nd = near_duplicates(srcs)
        for (who, year), grp in nd.items():
            print("%s %s" % (who, year))
            for e in grp:
                print("   %s  %s" % (e["id"][:12], e["string"][:150]))
        print("candidate groups: %d   strings in them: %d   merged: 0" % (len(nd), sum(len(g) for g in nd.values())))
        return 0
    if argv[0] == "trace":
        if len(argv) < 2:
            print("usage: provenance_chain.py trace <assumption_id | source_id | step_id>")
            return 2
        ident = argv[1]
        pool = sorted({e["id"] for e in srcs} | {e["id"] for e in ass} | set(steps))
        hits = [i for i in pool if i.startswith(ident)]
        if len(hits) != 1:
            print("id %r matches %d known ids (a unique prefix is accepted)" % (ident, len(hits)))
            return 2
        argv = [argv[0], hits[0]]
        rows = trace(steps, argv[1])
        for e in ass:
            if e["id"] == argv[1]:
                print("assumption %s: %s" % (e["id"], e["statement"]))
        for e in srcs:
            if e["id"] == argv[1]:
                print("source %s: %s" % (e["id"][:12], e["string"]))
        for sid, ent, field, how in rows:
            print("%s  %-10s  %-12s  %s" % (sid[:12], how, ent, field))
        print("steps: %d   entities: %d" % (len(rows), len({r[1] for r in rows})))
        return 0
    flags = stale(steps, srcs, ass, current_ids())
    shape = check_shape(steps)
    for sid, why in sorted(flags.items(), key=lambda kv: (steps[kv[0]][0], kv[0])):
        print("%s  %-12s  %-40s  %s" % (sid[:12], steps[sid][0], steps[sid][1]["params"].get("field"), ", ".join(why)))
    for f in shape:
        print("SHAPE  " + f)
    print("steps: %d   stale: %d   shape failures: %d" % (len(steps), len(flags), len(shape)))
    return 1 if flags or shape else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
