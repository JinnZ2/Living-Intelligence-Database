#!/usr/bin/env python3
"""
biosphere_candidates.py -- rule-based list of LID records that may depend on BIOSPHERE.
Python standard library only. No network. Deterministic. Reads, never writes, the repository.

  python3 biosphere_candidates.py <repo_root> <out.json>
  python3 biosphere_candidates.py --selftest

The owner stated that the biosphere is a dependency of many entities. This script does
not decide which ones. It lists candidates by two declared rules, and every candidate
is UNCHECKED until the owner reads it:

  B1  ORGANISM_RECORD   the record's ontology is 'animal' or 'plant' (a living organism
                        that exists inside the biosphere's material and energy boundary).
  B2  CONDITION_TERM    an attribute's scope text (definition, measurement_limits,
                        dependencies) names a biosphere-carried condition: one of TERMS.

A record can match both. A record matching neither is listed as NO_RULE_MATCHED, which
does not mean independent (for example, a social or AI record may still depend on the
biosphere through the people or the energy that carry it). The terms are an
English-language word list; matching them is a lexical test, not a reading.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

TERMS = {
    "sunlight": r"\bsun(?:light|shine)?\b|\bsolar\b|\birradiance\b|\bphotosynth\w*",
    "water": r"\bwater\b|\bhumidity\b|\bmoisture\b|\brain\w*\b|\bdrought\b",
    "temperature": r"\btemperature\w*\b|°C|\bthermal\b|\bheat\b|\bcold\b",
    "carbon": r"\bcarbon\b|\bCO2\b|\bCO₂\b",
    "oxygen": r"\boxygen\b|\bhypoxi\w*|\bO2\b|\bO₂\b",
    "soil": r"\bsoil\w*\b|\bsubstrate\b",
    "nutrient": r"\bnutrient\w*\b|\bnitrogen\b|\bphosph\w*",
    "season": r"\bseason\w*\b|\bwinter\b|\bsummer\b|\bspring\b|\bphotoperiod\b|\bday length\b",
}
TERM_RE = {k: re.compile(v, re.I) for k, v in TERMS.items()}
ORGANISM_ONTOLOGIES = ("animal", "plant")


def scope_text(av):
    sc = av.get("scope") if isinstance(av, dict) else None
    if not isinstance(sc, dict):
        return ""
    parts = []
    for k in ("definition", "measurement_limits", "dependencies"):
        v = sc.get(k)
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            parts.extend(str(x) for x in v)
    return " ".join(parts)


def terms_in(text):
    return sorted(k for k, rx in TERM_RE.items() if rx.search(text or ""))


def classify(record):
    rules, term_hits = [], {}
    if record.get("ontology") in ORGANISM_ONTOLOGIES:
        rules.append("B1")
    for an, av in (record.get("attributes") or {}).items():
        t = terms_in(scope_text(av))
        if t:
            term_hits[an] = t
    if term_hits:
        rules.append("B2")
    return rules, term_hits


def run(root):
    root = Path(root)
    idx = json.load(open(root / "ontology_index.json"))
    rows, failures = [], []
    for ent in idx["entities"]:
        try:
            d = json.load(open(root / ent["path"]))
        except (OSError, ValueError) as ex:
            failures.append({"id": ent["id"], "path": ent["path"], "reason": type(ex).__name__})
            continue
        rules, hits = classify(d)
        rows.append({"id": ent["id"], "path": ent["path"], "ontology": d.get("ontology"),
                     "rules": rules, "terms_by_attribute": hits,
                     "result": "CANDIDATE" if rules else "NO_RULE_MATCHED",
                     "status": "UNCHECKED"})
    by = {}
    for r in rows:
        key = "+".join(r["rules"]) or "NONE"
        by[key] = by.get(key, 0) + 1
    term_counts = {}
    for r in rows:
        for t in sorted({t for ts in r["terms_by_attribute"].values() for t in ts}):
            term_counts[t] = term_counts.get(t, 0) + 1
    return {"record": "BIOSPHERE_DEPENDENCY_CANDIDATES", "status": "PROPOSED; every row UNCHECKED",
            "rules": __doc__.split("A record can match")[0].strip(), "terms": TERMS,
            "records": len(rows), "load_failures": failures, "rule_counts": dict(sorted(by.items())),
            "records_per_term": dict(sorted(term_counts.items())), "rows": rows}


def selftest():
    cases = [
        ({"ontology": "animal", "attributes": {}}, ["B1"]),
        ({"ontology": "ai", "attributes": {"x": {"scope": {"definition": "accuracy on CIFAR-10"}}}}, []),
        ({"ontology": "plant", "attributes": {"x": {"scope": {"measurement_limits": "falls below 12°C"}}}}, ["B1", "B2"]),
        ({"ontology": "energy", "attributes": {"x": {"scope": {"definition": "solar irradiance at 1 AU"}}}}, ["B2"]),
        ({"ontology": "shape", "attributes": {"x": {"scope": {"definition": "the plane tiling"}}}}, []),
    ]
    ok = True
    for rec, want in cases:
        got, _ = classify(rec)
        ok &= got == want
        print("PASS" if got == want else "FAIL", want, "got", got)
    print("selftest", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(0 if selftest() else 1)
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    out = run(sys.argv[1])
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, ensure_ascii=False, sort_keys=False) + "\n")
    print(json.dumps({k: out[k] for k in ("records", "rule_counts", "records_per_term", "load_failures")}))
    if out["load_failures"]:
        sys.exit(2)
