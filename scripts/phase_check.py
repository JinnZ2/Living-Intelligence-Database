#!/usr/bin/env python3
"""Checker for being_tense, phase_now and carried_from_phase (process form, dX/dt).

    python3 scripts/phase_check.py              check registry/process_forms.json; exit 1 on any violation
    python3 scripts/phase_check.py --selftest

Rules: registry/DECLARED.json, amendment 'process form addendum: being_tense, phase_now,
carried_from_phase'. All of these fields are PROPOSED. Null = not assessed.

Violations (exit 1):
  BAD_TENSE              being_tense outside CURRENTLY_BEING | HAVING_BEEN | PROJECTED | null
  CYCLE_REF_MISSING      a cycle_ref that is not an id in registry/cycles.json
  PHASE_NOT_IN_CYCLE     the cycle lists its phases and this phase is not among them
  NOT_COMPLETED          a carried phase that is not earlier than phase_now in the same cycle
  BAD_STILL_ACTING       still_acting outside yes | no | unmeasured
  CARRIED_TENSE          a carried item marked with a being_tense other than HAVING_BEEN
  NOW_TENSE              a phase_now item marked with a being_tense other than CURRENTLY_BEING
  UNSOURCED_NOT_FLAGGED  a carried item with no source that is not PROPOSED + unsourced true
  CARRY_DELETED          a carried item in the last committed file that is missing now
  SCHEMA                 the file does not validate (needs jsonschema; without it SCHEMA_NOT_RUN, exit 1)
Recorded gaps (listed, exit unchanged):
  ORDER_NOT_CHECKABLE    the cycle lists no phases, or the subject has no phase_now in that cycle
Stdlib for every rule but SCHEMA.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = os.path.join(ROOT, "registry", "process_forms.json")
CYCLES = os.path.join(ROOT, "registry", "cycles.json")
SCHEMA = os.path.join(ROOT, "schemas", "translation_loss_blocks.schema.json")
TENSE = ("CURRENTLY_BEING", "HAVING_BEEN", "PROJECTED", None)
ACTING = ("yes", "no", "unmeasured")


def subjects(doc):
    for r in doc.get("phase_records", []):
        yield r["subject"], r
    for r in doc.get("process_forms", []):
        if any(k in r for k in ("being_tense", "phase_now", "carried_from_phase")):
            yield r["attribute"], r


def carry_keys(doc):
    return {(s, c.get("cycle_ref"), c.get("phase"), c.get("carried"))
            for s, r in subjects(doc) for c in (r.get("carried_from_phase") or [])}


def check(doc, cycles, previous=None):
    C = {c["id"]: c for c in cycles}
    viol, gaps = [], []
    for subj, r in subjects(doc):
        if r.get("being_tense") not in TENSE:
            viol.append(["BAD_TENSE", subj, r.get("being_tense")])
        now = {}
        for p in r.get("phase_now") or []:
            ref = p.get("cycle_ref")
            if ref not in C:
                viol.append(["CYCLE_REF_MISSING", subj, "phase_now", ref])
                continue
            now[ref] = p.get("phase")
            if C[ref].get("phases") and p.get("phase") not in C[ref]["phases"]:
                viol.append(["PHASE_NOT_IN_CYCLE", subj, "phase_now", ref, p.get("phase")])
            if p.get("being_tense", "CURRENTLY_BEING") not in ("CURRENTLY_BEING",):
                viol.append(["NOW_TENSE", subj, ref, p.get("being_tense")])
        for c in r.get("carried_from_phase") or []:
            ref, ph = c.get("cycle_ref"), c.get("phase")
            if c.get("still_acting") not in ACTING:
                viol.append(["BAD_STILL_ACTING", subj, ref, c.get("still_acting")])
            if c.get("being_tense", "HAVING_BEEN") != "HAVING_BEEN":
                viol.append(["CARRIED_TENSE", subj, ref, c.get("being_tense")])
            if not c.get("source") and not (c.get("status") == "PROPOSED" and c.get("unsourced") is True):
                viol.append(["UNSOURCED_NOT_FLAGGED", subj, ref, ph])
            if ref not in C:
                viol.append(["CYCLE_REF_MISSING", subj, "carried_from_phase", ref])
                continue
            order = C[ref].get("phases")
            if not order:
                gaps.append(["ORDER_NOT_CHECKABLE", subj, ref, ph, "the cycle lists no phases"])
                continue
            if ph not in order:
                viol.append(["PHASE_NOT_IN_CYCLE", subj, "carried_from_phase", ref, ph])
                continue
            if ref not in now:
                gaps.append(["ORDER_NOT_CHECKABLE", subj, ref, ph, "no phase_now in this cycle"])
            elif now[ref] in order and order.index(ph) >= order.index(now[ref]):
                viol.append(["NOT_COMPLETED", subj, ref, ph, "phase_now is %s" % now[ref]])
    if previous is not None:
        for k in sorted(carry_keys(previous) - carry_keys(doc), key=str):
            viol.append(["CARRY_DELETED"] + list(k))
    return viol, gaps


def committed():
    """The file as last committed, or None when there is none (first version)."""
    r = subprocess.run(["git", "-C", ROOT, "show", "HEAD:registry/process_forms.json"], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else None


def selftest():
    cyc = [{"id": "CY_X", "phases": ["a", "b", "c"]}, {"id": "CY_NOPH"}]

    def rec(now="c", carried="a", ref="CY_X", **kw):
        c = {"cycle_ref": ref, "phase": carried, "carried": "imprint", "still_acting": "yes", "source": None,
             "status": "PROPOSED", "unsourced": True}
        c.update(kw)
        return {"phase_records": [{"subject": "S", "being_tense": None, "status": "PROPOSED",
                                   "phase_now": [{"cycle_ref": "CY_X", "phase": now, "observed_at": None, "scope": None}],
                                   "carried_from_phase": [c]}]}
    cases = [("earlier phase carried: no violation", rec(), None),
             ("carried phase equals phase_now", rec(now="b", carried="b"), "NOT_COMPLETED"),
             ("carried phase later than phase_now", rec(now="a", carried="c"), "NOT_COMPLETED"),
             ("cycle_ref not in the registry", rec(ref="CY_NONE"), "CYCLE_REF_MISSING"),
             ("phase the cycle does not list", rec(carried="z"), "PHASE_NOT_IN_CYCLE"),
             ("still_acting outside the vocabulary", rec(still_acting="maybe"), "BAD_STILL_ACTING"),
             ("still_acting unmeasured is allowed", rec(still_acting="unmeasured"), None),
             ("no source and no unsourced flag", rec(unsourced=False), "UNSOURCED_NOT_FLAGGED"),
             ("carried item marked CURRENTLY_BEING", rec(being_tense="CURRENTLY_BEING"), "CARRIED_TENSE")]
    ok = []
    for name, doc, want in cases:
        v, _ = check(doc, cyc)
        codes = [x[0] for x in v]
        good = (codes == []) if want is None else (want in codes)
        ok.append(good)
        print("%s  %s  %s" % ("PASS" if good else "FAIL", name, codes))
    v, g = check(rec(ref="CY_NOPH"), cyc)
    good = v == [] and [x[0] for x in g] == ["ORDER_NOT_CHECKABLE"]
    ok.append(good)
    print("%s  a cycle with no phase list is a recorded gap, not a pass and not a violation" % ("PASS" if good else "FAIL"))
    bad = rec()
    bad["phase_records"][0]["being_tense"] = "WAS"
    good = "BAD_TENSE" in [x[0] for x in check(bad, cyc)[0]]
    ok.append(good)
    print("%s  being_tense outside the vocabulary" % ("PASS" if good else "FAIL"))
    empty = rec()
    empty["phase_records"][0]["carried_from_phase"] = []
    good = "CARRY_DELETED" in [x[0] for x in check(empty, cyc, previous=rec())[0]]
    ok.append(good)
    print("%s  a carried item removed since the last committed file" % ("PASS" if good else "FAIL"))
    good = check(rec(), cyc, previous=rec())[0] == []
    ok.append(good)
    print("%s  an unchanged file has no deletion" % ("PASS" if good else "FAIL"))
    print("checks: %d   failed: %d" % (len(ok), ok.count(False)))
    return all(ok)


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(0 if selftest() else 1)
    doc = json.load(open(FILE, encoding="utf-8"))
    cycles = json.load(open(CYCLES, encoding="utf-8"))["cycles"]
    viol, gaps = check(doc, cycles, previous=committed())
    try:
        from jsonschema import Draft7Validator
        for e in Draft7Validator(json.load(open(SCHEMA, encoding="utf-8"))).iter_errors(doc):
            viol.append(["SCHEMA", "/".join(str(p) for p in e.absolute_path), e.message[:160]])
        schema_state = "RUN"
    except ImportError:
        schema_state = "NOT_RUN (jsonschema not installed)"
        viol.append(["SCHEMA_NOT_RUN", "the file was not validated against the schema"])
    n = sum(1 for _ in subjects(doc))
    print("subjects: %d   carried items: %d   schema pass: %s" % (n, len(carry_keys(doc)), schema_state))
    for s, r in subjects(doc):
        print("  %s  being_tense %s" % (s, r.get("being_tense")))
        for p in r.get("phase_now") or []:
            print("    now      %s / %s   observed_at %s" % (p["cycle_ref"], p["phase"], p["observed_at"]))
        for c in r.get("carried_from_phase") or []:
            print("    carried  %s / %s -> %s   still_acting %s   status %s%s"
                  % (c["cycle_ref"], c["phase"], c["carried"], c["still_acting"], c["status"],
                     " (unsourced)" if c.get("unsourced") else ""))
    print("recorded gaps (%d):" % len(gaps))
    for g in gaps:
        print("  " + "  ".join(str(x) for x in g))
    print("violations (%d):" % len(viol))
    for v in viol:
        print("  " + "  ".join(str(x) for x in v))
    sys.exit(1 if viol else 0)
