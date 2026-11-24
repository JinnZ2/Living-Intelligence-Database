#!/usr/bin/env python3
"""Validate every reference trace against the schema version it is pinned to.

    python3 validate_pins.py            validate; exit 1 if any trace fails its pin
    python3 validate_pins.py --write    also (re)write schema_pins.json from the PINS table below

Rule (registry/DECLARED.json, 'trace v0.4: severity assignment; schema pinning; ...'):
v0.1-v0.3 are pinned to the schema as received (0.1.0, Kimi); v0.4 and later to the adopted
0.3.0. Amended the same day ('schema 0.2.0 and 0.4.0; ...'): v0.3 -> 0.2.0 (as received plus
status_history); v0.4 -> the frozen 0.3.0 copy; v0.5 -> 0.4.0.
Close-out order: the 0.2.0 label is renamed 0.1.0+status_history (bytes unchanged); v0.5 -> the
frozen 0.4.0 copy; v0.6 -> 0.5.0; each entry carries its results file and superseded_by. A trace that fails its pin is reported as failing. It is never moved to another pin.
Needs jsonschema (as scripts/build_index.py does); without it the result is NOT_RUN, exit 2.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
AS_RECEIVED = "audit/2026-11-24/kimi_2026-11-25/lid-schema-additions/schemas/reference_trace.schema.json"
ADOPTED = "schemas/reference_trace.schema.json"
S01SH = "schemas/pinned/reference_trace.0.1.0+status_history.schema.json"
S030 = "schemas/pinned/reference_trace.0.3.0.schema.json"
S040 = "schemas/pinned/reference_trace.0.4.0.schema.json"
# (trace file, trace version, schema label, kind, schema file, stored results file, superseded_by)
PINS = [
    ("reference_trace_BE_hex.json", "0.1", "0.1.0", "as received (Kimi)", AS_RECEIVED, "trace_check_results.json", "0.2"),
    ("reference_trace_BE_hex_v0.2.json", "0.2", "0.1.0", "as received (Kimi)", AS_RECEIVED, "trace_check_results_v0.2.json", "0.3"),
    ("reference_trace_BE_hex_v0.3.json", "0.3", "0.1.0+status_history", "as received + status_history", S01SH, "trace_check_results_v0.3.json", "0.4"),
    ("reference_trace_BE_hex_v0.4.json", "0.4", "0.3.0", "adopted, frozen copy", S030, "trace_check_results_v0.4.json", "0.5"),
    ("reference_trace_BE_hex_v0.5.json", "0.5", "0.4.0", "adopted, frozen copy", S040, "trace_check_results_v0.5.json", "0.6"),
    ("reference_trace_BE_hex_v0.6.json", "0.6", "0.5.0", "adopted", ADOPTED, "trace_check_results_v0.6.json", None),
]
FORMER_LABEL = {"0.1.0+status_history": "0.2.0"}   # close-out order: label renamed, bytes and sha256 unchanged


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def pins_doc():
    return {"record": "REFERENCE_TRACE_SCHEMA_PINS", "date": "2026-11-24", "status": "PROPOSED",
            "rule": "each trace file is validated against the one schema version named here; v0.1-v0.3 are not "
                    "edited, so their pin is written in this file only",
            "note": "the as-received schema file carries no version field; 0.1.0 is the name the owner's order "
                    "gives it. The other schemas' versions are read from their x-lid blocks. A pin names its "
                    "schema by file and sha256. The schema labelled 0.1.0+status_history was first "
                    "labelled 0.2.0 and its file still says so inside (bytes unchanged).",
            "modes": "a trace with superseded_by is historical: it passes iff rerunning the checker reproduces "
                     "its stored findings exactly. The one trace with superseded_by null is current: 0 ERROR.",
            "pins": [dict({"trace": t, "trace_version": v, "schema_version": sv, "schema_kind": kind, "schema": s,
                           "schema_sha256": sha(s), "results": res, "superseded_by": sup},
                          **({"former_label": FORMER_LABEL[sv]} if sv in FORMER_LABEL else {}))
                     for t, v, sv, kind, s, res, sup in PINS]}


def main():
    if "--write" in sys.argv:
        json.dump(pins_doc(), open(os.path.join(HERE, "schema_pins.json"), "w"), indent=1)
        open(os.path.join(HERE, "schema_pins.json"), "a").write("\n")
    doc = json.load(open(os.path.join(HERE, "schema_pins.json")))
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        print("NOT_RUN: jsonschema is not installed")
        return 2
    bad = 0
    for p in doc["pins"]:
        schema = json.load(open(os.path.join(ROOT, p["schema"]), encoding="utf-8"))
        trace = json.load(open(os.path.join(HERE, p["trace"]), encoding="utf-8"))
        problems = []
        if sha(p["schema"]) != p["schema_sha256"]:
            problems.append("schema file changed since it was pinned")
        if trace.get("version") != p["trace_version"]:
            problems.append("trace version is %r" % trace.get("version"))
        declared = schema.get("x-lid", {}).get("version")
        if declared is not None and declared not in (p["schema_version"], p.get("former_label")):
            problems.append("schema file says version %s" % declared)
        errs = sorted(Draft7Validator(schema).iter_errors(trace), key=lambda e: list(e.absolute_path))
        problems += ["%s: %s" % ("/".join(str(x) for x in e.absolute_path) or "(top)", e.message[:110]) for e in errs]
        bad += bool(problems)
        print("%-4s v%s vs %s %s: %d problem(s)" % ("PASS" if not problems else "FAIL", p["trace_version"],
                                                    p["schema_version"], p["schema_kind"], len(problems)))
        for x in problems[:12]:
            print("       " + x)
    print("pins: %d   failing: %d" % (len(doc["pins"]), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
