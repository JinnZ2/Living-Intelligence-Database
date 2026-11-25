#!/usr/bin/env python3
"""build_rev3.py -- writes reference_trace.schema.rev3.json (PROPOSED by this audit) from Kimi's
rev2, which is read from ../kimi_2026-11-25_rev2/ and not edited. Stdlib only. Deterministic.

Two changes, and only these (findings R1, R2 in LID_review_of_Kimi_rev2_and_pipeline_gate_2026-11-24.md):
  R1  status_history[].date: pattern '^\\d{4}-\\d{2}-\\d{2}$'  ->  ASCII digits, month 01-12,
      day 01-31, minLength 10, maxLength 10. (Python re: \\d matches any Unicode digit and $
      matches before a trailing newline.) Calendar validity (2026-02-30) stays checker territory.
  R2  top-level date: keeps format 'date' (asserted when a validator enables format checking) and
      adds the same pattern and lengths, so it is enforced when format checking is off.
Fails if rev2's two date properties are not where and what this script expects.
"""
import copy, hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REV2 = HERE.parent / "kimi_2026-11-25_rev2" / "reference_trace.schema.rev2.json"
PATTERN = "^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"


def main(out):
    raw = REV2.read_bytes(); s = json.loads(raw); r3 = copy.deepcopy(s)
    hist = r3["properties"]["nodes"]["items"]["properties"]["status_history"]["items"]["properties"]["date"]
    top = r3["properties"]["date"]
    if hist != {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                "description": "YYYY-MM-DD. A pattern, not format:date, so it is enforced even when format assertion is off."}:
        sys.exit(f"FAIL: rev2 history date is not as reviewed: {hist}")
    if top != {"type": "string", "format": "date"}:
        sys.exit(f"FAIL: rev2 top-level date is not as reviewed: {top}")
    hist.update({"pattern": PATTERN, "minLength": 10, "maxLength": 10,
                 "description": "YYYY-MM-DD. ASCII digits, month 01-12, day 01-31, exactly 10 characters. A pattern, not format:date, so it is enforced even when format assertion is off. Calendar validity (e.g. 02-30) is checker territory. rev3 (PROPOSED, audit 2026-11-24, finding R1)."})
    top.update({"pattern": PATTERN, "minLength": 10, "maxLength": 10,
                "description": "YYYY-MM-DD. format 'date' is asserted only when a validator enables format checking; the pattern and lengths hold either way. rev3 (PROPOSED, audit 2026-11-24, finding R2)."})
    r3["$comment"] = ("rev3, PROPOSED by the audit of 2026-11-24 (not by Kimi). Built by schema_rev3/build_rev3.py from rev2 "
                      f"(sha256 {hashlib.sha256(raw).hexdigest()}); changes R1 and R2 only.")
    Path(out).write_text(json.dumps(r3, indent=4, ensure_ascii=False) + "\n")
    print(json.dumps({"out": str(out), "sha256": hashlib.sha256(Path(out).read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(HERE / "reference_trace.schema.rev3.json"))
