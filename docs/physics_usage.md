# Physics usage of the database

Status: PROPOSED. Co-authored (JinnZ2 + Claude), 2026-11-24. Stdlib only.

## The idea

A living system that persists has already run an experiment: its mechanism
was tried against the physics of its setting and it is still here. The
database records those mechanisms. This file describes two ways to use the
records, and what each one can and cannot change.

This is a way of reading the records, not a finding. Persistence shows that
a mechanism was sufficient in its setting. It does not show the mechanism
is optimal, and it says nothing outside the recorded `scope`.

Every path below is assembled from database records and their cited sources,
by step id and source id. Nothing is taken from a model's output.

## Two tracks

| | Track A: runtime reference | Track B: example export |
|---|---|---|
| file | `reference/lid_reference.jsonl` | `examples/lid_examples.jsonl` |
| tool | `scripts/export_reference.py` | `scripts/export_examples.py` |
| used | read during a session, under `reference/READING_PROTOCOL.md` | as input to a separate training run |
| changes | what one session can look up; nothing persists after it | nothing by itself. A model changes only if someone runs training on it |

A runtime reference affects one session. Training needs a separate run, and
no training was done here.

## Track A

`export_reference.py` copies the head step of every field into one line per
entity and adds a `reading` label derived from the step. It assigns no
status. The evidence-type table in `docs/provenance_chain.md` stays not
applied, so 227 attribute values read NOT_ASSESSED.

| reading | fields |
|---|---|
| OBSERVED | 11 |
| DERIVED | 1 |
| PROPOSED | 12 |
| NOT_ASSESSED | 227 |
| UNSOURCED | 12 |
| NO_INFORMATION | 40 |
| total | 303, across 122 entities |

Test (`export_reference.py --test`, questions in
`reference/planted_questions.json`): 10 planted questions answered from the
reference alone, each citing step ids; 10 of 10 give the expected reading.
One planted wrong record (a copy of ANT `coordination.carrier` with the
status raised to OBSERVED and the value changed) is refused: its value and
status differ from the step it cites.

An outside-reader version of this test is packaged under `blind/` (see
`blind/README.md`); it has not been given to any reader.

Limits of the test: the questions and the expected readings were written by
the same hand that wrote the answering function, and the function is a
lookup, not a model. The test shows the reference carries what the protocol
needs and that a changed field is caught. It does not show that a model
reading the file follows the protocol.

## Track B

`export_examples.py` writes one example per field that passes the filters
declared in `registry/DECLARED.json` (amendment "physics usage: example
export", committed before the script existed). It refuses to run when the
reference fails its own check, and refuses to write when its own check fails.

An example holds `question`, `derivation_path`, `answer` (claim, status,
scope) and `provenance` (step ids, source ids). The path lists the entity's
included fields in the declared order observation, mechanism, physics, ending
with the target and a status element. It is an ordering of record fields by
declared role. No stored step names another field as its input, so the path
does not claim one field was derived from another. The role mapping is
PROPOSED and was written here.

| kind | rule | train | hold-out |
|---|---|---|---|
| OBSERVED | status OBSERVED, with a source | 5 | 6 |
| DERIVED | status DERIVED, with a source; basis stated | 1 | 0 |
| PROPOSED | labeled "PROPOSED, not established" | 5 | 1 |
| UNMEASURED | the field is null; the claim is "unmeasured" | 28 | 12 |
| CONTESTED_LABEL | the label does not decide; function fields given | 2 | 0 |
| total | | 41 | 19 |

| answer status | train | hold-out |
|---|---|---|
| OBSERVED | 5 | 6 |
| DERIVED (basis: OBSERVED) | 1 | 0 |
| PROPOSED | 5 | 1 |
| null | 30 | 12 |

| ontology type | train | hold-out |
|---|---|---|
| plant | 28 | 9 |
| social | 13 | 10 |

Hold-out, by entity, stratified (amendment "stratified hold-out", declared
before this split was computed). `has_statused_field` is yes when the entity
has at least one OBSERVED, DERIVED or PROPOSED example. Within a stratum the
entities are sorted by sha256 of the entity id and the first
max(1, ceil(0.2 × n)) are held out.

| has_statused_field | entities, in sha256 order | hold-out |
|---|---|---|
| yes (3) | VENUS, ANT, STONE_LEDGER | VENUS |
| no (5) | BEE_NEST_SITE, MY, SLIME, QUORUM, MIMOSA | BEE_NEST_SITE |

**n too small to measure.** With 8 entities and 2 held out, the split shows
the rule works. No rate computed on it is a measurement.

The first split (commit `2f3d933`: first 2 of 8 by sha256, unstratified)
held out BEE_NEST_SITE and MY, 17 examples, all UNMEASURED.

Excluded fields: 225 NOT_ASSESSED (values with a source and no status tag),
12 UNSOURCED, 6 `assumption_trace`.

What the counts show:

- 8 of 122 entities give any example, in 2 of 9 ontology types. The other
  114 entities have attribute values only, and those carry no status tag.
- 40 of 60 examples are UNMEASURED. The set mostly teaches the void.
- VENUS is the only entity with `gate_sensing` or statused
  `functional_intelligence` fields, and it is held out. Train therefore has
  no OBSERVED or PROPOSED example from those two blocks: its 11 statused
  examples are all `coordination` fields of ANT and STONE_LEDGER. The
  hold-out tests those blocks on an unseen entity with no train example of
  the same block.
- 5 of the 12 PROPOSED fields and 1 of the 2 DERIVED fields are not targets:
  the 6 `assumption_trace` fields are PROPOSED and excluded by rule, and one
  DERIVED field has no source.

No model was trained. Whether these examples change a model is not tested
here and needs a separate run.

## Source-opening pass

`docs/source_opening_plan.md` (written by `scripts/source_plan.py`) ranks the
231 unopened sources. It is a plan: nothing was fetched. Status comes from
reading the source, not from its evidence_type.

Stage 1 (existence check, top 10 entities) is in `docs/existence_check.md`.
It asks only whether a cited work can be found in PubMed as cited. It read no
abstract, so it gave no field a status and marked no source opened.
