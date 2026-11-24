# Blind package

Status: PROPOSED; not yet given to any reader. Co-authored (JinnZ2 + Claude),
2026-11-24. Built by `scripts/build_blind.py`; do not edit the files by hand.

Hand over `package/` only, the four files and nothing else:

| file | holds |
|---|---|
| `package/READING_PROTOCOL.md` | a byte copy of `reference/READING_PROTOCOL.md` |
| `package/lid_reference.jsonl` | a copy of the reference with one field changed |
| `package/questions.jsonl` | 10 questions: id, question, entity id |
| `package/answer_template.json` | instructions and 10 empty answers citing step ids |

Kept out of the package: this file, `expected.jsonl` (the expected reading
per question and the changed field, with the true record) and `MANIFEST.json`
(sha256 of every file).

**`package/lid_reference.jsonl` is not the reference.** It differs from
`reference/lid_reference.jsonl` in exactly one field. Nothing inside the
package says which, or that there is one. Do not use the package copy for
anything else.

## What a returned answer file can show

- Whether the reader gives the expected reading and cites the expected step
  id, per question.
- Whether PROPOSED is worded as a proposal and null as no information.
- Whether the changed field is stated as an observation or refused, and on
  what ground. From the package alone it can be caught by status and
  provenance: it reads OBSERVED with no source id.

## What it cannot show

- 10 questions and one reader are too few to measure a rate.
- The repository is public and holds `expected.jsonl`. A reader with access
  to the repository, or trained on it, is not blind. The test is blind only
  for a reader given the package and nothing else.
- Scoring is by hand against `expected.jsonl`. No scorer is written.
