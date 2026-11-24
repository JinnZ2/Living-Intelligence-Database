#!/usr/bin/env python3
"""Re-check the 2026-11-24 audit findings against a repository copy. Run from the root of a COPY.

    cd /path/to/copy && OUT=recheck.json python3 /path/to/recheck_main.py

Independent of validation/fixtures/: these probes use the real ontology data plus the same
fixtures instrument_tests.py used, so the earlier numbers can be compared one-to-one.
Each probe runs in default mode, and where the instrument has a legacy switch, in legacy mode as
well, to show whether legacy still reproduces the earlier reading. Stdlib only; no network.
Nothing in the copy is written except a temporary index during the build probes, which is
restored byte-for-byte afterwards.
"""
import collections, hashlib, inspect, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path.cwd(); sys.path.insert(0, str(ROOT / "validation"))
import verify, falsifier, dependency_tree as dt, audit, scope_checker as sc

R = {}
def rec(k, v): R[k] = v; print(f"== {k}:", json.dumps(v, ensure_ascii=False)[:700])
def has_kw(fn, kw): return kw in inspect.signature(fn).parameters
LEG = has_kw(falsifier.falsify, "legacy")
rec("meta", {"head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
             "legacy_switch_present": LEG})

idx = json.load(open(ROOT / "ontology_index.json"))
hyd = {"entities": [json.load(open(ROOT / e["path"])) for e in idx["entities"] if (ROOT / e["path"]).exists()]}
ids = {e["id"] for e in idx["entities"]}
rec("index", {"entities": len(idx["entities"]), "relations": len(idx["relations"]),
              "ontology_json_files": sum(1 for _ in (ROOT / "ontology").rglob("*.json")),
              "relational_dir_files": sorted(p.name for p in (ROOT / "ontology" / "relational").glob("*.json")),
              "relational_ids_in_index": sorted(e["id"] for e in idx["entities"] if "relational" in e.get("path", ""))})

def cli(args):
    r = subprocess.run([sys.executable] + args, capture_output=True, text=True)
    try: o = json.loads(r.stdout)
    except ValueError: o = {"_stdout": r.stdout[:200], "_stderr": r.stderr[-200:]}
    return r.returncode, o
pick = lambda o, ks: {k: o.get(k) for k in ks}
VK = ["verdict", "entities_consulted", "tests_gathered", "evidence_count", "tests_passed", "posterior_probability"]

# ---- verify.py
for label, extra in [("default", []), ("legacy", ["--legacy"])]:
    if label == "legacy" and not LEG: continue
    c, o = cli(["validation/verify.py", "--claim", "no_such_claim"] + extra)
    rec(f"V1.unknown_claim.{label}", {"exit": c, **pick(o, VK)})
    c, o = cli(["validation/verify.py", "--claim", "hex_efficiency", "--domain", "hex"] + extra)
    rec(f"V2.readme_example_hex_efficiency.{label}", {"exit": c, **pick(o, VK)})
    c, o = cli(["validation/verify.py", "--claim", "always_true"] + extra)
    rec(f"V3.cli_always_true_real_index.{label}", {"exit": c, **pick(o, VK)})

def fx(n, conf=0.9):
    return {"entities": [{"id": "FX", "attributes": {f"a{i}": {"value": 1, "scope": {"definition": "x", "evidence": {"relational_confidence": conf}}} for i in range(n)}}]}
calls = [0]
def claim(): calls[0] += 1; return True
for label, kw in [("default", {}), ("legacy", {"legacy": True})]:
    if label == "legacy" and not LEG: continue
    curve = []
    for n in [0, 1, 2, 5, 10, 20]:
        calls[0] = 0; o = verify.verify_claim(claim, ontology=fx(n), prior=0.5, **kw)
        curve.append({"n": n, "calls": calls[0], "posterior": o["posterior_probability"], "verdict": o.get("verdict")})
    rec(f"V4.posterior_vs_attribute_count.{label}", curve)
    calls[0] = 0; o = verify.verify_claim(claim, ontology=hyd, prior=0.5, **kw)
    rec(f"V5.hydrated_always_true.{label}", {"tests_gathered": o["tests_gathered"], "calls": calls[0], "evidence_count": o.get("evidence_count"), "posterior": o["posterior_probability"]})
rec("V6.empty_scope_text_overlap", sc.scope_match("", "anything"))

# ---- falsifier.py
def fals_all(**kw):
    res = collections.Counter(); outc = collections.Counter(); resist = collections.Counter(); ce = 0; errs = collections.Counter()
    for e in idx["entities"]:
        try: o = falsifier.falsify(e["id"], ontology=idx, **kw)
        except Exception as ex: errs[type(ex).__name__] += 1; continue
        if "error" in o: res["error:" + o["error"].split(" ")[0]] += 1; continue
        res["ran"] += 1; ce += o["counterexamples_generated"]; resist[str(o["falsification_resistance"])] += 1
        for d in o["details"]: outc[d.get("outcome", "survived" if d["falsification_risk"] == "low" else d["falsification_risk"])] += 1
    return {"outcomes": dict(res), "exceptions": dict(errs), "counterexamples": ce, "check_outcomes": dict(outc), "resistance_values": dict(resist)}
rec("F1.all_entities.default", fals_all())
if LEG: rec("F1.all_entities.legacy", fals_all(legacy=True))
# control: the same counterexamples searched against the full (hydrated) records, not the thin index
def fals_all_h():
    outc = collections.Counter(); resist = collections.Counter()
    for e in idx["entities"]:
        o = falsifier.falsify(e["id"], ontology=idx)
        if "error" in o: continue
        resist[str(o["falsification_resistance"])] += 1
        for d in o["details"]:
            r = falsifier.check_counterexample(d["counterexample"], hyd)
            outc[r.get("outcome") or ("survived" if r["falsification_risk"] == "low" else r["falsification_risk"])] += 1
    return {"check_outcomes_vs_hydrated": dict(outc)}
rec("F1b.search_against_full_records.default", fals_all_h())
tmp = Path(tempfile.mkdtemp()); (tmp / "e.json").write_text(json.dumps({"id": "FZ", "attributes": {"k": {"value": 1, "scope": {}}}}))
o = falsifier.falsify("FZ", ontology={"entities": [{"id": "FZ", "path": str(tmp / "e.json")}]})
rec("F2.empty_scope_fixture", pick(o, ["counterexamples_generated", "tests_survived", "falsification_resistance", "resistance_reason"]))
o = falsifier.falsify("FZ", ontology={"entities": [{"id": "FZ", "path": "does/not/exist.json"}]})
rec("F3.missing_file", pick(o, ["error", "load_failures"]))
c, o = cli(["validation/falsifier.py", "--entity", "COUNCIL"])
rec("F4.readme_example_COUNCIL", {"exit": c, **pick(o, ["error", "mode"])})

# ---- dependency_tree.py
rep = {}
g = dt.build_dependency_graph(idx, report=rep) if has_kw(dt.build_dependency_graph, "report") else dt.build_dependency_graph(idx)
link_edges = sum(1 for s, v in g.items() for t, rt in v if rt != "dependency")
dep_edges = sum(1 for s, v in g.items() for t, rt in v if rt == "dependency")
idx_set = collections.Counter((r["source"], r["target"], r["relation"]) for r in idx["relations"])
tr_set = collections.Counter((s, t, rt) for s, v in g.items() for t, rt in v if rt != "dependency")
rec("D1.edges", {"index_relations": len(idx["relations"]), "tracer_link_edges": link_edges, "tracer_scope_dependency_edges": dep_edges,
                 "in_index_not_tracer": [list(k) for k in (idx_set - tr_set)], "in_tracer_not_index": [list(k) for k in list(tr_set - idx_set)[:10]],
                 "reported_unresolved": rep.get("unresolved"), "reported_non_entity_scope_deps": len(rep.get("non_entity_scope_dependencies") or []),
                 "reported_load_failures": rep.get("load_failures")})
dropped = [(e["id"], an, d) for e in hyd["entities"] for an, av in e.get("attributes", {}).items() if sc.is_scoped(av)
           for d in av["scope"].get("dependencies", []) if d not in ids and d not in dt.ROSETTA_STONE]
rec("D2.scope_dependencies_not_entities", {"count": len(dropped), "listed_by_tracer": len(rep.get("non_entity_scope_dependencies") or [])})
o = dt.dependency_tree("WOLF_PACK", ontology=idx, max_depth=1)
rec("D3.WOLF_PACK_children", [(c["id"], c.get("relation"), c.get("type", "entity")) for c in o["tree"]["dependencies"]])
for goal in ["COUNCIL", "maintain a watershed for 7 generations"]:
    c, o = cli(["validation/dependency_tree.py", "--goal", goal])
    rec(f"D4.readme_example_goal:{goal}", {"exit": c, "error": o.get("error"), "start": o.get("start_entity")})

# ---- audit.py
a = audit.audit(idx, repo_root=ROOT)
rec("A1.real_run", {"total": a["total_entities"], "loaded": a.get("entities_loaded"), "load_failures": a.get("load_failures"),
                    "unscoped_numerics": len(a["unscoped_numerics"]), "noun_pretenders": len(a["noun_pretenders"]),
                    "contradictions": len(a["possible_contradictions"]), "missing_deps": len(a["dependency_checks"]),
                    "scoped_ratio": a["scoped_ratio"], "confidence_distribution": dict(a["confidence_distribution"])})
aud = collections.Counter((c.get("entity"), c.get("attribute"), c.get("missing_dependency")) for c in a["dependency_checks"])
trc = collections.Counter((c["source"], c["attribute"], c["dependency"]) for c in (rep.get("non_entity_scope_dependencies") or []))
rec("A1b.instrument_disagreement_same_field", {"audit_missing_deps": len(a["dependency_checks"]), "tracer_listed_non_entity": len(rep.get("non_entity_scope_dependencies") or []),
    "audit_record_keys": sorted(a["dependency_checks"][0]) if a["dependency_checks"] else None,
    "in_audit_not_tracer": [list(k) for k in (aud - trc)][:8]})
av = {"value": 1, "scope": {"evidence": {}}}
nexp = sum(1 for e in hyd["entities"] for an, v in e.get("attributes", {}).items() if sc.is_scoped(v)
           and "relational_confidence" not in v["scope"].get("evidence", {}) and "relational_confidence" not in v["scope"])
rec("A2.confidence_fallback", {"scope_checker": sc.extract_confidence(av), "audit_bucket": 0.5, "real_attrs_affected": nexp})
a = audit.audit({"entities": [{"id": "GHOST", "path": "nope.json"}]}, repo_root=ROOT)
rec("A3.missing_file", pick(a, ["total_entities", "entities_loaded", "scoped_ratio", "load_failures"]))
a = audit.audit({"entities": []}, repo_root=ROOT)
rec("A4.no_numerics_ratio", pick(a, ["scoped_ratio", "scoped_ratio_reason"]))

# ---- build_index.py (index restored byte-for-byte afterwards)
IDXF = ROOT / "ontology_index.json"; orig = IDXF.read_bytes(); h0 = hashlib.sha1(orig).hexdigest()
def build(extra=()):
    r = subprocess.run([sys.executable, "scripts/build_index.py", *extra], capture_output=True, text=True)
    return r.returncode, hashlib.sha1(IDXF.read_bytes()).hexdigest(), r.stdout
try:
    c, h, out = build()
    rb = json.loads(IDXF.read_text())
    rec("B1.rebuild", {"exit": c, "index_bytes_changed": h != h0, "entities": len(rb["entities"]), "relations": len(rb["relations"]),
                       "same_entity_ids": {e["id"] for e in rb["entities"]} == ids,
                       "relational_skipped_message": [l.strip() for l in out.splitlines() if "relational" in l.lower()][:3]})
    IDXF.write_bytes(orig)
    victim = ROOT / idx["entities"][0]["path"]; vb = victim.read_bytes()
    d = json.loads(vb); d.setdefault("links", []).append({"target": "NO_SUCH_ENTITY_X", "relation": "synergy"}); victim.write_text(json.dumps(d))
    c, h, out = build(); rec("B2.extra_broken_link", {"exit": c, "index_written": h != h0})
    IDXF.write_bytes(orig)
    if LEG:
        c, h, out = build(["--legacy"]); rec("B2.extra_broken_link.legacy", {"exit": c, "index_written": h != h0})
        IDXF.write_bytes(orig)
    victim.write_bytes(vb)
    d = json.loads(vb); d.pop("id", None); victim.write_text(json.dumps(d))
    c, h, out = build(); rb = json.loads(IDXF.read_text())
    rec("B3.record_missing_id", {"exit": c, "index_written": h != h0, "entities_in_written_index": len(rb["entities"]),
                                 "message": [l.strip() for l in out.splitlines() if "Skipping" in l][:2]})
    IDXF.write_bytes(orig); victim.write_bytes(vb)
    dup = victim.with_name("zz_recheck_duplicate.json"); dup.write_bytes(vb)
    IDXF.write_bytes(b"SENTINEL")  # a write of any content replaces this; content-hash alone cannot tell
    try:
        c, h, out = build(); rec("B4.validation_error_write_order", {"exit": c, "index_written": IDXF.read_bytes() != b"SENTINEL",
                                 "message": [l.strip() for l in out.splitlines() if "Duplicate" in l or "NOT written" in l][:3]})
    finally:
        dup.unlink(); IDXF.write_bytes(orig)
finally:
    IDXF.write_bytes(orig)
rec("B.restored", hashlib.sha1(IDXF.read_bytes()).hexdigest() == h0)

# ---- data-level ledger counts (no instrument involved)
attrs = [v for e in hyd["entities"] for v in e.get("attributes", {}).values() if sc.is_scoped(v)]
rec("L.data_counts", {"scoped_attrs": len(attrs), "single_float_value": sum(1 for v in attrs if isinstance(v.get("value"), float)),
                      "condition_block": sum(1 for v in attrs if "condition" in v["scope"]),
                      "deviation_field": sum(1 for v in attrs if "deviation" in v or "deviation" in v["scope"]),
                      "files_with_temporal_range": sum(1 for p in (ROOT / "ontology").rglob("*.json") if "temporal_range" in p.read_text())})
json.dump(R, open(os.environ.get("OUT", "recheck.json"), "w"), indent=1, ensure_ascii=False)
