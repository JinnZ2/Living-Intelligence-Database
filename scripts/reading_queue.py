#!/usr/bin/env python3
"""
reading_queue.py -- list the fields waiting for a reading. Stdlib only.

  python3 scripts/reading_queue.py            # write docs/reading_queue.md
  python3 scripts/reading_queue.py --check    # the written file matches a fresh run

One row per attribute field and found work: entity, field, value, the field's
definition text, PMID, DOI. No abstract text and no judgment. Works in state
FOUND_AS_CITED or FOUND_DIFFERS only; MATCH_SUSPECT is left out.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import provenance_chain as pc   # noqa: E402
import export_reference as er   # noqa: E402

ROOT = pc.ROOT
OUT = ROOT / "docs" / "reading_queue.md"


def rows(root=ROOT):
    reg = {e["id"]: e for e in json.loads((root / "registry" / "sources.json").read_text(encoding="utf-8"))["sources"]}
    out = []
    for ent, (path, steps) in sorted(er.head_steps(root).items()):
        d = json.loads((root / path).read_text(encoding="utf-8"))
        for s in steps:
            field = s["params"]["field"]
            if not field.startswith("attributes."):
                continue
            a = d["attributes"][field.split(".", 1)[1]]
            definition = (a.get("scope") or {}).get("definition") if isinstance(a, dict) else None
            for sid in s["inputs"]:
                ex = reg[sid].get("existence") or {}
                for w in ex.get("works", []):
                    m = w.get("matched_record")
                    if w["state"] in ("FOUND_AS_CITED", "FOUND_DIFFERS") and m and m.get("pmid"):
                        out.append({"entity": ent, "field": field, "value": s["value"], "definition": definition,
                                    "pmid": m["pmid"], "doi": m.get("doi"), "source_id": sid, "step_id": s["id"],
                                    "cited": "%s (%s)" % (w["cited"]["author"], w["cited"]["year"]),
                                    "state": w["state"]})
    return out


def render(root=ROOT):
    rs = rows(root)
    L = ["# Reading queue", "",
         "Status: waiting for readings. Written by `scripts/reading_queue.py`; do not edit",
         "by hand. Co-authored (JinnZ2 + Claude).", "",
         "One row per attribute field and found work: %d rows, %d fields. No abstract text"
         % (len(rs), len({(r["entity"], r["field"]) for r in rs})),
         "and no judgment is in this file. The readings arrive from an outside reader as",
         "`registry/attribute_readings.json`; the scripts here then build the steps and",
         "re-export. Rules: `registry/DECLARED.json`, amendments \"claim/number split\" and",
         "\"NOT_ADDRESSED + reading queue\".", "",
         "| entity | field | value | field definition text | PMID | DOI |", "|---|---|---|---|---|---|"]
    for r in rs:
        L.append("| %s | %s | %s | %s | %s | %s |" % (
            r["entity"], r["field"], json.dumps(r["value"]), (r["definition"] or "none recorded").replace("|", "\\|"),
            r["pmid"], r["doi"] or "none"))
    L += ["", "## Keys for the readings file", "",
          "| entity | field | cited as | existence state | source id | head step id |", "|---|---|---|---|---|---|"]
    for r in rs:
        L.append("| %s | %s | %s | %s | `%s` | `%s` |" % (r["entity"], r["field"], r["cited"], r["state"],
                                                        r["source_id"], r["step_id"]))
    L += ["", "## Values a reading may take", "",
          "- `claim_support`: STATED, RELATED, CONTRADICTED, NOT_ADDRESSED, NOT_READ",
          "- `number_support`: STATED, NOT_STATED",
          "- a quote of at most 25 words per field and work", ""]
    return "\n".join(L)


def main(argv):
    text = render()
    if "--check" in argv:
        same = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print("docs/reading_queue.md matches a fresh run: %s" % same)
        return 0 if same else 1
    OUT.write_text(text, encoding="utf-8")
    rs = rows()
    print("wrote %s: %d rows, %d fields" % (OUT.relative_to(ROOT), len(rs), len({(r["entity"], r["field"]) for r in rs})))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
