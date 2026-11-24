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
       - status tags are OBSERVED / DERIVED / PROPOSED or null; DERIVED may
         carry a basis: "DERIVED (basis: PROPOSED)" or "DERIVED (basis: OBSERVED)"
       - a field that holds a value has a status tag; a field with no value
         has none (energy_cost with joules null counts as no value)
       - sources keys are field names; values are null or lists of strings
  2. schemas/coordination.schema.json is referenced by every per-type schema
  3. the inline copy in schemas/intelligence.schema.json equals the shared block

  4. the same for the "gate_sensing", "functional_intelligence" and
     "observation_context" blocks (shape, status tags, yes/no/unmeasured
     values, context values), and for their shared schema files

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
STATUS = ("OBSERVED", "DERIVED", "PROPOSED",
          "DERIVED (basis: PROPOSED)", "DERIVED (basis: OBSERVED)")
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
    if c is None:  # null block: slot present, no information
        return out
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
            out.append("status.%s = %r is not one of: %s" % (k, st[k], ", ".join(STATUS)))
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


GATE_FIELDS = ("limit_sensed", "early_signal", "response", "lead_time")
CAPS = ("adapts", "signals", "responds_to_other", "changes_environment", "co_adapts")
CONTEXTS = ("lab", "field", "long_term_coupled", "mixed")
BLOCK_FIELDS = {"coordination": FIELDS, "gate_sensing": GATE_FIELDS,
                "functional_intelligence": CAPS + ("coupling_note", "contested_label")}
SHARED = ("coordination", "gate_sensing", "functional_intelligence", "observation_context")


def _str_list_or_null(v):
    return v is None or (isinstance(v, list) and all(isinstance(x, str) for x in v))


def _notes_ok(no):
    return no is None or (isinstance(no, dict) and all(
        v is None or isinstance(v, str) for v in no.values()))


def check_gate(g):
    """Failures for one gate_sensing block."""
    out = []
    if g is None:  # null block: slot present, no information
        return out
    if not isinstance(g, dict):
        return ["gate_sensing is not an object"]
    for k in GATE_FIELDS + ("status", "sources"):
        if k not in g:
            out.append("gate_sensing: missing key '%s' (null is kept, never dropped)" % k)
    for k in g:
        if k not in GATE_FIELDS + ("status", "sources", "notes"):
            out.append("gate_sensing: unknown key '%s'" % k)
    for k in GATE_FIELDS[:3]:
        if g.get(k) is not None and not isinstance(g.get(k), str):
            out.append("gate_sensing.%s must be a string or null" % k)
    lt = g.get("lead_time")
    measured = False
    if lt is not None:
        if not isinstance(lt, dict) or not all(k in lt for k in ("value", "unit", "note")):
            out.append("gate_sensing.lead_time must be null or {value, unit, note}")
        else:
            v = lt["value"]
            if v is not None and not _is_num(v):
                out.append("gate_sensing.lead_time.value must be a number or null")
            if _is_num(v):
                measured = True
                if not (isinstance(lt["unit"], str) and lt["unit"].strip()):
                    out.append("gate_sensing.lead_time has a value but no unit")
            elif not (isinstance(lt["note"], str) and lt["note"].strip()):
                out.append("gate_sensing.lead_time.value is null with no note (write 'unmeasured')")
    st = g.get("status") if isinstance(g.get("status"), dict) else {}
    if g.get("status") is not None and not isinstance(g.get("status"), dict):
        out.append("gate_sensing.status must be null or an object")
    for k in st:
        if k not in GATE_FIELDS:
            out.append("gate_sensing.status: '%s' is not a field name" % k)
        elif st[k] is not None and st[k] not in STATUS:
            out.append("gate_sensing.status.%s = %r is not a status tag" % (k, st[k]))
    for k in GATE_FIELDS:
        has = measured if k == "lead_time" else g.get(k) is not None
        tag = st.get(k)
        if has and tag is None:
            out.append("gate_sensing.%s holds a value but has no status tag" % k)
        if k in g and not has and tag is not None:
            out.append("gate_sensing.%s holds no value but carries status %r" % (k, tag))
    so = g.get("sources")
    if so is not None and not isinstance(so, dict):
        out.append("gate_sensing.sources must be null or an object")
        so = None
    for k, v in (so or {}).items():
        if k not in GATE_FIELDS:
            out.append("gate_sensing.sources: '%s' is not a field name" % k)
        elif not _str_list_or_null(v):
            out.append("gate_sensing.sources.%s must be null or a list of strings" % k)
    if not _notes_ok(g.get("notes")):
        out.append("gate_sensing.notes must be null or an object of strings")
    return out


def check_functional(f):
    """Failures for one functional_intelligence block."""
    out = []
    if f is None:  # null block: slot present, no information
        return out
    if not isinstance(f, dict):
        return ["functional_intelligence is not an object"]
    keys = CAPS + ("coupling_note", "contested_label")
    for k in keys:
        if k not in f:
            out.append("functional_intelligence: missing key '%s' (null is kept, never dropped)" % k)
    for k in f:
        if k not in keys + ("notes",):
            out.append("functional_intelligence: unknown key '%s'" % k)
    for k in CAPS:
        c = f.get(k)
        if c is None:
            continue
        if not isinstance(c, dict) or not all(x in c for x in ("value", "status", "source")):
            out.append("functional_intelligence.%s must be null or {value, status, source}" % k)
            continue
        for x in c:
            if x not in ("value", "status", "source", "note"):
                out.append("functional_intelligence.%s: unknown key '%s'" % (k, x))
        v, tag = c["value"], c["status"]
        if v not in ("yes", "no", "unmeasured"):
            out.append("functional_intelligence.%s.value = %r is not yes / no / unmeasured" % (k, v))
        if tag is not None and tag not in STATUS:
            out.append("functional_intelligence.%s.status = %r is not a status tag" % (k, tag))
        if v in ("yes", "no") and tag is None:
            out.append("functional_intelligence.%s is %s but has no status tag" % (k, v))
        if v == "unmeasured" and tag is not None:
            out.append("functional_intelligence.%s is unmeasured but carries status %r" % (k, tag))
        if not _str_list_or_null(c["source"]):
            out.append("functional_intelligence.%s.source must be null or a list of strings" % k)
    if f.get("coupling_note") is not None and not isinstance(f.get("coupling_note"), str):
        out.append("functional_intelligence.coupling_note must be a string or null")
    cl = f.get("contested_label")
    if cl is not None:
        if not isinstance(cl, list):
            out.append("functional_intelligence.contested_label must be null or a list")
        else:
            for e in cl:
                if not (isinstance(e, dict) and isinstance(e.get("label"), str)
                        and "claimed_by" in e and "disputed_by" in e
                        and _str_list_or_null(e["claimed_by"])
                        and _str_list_or_null(e["disputed_by"])):
                    out.append("contested_label entries need a string 'label' and "
                               "'claimed_by' / 'disputed_by' (list of strings or null)")
    if not _notes_ok(f.get("notes")):
        out.append("functional_intelligence.notes must be null or an object of strings")
    return out


def check_context(oc):
    """Failures for one observation_context block (null is allowed)."""
    out = []
    if oc is None:
        return out
    if not isinstance(oc, dict):
        return ["observation_context must be null or an object"]
    for k, v in oc.items():
        block, _, field = k.partition(".")
        if block not in BLOCK_FIELDS or field not in BLOCK_FIELDS[block]:
            out.append("observation_context: key '%s' is not '<block>.<field>' of a known block" % k)
        if v is not None and v not in CONTEXTS:
            out.append("observation_context.%s = %r is not one of %s or null" % (k, v, " / ".join(CONTEXTS)))
    return out


def check_schemas(root=ROOT):
    out = []
    sd = root / "schemas"
    try:
        intel = json.loads((sd / "intelligence.schema.json").read_text(encoding="utf-8"))["properties"]
    except Exception as exc:
        return ["schemas/intelligence.schema.json: %s" % exc]
    per_type = {}
    for t in PER_TYPE:
        try:
            per_type[t] = json.loads((sd / ("%s.schema.json" % t)).read_text(encoding="utf-8"))["properties"]
        except Exception as exc:
            out.append("schemas/%s.schema.json: %s" % (t, exc))
    for name in SHARED:
        fn = "%s.schema.json" % name
        try:
            shared = json.loads((sd / fn).read_text(encoding="utf-8"))
        except Exception as exc:  # absent or unparseable
            out.append("schemas/%s: %s" % (fn, exc))
            continue
        for t, props in per_type.items():
            if props.get(name) != {"$ref": fn}:
                out.append("schemas/%s.schema.json does not $ref %s" % (t, fn))
        block = {k: v for k, v in shared.items() if k not in ("$schema", "$id")}
        if intel.get(name) != block:
            out.append("schemas/intelligence.schema.json inline '%s' differs from %s" % (name, fn))
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
        if not isinstance(d, dict):
            continue
        rel = str(p.relative_to(root))
        for name, fn in (("gate_sensing", check_gate),
                         ("functional_intelligence", check_functional),
                         ("observation_context", check_context)):
            if name in d:
                for f in fn(d[name]):
                    fails.append((rel, f))
                rows.append((rel, name, None))
        if "coordination" not in d:
            continue
        c = d["coordination"]
        for f in check_block(c):
            fails.append((rel, f))
        filled = sum(1 for k in FIELDS if isinstance(c, dict) and has_value(c, k))
        rows.append((rel, "coordination", filled))
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


GOOD_GATE = {
    "limit_sensed": "x", "early_signal": "y", "response": None,
    "lead_time": {"value": None, "unit": None, "note": "unmeasured"},
    "status": {"limit_sensed": "DERIVED (basis: OBSERVED)", "early_signal": "OBSERVED"},
    "sources": {"early_signal": ["Someone (1900)"]},
}
GOOD_FI = {
    "adapts": {"value": "yes", "status": "OBSERVED", "source": ["Someone (1900)"]},
    "signals": {"value": "unmeasured", "status": None, "source": None},
    "responds_to_other": None, "changes_environment": None, "co_adapts": None,
    "coupling_note": "prey",
    "contested_label": [{"label": "learning", "claimed_by": ["A (1900)"], "disputed_by": None}],
}
GOOD_OC = {"gate_sensing.early_signal": "lab", "functional_intelligence.adapts": None}


def selftest():
    def bad(fn):
        c = copy.deepcopy(GOOD)
        fn(c)
        return check_block(c)

    def badg(fn):
        g = copy.deepcopy(GOOD_GATE)
        fn(g)
        return check_gate(g)

    def badf(fn):
        f = copy.deepcopy(GOOD_FI)
        fn(f)
        return check_functional(f)

    cases = [
        ("clean gate_sensing passes", lambda: check_gate(GOOD_GATE) == []),
        ("gate_sensing dropped key fires", lambda: badg(lambda g: g.pop("response"))),
        ("gate_sensing value without status fires", lambda: badg(lambda g: g["status"].pop("early_signal"))),
        ("measured lead_time without unit fires", lambda: badg(
            lambda g: (g["lead_time"].update(value=3), g["status"].update(lead_time="OBSERVED")))),
        ("unmeasured lead_time with status fires", lambda: badg(lambda g: g["status"].update(lead_time="OBSERVED"))),
        ("lead_time null value with no note fires", lambda: badg(lambda g: g["lead_time"].update(note=None))),
        ("clean functional_intelligence passes", lambda: check_functional(GOOD_FI) == []),
        ("capability 'maybe' fires", lambda: badf(lambda f: f["adapts"].update(value="maybe"))),
        ("yes without status fires", lambda: badf(lambda f: f["adapts"].update(status=None))),
        ("unmeasured with status fires", lambda: badf(lambda f: f["signals"].update(status="OBSERVED"))),
        ("capability dropped fires", lambda: badf(lambda f: f.pop("co_adapts"))),
        ("contested_label absent does not fire (null allowed)", lambda: badf(
            lambda f: f.update(contested_label=None)) == []),
        ("contested_label without disputed_by key fires", lambda: badf(
            lambda f: f["contested_label"][0].pop("disputed_by"))),
        ("yes/no stands with every label disputed", lambda: badf(
            lambda f: f["contested_label"][0].update(disputed_by=["B (1901)"])) == []),
        ("clean observation_context passes", lambda: check_context(GOOD_OC) == []),
        ("null observation_context passes", lambda: check_context(None) == []),
        ("context 'greenhouse' fires", lambda: check_context({"gate_sensing.response": "greenhouse"})),
        ("context on an unknown field fires", lambda: check_context({"gate_sensing.price": "lab"})),
        ("clean block passes", lambda: check_block(GOOD) == []),
        ("all-null block passes", lambda: check_block(
            dict({k: None for k in KEYS})) == []),
        ("dropped key fires", lambda: bad(lambda c: c.pop("closure"))),
        ("unknown key fires", lambda: bad(lambda c: c.update(price="1"))),
        ("bad status tag fires", lambda: bad(lambda c: c["status"].update(carrier="TRUE"))),
        ("DERIVED with a basis passes", lambda: bad(
            lambda c: c["status"].update(loop_topology="DERIVED (basis: PROPOSED)")) == []),
        ("DERIVED with an unknown basis fires", lambda: bad(
            lambda c: c["status"].update(loop_topology="DERIVED (basis: GUESS)"))),
        ("basis on a non-DERIVED tag fires", lambda: bad(
            lambda c: c["status"].update(carrier="OBSERVED (basis: PROPOSED)"))),
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
        ("null block passes (all four blocks)", lambda: not any(
            fn(None) for fn in (check_block, check_gate, check_functional, check_context))),
        ("non-object non-null block fires (all four blocks)", lambda: all(
            fn(v) for fn in (check_block, check_gate, check_functional, check_context)
            for v in ("x", 0, [], False))),
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
    print("blocks found: %d" % len(rows))
    for rel, name, filled in sorted(rows):
        extra = "" if filled is None else "  fields with a value: %d of %d" % (filled, len(FIELDS))
        print("  %-50s %-24s%s" % (rel, name, extra))
    for rel, f in fails:
        print("FAIL %s: %s" % (rel, f))
    for f in sfails:
        print("FAIL %s" % f)
    print("failures: %d" % (len(fails) + len(sfails)))
    return 1 if (fails or sfails) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
