"""Stdlib checker for a reference dependency trace. No network. Deterministic.
Checks: node status/source rules, dangling deps, layers reached, path to D0,
cycle naming/period/parent, nesting order, timescale separation ratios."""
import json, math, os, sys   # os: 2026-11-24, the exit lines below used it without an import when a trace had no repo_bindings (v0.1 crashed with NameError after writing its output)
# 2026-11-24 (order 'process form + Kimi schemas'): --selftest. Runs this same file on a
# clean constructed trace (must exit 0) and on one with a dangling dependency (must exit 1).
if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
    import subprocess, tempfile
    node = lambda i, layer, deps: {"id": i, "layer": layer, "status": "TRACED", "source": ["constructed"], "depends_on": deps}
    cyc = lambda i, per, par: {"id": i, "name": i.lower(), "period_s": per, "parent": par, "status": "TRACED", "source": ["constructed"]}
    clean = {"record": "SELFTEST", "nodes": [node("P", "D5_pattern", ["L"]), node("L", "D0_law", [])], "cycles": []}
    dirty = {"record": "SELFTEST", "nodes": [node("P", "D5_pattern", ["L", "MISSING"]), node("L", "D0_law", [])], "cycles": []}
    nest = {"record": "SELFTEST", "nodes": clean["nodes"], "cycles": [cyc("CY_A", 10, "CY_B"), cyc("CY_B", 5, None)]}
    ok = []
    with tempfile.TemporaryDirectory() as t:
        info = {"record": "SELFTEST", "nodes": [node("P", "D5_pattern", ["L"]), dict(node("L", "D0_law", []), note="GAP: constructed")],
                "cycles": [cyc("CY_A", None, "CY_B"), cyc("CY_B", 5, None)]}
        nosrc = {"record": "SELFTEST", "nodes": [node("P", "D5_pattern", ["L"]), dict(node("L", "D0_law", []), source=[])], "cycles": []}
        mism = {"record": "SELFTEST", "nodes": [node("P", "D5_pattern", ["L"]), dict(node("L", "D0_law", []), note="x -> CITATION_MISMATCH")], "cycles": []}
        other = {"record": "SELFTEST", "nodes": [node("P", "D5_pattern", ["L"]), dict(node("L", "D0_law", []), status="VERIFIED")], "cycles": []}
        prop_cyc = {"record": "SELFTEST", "nodes": clean["nodes"],
                    "cycles": [dict(cyc("CY_A", 5, "CY_B"), status="PROPOSED", source=None, unsourced=True), cyc("CY_B", 50, None)]}
        traced_cyc = {"record": "SELFTEST", "nodes": clean["nodes"], "cycles": [dict(cyc("CY_A", 5, None), source=None)]}
        mism2 = {"record": "SELFTEST", "nodes": [node("P", "D5_pattern", ["L"]), dict(node("L", "D0_law", []), note="x -> SCOPE_MISMATCH")], "cycles": []}
        for name, rec_, want, must in (("clean trace exits 0", clean, 0, None),
                                       ("dangling dependency exits 1", dirty, 1, "DANGLING_DEP"),
                                       ("nesting violation exits 1", nest, 1, "NESTING_VIOLATION"),
                                       ("INFO-only trace (GAP, no period, top-level cycle) exits 0", info, 0, "CYCLE_NO_PERIOD"),
                                       ("TRACED node without a source exits 1", nosrc, 1, "NO_SOURCE"),
                                       ("noted CITATION_MISMATCH exits 1", mism, 1, "NOTED_MISMATCH"),
                                       ("BAD_STATUS exits 1", other, 1, "BAD_STATUS"),
                                       ("PROPOSED cycle without a source: CYCLE_NO_SOURCE is INFO, exits 0", prop_cyc, 0, "CYCLE_NO_SOURCE"),
                                       ("TRACED cycle without a source: CYCLE_NO_SOURCE is ERROR, exits 1", traced_cyc, 1, "CYCLE_NO_SOURCE"),
                                       ("noted SCOPE_MISMATCH exits 1", mism2, 1, "NOTED_MISMATCH")):
            src, dst = os.path.join(t, "in.json"), os.path.join(t, "out.json")
            json.dump(rec_, open(src, "w"))
            r = subprocess.run([sys.executable, os.path.abspath(__file__), src, dst], capture_output=True, text=True,
                               env={k: v for k, v in os.environ.items() if k != "LID_STRICT"})
            got = [f[0] for f in json.load(open(dst))["findings"]]
            # only the named finding is asserted; the INFO-only case asserts its whole set
            good = r.returncode == want and (must is None or must in got) and (want == 1 or must is not None or got == [])
            if name.startswith("INFO-only"):
                good = good and sorted(set(got)) == ["CYCLE_NO_PERIOD", "CYCLE_TOP_LEVEL", "GAP"]
            ok.append(good)
            print("%s  %s  (exit %d, findings %s)" % ("PASS" if good else "FAIL", name, r.returncode, got))
        # 2026-11-24 (order 'pins + entity correction'): ENTITY_TRACE_DIVERGENCE, against a constructed entity file
        hist = [{"version": "0", "status": "TRACED", "note": "record cites x -> CITATION_MISMATCH"}]
        div = {"record": "SELFTEST", "subject": {"entity": "E", "attribute": "a"},
               "nodes": [node("P", "D5_pattern", ["L"]), dict(node("L", "D0_law", []), status_history=hist)], "cycles": []}
        ent = lambda ev: {"id": "E", "attributes": {"a": {"value": 1, "scope": {"evidence": ev}}}}
        for name, entity, want, has in (("correction in the trace, none on the entity: ENTITY_TRACE_DIVERGENCE, exits 1", ent({"source": "s"}), 1, True),
                                        ("entity carries the correction: no divergence, exits 0", ent({"source": "s", "correction": {"source": "c", "scope": "2D"}}), 0, False),
                                        ("correction without a scope does not count as carried, exits 1", ent({"source": "s", "correction": {"source": "c", "scope": ""}}), 1, True)):
            src, dst, ef = os.path.join(t, "in.json"), os.path.join(t, "out.json"), os.path.join(t, "entity.json")
            json.dump(div, open(src, "w")); json.dump(entity, open(ef, "w"))
            r = subprocess.run([sys.executable, os.path.abspath(__file__), src, dst], capture_output=True, text=True,
                               env=dict({k: v for k, v in os.environ.items() if k != "LID_STRICT"}, LID_ENTITY_FILE=ef))
            got = [f[0] for f in json.load(open(dst))["findings"]]
            good = r.returncode == want and (("ENTITY_TRACE_DIVERGENCE" in got) == has)
            ok.append(good)
            print("%s  %s  (exit %d, findings %s)" % ("PASS" if good else "FAIL", name, r.returncode, got))
    print("checks: %d   failed: %d" % (len(ok), ok.count(False)))
    sys.exit(0 if all(ok) else 1)
rec = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "reference_trace_BE_hex.json"))
N = {n["id"]: n for n in rec["nodes"]}; C = {c["id"]: c for c in rec["cycles"]}
out = {"record": rec["record"], "findings": [], "summary": {}}
F = out["findings"].append
STAT = {"TRACED", "DERIVED", "PROPOSED", "UNKNOWN", "CONTESTED", "RECORDED_UNVERIFIED"}
for n in N.values():
    if n["status"] not in STAT: F(["BAD_STATUS", n["id"], n["status"]])
    if n["status"] in {"TRACED", "DERIVED", "CONTESTED"} and not n.get("source"): F(["NO_SOURCE", n["id"]])
    for d in n.get("depends_on", []):
        if d not in N: F(["DANGLING_DEP", n["id"], d])
    import re
    for m in re.findall(r"[A-Z_]+_MISMATCH", n.get("note", "")): F(["NOTED_MISMATCH", n["id"], m])
    if "GAP" in n.get("note", ""): F(["GAP", n["id"], n["note"]])
# paths from root pattern
root = [n for n in N.values() if n["layer"] == "D5_pattern"][0]["id"]
def paths(i, seen=()):
    deps = [d for d in N[i].get("depends_on", []) if d in N and d not in seen]
    if not deps: return [[i]]
    return [[i] + p for d in deps for p in paths(d, seen + (i,))]
P = paths(root)
leaf_layers = {}
for p in P: leaf_layers.setdefault(N[p[-1]]["layer"], []).append(" > ".join(p))
weak = [p for p in P if any(N[x]["status"] in {"PROPOSED", "UNKNOWN"} for x in p[1:])]
out["summary"]["layers_present"] = sorted({n["layer"] for n in N.values()})
out["summary"]["paths_total"] = len(P)
out["summary"]["paths_ending_at_D0"] = sum(N[p[-1]]["layer"] == "D0_law" for p in P)
out["summary"]["paths_ending_elsewhere"] = {k: v for k, v in leaf_layers.items() if k != "D0_law"}
out["summary"]["paths_through_PROPOSED_or_UNKNOWN"] = len(weak)
out["summary"]["status_counts"] = {s: sum(n["status"] == s for n in N.values()) for s in sorted(STAT)}
# cycles
for c in C.values():
    if not c.get("name"): F(["CYCLE_UNNAMED", c["id"]])
    if c.get("period_s") is None: F(["CYCLE_NO_PERIOD", c["id"], c["status"]])
    if c["status"] == "TRACED" and not c.get("source"): F(["CYCLE_NO_SOURCE", c["id"]])
    # 2026-11-24 (order 'trace v0.4'): also raised for a PROPOSED cycle with no source, as INFO.
    # The status is written into the finding; the TRACED form above is unchanged.
    if c["status"] == "PROPOSED" and not c.get("source"): F(["CYCLE_NO_SOURCE", c["id"], "PROPOSED"])
    if c.get("parent") and c["parent"] not in C: F(["CYCLE_DANGLING_PARENT", c["id"], c["parent"]])
    if c.get("parent") is None: F(["CYCLE_TOP_LEVEL", c["id"], c["name"]])
ladder = []
for c in C.values():
    p = C.get(c.get("parent"))
    if p and c.get("period_s") and p.get("period_s"):
        r = p["period_s"] / c["period_s"]
        if r <= 1: F(["NESTING_VIOLATION", c["id"], p["id"], round(r, 3)])
        ladder.append({"child": c["name"], "parent": p["name"], "ratio": round(r, 1), "log10_separation": round(math.log10(r), 2)})
    elif p:
        ladder.append({"child": c["name"], "parent": p["name"], "ratio": None, "log10_separation": None, "reason": "period missing on one side"})
out["summary"]["cycle_ladder"] = sorted(ladder, key=lambda x: (x["log10_separation"] is None, x["log10_separation"] or 0))
spans = [c["period_s"] for c in C.values() if c.get("period_s")]
out["summary"]["cycle_span_log10_s"] = [round(math.log10(min(spans)), 2), round(math.log10(max(spans)), 2)] if spans else None   # 2026-11-24: None when no cycle has a period (was a crash)
# --- optional v0.2 sections -------------------------------------------------
def reaches_D0(i, seen=()):
    if N[i]["layer"] == "D0_law": return True
    return any(reaches_D0(d, seen + (i,)) for d in N[i].get("depends_on", []) if d in N and d not in seen)
ED = rec.get("environment_differential")
if ED:
    for k in list(ED.get("invariant_nodes", {})) + list(ED.get("unknown_dependence", {})):
        if k not in N: F(["DIFF_UNKNOWN_NODE", k])
    for v in ED.get("variant_nodes", []):
        if not v.get("source"): F(["DIFF_NO_SOURCE", v["node"]])
        for r in ED["regimes"]:
            if r not in v: F(["DIFF_REGIME_MISSING", v["node"], r])
    for z in ED.get("sensitivities", []):
        miss = [f for f in ("of", "to", "sign", "scope", "source") if not z.get(f)]
        if miss: F(["SENSITIVITY_INCOMPLETE", z.get("of"), miss])
    roots = [i for i in N if N[i]["layer"] in ("D4_entity", "D3_material") and i not in {"D4_FLOWERS", "D4_HOT_WORKERS", "M_WAX", "M_GLANDS"}]
    out["summary"]["differential"] = {
        "invariant": len(ED.get("invariant_nodes", {})), "unknown_dependence": len(ED.get("unknown_dependence", {})),
        "variant": len(ED.get("variant_nodes", [])), "sensitivities": len(ED.get("sensitivities", [])),
        "sensitivity_signs": [z["sign"] for z in ED.get("sensitivities", [])],
        "new_roots_reach_D0": {i: reaches_D0(i) for i in roots}}
RB = rec.get("repo_bindings")
if RB:
    import os
    # 2026-11-24: when posted at audit/2026-11-24/reference/ the repository file sits
    # three levels up; that path is tried after LID_BEE and before the original default.
    _repo_rel = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..",
                             "ontology", "animal", "bee.json")
    bee = os.environ.get("LID_BEE") or (_repo_rel if os.path.exists(_repo_rel)
                                        else "/home/user/workspace/lid/ontology/animal/bee.json")
    attrs = json.load(open(bee))["attributes"] if os.path.exists(bee) else None
    bound = unbound = 0
    for b in RB:
        for t in b["binds_to"]:
            if t not in N and t not in C: F(["BINDING_TARGET_MISSING", b["repo_dependency"], t])
        if attrs is not None:
            deps = attrs.get(b["attribute"], {}).get("scope", {}).get("dependencies", [])
            if b["repo_dependency"] not in deps: F(["BINDING_STRING_NOT_IN_REPO", b["attribute"], b["repo_dependency"]])
        bound += bool(b["binds_to"]); unbound += not b["binds_to"]
    out["summary"]["repo_bindings"] = {"checked_against": bee if attrs is not None else "NOT_AVAILABLE", "bound": bound, "unbound": unbound}
# --- ENTITY_TRACE_DIVERGENCE (2026-11-24, registry/DECLARED.json, 'schema 0.2.0 and 0.4.0; ...') ---
# The trace records a correction (a *_MISMATCH word in a node's note or in a status_history note)
# that the entity's attribute does not carry (scope.evidence.correction with source and scope).
# Presence only: the text of the correction is not compared. Runs when the trace names a subject.
SUBJ = rec.get("subject")
if SUBJ:
    import re as _re
    _root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
    _ef = os.environ.get("LID_ENTITY_FILE")
    if not _ef:
        try:
            _ix = json.load(open(os.path.join(_root, "ontology_index.json")))
            _ef = next((os.path.join(_root, e["path"]) for e in _ix["entities"] if e["id"] == SUBJ["entity"]), None)
        except (OSError, ValueError):
            _ef = None
    recorded = [n["id"] for n in N.values()
                if _re.search(r"[A-Z_]+_MISMATCH", " ".join([n.get("note", "")] + [h.get("note", "") for h in n.get("status_history", [])]))]
    if _ef and os.path.exists(_ef):
        _ev = json.load(open(_ef)).get("attributes", {}).get(SUBJ["attribute"], {})
        _ev = (_ev.get("scope", {}) if isinstance(_ev, dict) else {}).get("evidence", {}) or {}
        _c = _ev.get("correction") or {}
        carried = bool(_c.get("source")) and bool(_c.get("scope"))
        if not carried:
            for i in recorded: F(["ENTITY_TRACE_DIVERGENCE", i, "%s.%s" % (SUBJ["entity"], SUBJ["attribute"])])
        out["summary"]["entity_trace_divergence"] = {"state": "CHECKED", "correction_recorded_by": recorded, "entity_carries_correction": carried}
    else:
        out["summary"]["entity_trace_divergence"] = {"state": "NOT_RUN", "reason": "entity file not available", "correction_recorded_by": recorded}
json.dump(out, open(sys.argv[2] if len(sys.argv) > 2 else "trace_check_results.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))

# 2026-11-24 note: opt-in loud exit. LID_STRICT=1 exits 1 if there are any findings.
# The default exit (0) and the output file are unchanged, so earlier results stay reproducible.
# Raised by an outside reader (Kimi, 2026-11-25): findings were silent to CI.
if os.environ.get("LID_STRICT") == "1" and out["findings"]:
    print(f"STRICT: {len(out['findings'])} findings", file=sys.stderr)
    sys.exit(1)

# 2026-11-24, later (order 'process form + Kimi schemas'): any finding exited 1.
# 2026-11-24, follow-up order (registry/DECLARED.json, 'trace_check severities; ...'): severities.
# ERROR exits 1. INFO is reported and exits 0. A code with no declared severity is ERROR.
# The findings list and the output file are unchanged; severities are printed to stderr.
# 2026-11-24, order 'trace v0.4' (registry/DECLARED.json, 'trace v0.4: severity assignment; ...'):
# the owner assigned the codes left open: BAD_STATUS, CYCLE_UNNAMED, CYCLE_DANGLING_PARENT, DIFF_*,
# SENSITIVITY_INCOMPLETE and every *_MISMATCH are ERROR. CYCLE_NO_SOURCE is ERROR for a TRACED
# cycle and INFO for a PROPOSED one. Any other code is ERROR.
INFO = {"CYCLE_NO_PERIOD", "CYCLE_TOP_LEVEL", "GAP"}
def severity(f):
    if f[0] == "CYCLE_NO_SOURCE":
        return "INFO" if len(f) > 2 and f[2] == "PROPOSED" else "ERROR"
    return "INFO" if f[0] in INFO else "ERROR"
_err = [f for f in out["findings"] if severity(f) == "ERROR"]
_inf = [f for f in out["findings"] if severity(f) == "INFO"]
print("ERROR %d   INFO %d" % (len(_err), len(_inf)), file=sys.stderr)
for f in _err: print("  ERROR  " + "  ".join(str(x) for x in f[:3]), file=sys.stderr)
for f in _inf: print("  INFO   " + "  ".join(str(x) for x in f[:2]), file=sys.stderr)
sys.exit(1 if _err else 0)
