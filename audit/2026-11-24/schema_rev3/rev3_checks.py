#!/usr/bin/env python3
"""rev3_checks.py -- known-answer checks for findings R1-R3, run against rev2, rev3 and a rev3 with
status_history stripped. Needs jsonschema (Draft7Validator). Deterministic.

  python3 rev3_checks.py [--suite]    --suite also runs Kimi's 36-check suite against rev3

R1  history-entry date: what must be accepted and rejected.
R2  top-level date: rejected without a format checker.
R3  each of the five negative cases in Kimi's section 9 is rejected for its own reason: the check
    names the validator keyword and the instance path it expects, not "some error happened".
Expected (declared before running): rev3 passes every check; rev2 fails R1 and R2 and passes R3;
the stripped rev3 fails R3 (it rejects for the wrong reason, additionalProperties).
Trace: ../reference/reference_trace_BE_hex_v0.3.json. Exit 0 = every schema behaved as expected.
"""
import copy, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
from jsonschema import Draft7Validator

HERE = Path(__file__).resolve().parent
AUD = HERE.parent
TRACE = json.loads((AUD / "reference" / "reference_trace_BE_hex_v0.3.json").read_text())
REV2 = json.loads((AUD / "kimi_2026-11-25_rev2" / "reference_trace.schema.rev2.json").read_text())
REV3 = json.loads((HERE / "reference_trace.schema.rev3.json").read_text())
N = 5  # the node Kimi's suite edits (C_FLOW_T, carries status_history)


def strip(o):
    if isinstance(o, dict):
        o.pop("status_history", None)
        for v in o.values():
            strip(v)
    elif isinstance(o, list):
        for v in o:
            strip(v)
    return o


def with_hist_date(d):
    x = copy.deepcopy(TRACE); x["nodes"][N]["status_history"][0]["date"] = d; return x


def with_top_date(d):
    x = copy.deepcopy(TRACE); x["date"] = d; return x


def errs(schema, inst):
    return list(Draft7Validator(schema).iter_errors(inst))


def checks(schema):
    out = []
    def c(group, name, ok, seen=""):
        out.append((group, name, bool(ok), seen))
    for d in ["2026-11-24", "2026-02-30"]:
        e = errs(schema, with_hist_date(d)); c("R1", f"history date {d!r} accepted", not e, e[:1])
    for d in ["2026-13-45", "0000-00-00", "２０２６-１１-２４", "2026-11-24\n", "2026-1-24"]:
        c("R1", f"history date {d!r} rejected", errs(schema, with_hist_date(d)))
    c("R2", "top-level date '2026-11-24' accepted", not errs(schema, with_top_date("2026-11-24")))
    for d in ["not a date", "2026-99-99"]:
        c("R2", f"top-level date {d!r} rejected (no format checker)", errs(schema, with_top_date(d)))
    base = ["nodes", N, "status_history"]
    cases = []
    x = with_hist_date("24 Nov 2026"); cases.append(("malformed date", x, "pattern", base + [0, "date"]))
    x = copy.deepcopy(TRACE); x["nodes"][N]["status_history"] = "was TRACED in 0.2"; cases.append(("history as string", x, "type", base))
    x = copy.deepcopy(TRACE); x["nodes"][N]["status_history"][0]["status"] = "HALF_TRACED"; cases.append(("out-of-vocabulary status", x, "enum", base + [0, "status"]))
    x = copy.deepcopy(TRACE); x["nodes"][N]["status_history"] = []; cases.append(("empty history", x, "minItems", base))
    x = copy.deepcopy(TRACE); del x["nodes"][N]["status_history"][0]["version"]; cases.append(("entry missing version", x, "required", base + [0]))
    for name, inst, kw, path in cases:
        e = errs(schema, inst)
        hit = any(er.validator == kw and list(er.absolute_path) == path for er in e)
        c("R3", f"{name}: rejected by '{kw}' at {'/'.join(map(str, path))}", hit,
          [(er.validator, "/".join(map(str, er.absolute_path))) for er in e[:2]])
    return out


def suite_on(schema_path):
    pkg = AUD / "kimi_2026-11-25" / "lid-schema-additions"
    suite = AUD / "kimi_2026-11-25_rev2" / "validate_loud.36checks.py"
    tmp = Path(tempfile.mkdtemp(prefix="rev3_"))
    try:
        shutil.copytree(pkg, tmp / "pkg")
        shutil.copy(schema_path, tmp / "pkg" / "schemas" / "reference_trace.schema.json")
        os.makedirs("/tmp/audit/lid_audit", exist_ok=True)
        if not Path("/tmp/audit/lid_audit/reference").exists():
            shutil.copytree(AUD / "reference", "/tmp/audit/lid_audit/reference")
        r = subprocess.run([sys.executable, str(suite), str(tmp / "pkg")], capture_output=True, text=True)
        return r.returncode, (r.stdout.strip().splitlines() or [""])[-1]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    expect = {"rev3": {"R1": True, "R2": True, "R3": True},
              "rev2": {"R1": False, "R2": False, "R3": True},
              "rev3_stripped": {"R3": False}}
    schemas = {"rev3": REV3, "rev2": REV2, "rev3_stripped": strip(copy.deepcopy(REV3))}
    bad = 0; report = {}
    for label, s in schemas.items():
        rows = checks(s); report[label] = rows
        for grp, want in expect[label].items():
            got = all(ok for g, _, ok, _ in rows if g == grp)
            flag = "as expected" if got == want else "UNEXPECTED"
            bad += got != want
            print(f"{label:14s} {grp}: {'all pass' if got else 'some fail':9s} ({flag})")
        for g, n, ok, seen in rows:
            if not ok and label == "rev3":
                print(f"   FAIL rev3 {g} {n} {seen}")
    if "--suite" in sys.argv:
        code, last = suite_on(HERE / "reference_trace.schema.rev3.json")
        print(f"Kimi 36-check suite on rev3: exit {code} :: {last}")
        bad += code != 0
    print("rev3_checks:", "OK" if not bad else f"{bad} UNEXPECTED")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
