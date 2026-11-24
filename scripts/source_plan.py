#!/usr/bin/env python3
"""
source_plan.py -- rank unopened sources by the attribute fields each would unblock.
Plan only: reads the chain and the registry, fetches nothing. Stdlib only.

  python3 scripts/source_plan.py            # write docs/source_opening_plan.md
  python3 scripts/source_plan.py --check    # the written file matches a fresh run

A field is "unblocked" by a source when that source is an input of the field's
head step and the field reads NOT_ASSESSED (a value with a source and no status
tag). Opening the source is what could give the field a status; the count says
nothing about what the source will turn out to say.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import provenance_chain as pc   # noqa: E402
import export_reference as er   # noqa: E402

ROOT = pc.ROOT
OUT = ROOT / "docs" / "source_opening_plan.md"
TOP = 25
_PMID = re.compile(r"PMID:?\s*(\d{4,9})")
_DOI = re.compile(r"\b(10\.\d{4,9}/[^\s\]\[;,]+)")
_LOC = re.compile(r"\b\d{1,4}\s*(?:\(\d+\))?\s*:\s*\d+(?:\s*[-\u2013]\s*\d+)?")


def works(text):
    """How many works the string names: its ';'-separated parts."""
    return len([p for p in text.split(";") if p.strip()])


def locator(text):
    """A volume:pages locator in the string, or None."""
    m = _LOC.search(text)
    return m.group(0) if m else None


def identifiers(text):
    pm, doi = _PMID.search(text), _DOI.search(text)
    return (pm.group(1) if pm else None, doi.group(1).rstrip(".)") if doi else None)


def rank(root=ROOT):
    srcs = pc.load(root / "registry" / "sources.json", {"sources": []})["sources"]
    rows = {e["id"]: {"entry": e, "fields": [], "other": 0} for e in srcs}
    for ent, (_, steps) in sorted(er.head_steps(root).items()):
        for s in steps:
            for sid in s["inputs"]:
                if sid not in rows:
                    continue
                if s["params"]["field"].startswith("attributes.") and er.reading(s) == "NOT_ASSESSED":
                    rows[sid]["fields"].append((ent, s["params"]["field"]))
                else:
                    rows[sid]["other"] += 1
    unopened = [r for r in rows.values() if r["entry"]["opened"] is False]
    group = {}
    for grp in pc.near_duplicates(srcs).values():
        ids = [e["id"] for e in grp]
        n = sum(len(rows[i]["fields"]) for i in ids if rows[i]["entry"]["opened"] is False)
        for i in ids:
            group[i] = (n, sorted(ids))
    for r in unopened:
        r["group_fields"], r["group"] = group.get(r["entry"]["id"], (len(r["fields"]), [r["entry"]["id"]]))
        r["works"] = works(r["entry"]["string"])
    unopened.sort(key=lambda r: (-len(r["fields"]), -r["group_fields"], r["works"], r["entry"]["id"]))
    return srcs, unopened


def render(root=ROOT):
    srcs, un = rank(root)
    total = sum(len(r["fields"]) for r in un)
    with_id = sum(1 for r in un if any(identifiers(r["entry"]["string"])))
    hist = {}
    for r in un:
        hist[len(r["fields"])] = hist.get(len(r["fields"]), 0) + 1
    L = ["# Source-opening pass: plan", "",
         "Status: PROPOSED plan. Nothing was fetched or opened. Written by",
         "`scripts/source_plan.py` from the chain and `registry/sources.json`;",
         "do not edit by hand. Co-authored (JinnZ2 + Claude), 2026-11-24.", "",
         "Status comes from reading the source, not from its evidence_type. A field",
         "is counted as unblocked by a source when the source is an input of the",
         "field's head step and the field reads NOT_ASSESSED. The count is how many",
         "fields a reading could give a status to. It is not a forecast of what the",
         "source says.", "",
         "| | |", "|---|---|",
         "| sources in the registry | %d |" % len(srcs),
         "| opened (abstract read) | %d |" % (len(srcs) - len(un)),
         "| unopened | %d |" % len(un),
         "| unopened with a PMID or DOI in the string | %d |" % with_id,
         "| NOT_ASSESSED attribute fields behind unopened sources | %d |" % total,
         "| those behind the top %d | %d |" % (TOP, sum(len(r["fields"]) for r in un[:TOP])), "",
         "Fields per unopened source: " + ", ".join(
             "%d source(s) unblock %d" % (n, k) for k, n in sorted(hist.items(), reverse=True)) + ".", "",
         "## Top %d" % TOP, "",
         "**The rank by fields unblocked is flat.** One source string is one attribute",
         "field: every unopened source unblocks 1 field or 0. So the first key decides",
         "nothing, and the order below comes from the tie-breaks:", "",
         "1. fields unblocked by the string (1 for all 25);",
         "2. `group`: fields behind the string's near-duplicate candidate group",
         "   (`provenance_chain.py dups`: same first word and same year). A group is",
         "   a candidate that several strings name one work, so one reading may serve",
         "   several fields. Nothing was merged and no candidate was confirmed;",
         "3. `works`: fewer works named in the string first (its `;`-separated parts),",
         "   as fewer things to open per field;",
         "4. source id.", "",
         "No string carries a PMID or a DOI, so none is listed. `locator` is a",
         "volume:pages pattern found in the string, when there is one.", "",
         "| # | fields | group | works | source id | PMID | DOI | locator | entities | source string |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(un[:TOP], 1):
        e = r["entry"]
        pm, doi = identifiers(e["string"])
        ents = sorted({x[0] for x in r["fields"]})
        L.append("| %d | %d | %d | %d | `%s` | %s | %s | %s | %s | %s |" % (
            i, len(r["fields"]), r["group_fields"], r["works"], e["id"][:12], pm or "not in string",
            doi or "not in string", locator(e["string"]) or "none", ", ".join(ents),
            e["string"].replace("|", "\\|")))
    L += ["", "## Fields behind the top %d" % TOP, ""]
    for i, r in enumerate(un[:TOP], 1):
        L.append("%d. `%s`: %s" % (i, r["entry"]["id"][:12],
                                   "; ".join("%s %s" % f for f in r["fields"])))
    L += ["", "## What the plan does not settle", "",
          "- Whether a string names one findable work. \"not in string\" means the",
          "  string carries no PMID or DOI; the work has to be searched for by author,",
          "  year and topic, and a search can come back empty or ambiguous.",
          "- Whether the source supports the value. A reading can end in OBSERVED,",
          "  DERIVED, PROPOSED, or in the value being withdrawn.",
          "- Order of work. The rank is by count only. It does not weigh how hard a",
          "  source is to obtain or how much the fields matter.", ""]
    return "\n".join(L)


def main(argv):
    text = render()
    if "--check" in argv:
        same = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print("docs/source_opening_plan.md matches a fresh run: %s" % same)
        return 0 if same else 1
    OUT.write_text(text, encoding="utf-8")
    _, un = rank()
    print("wrote %s" % OUT.relative_to(ROOT))
    for i, r in enumerate(un[:TOP], 1):
        pm, doi = identifiers(r["entry"]["string"])
        print("%2d  f%d g%d w%d  %s  PMID %s  DOI %s  %-13s %s" % (
            i, len(r["fields"]), r["group_fields"], r["works"], r["entry"]["id"][:12], pm or "-", doi or "-",
            ",".join(sorted({x[0] for x in r["fields"]})), r["entry"]["string"][:100]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
