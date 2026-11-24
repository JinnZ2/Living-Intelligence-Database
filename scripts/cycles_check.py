#!/usr/bin/env python3
"""Cycle registry: build from the reference trace, validate, check nesting.

    python3 scripts/cycles_check.py              check registry/cycles.json; exit 1 on any violation
    python3 scripts/cycles_check.py --build      write registry/cycles.json from the v0.3 reference trace
    python3 scripts/cycles_check.py --selftest

Rules: registry/DECLARED.json, amendment 'process form + Kimi schemas'.
Violations (exit 1): schema error, unnamed cycle, duplicate id, parent that does not exist,
parent loop, parent period not longer than the child's, TRACED without a source, the retired
status PROPOSED_UNSOURCED, unsourced flag on a status other than PROPOSED, PROPOSED with no
source and no unsourced flag.
Recorded gaps (listed, exit unchanged): no period, top-level cycle, ratio not computable.
Stdlib for every rule above. The JSON Schema pass needs jsonschema; without it that one
pass is reported NOT_RUN and the exit is 1, because the file was not validated.
"""
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "registry", "cycles.json")
TRACE = os.path.join(ROOT, "audit", "2026-11-24", "reference", "reference_trace_BE_hex_v0.3.json")
SCHEMA = os.path.join(ROOT, "schemas", "cycle_registry.schema.json")
STATUS = {"TRACED", "PROPOSED", "UNKNOWN"}


# Cycles that do not come from the reference trace. Each names the order that added it.
ADDED = [
    {"id": "CY_SALMON_LIFE", "name": "salmon life cycle", "kind": "life_cycle",
     "context": "example cycle from the owner's addendum of 2026-11-24 (process form: being_tense, phase_now, "
                "carried_from_phase); no population or species named",
     "period_text": "not attached", "status": "PROPOSED", "unsourced": True, "source": None,
     "phases": ["juvenile", "spawning"],
     "note": "Holds only the two phases the addendum names, in the order its example implies (juvenile is completed "
             "when spawning is now). No other phase, no period and no parent is supplied; none was typed from memory."},
]


def build():
    t = json.load(open(TRACE, encoding="utf-8"))
    cycles = []
    for c in t["cycles"]:
        c = dict(c)
        if c["status"] == "PROPOSED_UNSOURCED":          # the declared mapping
            c["legacy_status"] = c["status"]
            c["status"] = "PROPOSED"
            c["unsourced"] = True
        cycles.append(c)
    n_trace = len(cycles)
    cycles += [dict(c) for c in ADDED]
    return {"record": "CYCLE_REGISTRY_BE_HEX", "version": "0.1", "date": "2026-11-24", "status": "PROPOSED",
            "baseline_commit": t["baseline_commit"],
            "note": "The %d cycles of audit/2026-11-24/reference/reference_trace_BE_hex_v0.3.json, copied field for "
                    "field. One change: the retired status PROPOSED_UNSOURCED is written PROPOSED with unsourced "
                    "true and legacy_status kept. No period, source or parent was added or changed. These are the "
                    "cycles of one trace (honeybee comb), not a registry of every cycle in the database. "
                    "Added since, outside the trace: %s."
                    % (n_trace, ", ".join(c["id"] for c in ADDED)),
            "cycles": cycles}


def check(reg, schema_pass=True):
    viol, gaps, ladder = [], [], []
    if schema_pass:
        try:
            from jsonschema import Draft7Validator
            for e in Draft7Validator(json.load(open(SCHEMA, encoding="utf-8"))).iter_errors(reg):
                viol.append(["SCHEMA", "/".join(str(p) for p in e.absolute_path), e.message[:160]])
            schema_state = "RUN"
        except ImportError:
            schema_state = "NOT_RUN (jsonschema not installed)"
            viol.append(["SCHEMA_NOT_RUN", "", "the file was not validated against the schema"])
    else:
        schema_state = "SKIPPED (selftest)"
    ids = [c.get("id") for c in reg["cycles"]]
    for i in sorted({i for i in ids if ids.count(i) > 1}):
        viol.append(["DUPLICATE_ID", i])
    C = {c["id"]: c for c in reg["cycles"]}
    for c in reg["cycles"]:
        i, st = c["id"], c.get("status")
        if not c.get("name"):
            viol.append(["CYCLE_UNNAMED", i])
        if st == "PROPOSED_UNSOURCED":
            viol.append(["RETIRED_STATUS", i, st])
        elif st not in STATUS:
            viol.append(["BAD_STATUS", i, st])
        if st == "TRACED" and not c.get("source"):
            viol.append(["CYCLE_NO_SOURCE", i])
        if c.get("unsourced") and st != "PROPOSED":
            viol.append(["UNSOURCED_FLAG_ON", i, st])
        if st == "PROPOSED" and not c.get("source") and c.get("unsourced") is not True:
            viol.append(["PROPOSED_NO_SOURCE_NO_FLAG", i])
        par = c.get("parent")
        if par is None:
            gaps.append(["CYCLE_TOP_LEVEL", i])
        elif par not in C:
            viol.append(["CYCLE_DANGLING_PARENT", i, par])
        else:
            seen, k = {i}, par
            while k is not None and k in C and k not in seen:
                seen.add(k)
                k = C[k].get("parent")
            if k in seen:
                viol.append(["PARENT_LOOP", i, k])
            p = C[par]
            if c.get("period_s") and p.get("period_s"):
                r = p["period_s"] / c["period_s"]
                if r <= 1:
                    viol.append(["NESTING_VIOLATION", i, par, round(r, 3)])
                ladder.append({"child": i, "parent": par, "ratio": round(r, 1), "log10_separation": round(math.log10(r), 2)})
            else:
                gaps.append(["RATIO_NOT_COMPUTABLE", i, par, "period missing on %s" % (
                    "both" if not c.get("period_s") and not p.get("period_s") else i if not c.get("period_s") else par)])
        if c.get("period_s") is None:
            gaps.append(["CYCLE_NO_PERIOD", i, st])
    return {"schema_pass": schema_state, "cycles": len(reg["cycles"]), "violations": viol, "gaps": gaps,
            "status_counts": {s: sum(c.get("status") == s for c in reg["cycles"]) for s in sorted(STATUS)},
            "unsourced": [c["id"] for c in reg["cycles"] if c.get("unsourced")],
            "ladder": sorted(ladder, key=lambda x: x["log10_separation"])}


def dump(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def selftest():
    def cy(i, per, par, **kw):
        d = {"id": i, "name": i.lower(), "kind": "oscillation", "context": "constructed", "period_text": "constructed",
             "period_s": per, "parent": par, "status": "TRACED", "source": ["constructed"]}
        d.update(kw)
        return d
    base = [cy("CY_A", 1, "CY_B"), cy("CY_B", 10, None)]
    cases = [("clean pair: no violation", base, None),
             ("child slower than parent", [cy("CY_A", 20, "CY_B"), cy("CY_B", 10, None)], "NESTING_VIOLATION"),
             ("equal periods", [cy("CY_A", 10, "CY_B"), cy("CY_B", 10, None)], "NESTING_VIOLATION"),
             ("parent that does not exist", [cy("CY_A", 1, "CY_Z"), cy("CY_B", 10, None)], "CYCLE_DANGLING_PARENT"),
             ("parent loop", [cy("CY_A", 1, "CY_B"), cy("CY_B", 10, "CY_A")], "PARENT_LOOP"),
             ("retired status", base + [cy("CY_C", None, "CY_B", status="PROPOSED_UNSOURCED", source=None)], "RETIRED_STATUS"),
             ("PROPOSED, no source, no flag", base + [cy("CY_C", None, "CY_B", status="PROPOSED", source=None)],
              "PROPOSED_NO_SOURCE_NO_FLAG"),
             ("PROPOSED + unsourced flag: no violation",
              base + [cy("CY_C", None, "CY_B", status="PROPOSED", source=None, unsourced=True)], None),
             ("unsourced flag on TRACED", base + [cy("CY_C", 2, "CY_B", unsourced=True)], "UNSOURCED_FLAG_ON"),
             ("TRACED without source", base + [cy("CY_C", 2, "CY_B", source=None)], "CYCLE_NO_SOURCE"),
             ("duplicate id", base + [cy("CY_A", 2, "CY_B")], "DUPLICATE_ID")]
    ok = []
    for name, cycles, want in cases:
        codes = [v[0] for v in check({"cycles": cycles}, schema_pass=False)["violations"]]
        good = (codes == []) if want is None else (want in codes)
        ok.append(good)
        print("%s  %s  %s" % ("PASS" if good else "FAIL", name, codes))
    g = check({"cycles": [cy("CY_A", None, "CY_B"), cy("CY_B", 10, None)]}, schema_pass=False)
    good = g["violations"] == [] and sorted(x[0] for x in g["gaps"]) == ["CYCLE_NO_PERIOD", "CYCLE_TOP_LEVEL",
                                                                        "RATIO_NOT_COMPUTABLE"]
    ok.append(good)
    print("%s  a missing period is a recorded gap, not a violation and not a zero" % ("PASS" if good else "FAIL"))
    print("checks: %d   failed: %d" % (len(ok), ok.count(False)))
    return all(ok)


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(0 if selftest() else 1)
    if sys.argv[1:] == ["--build"]:
        open(REG, "w", encoding="utf-8").write(dump(build()))
        print("wrote registry/cycles.json")
    reg = json.load(open(REG, encoding="utf-8"))
    res = check(reg)
    print("cycles: %d   schema pass: %s   status: %s   unsourced: %s"
          % (res["cycles"], res["schema_pass"], res["status_counts"], res["unsourced"]))
    print("nesting ladder (parent period / child period):")
    for x in res["ladder"]:
        print("  %-16s in %-16s ratio %14.1f   log10 %.2f" % (x["child"], x["parent"], x["ratio"], x["log10_separation"]))
    print("recorded gaps (%d):" % len(res["gaps"]))
    for g in res["gaps"]:
        print("  " + "  ".join(str(x) for x in g))
    print("violations (%d):" % len(res["violations"]))
    for v in res["violations"]:
        print("  " + "  ".join(str(x) for x in v))
    sys.exit(1 if res["violations"] else 0)
