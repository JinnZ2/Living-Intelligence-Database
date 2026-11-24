"""Stdlib checker for a reference dependency trace. No network. Deterministic.
Checks: node status/source rules, dangling deps, layers reached, path to D0,
cycle naming/period/parent, nesting order, timescale separation ratios."""
import json, math, sys
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
out["summary"]["cycle_span_log10_s"] = [round(math.log10(min(spans)), 2), round(math.log10(max(spans)), 2)]
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
json.dump(out, open(sys.argv[2] if len(sys.argv) > 2 else "trace_check_results.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
