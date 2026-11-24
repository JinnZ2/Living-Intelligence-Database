#!/usr/bin/env python3
"""Run every reference-trace check and print one line each.

    python3 run_all.py            exit 1 if any line fails

  pins        each trace against the schema it is pinned to (validate_pins.py)
  historical  a trace with superseded_by in schema_pins.json: rerun trace_check.py with
              LID_HISTORICAL=1; PASS iff the findings list equals the stored one exactly
  current     the trace with superseded_by null: PASS iff trace_check.py reports 0 ERROR,
              and its stored findings also reproduce
Rule: registry/DECLARED.json, 'close-out: ...'. Stdlib only (validate_pins.py needs jsonschema).
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    rows = []
    r = subprocess.run([sys.executable, os.path.join(HERE, "validate_pins.py")], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.startswith(("PASS", "FAIL", "NOT_RUN")):
            rows.append(("pin", line.split()[0], line[5:].strip()))
    pins = json.load(open(os.path.join(HERE, "schema_pins.json")))["pins"]
    for p in pins:
        hist = p["superseded_by"] is not None
        env = {k: v for k, v in os.environ.items() if k not in ("LID_STRICT", "LID_HISTORICAL")}
        if hist:
            env["LID_HISTORICAL"] = "1"
        with tempfile.TemporaryDirectory() as t:
            dst = os.path.join(t, "out.json")
            c = subprocess.run([sys.executable, os.path.join(HERE, "trace_check.py"), os.path.join(HERE, p["trace"]), dst],
                               capture_output=True, text=True, env=env)
            got = json.load(open(dst))["findings"]
        stored = json.load(open(os.path.join(HERE, p["results"])))["findings"]
        counts = c.stderr.splitlines()[0].strip() if c.stderr else "no severity line"
        same = got == stored
        if hist:
            ok = same
            what = "v%s historical (superseded by %s): stored findings reproduce: %s; %s; exit %d" % (
                p["trace_version"], p["superseded_by"], "yes" if same else "NO", counts, c.returncode)
        else:
            ok = c.returncode == 0 and same
            what = "v%s current: %s; exit %d; stored findings reproduce: %s" % (
                p["trace_version"], counts, c.returncode, "yes" if same else "NO")
        rows.append(("trace", "PASS" if ok else "FAIL", what))
    current = [p for p in pins if p["superseded_by"] is None]
    rows.append(("shape", "PASS" if len(current) == 1 else "FAIL", "exactly one current trace: %d" % len(current)))
    for kind, state, what in rows:
        print("%-5s %-7s %s" % (kind, state, what))
    bad = sum(state != "PASS" for _, state, _ in rows)
    print("lines: %d   failing: %d" % (len(rows), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
