#!/usr/bin/env python3
"""coordination_check.py -- shape and status-tag check for "coordination" blocks.

Standard library only (no jsonschema). Checks:

  1. every ontology/*/*.json that carries a "coordination" block:
       - all ten keys present (null is kept, a missing key is a failure)
       - no unknown keys
       - text fields are a string or null
       - energy_cost is null or {joules: number|null, note, [per]};
         joules null needs a note (e.g. "unmeasured")
       - loop_topology is null or {cycles, observer_cuts}; every cycle id
         named under cycles_surviving exists
       - assumption_trace is null or a list of strings
       - status tags are OBSERVED / DERIVED / PROPOSED or null
       - a field that holds a value has a status tag; a field with no value
         has none (energy_cost with joules null counts as no value)
       - sources keys are field names; values are null or lists of strings
  2. schemas/coordination.schema.json is referenced by every per-type schema
  3. the inline copy in schemas/intelligence.schema.json equals the shared block

It does not check that a source says what a field says.

  python3 validation/coordination_check.py             # exit 0 = no failure
  python3 validation/coordination_check.py --selftest  # planted defects must fire
"""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT = ("carrier", "signal", "record", "closure", "trust_basis")
FIELDS = TEXT + ("energy_cost", "loop_topology", "assumption_trace")
KEYS = FIELDS + ("sources", "status")
OPTIONAL = ("notes",)
STATUS = ("OBSERVED", "DERIVED", "PROPOSED")
PER_TYPE = ("ai", "animal", "crystal", "energy", "plant", "plasma", "shape",
            "social", "temporal")


def _is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def has_value(c, k):
    """A field holds a value if it is not null. energy_cost holds one only
    when joules is a number: {joules: null, note: "unmeasured"} is no value."""
    v = c.get(k)
    if k == "energy_cost" and isinstance(v, dict):
        return _is_num(v.get("joules"))
    return v is not None


def check_block(c):
    """Return a list of failure strings for one coordination block."""
    out = []
    if not isinstance(c, dict):
        return ["block is not an object"]
    for k in KEYS:
        if k not in c:
            out.append("missing key '%s' (null is kept, never dropped)" % k)
    for k in c:
        if k not in KEYS + OPTIONAL:
            out.append("unknown key '%s'" % k)
    for k in TEXT:
        v = c.get(k)
        if v is not None and not isinstance(v, str):
            out.append("'%s' must be a string or null" % k)

    e = c.get("energy_cost")
    if e is not None:
        if not isinstance(e, dict) or "joules" not in e or "note" not in e:
            out.append("energy_cost must be null or an object with 'joules' and 'note'")
        else:
            for k in e:
                if k not in ("joules", "per", "note"):
                    out.append("energy_cost: unknown key '%s'" % k)
            j = e["joules"]
            if j is not None and not _is_num(j):
                out.append("energy_cost.joules must be a number or null")
            if j is None and not (isinstance(e["note"], str) and e["note"].strip()):
                out.append("energy_cost.joules is null with no note (write 'unmeasured')")

    lt = c.get("loop_topology")
    if lt is not None:
        if not isinstance(lt, dict) or "cycles" not in lt or "observer_cuts" not in lt:
            out.append("loop_topology must be null or an object with 'cycles' and 'observer_cuts'")
        else:
            ids = set()
            for cy in lt["cycles"] or []:
                if not (isinstance(cy, dict) and isinstance(cy.get("id"), str)
                        and isinstance(cy.get("path"), str)):
                    out.append("loop_topology.cycles: each cycle needs string 'id' and 'path'")
                else:
                    ids.add(cy["id"])
            for cut in lt["observer_cuts"] or []:
                if not (isinstance(cut, dict) and isinstance(cut.get("cut"), str)
                        and isinstance(cut.get("cycles_surviving"), list)):
                    out.append("loop_topology.observer_cuts: each cut needs 'cut' and a list 'cycles_surviving'")
                    continue
                for i in cut["cycles_surviving"]:
                    if i not in ids:
                        out.append("observer cut names cycle '%s' which is not in cycles" % i)

    at = c.get("assumption_trace")
    if at is not None and not (isinstance(at, list) and all(isinstance(x, str) for x in at)):
        out.append("assumption_trace must be null or a list of strings")

    st = c.get("status")
    if st is not None and not isinstance(st, dict):
        out.append("status must be null or an object")
        st = None
    for k in (st or {}):
        if k not in FIELDS:
            out.append("status: '%s' is not a field name" % k)
        elif st[k] is not None and st[k] not in STATUS:
            out.append("status.%s = %r is not one of %s" % (k, st[k], "/".join(STATUS)))
    for k in FIELDS:
        tag = (st or {}).get(k)
        if has_value(c, k) and tag is None:
            out.append("'%s' holds a value but has no status tag" % k)
        if k in c and not has_value(c, k) and tag is not None:
            out.append("'%s' holds no value but carries status %r" % (k, tag))

    so = c.get("sources")
    if so is not None and not isinstance(so, dict):
        out.append("sources must be null or an object")
        so = None
    for k, v in (so or {}).items():
        if k not in FIELDS:
            out.append("sources: '%s' is not a field name" % k)
        elif v is not None and not (isinstance(v, list) and all(isinstance(x, str) for x in v)):
            out.append("sources.%s must be null or a list of strings" % k)

    no = c.get("notes")
    if no is not None and not (isinstance(no, dict) and all(
            v is None or isinstance(v, str) for v in no.values())):
        out.append("notes must be null or an object of strings")
    return out


def check_schemas(root=ROOT):
    out = []
    sd = root / "schemas"
    try:
        shared = json.loads((sd / "coordination.schema.json").read_text(encoding="utf-8"))
    except Exception as exc:  # absent or unparseable
        return ["schemas/coordination.schema.json: %s" % exc]
    for t in PER_TYPE:
        p = sd / ("%s.schema.json" % t)
        try:
            ref = json.loads(p.read_text(encoding="utf-8"))["properties"].get("coordination")
        except Exception as exc:
            out.append("schemas/%s.schema.json: %s" % (t, exc))
            continue
        if ref != {"$ref": "coordination.schema.json"}:
            out.append("schemas/%s.schema.json does not $ref coordination.schema.json" % t)
    try:
        inline = json.loads((sd / "intelligence.schema.json").read_text(
            encoding="utf-8"))["properties"]["coordination"]
    except Exception as exc:
        out.append("schemas/intelligence.schema.json: no inline coordination block (%s)" % exc)
    else:
        block = {k: v for k, v in shared.items() if k not in ("$schema", "$id")}
        if inline != block:
            out.append("schemas/intelligence.schema.json inline block differs from coordination.schema.json")
    return out


def scan(root=ROOT):
    """Return (rows, failures). rows = (path, n_filled_fields) per block found."""
    rows, fails = [], []
    for p in sorted((root / "ontology").glob("*/*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            fails.append((str(p.relative_to(root)), "unreadable: %s" % exc))
            continue
        if not isinstance(d, dict) or "coordination" not in d:
            continue
        c = d["coordination"]
        rel = str(p.relative_to(root))
        for f in check_block(c):
            fails.append((rel, f))
        filled = sum(1 for k in FIELDS if isinstance(c, dict) and has_value(c, k))
        rows.append((rel, filled))
    return rows, fails


GOOD = {
    "carrier": "x", "signal": None, "record": None, "closure": None,
    "trust_basis": None, "energy_cost": {"joules": None, "note": "unmeasured"},
    "loop_topology": {"cycles": [{"id": "L1", "path": "a -> b -> a"}],
                      "observer_cuts": [{"cut": "a only", "cycles_surviving": []}]},
    "assumption_trace": ["coordination requires money"],
    "sources": {"carrier": ["Someone (1900)"]},
    "status": {"carrier": "OBSERVED",
               "loop_topology": "DERIVED", "assumption_trace": "PROPOSED"},
}


def selftest():
    def bad(fn):
        c = copy.deepcopy(GOOD)
        fn(c)
        return check_block(c)

    cases = [
        ("clean block passes", lambda: check_block(GOOD) == []),
        ("all-null block passes", lambda: check_block(
            dict({k: None for k in KEYS})) == []),
        ("dropped key fires", lambda: bad(lambda c: c.pop("closure"))),
        ("unknown key fires", lambda: bad(lambda c: c.update(price="1"))),
        ("bad status tag fires", lambda: bad(lambda c: c["status"].update(carrier="TRUE"))),
        ("value without status fires", lambda: bad(lambda c: c["status"].pop("carrier"))),
        ("status on a null field fires", lambda: bad(lambda c: c["status"].update(signal="OBSERVED"))),
        ("joules as text fires", lambda: bad(lambda c: c["energy_cost"].update(joules="low"))),
        ("measured joules without status fires", lambda: bad(lambda c: c["energy_cost"].update(joules=2.5))),
        ("status on unmeasured joules fires", lambda: bad(lambda c: c["status"].update(energy_cost="OBSERVED"))),
        ("joules null with no note fires", lambda: bad(lambda c: c["energy_cost"].update(note=None))),
        ("cut naming an absent cycle fires", lambda: bad(
            lambda c: c["loop_topology"]["observer_cuts"][0].update(cycles_surviving=["L9"]))),
        ("assumption_trace as text fires", lambda: bad(lambda c: c.update(assumption_trace="x"))),
        ("sources under a non-field key fires", lambda: bad(lambda c: c["sources"].update(price=["x"]))),
        ("number in a text field fires", lambda: bad(lambda c: c.update(carrier=3))),
    ]
    failed = 0
    for name, fn in cases:
        ok = bool(fn())
        failed += not ok
        print("  %s  %s" % ("ok  " if ok else "FAIL", name))
    print("selftest checks: %d   failed: %d" % (len(cases), failed))
    return failed


def main(argv):
    if "--selftest" in argv:
        return 1 if selftest() else 0
    rows, fails = scan()
    sfails = check_schemas()
    print("coordination blocks found: %d" % len(rows))
    for rel, filled in rows:
        print("  %-52s fields with a value: %d of %d" % (rel, filled, len(FIELDS)))
    for rel, f in fails:
        print("FAIL %s: %s" % (rel, f))
    for f in sfails:
        print("FAIL %s" % f)
    print("failures: %d" % (len(fails) + len(sfails)))
    return 1 if (fails or sfails) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
