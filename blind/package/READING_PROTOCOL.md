# Reading protocol for `lid_reference.jsonl`

Status: PROPOSED. Co-authored (JinnZ2 + Claude), 2026-11-24. This is for a
reader, human or model, that uses the reference inside one session. It is
separate from the repo-level `READING_PROTOCOL.md`, which still applies.

One line per entity. Each line has `fields`; each field is copied from one
head step of the provenance chain.

## Rules

1. **Read `reading` and `status` before `value`.** The value means nothing
   until you know which of the six readings it carries.
2. **PROPOSED is not a fact.** Say "proposed" when you use it. The same holds
   for DERIVED: name its basis (`DERIVED (basis: PROPOSED)` is still proposed).
3. **Null is no information.** A null value is not "no", not "zero" and not
   "absent in nature". `void.reason` gives the record's words for the gap
   when it has any.
4. **Follow the ids.** `step_id` names the step in `provenance/<id>.json`;
   `source_ids` name entries in `registry/sources.json`. Cite the step id
   with anything you take from a field.
5. **Label slots stay open; function fields decide.** A `contested_label`
   entry records that a word was claimed or disputed, and by which source.
   It does not answer the question. The five `functional_intelligence`
   capability fields do, and when they are null the answer is "no information".

## The six readings

| `reading` | when | how to use it |
|---|---|---|
| OBSERVED | status OBSERVED, with a source | as an observation, inside its `scope` |
| DERIVED | status DERIVED, with a source | as a derivation; state the basis |
| PROPOSED | status PROPOSED | as a proposal only |
| NOT_ASSESSED | a value with a source and no status tag | "recorded with a source, status not assessed". Most attribute values are here |
| UNSOURCED | a value with no source (void UNMAPPED) | not as a finding |
| NO_INFORMATION | the field is null (void VOID or LEXICAL_VOID) | "no information" |

Void is read before status: a DERIVED value with no source reads UNSOURCED.

## What the reference does not tell you

- That a source is correct. No source was opened by the export. `opened` in
  `registry/sources.json` says which strings record an abstract having been read.
- Anything about a field that is not in it. A missing field is not a null field.
- History. Superseded steps are only in `provenance/`. Every line carries
  `snapshot_class: SUMMARY_ONLY`.

## Checking a field

`python3 scripts/export_reference.py --check` refuses a field whose step id
is not a head step, or whose value, status, void or source ids differ from
that step, or whose source id is not in the registry. A field that fails is
not to be used.
