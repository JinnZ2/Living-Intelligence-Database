#!/usr/bin/env python3
"""
export_examples.py -- examples built from the provenance chain. Stdlib only.

  python3 scripts/export_examples.py            # write examples/lid_examples.jsonl + MANIFEST.json
  python3 scripts/export_examples.py --check    # verify the written files against the chain

Rules: registry/DECLARED.json, amendment "physics usage: example export"
(filters, roles, path rule, hold-out split by entity). Every path is assembled
from stored steps and their source ids. This script trains nothing.
"""

import hashlib
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import provenance_chain as pc   # noqa: E402
import export_reference as er   # noqa: E402

ROOT = pc.ROOT
OUT = ROOT / "examples" / "lid_examples.jsonl"
MANIFEST = ROOT / "examples" / "MANIFEST.json"
HOLDOUT_FRACTION = 0.2
KINDS = ("OBSERVED", "DERIVED", "PROPOSED", "UNMEASURED", "CONTESTED_LABEL")
EXCLUDED = ("NOT_ASSESSED", "UNSOURCED", "assumption_trace")
CAPS = ["functional_intelligence." + c for c in pc.CAPS]

# role order, then field order inside a role (declared)
ROLE_FIELDS = (
    ("observation", CAPS + ["gate_sensing.limit_sensed", "gate_sensing.early_signal"]),
    ("mechanism", ["coordination.carrier", "coordination.signal", "coordination.record",
                   "coordination.closure", "coordination.trust_basis", "coordination.loop_topology",
                   "gate_sensing.response"]),
    ("physics", ["coordination.energy_cost", "gate_sensing.lead_time"]),
)
ROLE_RANK = {r: i for i, (r, _) in enumerate(ROLE_FIELDS)}
FIELD_ROLE = {f: r for r, fs in ROLE_FIELDS for f in fs}
FIELD_POS = {f: i for _, fs in ROLE_FIELDS for i, f in enumerate(fs)}

TEMPLATES = {
    "coordination.carrier": "What carries the coordination signal in {name}?",
    "coordination.signal": "What is the coordination signal in {name}?",
    "coordination.record": "Where is the record of coordination held in {name}?",
    "coordination.closure": "What closes a coordination loop in {name}?",
    "coordination.trust_basis": "What is trust based on in {name}?",
    "coordination.energy_cost": "What does coordination cost in energy in {name}?",
    "coordination.loop_topology": "What is the loop topology of coordination in {name}?",
    "gate_sensing.limit_sensed": "Which limit does {name} sense?",
    "gate_sensing.early_signal": "What is the early signal of that limit in {name}?",
    "gate_sensing.response": "How does {name} respond to the early signal?",
    "gate_sensing.lead_time": "How much lead time does the early signal give {name}?",
    "functional_intelligence.adapts": "Does {name} adapt?",
    "functional_intelligence.signals": "Does {name} signal?",
    "functional_intelligence.responds_to_other": "Does {name} respond to another organism or agent?",
    "functional_intelligence.changes_environment": "Does {name} change its environment?",
    "functional_intelligence.co_adapts": "Does {name} co-adapt with another organism or agent?",
}


def role_of(field):
    if field.startswith("attributes."):
        return "observation"
    return FIELD_ROLE.get(field)


def sort_key(field):
    # attributes (null ones only reach here) come first inside observation, by name
    if field.startswith("attributes."):
        return (ROLE_RANK["observation"], -1, field)
    return (ROLE_RANK[FIELD_ROLE[field]], FIELD_POS[field], field)


def kind_of(step):
    """Example kind for a step, or the reason it is excluded."""
    field = step["params"]["field"]
    if field == "coordination.assumption_trace":
        return None, "assumption_trace"
    rd = er.reading(step)
    if ".contested_label[" in field:
        return ("CONTESTED_LABEL", None) if rd != "UNSOURCED" and step["value"] is not None else (None, rd)
    if rd == "NO_INFORMATION":
        return "UNMEASURED", None
    if rd in ("OBSERVED", "DERIVED", "PROPOSED"):
        return rd, None
    return None, rd   # NOT_ASSESSED or UNSOURCED


def element(step, role):
    return {"role": role, "field": step["params"]["field"], "reading": er.reading(step),
            "value": step["value"], "status": step["status"], "step_id": step["id"],
            "source_ids": list(step["inputs"]), "void": step["void"]}


def _text(v):
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)


def answer_for(step, kind, caps, assumptions):
    scope = {"step_scope": step["scope"]}
    if step["params"]["field"].startswith("coordination."):
        scope["assumption_ids"] = assumptions
    a = {"kind": kind, "status": step["status"], "scope": scope}
    if kind == "UNMEASURED":
        a["claim"] = "unmeasured"
        a["value"] = None
        a["void"] = step["void"]
        reason = (step["void"] or {}).get("reason")
        a["stated_as"] = "Unmeasured: the record holds no value for this field" + \
            (" (%s)." % reason.rstrip(".") if reason else "; no reason is recorded.")
    elif kind == "OBSERVED":
        a["claim"] = _text(step["value"])
        a["stated_as"] = "OBSERVED: " + a["claim"]
    elif kind == "DERIVED":
        a["claim"] = _text(step["value"])
        a["stated_as"] = "%s: %s" % (step["status"], a["claim"])
    elif kind == "PROPOSED":
        a["claim"] = _text(step["value"])
        a["stated_as"] = "PROPOSED, not established: " + a["claim"]
    else:   # CONTESTED_LABEL
        p = step["params"]
        nc, nd = len(p.get("claimed_by") or []), len(p.get("disputed_by") or [])
        fn = "; ".join("%s %s" % (c["params"]["field"].split(".")[-1],
                                  "unmeasured" if c["value"] is None
                                  else "%s (%s)" % (_text(c["value"]), c["status"])) for c in caps)
        a["claim"] = "The label %r is recorded as contested (claimed by %d source(s), disputed by %d). " \
                     "A label does not decide; the function fields do: %s." % (step["value"], nc, nd, fn or "none recorded")
        a["label"] = step["value"]
        a["claimed_by"], a["disputed_by"] = p.get("claimed_by") or [], p.get("disputed_by") or []
        a["stated_as"] = a["claim"]
    return a


def build(root=ROOT):
    """Returns (examples, excluded_counts, entity_info)."""
    examples, excluded = [], {k: 0 for k in EXCLUDED}
    info = {}
    for ent, (path, steps) in sorted(er.head_steps(root).items()):
        try:
            d = json.loads((root / path).read_text(encoding="utf-8"))
        except Exception:
            d = {}
        name, ont = d.get("name") or ent, d.get("ontology")
        info[ent] = {"name": name, "ontology": ont, "path": path}
        kinds = {}
        for s in steps:
            k, why = kind_of(s)
            if k is None:
                excluded[why] += 1
            else:
                kinds[s["id"]] = k
        included = [s for s in steps if s["id"] in kinds]
        pathable = sorted((s for s in included if kinds[s["id"]] != "CONTESTED_LABEL"),
                          key=lambda s: sort_key(s["params"]["field"]))
        caps = [s for s in pathable if s["params"]["field"] in CAPS]
        at = next((s for s in steps if s["params"]["field"] == "coordination.assumption_trace"), None)
        assumptions = (at["assumptions"] or []) if at else []
        for s in included:
            field, kind = s["params"]["field"], kinds[s["id"]]
            if kind == "CONTESTED_LABEL":
                before, role = caps, "label"
                question = "Is the label %r settled for %s?" % (s["value"], name)
            else:
                role = role_of(field)
                before = [x for x in pathable if sort_key(x["params"]["field"]) < sort_key(field)]
                question = TEMPLATES[field].format(name=name) if field in TEMPLATES else \
                    "What is the value of %s for %s?" % (field.split(".", 1)[1].replace("_", " "), name)
            dpath = [element(x, role_of(x["params"]["field"])) for x in before] + [element(s, role)]
            dpath.append({"role": "status", "field": field, "status": s["status"],
                          "status_note": s["status_note"], "reading": er.reading(s), "void": s["void"],
                          "step_id": s["id"]})
            src = []
            for e in dpath[:-1]:
                src += [i for i in e["source_ids"] if i not in src]
            examples.append({
                "id": "EX-" + pc.sha(pc.canon({"entity": ent, "field": field, "step": s["id"]}))[:16],
                "entity": ent, "ontology": ont, "kind": kind, "split": None,
                "question": question, "derivation_path": dpath,
                "answer": answer_for(s, kind, caps, assumptions),
                "provenance": {"step_ids": [e["step_id"] for e in dpath[:-1]], "source_ids": src}})
    return examples, excluded, info


STATUSED_KINDS = ("OBSERVED", "DERIVED", "PROPOSED")


def split(examples):
    """Hold out whole entities, stratified by has_statused_field (amendment
    'stratified hold-out'): per stratum, the first max(1, ceil(0.2 * n)) by
    sha256 of the entity id. Returns (held, entities, strata)."""
    def order(x):
        return hashlib.sha256(x.encode("utf-8")).hexdigest()
    ents = sorted({e["entity"] for e in examples}, key=order)
    statused = {e["entity"] for e in examples if e["kind"] in STATUSED_KINDS}
    strata, held = {}, []
    for name, members in (("yes", [x for x in ents if x in statused]),
                          ("no", [x for x in ents if x not in statused])):
        h = members[:max(1, math.ceil(HOLDOUT_FRACTION * len(members)))] if members else []
        strata[name] = {"entities": members, "holdout": h}
        held += h
    for e in examples:
        e["split"] = "holdout" if e["entity"] in held else "train"
    return held, ents, strata


def counts(examples, key):
    out = {}
    for e in examples:
        k = e[key] if key != "status" else (e["answer"]["status"] or "null")
        out.setdefault(k, {"train": 0, "holdout": 0})
        out[k][e["split"]] += 1
    return dict(sorted(out.items(), key=lambda kv: str(kv[0])))


def check(examples, held, root=ROOT, strata=None):
    """Failure strings for the declared checks."""
    bad = []
    hb = er.head_steps(root)
    head_ids = {s["id"]: s for _, steps in hb.values() for s in steps}
    sides = {}
    for e in examples:
        sides.setdefault(e["entity"], set()).add(e["split"])
        if (e["split"] == "holdout") != (e["entity"] in held):
            bad.append("%s: split disagrees with the hold-out list" % e["id"])
        for el in e["derivation_path"]:
            s = head_ids.get(el["step_id"])
            if s is None:
                bad.append("%s: %s is not a head step" % (e["id"], el["step_id"][:12]))
                continue
            if el["role"] == "status":
                if s["status"] != el["status"]:
                    bad.append("%s: status element differs from the step" % e["id"])
                continue
            if pc.canon(s["value"]) != pc.canon(el["value"]) or s["status"] != el["status"] \
                    or list(s["inputs"]) != el["source_ids"]:
                bad.append("%s: path element %s differs from its step" % (e["id"], el["field"]))
            if el["reading"] in ("UNSOURCED", "NOT_ASSESSED") and e["kind"] != "CONTESTED_LABEL":
                bad.append("%s: %s element in the path" % (e["id"], el["reading"]))
        a, k = e["answer"], e["kind"]
        if k == "OBSERVED" and a["status"] != "OBSERVED":
            bad.append("%s: OBSERVED example without status OBSERVED" % e["id"])
        if k == "PROPOSED" and not a["stated_as"].startswith("PROPOSED, not established"):
            bad.append("%s: PROPOSED answer not labeled" % e["id"])
        if k == "DERIVED" and not a["stated_as"].startswith("DERIVED (basis:"):
            bad.append("%s: DERIVED answer without its basis" % e["id"])
        if k == "UNMEASURED" and (a["value"] is not None or a["claim"] != "unmeasured"):
            bad.append("%s: UNMEASURED answer carries a value" % e["id"])
        if k in ("OBSERVED", "DERIVED", "PROPOSED") and not e["provenance"]["source_ids"]:
            bad.append("%s: no source id" % e["id"])
    for name, st in (strata or {}).items():
        if st["entities"] and not st["holdout"]:
            bad.append("stratum %s has no hold-out entity" % name)
    for ent, s in sides.items():
        if len(s) != 1:
            bad.append("%s: on both sides of the split" % ent)
    if len({e["id"] for e in examples}) != len(examples):
        bad.append("example ids are not unique")
    return bad


def main(argv):
    ref_rows = er.read() if er.OUT.exists() else None
    if ref_rows is None or er.verify_rows(ref_rows) or ref_rows != er.build_rows():
        print("refused: reference/lid_reference.jsonl is missing or fails its check; run export_reference.py")
        return 1
    examples, excluded, info = build()
    held, ents, strata = split(examples)
    bad = check(examples, held, strata=strata)
    text = "".join(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n" for e in examples)
    manifest = {
        "snapshot_class": "SUMMARY_ONLY",
        "note": "Counts and the hold-out list for examples/lid_examples.jsonl. No model was trained. "
                "A derivation_path is an ordering of record fields by declared role; it does not claim "
                "that one field was derived from another.",
        "declared": "registry/DECLARED.json, amendment 'physics usage: example export'",
        "declared_commit": pc.declared_commit(ROOT),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "examples": len(examples),
        "entities_with_examples": ents and sorted(ents),
        "holdout_entities": held, "holdout_fraction": HOLDOUT_FRACTION,
        "holdout_strata": {"key": "has_statused_field", "strata": strata},
        "measurement_note": "n too small to measure: the split shows the rule works; "
                            "no rate computed on it is a measurement",
        "by_split": {s: sum(e["split"] == s for e in examples) for s in ("train", "holdout")},
        "by_kind": counts(examples, "kind"), "by_status": counts(examples, "status"),
        "by_ontology": counts(examples, "ontology"),
        "excluded_fields": excluded,
        "entities_in_chain": len(info),
        "entities_without_examples": len(info) - len(ents),
    }
    if "--check" in argv:
        same = OUT.exists() and OUT.read_text(encoding="utf-8") == text and \
            json.loads(MANIFEST.read_text(encoding="utf-8")) == manifest
        for b in bad:
            print("FAIL " + b)
        print("examples: %d   check failures: %d   files match a fresh export: %s" % (len(examples), len(bad), same))
        return 1 if bad or not same else 0
    if bad:
        for b in bad:
            print("FAIL " + b)
        print("refused to write: %d check failures" % len(bad))
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote %s (%d examples)" % (OUT.relative_to(ROOT), len(examples)))
    for title, key in (("kind", "by_kind"), ("status", "by_status"), ("ontology", "by_ontology")):
        print("by %s:" % title)
        for k, v in manifest[key].items():
            print("  %-16s train %3d   holdout %3d" % (k, v["train"], v["holdout"]))
    print("excluded fields: %s" % excluded)
    print("entities with examples: %d of %d   hold-out: %s" % (len(ents), len(info), ", ".join(held)))
    for name, st in strata.items():
        print("  has_statused_field=%-3s entities %s   hold-out %s"
              % (name, ", ".join(st["entities"]), ", ".join(st["holdout"])))
    print("n too small to measure")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
