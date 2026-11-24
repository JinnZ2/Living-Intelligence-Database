#!/usr/bin/env python3
"""Find deviation information already written in measurement_limits prose. Nothing is invented.

    python3 deviation_extract.py REPO_ROOT [OUT.json]      (reads REPO_ROOT, never writes it)
    python3 deviation_extract.py --selftest

Python standard library only. Deterministic. No network.

For every scoped attribute, the prose is kept verbatim, with its sha256. Each numeric expression
in it is located by character offsets and given ONE role by a declared rule:

  DEVIATION_CANDIDATE   spread or uncertainty language ('±', 'uncertainty', 'error', 'deviat',
                        'accuracy', 'precision', 'tolerance', 'varies', 'variation') in the same
                        sentence as a unitless or percent number. Whether the spread belongs to
                        THIS attribute's value, rather than to something else the sentence
                        mentions, is UNCHECKED: a reader decides.
  SENSITIVITY_CANDIDATE a rate per unit of a condition ('%/bar', 'per °C', '/K'). This is a
                        derivative, not a spread.
  CONDITION_NUMBER      a number carrying a physical or count unit, with no spread language.
                        It is raw material for a regime axis (ledger L03), not a deviation.
  SELF_REFERENCE        the number is the attribute's own value, quoted in the prose.
  CONDITIONAL_CHANGE    a change verb with a percent or fold, or '<verb> ... by <amount>'
                        ('decreases 25% in dim light', 'reduce D by 0.3-0.8 units'):
                        how the value moves when a condition changes. Close to a sensitivity,
                        but the size of the condition change is not always given.
  VALUE_RANGE_CANDIDATE a range on the value's own 0–1 scale ('range 0.6-0.95 depending on
                        conditions'): the value under other conditions, i.e. scope.
  UNCHECKED             a number whose role the rules cannot settle.
Rules are applied in the order R0, R3, R1, R6, R7, R2, R4, R5; the first that fits decides.
Sentences that say 'varies' or 'variable' with no number are recorded as QUALITATIVE_VARIATION:
spread exists and its size is UNKNOWN.

Interval arithmetic is done only for an absolute '±x' on a unitless value. The result is a
DERIVED candidate interval: no value is replaced, and nothing is written into any record.
"""
import hashlib, json, re, sys
from pathlib import Path

UNIT = (r"(?:°C|°F|K\b|kelvin|mK|µK|nK|cm|mm|µm|nm|km|m\b|s\b|ms|µs|ns|min|minutes?|h\b|hours?|days?|weeks?|"
        r"months?|years?|yr|Gyr|Myr|Ma\b|Ga\b|Hz|kHz|MHz|GHz|THz|Pa|kPa|MPa|GPa|bar|atm|eV|keV|MeV|GeV|W\b|kW|MW|"
        r"J\b|kJ|cal|kcal|g\b|kg|mg|µg|L\b|mL|V\b|mV|kV|A\b|mA|T\b|mT|nT|dB|ppm|ppb|layers?|workers?|"
        r"individuals?|generations?|cells?|neurons?|nodes?|species|meters?|kilometers?|seconds?|bits?|"
        r"tokens?|parameters?|samples?|steps?|×|x\b|fold|°)")
NUM = r"[<>≈~]?\s*\d+(?:[.,]\d+)?(?:\s*[–-]\s*\d+(?:[.,]\d+)?)?"
SPREAD = re.compile(r"±|\buncertaint|\berror\b|\berrors\b|deviat|\baccura|\bprecis|toleranc|\bvar(?:ies|y|iation|iability|iable)\b", re.I)
VARIES = re.compile(r"\bvar(?:ies|y|iation|iability|iable)\b", re.I)
EXPR = re.compile(r"(±\s*)?(" + NUM + r")\s*(%)?(\s*(?:/|per\s+)\s*" + UNIT + r")?(?:-|\s*)(" + UNIT + r")?")
SENT = re.compile(r".+?(?:[.;!?](?=\s|$)|$)", re.S)


CHANGE = re.compile(r"\b(?:decreas|increas|drop|rise|rises|rising|chang|reduc|degrad|improv|fall|falls|shrink|grow|boost|lower|rais)\w*", re.I)


def classify(sentence, m, value):
    pm, num, pct, per, unit = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
    nums = numbers(num)
    spread = bool(SPREAD.search(sentence))
    isnum = isinstance(value, (int, float)) and not isinstance(value, bool)
    if isnum and not pm and not pct and not unit and len(nums) == 1 and nums[0] == float(value):
        return "SELF_REFERENCE", "R0: the number is the attribute's own value"
    if per:
        return "SENSITIVITY_CANDIDATE", "R3: rate per unit of a condition"
    if pm:
        return "DEVIATION_CANDIDATE", "R1: explicit ±"
    by_amount = bool(re.search(r"\bby\s*~?\s*$", sentence[:m.start()])) and CHANGE.search(sentence)
    if by_amount or ((pct or (unit and unit.strip() in ("×", "x", "fold"))) and CHANGE.search(sentence)):
        return "CONDITIONAL_CHANGE", "R6: change verb with a percent or fold: a change under a condition, not a spread"
    if (isnum and 0 <= value <= 1 and not pct and not unit and len(nums) == 2
            and all(0 <= n <= 1 for n in nums) and "." in num):
        return "VALUE_RANGE_CANDIDATE", "R7: a range on the value's own 0–1 scale: the value under other conditions"
    if spread and (pct or ("." in num and not unit)):
        return "DEVIATION_CANDIDATE", "R2: spread language with a percent, or a unitless decimal"
    if unit and not spread:
        return "CONDITION_NUMBER", "R4: unit-bearing number, no spread language"
    return "UNCHECKED", "R5: role not settled by the rules"


def numbers(s):
    return [float(x.replace(",", ".")) for x in re.findall(r"\d+(?:[.,]\d+)?", s)]


def extract(text, value):
    out, qual = [], []
    for sm in SENT.finditer(text or ""):
        sent = sm.group(0)
        found = False
        for m in EXPR.finditer(sent):
            if not re.search(r"\d", m.group(2)):
                continue
            # a bare integer that is part of a word or label (e.g. 'd10', 'H2O', 'L5') is skipped
            st = sm.start() + m.start(2) + (len(m.group(2)) - len(m.group(2).lstrip("<>≈~ ")))
            if st > 0 and (text[st - 1].isalpha() or text[st - 1] in "_^"):
                continue
            role, rule = classify(sent, m, value)
            e = {"span": m.group(0).strip(), "start": sm.start() + m.start(), "end": sm.start() + m.end(),
                 "role": role, "rule": rule, "numbers": numbers(m.group(2)),
                 "percent": bool(m.group(3)), "pm": bool(m.group(1)),
                 "unit": (m.group(5) or "").strip() or None, "per": (m.group(4) or "").strip() or None}
            if (e["pm"] and not e["percent"] and not e["unit"] and len(e["numbers"]) == 1
                    and isinstance(value, (int, float)) and not isinstance(value, bool)):
                d = e["numbers"][0]
                e["derived_interval"] = {"low": round(value - d, 10), "high": round(value + d, 10),
                                         "label": "DERIVED candidate; value unchanged; ownership of the spread UNCHECKED"}
            out.append(e); found = True
        if not found and VARIES.search(sent):
            qual.append({"sentence": sent.strip(), "start": sm.start(), "role": "QUALITATIVE_VARIATION",
                         "note": "spread exists; size UNKNOWN"})
    return out, qual


def summarise(exprs, qual):
    roles = {e["role"] for e in exprs}
    if "DEVIATION_CANDIDATE" in roles:
        return "HAS_DEVIATION_CANDIDATE"
    if "VALUE_RANGE_CANDIDATE" in roles:
        return "HAS_VALUE_RANGE"
    if "CONDITIONAL_CHANGE" in roles:
        return "HAS_CONDITIONAL_CHANGE"
    if "SENSITIVITY_CANDIDATE" in roles:
        return "HAS_SENSITIVITY_ONLY"
    if qual:
        return "QUALITATIVE_ONLY"
    if exprs:
        return "NUMBERS_NOT_DEVIATION"
    return "NO_NUMBER"


def run(root):
    root = Path(root)
    idx = json.load(open(root / "ontology_index.json"))
    rows, load_failures = [], []
    for ent in idx["entities"]:
        try:
            d = json.load(open(root / ent["path"]))
        except (OSError, ValueError) as ex:
            load_failures.append({"id": ent["id"], "path": ent["path"], "reason": type(ex).__name__}); continue
        for an, av in d.get("attributes", {}).items():
            if not (isinstance(av, dict) and isinstance(av.get("scope"), dict)):
                continue
            ml = av["scope"].get("measurement_limits")
            exprs, qual = extract(ml if isinstance(ml, str) else "", av.get("value"))
            rows.append({"entity": ent["id"], "path": ent["path"], "attribute": an, "value": av.get("value"),
                         "measurement_limits": ml,
                         "measurement_limits_sha256": hashlib.sha256((ml or "").encode()).hexdigest() if isinstance(ml, str) else None,
                         "expressions": exprs, "qualitative": qual, "summary": summarise(exprs, qual),
                         "status": "PROPOSED; every candidate is UNCHECKED until read"})
    counts = {}
    for r in rows:
        counts[r["summary"]] = counts.get(r["summary"], 0) + 1
    role_counts = {}
    for r in rows:
        for e in r["expressions"]:
            role_counts[e["role"]] = role_counts.get(e["role"], 0) + 1
    return {"record": "DEVIATION_EXTRACTION", "status": "PROPOSED", "rules": __doc__.split("Interval arithmetic")[0].strip(),
            "attributes": len(rows), "load_failures": load_failures,
            "attribute_summary_counts": dict(sorted(counts.items())), "expression_role_counts": dict(sorted(role_counts.items())),
            "derived_intervals": sum(1 for r in rows for e in r["expressions"] if "derived_interval" in e),
            "rows": rows}


def selftest():
    cases = [  # known answers taken from real prose in the repository
        ("Varies ±0.01 with cell aspect ratio", 0.97, "DEVIATION_CANDIDATE", {"low": 0.96, "high": 0.98}),
        ("Satellite constellation coverage gaps introduce systematic uncertainty of ±25%.", 0.92, "DEVIATION_CANDIDATE", None),
        ("Perfect Pascal's law requires ideal incompressibility — water deviates 0.004%/bar.", 0.99, "SENSITIVITY_CANDIDATE", None),
        ("Regeneration rate is temperature-dependent — faster in warmer water (22°C: 6 weeks; 15°C: 10 weeks).", 0.78, "CONDITION_NUMBER", None),
        ("Novel environments require 20-30 minutes of exploration before stable place field maps form.", 0.92, "CONDITION_NUMBER", None),
        ("Unihemispheric fraction varies with perceived predation risk.", 0.92, "QUALITATIVE_VARIATION", None),
        ("d⁰ and d10 metals gain no stabilization", 0.93, None, None),
        ("Measured values range 0.6-0.95 depending on conditions.", 0.85, "VALUE_RANGE_CANDIDATE", None),
        ("Strike accuracy decreases 25% in sub-optimal illumination.", 0.92, "CONDITIONAL_CHANGE", None),
        ("The 0.97 measures the accuracy of retention.", 0.97, "SELF_REFERENCE", None),
        ("Storm damage and bleaching reduce D by 0.3-0.8 units.", 0.91, "CONDITIONAL_CHANGE", None),
        # a unit-bearing number in a sentence that also has spread language ("error", about a different
        # quantity): the rules cannot tell which quantity the number belongs to, so UNCHECKED by design.
        ("The 6-hour phase shift produces predictable 90° error.", 0.93, "UNCHECKED", None),
        ("Novel environments require a 6-hour wait.", 0.93, "CONDITION_NUMBER", None),
        ("Thermoregulation precision requires minimum colony size of ~5000 bees.", 0.94, "UNCHECKED", None),
    ]
    ok = True
    for text, v, want, interval in cases:
        ex, q = extract(text, v)
        got = ex[0]["role"] if ex else (q[0]["role"] if q else None)
        good = got == want and (interval is None or ex[0].get("derived_interval", {}).get("low") == interval["low"]
                                and ex[0].get("derived_interval", {}).get("high") == interval["high"])
        print(("PASS" if good else "FAIL"), want, "<-", text[:70], "| got", got)
        ok &= good
    print("selftest", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:2] == ["--selftest"]:
        sys.exit(selftest())
    res = run(sys.argv[1])
    out = sys.argv[2] if len(sys.argv) > 2 else "deviation_extraction_results.json"
    json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: res[k] for k in ["attributes", "attribute_summary_counts", "expression_role_counts", "derived_intervals", "load_failures"]}, ensure_ascii=False))
