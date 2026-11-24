#!/usr/bin/env python3
"""Extraction pass: deviation / range prose in scope.measurement_limits -> confidence records.

    python3 scripts/extract_deviation.py            write registry/confidence_records.json
    python3 scripts/extract_deviation.py --check    recompute and compare with the file; exit 1 if it differs
    python3 scripts/extract_deviation.py --selftest

Transcription only (registry/DECLARED.json, amendment 'process form + Kimi schemas').
Every string written is copied from an entity file: the prose (quote) and the matched
expressions. No number is parsed, computed, rounded or added. certainty and recurrence
are null: not recorded. Entity files are read and never written. Stdlib only.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "registry", "confidence_records.json")
NUM = r"\d+(?:[.,]\d+)?"
# Declared patterns. Order is the report order.
PATTERNS = [
    ("numeric_range", re.compile(NUM + r"\s*[-\u2013]\s*" + NUM + r"(?:\s*%)?")),
    ("percent", re.compile(NUM + r"\s*%")),
    ("varies", re.compile(r"\bvaries\b", re.I)),
    ("plus_minus", re.compile("\u00b1\\s*" + NUM + r"(?:\s*[-\u2013]\s*" + NUM + r")?(?:\s*%)?|\u00b1")),
]
# Words that suggest variation without the declared word 'varies'. Listed, never extracted.
NEAR = re.compile(r"\bvar(?:y|ied|ying|iable|iables|iation|iations|iability)\b", re.I)
KIND = {"numeric_range": "range", "percent": "percent", "plus_minus": "plus_minus_unspecified",
        "varies": "varies_unquantified"}


def attributes():
    for path in sorted(glob.glob(os.path.join(ROOT, "ontology", "*", "*.json"))):
        ent = json.load(open(path, encoding="utf-8"))
        for name, a in (ent.get("attributes") or {}).items():
            if isinstance(a, dict) and isinstance(a.get("scope"), dict):
                yield os.path.relpath(path, ROOT), ent.get("id"), name, a["scope"].get("measurement_limits")


def expressions(text):
    out = []
    for kind, rx in PATTERNS:
        for m in rx.finditer(text):
            out.append({"kind": kind, "text": m.group(0)})
    return out


def build():
    records, near, total, no_prose = [], [], 0, 0
    counts = {k: 0 for k, _ in PATTERNS}
    for path, eid, name, prose in attributes():
        total += 1
        if not isinstance(prose, str) or not prose:
            no_prose += 1
            continue
        ex = expressions(prose)
        if not ex:
            if NEAR.search(prose):
                near.append({"attribute": "%s.%s" % (eid, name), "source_field": "%s#attributes.%s.scope.measurement_limits"
                             % (path, name), "quote": prose, "matched_word": NEAR.search(prose).group(0)})
            continue
        kinds = sorted({e["kind"] for e in ex})
        for k in kinds:
            counts[k] += 1
        records.append({
            "attribute": "%s.%s" % (eid, name),
            "source_field": "%s#attributes.%s.scope.measurement_limits" % (path, name),
            "scope_ref": "%s#attributes.%s.scope" % (path, name),
            "deviation": {"value": None, "kind": KIND[kinds[0]] if len(kinds) == 1 else "mixed",
                          "quote": prose, "expressions": ex},
            "certainty": None,
            "recurrence": None})
    return {
        "record": "CONFIDENCE_RECORDS_EXTRACTED", "version": "0.1", "date": "2026-11-24", "status": "PROPOSED",
        "note": "Transcribed from scope.measurement_limits by scripts/extract_deviation.py. deviation.quote is the "
                "prose verbatim; deviation.expressions are substrings of it. deviation.value is null: nothing was "
                "parsed. certainty and recurrence are null: not recorded, which is neither zero nor certain. "
                "scope_ref points at the attribute's scope block; no regime block exists yet. A matched expression "
                "is not shown to be a deviation of the attribute's value: 'varies', a range or a percentage can "
                "describe something else in the sentence. That reading has not been made.",
        "counts": {"attributes_with_a_scope": total, "without_measurement_limits_prose": no_prose,
                   "records": len(records), "by_expression_kind": counts,
                   "kinds_overlap": "an attribute can match more than one kind, so the kinds sum to more than the records",
                   "near_matches_not_extracted": len(near),
                   "ledger_2026-11-24": {"records": 92, "numeric_range": 55, "percent": 26, "varies": 23, "plus_minus": 6,
                                         "note": "as stated in audit/2026-11-24/LID_translation_loss_ledger_2026-11-24.md; "
                                                 "its matching rule is not in the repository"}},
        "patterns": {k: rx.pattern for k, rx in PATTERNS},
        "confidence_records": records,
        "near_matches": {"rule": "no declared pattern matched; the prose holds a word from the 'vary' family other than "
                                 "'varies'. Listed for a reader; no record was made.", "pattern": NEAR.pattern,
                         "items": near}}


def dump(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def selftest():
    ok = []
    e = expressions("Varies ±0.01 with cell aspect ratio")
    ok.append(("'varies' and the plus-minus expression are both found, verbatim",
               [(x["kind"], x["text"]) for x in e] == [("varies", "Varies"), ("plus_minus", "±0.01")]))
    e = expressions("±5–10% deviation.")
    ok.append(("a range inside a plus-minus is kept as written",
               ("plus_minus", "±5–10%") in [(x["kind"], x["text"]) for x in e]))
    ok.append(("prose with no expression gives no record", expressions("Measured on a single colony.") == []))
    ok.append(("'variable' is a near match, not an extraction",
               expressions("Highly variable across sites.") == [] and NEAR.search("Highly variable across sites.")))
    built = build()
    ok.append(("every expression is a substring of its quote",
               all(x["text"] in r["deviation"]["quote"] for r in built["confidence_records"]
                   for x in r["deviation"]["expressions"])))
    ok.append(("every quote is the entity file's prose, byte for byte",
               all(r["deviation"]["quote"] == p for r in built["confidence_records"]
                   for path, eid, name, p in attributes() if "%s.%s" % (eid, name) == r["attribute"]
                   and r["source_field"].startswith(path))))
    ok.append(("no value, certainty or recurrence is filled",
               all(r["deviation"]["value"] is None and r["certainty"] is None and r["recurrence"] is None
                   for r in built["confidence_records"])))
    for name, good in ok:
        print("%s  %s" % ("PASS" if good else "FAIL", name))
    print("checks: %d   failed: %d" % (len(ok), sum(not g for _, g in ok)))
    return all(g for _, g in ok)


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(0 if selftest() else 1)
    built = build()
    if sys.argv[1:] == ["--check"]:
        same = os.path.exists(OUT) and open(OUT, encoding="utf-8").read() == dump(built)
        print("registry/confidence_records.json matches a fresh extraction: %s" % ("yes" if same else "NO"))
        sys.exit(0 if same else 1)
    open(OUT, "w", encoding="utf-8").write(dump(built))
    c = built["counts"]
    print("attributes with a scope: %d   records: %d   near matches (not extracted): %d"
          % (c["attributes_with_a_scope"], c["records"], c["near_matches_not_extracted"]))
    for k, v in c["by_expression_kind"].items():
        print("  %-14s %d" % (k, v))
