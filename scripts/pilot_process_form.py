#!/usr/bin/env python3
"""Pilot conversion: BE.hexagonal_cell_efficiency -> process form, built from the v0.3 reference trace.

    python3 scripts/pilot_process_form.py            write the record into registry/process_forms.json
    python3 scripts/pilot_process_form.py --check    rebuild and compare; exit 1 if the stored record differs

Rule (registry/DECLARED.json, 'trace_check severities; status_history; reviewer slots; pilot
process form'): every value is copied from a named trace node, from registry/cycles.json or from
the entity file. Nothing is computed except graph reachability over the trace's depends_on.
A part the trace does not give is null with a reason. The stored scalar is kept beside the record
as legacy_scalar; the entity file is not edited. Stdlib only.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACE = "audit/2026-11-24/reference/reference_trace_BE_hex_v0.3.json"
ENTITY = "ontology/animal/bee.json"
ATTR = "hexagonal_cell_efficiency"
OUT = os.path.join(ROOT, "registry", "process_forms.json")
# Which trace nodes and which cycle fill which part. These are the reading; the values are the trace's.
DRIVER_NODES = ["F_FLOW", "E_BODY_HEAT", "D4_HOT_WORKERS"]
REGIME_NODE = "REGIME_HEX"
CYCLE = "CY_HEXFORM"
ERROR_FREE_INFO = {"CYCLE_NO_PERIOD", "CYCLE_TOP_LEVEL", "GAP"}


def j(rel):
    return json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))


def build():
    t, ent = j(TRACE), j(ENTITY)
    N = {n["id"]: n for n in t["nodes"]}
    C = {c["id"]: c for c in j("registry/cycles.json")["cycles"]}
    attr = ent["attributes"][ATTR]
    root = next(n for n in t["nodes"] if n["layer"] == "D5_pattern" and n.get("repo_entity") == ent["id"])
    seen, stack = [], list(root.get("depends_on", []))
    while stack:
        k = stack.pop(0)
        if k in N and k not in seen:
            seen.append(k)
            stack += N[k].get("depends_on", [])
    by_layer = {}
    for k in seen:
        by_layer.setdefault(N[k]["layer"], []).append(k)
    chain, k = [], C[CYCLE].get("parent")
    while k and k in C and k not in chain:
        chain.append(k)
        k = C[k].get("parent")
    reg = N[REGIME_NODE]
    results = j("audit/2026-11-24/reference/trace_check_results_v0.3.json")["findings"]
    conf = [r for r in j("registry/confidence_records.json")["confidence_records"]
            if r["attribute"] == "%s.%s" % (ent["id"], ATTR)]
    f = N["F_FLOW"]
    return {
        "attribute": "%s.%s" % (ent["id"], ATTR),
        "status": "PROPOSED",
        "form": {"kind": "state",
                 "quantity": attr["scope"]["definition"],
                 "value": {"y": root["value"]["y"], "node": root["id"], "node_status": root["status"]},
                 "units": None},
        "driver": "%s (%s, %s): %s Heat: %s (%s, %s)."
                  % (f["id"], f["layer"], f["status"], f["claim"], "E_BODY_HEAT", N["E_BODY_HEAT"]["layer"],
                     N["E_BODY_HEAT"]["status"]),
        "driver_nodes": [{"node": k, "layer": N[k]["layer"], "role": N[k]["role"], "status": N[k]["status"],
                          "claim": N[k]["claim"]} for k in DRIVER_NODES],
        "timescale": {"cycle_ref": CYCLE, "text": C[CYCLE]["period_text"], "nested_in": chain,
                      "note": "cycle context as recorded: %s. The cycle is the formation transient; the periods of "
                              "the enclosing cycles are in registry/cycles.json." % C[CYCLE]["context"]},
        "regime_bounds": reg["regime"]["bounds"],
        "regime": {"node": reg["id"], "status": reg["status"], "outside": reg["regime"].get("outside"),
                   "note": reg["note"]},
        "scope_ref": "%s#attributes.%s.scope" % (ENTITY, ATTR),
        "dependencies": {
            "root_node": root["id"],
            "direct": [{"node": k, "layer": N[k]["layer"], "role": N[k]["role"], "status": N[k]["status"]}
                       for k in root["depends_on"]],
            "reachable_by_layer": {k: by_layer[k] for k in sorted(by_layer)},
            "not_reached": sorted(k for k in N if k not in seen and k != root["id"])},
        "deviation": {"text": root["value"]["deviation"], "node": root["id"],
                      "confidence_record": "registry/confidence_records.json#%s" % conf[0]["attribute"] if conf else None,
                      "note": "as the trace records it; the prose it points to is quoted in the confidence record. "
                              "Not parsed into a number."},
        "being_tense": None,
        "phase_now": [],
        "carried_from_phase": [],
        "legacy_scalar": {"value": attr["value"], "source_field": "%s#attributes.%s.value" % (ENTITY, ATTR),
                          "flag": "LEGACY_SCALAR", "kept": True},
        "open_findings": [x for x in results if x[0] not in ERROR_FREE_INFO and x[1] in set(seen) | {root["id"]}],
        "trace": {"file": TRACE, "version": t["version"],
                  "sha256": hashlib.sha256(open(os.path.join(ROOT, TRACE), "rb").read()).hexdigest()},
        "source": [TRACE],
        "note": "Pilot. form.kind 'state' is this conversion's reading: the stored quantity is a ratio of a built "
                "structure; the trace does not classify it as rate or state. The value is the trace's root node, "
                "status RECORDED_UNVERIFIED. The driver is CONTESTED (four accounts kept) and the lower regime bound "
                "is CONDITIONAL on it. being_tense is null: not assessed. No number here is new."}


def dump(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    rec = build()
    doc = json.load(open(OUT, encoding="utf-8"))
    stored = [r for r in doc.get("process_forms", []) if r["attribute"] == rec["attribute"]]
    if sys.argv[1:] == ["--check"]:
        same = stored == [rec]
        print("stored pilot record matches a rebuild from the trace: %s" % ("yes" if same else "NO"))
        sys.exit(0 if same else 1)
    doc["process_forms"] = [r for r in doc.get("process_forms", []) if r["attribute"] != rec["attribute"]] + [rec]
    doc = {k: doc[k] for k in ("record", "version", "date", "status", "note", "process_forms", "phase_records") if k in doc}
    doc["note"] = doc["note"].split(" PILOT:")[0] + (" PILOT: one process_forms record, BE.hexagonal_cell_efficiency, "
                                                     "built by scripts/pilot_process_form.py from the v0.3 reference trace.")
    open(OUT, "w", encoding="utf-8").write(dump(doc))
    print("wrote the pilot record into registry/process_forms.json")
