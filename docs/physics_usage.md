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

Limits of the test: the questions and the expected readings were written by
the same hand that wrote the answering function, and the function is a
lookup, not a model. The test shows the reference carries what the protocol
needs and that a changed field is caught. It does not show that a model
reading the file follows the protocol.
