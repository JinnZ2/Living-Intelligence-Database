#!/usr/bin/env python3
"""Process-form flag: is an attribute stored as a process (dX/dt) or as a bare scalar?

    python3 scripts/process_form.py             report; exit 0 (a legacy scalar is a flag, not an error)
    python3 scripts/process_form.py --selftest

Rule (registry/DECLARED.json, amendment 'process form + Kimi schemas'): an attribute is a
process form when it carries process_form = {form {kind rate|state, quantity}, driver,
timescale {cycle_ref or text}, regime_bounds, scope_ref}. Anything else is LEGACY_SCALAR.
A process_form block with a missing part is INCOMPLETE and names the part.
A record in registry/process_forms.json counts for its attribute, provided the stored scalar
is kept beside it as legacy_scalar; the entity file is not edited.
Reads entity files; writes nothing. Stdlib only.
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = ("form", "driver", "timescale", "regime_bounds", "scope_ref")


def classify(attr):
    pf = attr.get("process_form") if isinstance(attr, dict) else None
    if not isinstance(pf, dict):
        return "LEGACY_SCALAR", []
    missing = [p for p in PARTS if p not in pf]
    form = pf.get("form")
    if not (isinstance(form, dict) and form.get("kind") in ("rate", "state") and form.get("quantity")):
        missing.append("form.kind/quantity")
    ts = pf.get("timescale")
    if "timescale" in pf and not (isinstance(ts, dict) and (ts.get("cycle_ref") or ts.get("text"))):
        missing.append("timescale.cycle_ref or text")
    return ("INCOMPLETE", sorted(set(missing))) if missing else ("PROCESS_FORM", [])


def registry_forms():
    """entity.attribute -> process_forms record in registry/process_forms.json (the entity file keeps its scalar)."""
    try:
        doc = json.load(open(os.path.join(ROOT, "registry", "process_forms.json"), encoding="utf-8"))
    except (IOError, OSError):
        return {}
    return {r["attribute"]: r for r in doc.get("process_forms", [])}


def survey():
    reg = registry_forms()
    rows = []
    for path in sorted(glob.glob(os.path.join(ROOT, "ontology", "*", "*.json"))):
        ent = json.load(open(path, encoding="utf-8"))
        for name, a in (ent.get("attributes") or {}).items():
            state, missing = classify(a)
            r = reg.get("%s.%s" % (ent.get("id"), name))
            if state == "LEGACY_SCALAR" and r is not None:
                state, missing = classify({"process_form": r})
                if state == "PROCESS_FORM" and not (r.get("legacy_scalar") or {}).get("flag") == "LEGACY_SCALAR":
                    state, missing = "INCOMPLETE", ["legacy_scalar (the stored scalar must be kept beside the form)"]
            rows.append((os.path.relpath(path, ROOT), ent.get("id"), name, state, missing))
    return rows


def selftest():
    full = {"value": 0.9, "process_form": {"form": {"kind": "rate", "quantity": "wax scales per worker"},
            "driver": "gland age", "timescale": {"cycle_ref": "CY_SCALE"}, "regime_bounds": None, "scope_ref": "x"}}
    part = {"value": 0.9, "process_form": {"form": {"kind": "rate", "quantity": "q"}, "driver": None}}
    ok = [("a bare scalar is LEGACY_SCALAR", classify({"value": 0.9, "scope": {}}) == ("LEGACY_SCALAR", [])),
          ("a full block is PROCESS_FORM (null driver or bounds allowed: recorded as not known)",
           classify(full) == ("PROCESS_FORM", [])),
          ("a partial block is INCOMPLETE and names the parts",
           classify(part) == ("INCOMPLETE", ["regime_bounds", "scope_ref", "timescale"])),
          ("a form that is neither rate nor state is INCOMPLETE",
           classify({"process_form": dict(full["process_form"], form={"kind": "score", "quantity": "q"})})[0]
           == "INCOMPLETE")]
    for name, good in ok:
        print("%s  %s" % ("PASS" if good else "FAIL", name))
    print("checks: %d   failed: %d" % (len(ok), sum(not g for _, g in ok)))
    return all(g for _, g in ok)


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(0 if selftest() else 1)
    rows = survey()
    for state in ("PROCESS_FORM", "INCOMPLETE", "LEGACY_SCALAR"):
        print("%-14s %d of %d attributes" % (state, sum(r[3] == state for r in rows), len(rows)))
    for r in rows:
        if r[3] == "PROCESS_FORM":
            print("  %s.%s  (record in registry/process_forms.json; legacy scalar kept beside it)" % (r[1], r[2]))
    for r in rows:
        if r[3] == "INCOMPLETE":
            print("  %s.%s missing %s" % (r[1], r[2], ", ".join(r[4])))
