#!/usr/bin/env python3
"""Known-answer fixtures for the validation instruments (validation/fixtures/DECLARED.json).

    python3 validation/fixtures/run_fixtures.py                 run all; exit 1 if any fixture fails
    python3 validation/fixtures/run_fixtures.py --json OUT      also write the table as JSON

Every fixture builds its own input in a temporary directory and calls the instrument the way a
caller would. Nothing in the repository is written. Stdlib only.
PASS = the instrument gave the declared answer. FAIL = it did not. NOT_RUN = the fixture could
not be executed (never counted as a pass). ERROR = the instrument raised.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VAL = ROOT / "validation"
sys.path.insert(0, str(VAL))


def scoped(conf=0.9, **scope):
    s = {"definition": "x", "evidence": {"relational_confidence": conf}}
    s.update(scope)
    return {"value": 1, "scope": s}


def f1(tmp):
    idx = tmp / "index.json"
    idx.write_text(json.dumps({"entities": [{"id": "FX", "attributes": {"a": scoped()}}]}))
    r = subprocess.run([sys.executable, str(VAL / "verify.py"), "--claim", "no_such_claim", "--ontology", str(idx)],
                       capture_output=True, text=True)
    try:
        o = json.loads(r.stdout)
    except ValueError:
        return False, "no JSON on stdout (exit %d): %s" % (r.returncode, (r.stdout + r.stderr).strip()[:120])
    seen = {"verdict": o.get("verdict"), "posterior_probability": o.get("posterior_probability", "absent"),
            "tests_passed": o.get("tests_passed", "absent")}
    ok = o.get("verdict") == "UNKNOWN" and o.get("posterior_probability", "absent") is None \
        and not o.get("tests_passed")
    return ok, seen


def f2(tmp):
    import verify
    calls = [0]

    def claim():
        calls[0] += 1
        return True

    def run(n):
        calls[0] = 0
        o = verify.verify_claim(claim, ontology={"entities": [{"id": "FX", "attributes": {"a%d" % i: scoped()
                                                                                         for i in range(n)}}]}, prior=0.5)
        return o, calls[0]
    o1, c1 = run(1)
    o5, c5 = run(5)
    seen = {"evidence_count": o5.get("evidence_count", "absent"), "claim_calls": c5,
            "posterior_5_attrs": o5.get("posterior_probability"), "posterior_1_attr": o1.get("posterior_probability")}
    ok = o5.get("evidence_count") == 1 and c5 == 1 and o5.get("posterior_probability") == o1.get("posterior_probability")
    return ok, seen


def _entity_file(tmp, name, entity):
    p = tmp / name
    p.write_text(json.dumps(entity))
    return str(p)


def f3(tmp):
    import falsifier
    a = _entity_file(tmp, "fa.json", {"id": "FA", "attributes": {"k": scoped(condition={"constraints": ["zzqx_never_present"]})}})
    oa = falsifier.falsify("FA", ontology={"entities": [{"id": "FA", "path": a}]})
    b = _entity_file(tmp, "fb.json", {"id": "FB", "attributes": {"k": {"value": 1, "scope": {}}}})
    ob = falsifier.falsify("FB", ontology={"entities": [{"id": "FB", "path": b}]})
    outcomes = [d.get("outcome", d.get("falsification_risk")) for d in oa.get("details", [])]
    seen = {"a_outcomes": outcomes, "a_survived": oa.get("tests_survived"),
            "a_resistance": oa.get("falsification_resistance", "absent"),
            "b_counterexamples": ob.get("counterexamples_generated"),
            "b_resistance": ob.get("falsification_resistance", "absent")}
    ok = (bool(outcomes) and all(x == "NOT_TESTED" for x in outcomes) and oa.get("tests_survived") == 0
          and oa.get("falsification_resistance", "absent") is None
          and ob.get("counterexamples_generated") == 0 and ob.get("falsification_resistance", "absent") is None)
    return ok, seen


def f4(tmp):
    import dependency_tree as dt
    a = _entity_file(tmp, "a.json", {"id": "A", "name": "a", "links": [{"relation": "synergy", "target": "NOT_THERE"}]})
    o = dt.dependency_tree("A", ontology={"entities": [{"id": "A", "name": "a", "path": a}]}, max_depth=2)
    unresolved = o.get("unresolved", "absent")
    children = [(c.get("id"), c.get("type")) for c in o.get("tree", {}).get("dependencies", [])]
    seen = {"unresolved": unresolved, "children": children}
    ok = isinstance(unresolved, list) and any(u.get("source") == "A" and u.get("target") == "NOT_THERE"
                                              and u.get("relation") == "synergy" for u in unresolved) \
        and ("NOT_THERE", "unresolved") in children
    return ok, seen


GHOST = {"entities": [{"id": "GHOST", "name": "ghost", "path": "does/not/exist.json"}]}


def _failed(report):
    lf = report.get("load_failures", "absent")
    return lf, isinstance(lf, list) and any(x.get("id") == "GHOST" and x.get("state") == "LOAD_FAILED" for x in lf)


def f5_falsifier(tmp):
    import falsifier
    o = falsifier.falsify("GHOST", ontology=GHOST)
    lf, ok = _failed(o)
    seen = {"load_failures": lf, "error": o.get("error"), "analysed": "counterexamples_generated" in o}
    return ok and "counterexamples_generated" not in o and "No scoped attributes" not in str(o.get("error")), seen


def f5_audit(tmp):
    import audit
    o = audit.audit(GHOST, repo_root=ROOT)
    lf, ok = _failed(o)
    seen = {"load_failures": lf, "total_entities": o.get("total_entities"), "scoped_ratio": o.get("scoped_ratio", "absent")}
    return ok and o.get("scoped_ratio", "absent") is None, seen


def f5_dependency_tree(tmp):
    import dependency_tree as dt
    o = dt.dependency_tree("GHOST", ontology=GHOST)
    lf, ok = _failed(o)
    seen = {"load_failures": lf, "start_entity": o.get("start_entity"), "error": (o.get("error") or "")[:60]}
    return ok and o.get("start_entity") is None, seen


def _build_copy(tmp, name, allowlist=True, extra_broken=False):
    d = tmp / name
    shutil.copytree(ROOT / "ontology", d / "ontology")
    shutil.copytree(ROOT / "schemas", d / "schemas")
    (d / "scripts").mkdir()
    shutil.copy(ROOT / "scripts" / "build_index.py", d / "scripts" / "build_index.py")
    al = ROOT / "registry" / "known_held_links.json"
    if allowlist and al.exists():
        (d / "registry").mkdir()
        shutil.copy(al, d / "registry" / "known_held_links.json")
    if extra_broken:
        p = d / "ontology" / "animal" / "bee.json"
        e = json.loads(p.read_text())
        e.setdefault("links", []).append({"relation": "synergy", "target": "NO_SUCH_ENTITY_FIXTURE"})
        p.write_text(json.dumps(e))
    r = subprocess.run([sys.executable, str(d / "scripts" / "build_index.py")], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr)


def f6(tmp):
    try:
        import jsonschema  # noqa: F401  (build_index.py needs it; without it the fixture cannot run)
    except ImportError:
        return None, "jsonschema not installed: scripts/build_index.py cannot run"
    a, _ = _build_copy(tmp, "a")
    b, _ = _build_copy(tmp, "b", extra_broken=True)
    c, _ = _build_copy(tmp, "c", allowlist=False)
    seen = {"a_as_is_with_allowlist_exit": a, "b_extra_broken_link_exit": b, "c_no_allowlist_exit": c}
    return (a == 0 and b == 1 and c == 1), seen


FIXTURES = [
    ("F1", "verify.py", "unknown claim -> UNKNOWN, posterior null", f1),
    ("F2", "verify.py", "one claim over 5 attributes -> evidence count 1", f2),
    ("F3", "falsifier.py", "no match -> NOT_TESTED; 0 tests -> no score", f3),
    ("F4", "dependency_tree.py", "unresolved link reported, not dropped", f4),
    ("F5a", "falsifier.py", "load fails -> LOAD_FAILED, no thin substitution", f5_falsifier),
    ("F5b", "audit.py", "load fails -> LOAD_FAILED, scoped_ratio null", f5_audit),
    ("F5c", "dependency_tree.py", "load fails -> LOAD_FAILED, not built from thin entry", f5_dependency_tree),
    ("F6", "scripts/build_index.py", "broken link -> exit 1 (one KNOWN_HELD link allowlisted)", f6),
]


def run_all():
    rows = []
    for fid, inst, must, fn in FIXTURES:
        tmp = Path(tempfile.mkdtemp(prefix="lidfx_"))
        try:
            ok, seen = fn(tmp)
            state = "NOT_RUN" if ok is None else ("PASS" if ok else "FAIL")
        except Exception as e:  # an instrument that raises has not given the declared answer
            state, seen = "ERROR", "%s: %s" % (type(e).__name__, str(e)[:160])
            if os.environ.get("LID_FIXTURE_TRACE"):
                traceback.print_exc()
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        rows.append({"id": fid, "instrument": inst, "must_read": must, "state": state, "observed": seen})
    return rows


if __name__ == "__main__":
    rows = run_all()
    for r in rows:
        print("%-4s %-8s %-24s %s" % (r["id"], r["state"], r["instrument"], r["must_read"]))
        print("       observed: %s" % json.dumps(r["observed"], ensure_ascii=False)[:300])
    counts = {s: sum(r["state"] == s for r in rows) for s in ("PASS", "FAIL", "ERROR", "NOT_RUN")}
    print("fixtures: %d   PASS %d   FAIL %d   ERROR %d   NOT_RUN %d"
          % (len(rows), counts["PASS"], counts["FAIL"], counts["ERROR"], counts["NOT_RUN"]))
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        git = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        json.dump({"record": "known-answer fixtures", "commit": git, "counts": counts, "fixtures": rows},
                  open(out, "w"), indent=2, ensure_ascii=False)
        open(out, "a").write("\n")
    sys.exit(0 if counts["PASS"] == len(rows) else 1)
