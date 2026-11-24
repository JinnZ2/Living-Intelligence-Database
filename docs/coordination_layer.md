# Coordination layer

Status: schema, one pilot record and four stubs. No field in any record is
OBSERVED yet. Co-authored (JinnZ2 + Claude), 2026-11-24.

## Purpose

Text corpora carry assumptions such as "coordination requires money" or "only
humans innovate". This layer gives each such assumption a place to be checked
against a physical mechanism in a living system. Every assumption points at an
entity record that can be opened and inspected; none is a stopping point.

The layer is an optional block named `coordination` on any entity. It is
defined once in `schemas/coordination.schema.json` and referenced from every
per-type schema (`ai`, `animal`, `crystal`, `energy`, `plant`, `plasma`,
`shape`, `social`, `temporal`). `schemas/intelligence.schema.json` carries an
inline copy; no entity uses that schema today.

## Fields

| field | meaning |
|---|---|
| `carrier` | the physical token exchanged (carbon, pheromone, phase, shell and art) |
| `signal` | how need or offer is sensed (gradient, quorum, dance) |
| `record` | where the state lives (environment, body, shared object) |
| `closure` | how an exchange completes and becomes visible |
| `trust_basis` | what accumulates (completed cycles, reinforcement) |
| `energy_cost` | upkeep of the coordination itself: `{joules, per, note}`. `joules` is a number only if a source measured it |
| `loop_topology` | `cycles` in the exchange, and `observer_cuts`: for each way of observing, which cycles are still inside the record |
| `assumption_trace` | list of corpus assumptions this entity tests |
| `sources` | citations per field (key = field name) |
| `status` | per field: `OBSERVED`, `DERIVED` or `PROPOSED` |
| `notes` | optional free text per field |

Status tags:

- `OBSERVED`: stated by a source that was opened and read. The citation says
  how deep the read was (abstract, full text).
- `DERIVED`: worked out from other fields of the same record. It is no stronger
  than the fields it rests on.
- `PROPOSED`: not checked. This includes statements carried from memory or
  from other repository text, and citations that were not opened.

A citation that was not opened is written with `[NOT OPENED]`.

## Null policy

- All ten keys are always present. A missing key is a validation failure.
- `null` means no information. It is kept, never dropped, and never read as
  zero, "none" or "does not apply".
- A field with no value has no status tag. A field with a value must have one.
- `energy_cost.joules` is `null` unless a source gives a measured number; the
  note then says `unmeasured`. No estimated or recalled number is entered.
- A stub is a block whose mechanism fields are all `null` and whose
  `assumption_trace` is filled. A stub records a question, not an answer.

## Loop topology and hidden cost

Coordination usually runs in a loop that passes through more than one body
and through the environment (for ants: forager -> trail -> next forager). An
observation boundary that cuts the loop removes part of it from the record.
The upkeep cost of the removed part is then not on the ledger, and it can be
read as 0. It was not measured as 0; it was outside the cut.

`loop_topology.observer_cuts` lists, per way of observing, which cycles
survive. A cut with an empty list is a view from which the coordination is
not visible at all.

Link to the loop-topology and hidden-cost findings: NOT LOCATED. No file by
either name is in this repository, and none was found in the sibling
checkouts searched (`simulators`, `method-layer`,
`thermodynamic-accountability-framework`). Add the path here when it is
known.

## Records

| record | state |
|---|---|
| `ontology/social/ant_colony.json` | pilot: all fields filled except `energy_cost.joules` (unmeasured). Text fields are PROPOSED: Goss 1989 and Deneubourg 1990 could not be opened. `loop_topology` is DERIVED from them |
| `ontology/plant/quorum_biofilm.json` | stub. Miller & Bassler 2001 read at abstract depth |
| `ontology/plant/slime_mold.json` | stub. Tero 2010 read at abstract depth |
| `ontology/plant/mycelium.json` | stub. Kiers 2011 and Karst 2023 read at abstract depth. Network claims flagged as contested |
| `ontology/social/honeybee_nest_site_selection.json` | stub, new entity. Seeley & Visscher 2004 and Seeley 2010 not opened |

Held, not created: a human stone-and-art debt ledger record, pending a
consent check.

## Checking

```sh
python3 validation/coordination_check.py             # shape + status tags, stdlib only
python3 validation/coordination_check.py --selftest  # planted defects must fire
python3 scripts/build_index.py                       # JSON Schema validation (needs jsonschema)
```

Neither check tests whether a source says what a field says.
