# Provenance chain

Status: PROPOSED. The chain is built and its selftest passes. What is **not**
established: that any source string in it is correct. The backfill copies
what the entity files say; it opens no source and adds no claim. Co-authored
(JinnZ2 + Claude), 2026-11-24. Stdlib only.

`validation/provenance.py` is a separate thing: a hand-written lineage table
for concepts, with no hashes. It is not used, read or edited by this chain.

## Purpose

Any later experiment, physics revision or scope change can be traced back
through the chain and re-run. Old versions are kept and never overwritten.

## Where things live

| path | holds |
|---|---|
| `registry/DECLARED.json` | the rules, committed before the tool existed (`1c31cf8`), with an amendment committed before the rebuild (`b8ca746`) and a second, "fixes v2", committed before the v2 rebuild (`c1eff92`) |
| `registry/assumptions.json` | one entry per assumption: `id`, `statement`, `domain`, `status`, `sources`, `supersedes` |
| `registry/sources.json` | one entry per exact source string: `id`, `string`, `same_as` (null), `opened` (false or a depth word), `fetched` (null or a date) |
| `provenance/<entity_id>.json` | the steps of one entity |
| `provenance/INDEX.json` | per-entity counts; `snapshot_class: SUMMARY_ONLY` |
| `provenance/as_received/MANIFEST.json` | sha256 of specimens as received |
| `schemas/provenance_step.schema.json` | validates the files under `provenance/`; no entity schema references it |
| `scripts/provenance_chain.py` | `build`, `trace`, `stale`, `dups`, `--selftest` |
| `provenance/v0_superseded/`, `registry/v0_superseded/` | the first build (303 steps, old id rules), kept unchanged; not part of the live chain |
| `provenance/v1_superseded/` | the second build (303 steps at `5a066a7`, id covering the entity file hash, old void mapping), moved unchanged; not part of the live chain. The registries did not change and stay in place |

Entity files are not changed by the chain and carry no provenance key.

## Step

| key | meaning |
|---|---|
| `id` | sha256 of the canonical JSON of `{entity_id, field_path, value_sha256, inputs, method, params, assumptions, scope, status}`. `entity_id` and `field_path` are `params.entity` and `params.field`; `value_sha256` is the sha256 of the value's canonical JSON; `params` is taken without `entity_file_sha256` |
| `inputs` | parent step ids or source ids (both 64 hex); `[]` when the field has no source |
| `method` | `{name, version}`; the backfill is `manual_entry`, version `1` |
| `params` | always `entity`, `field` and `entity_file_sha256` (the entity file's hash when the step was written: context, not in the id); for attributes also `evidence_type` and `reproducibility` as found |
| `value` | the field's value as found |
| `assumptions` | assumption ids (`A-…`); null = not assessed; `[]` = read, none named |
| `scope` | conditions the value holds under, as recorded; null = none recorded |
| `status` | the field's existing tag (OBSERVED / DERIVED (basis: …) / PROPOSED), or null when it has none |
| `status_note` | null, or why the status is null |
| `supersedes` | prior step id, or null |
| `declared_pre_run` | the latest commit that changed `registry/DECLARED.json` before the build |
| `claim` | null, or `{statement, evidence, refuter, state}` with state SUPPORTED / UNVERIFIED |
| `void` | null, or `{state, reason}` |
| `snapshot_class` | null, or one of the four classes below |

Canonical JSON: UTF-8, keys sorted, separators `,` and `:` with no spaces,
non-ASCII characters written as themselves.

`status_note`, `supersedes`, `declared_pre_run`, `claim`, `void`,
`snapshot_class` and `params.entity_file_sha256` are not part of the id.

A change to an entity file gives a new step only to a field whose value,
sources, params, assumptions, scope or status changed. The other fields keep
their step, which still shows the file hash it was written under. A revision
that changes only status, assumptions or scope is a new step that supersedes
the old one.

## Conventions copied from the bridge experiment

Copied from `JinnZ2/Geometric-to-Binary-Computational-Bridge`,
`experiments/experiment_bridge/`. Conventions only; no code was imported.

| convention | here | source path |
|---|---|---|
| declared before run | `registry/DECLARED.json` in its own commit; every step cites the latest declaring commit as `declared_pre_run`; a change is a dated entry under `amendments`, never an edit | `eqsearch/DECLARED.json`, `eqsearch/README.md` at main `e8b7d12` |
| as received | `provenance/as_received/` with a sha256 `MANIFEST.json`; a correction goes beside a specimen, never in place | `evidence/kimi_round2_as_received/MANIFEST.json`, `evidence/equation_search_as_received/MANIFEST.json`, `raw/manifest.json` at main `e8b7d12` |
| claim table | `claim` on a step and the table below: statement, evidence, refuter, state. Separate from `status` | `CLAIM_TABLE.md` at main `e8b7d12` |
| void states | `void.state`: REJECTED, UNMAPPED, LEXICAL_VOID, VOID, all four kept | `v1/README.md` lines 16-20, `v1/semantics.py`, `eqsearch/exact.py` at main `e8b7d12` |
| snapshot classes | `snapshot_class` on a summarized or coarse record | `snapshot/README.md`, `snapshot/snapshot_class.py` on branch `claude/snapshot-class` at `baa114e`; not on main at `e8b7d12` |

### Void states mapped to an LID null

The mapping is PROPOSED; it was written here, not taken from the bridge.

| state | LID condition | before (`5a066a7`) | now |
|---|---|---|---|
| VOID | the field is null; `reason` holds the record's words for the gap when it has any | 31 | 40 (9 with a reason) |
| UNMAPPED | the field has a value and no source | 12 | 12 |
| LEXICAL_VOID | a value for which no term exists in the record's language ("not interpretable at the moment"). The one case the backfill can detect is a `contested_label` entry whose label is null | 9 | 0; no record has one |
| REJECTED | a value failed a declared gate | 0 | 0; the chain declares no gate |

The 9 steps that read LEXICAL_VOID before are the null fields with a note
(`unmeasured`, or a note for the field). They now read VOID and keep the note
as `reason`.

In the bridge the four states describe a numerical code and its lexical
mapping. Here they describe a field and its source. The names are kept; the
referents differ.

### Snapshot classes

CONTEXT_FREE_EXACT, STABLE_LOSSY, CHAOTIC_REFRESH, SUMMARY_ONLY. A record
that is not a summary carries null. `provenance/INDEX.json` is SUMMARY_ONLY:
the steps cannot be rebuilt from it. `ontology_index.json` is also a
many-to-one summary of the entity files; it carries no such field because
`scripts/build_index.py` writes it and its shape was left alone.

### As received

The three files of abstract text fetched from NCBI in the build sessions are
listed by sha256 and by the PMIDs found in them. The text is not committed
and the files are not durable: the manifest is what remains.

## Usage

```sh
python3 scripts/provenance_chain.py build        # backfill; append steps for changed fields
python3 scripts/provenance_chain.py trace <id>   # assumption id, source id or step id; a unique prefix works
python3 scripts/provenance_chain.py stale        # exit 1 when anything is flagged
python3 scripts/provenance_chain.py dups         # near-duplicate source candidates
python3 scripts/provenance_chain.py --selftest
```

`trace` lists every step that uses the id, then every step downstream of
those through `inputs`, with the entity and field of each.

`stale` recomputes every hash and flags:

| flag | when |
|---|---|
| HASH_MISMATCH | a stored id differs from the id recomputed from the stored step |
| SOURCE_CHANGED | an input source is missing from the registry, or its text no longer hashes to its id |
| ASSUMPTION_CHANGED | an assumption is missing, superseded, or its statement no longer hashes to its id |
| FIELD_CHANGED | the head step of a field differs from the step computed now from the entity file |
| INPUT_CHANGED | a parent step is flagged or superseded; applied transitively |

## Revision rule

- Nothing is deleted and no stored step is edited.
- When an entity file changes, `build` appends a new step for each field
  whose value, sources, params, assumptions, scope or status changed, with
  `supersedes` set to the prior step id. The prior steps stay in the file.
- When an assumption changes, a new registry entry is appended with
  `supersedes`; the old entry stays. Steps that cite the old id read
  ASSUMPTION_CHANGED, and their children INPUT_CHANGED, until revised.
- A change to a declared rule is a dated entry under `amendments` in
  `registry/DECLARED.json`.

## Backfill

One step per field: `attributes.<name>`, `coordination.<field>`,
`gate_sensing.<field>`, `functional_intelligence.<capability>`,
`functional_intelligence.contested_label[i]`.

- A field with no source has `inputs: []`.
- `status` is copied as found. Attribute values carry `evidence_type` and
  `reproducibility`, not a status tag, so their step has status null and
  `status_note` "not assessed in this vocabulary"; the two fields are copied
  into `params` as found.
- `assumptions` is null (not assessed) on attribute steps, filled on the
  `coordination.assumption_trace` step, and `[]` on other block fields.
  The registry is seeded from `assumption_trace` lists only.
- `claim` is null on every backfilled step.
- Every chain in the backfill is one step long: no field names another
  field as its input. Longer chains exist only in the selftest so far.
- Source ids are per exact string. Two spellings of one work are two
  sources. Nothing was merged and every `same_as` is null. `dups` lists
  candidate groups (same first word and same first year): 11 groups, 24
  strings. A candidate is not a finding that two strings are one work.
- `opened` and `fetched` are read from the string's own bracket note. 3
  strings say an abstract was read on 2026-11-24; the other 231 are `false`.

### Evidence type to status: PROPOSED mapping, not applied

No step uses this table. It is written here so it can be argued with.

| `evidence_type` (count of attribute values) | proposed status | open point |
|---|---|---|
| `lab_measurement` (132), `field_observation` (47), `cyclic_observation` (24) | OBSERVED | only if the source is opened and says so; none was opened |
| `mathematical_proof` (11), `simulation` (4), `theoretical` (4) | DERIVED | a basis would have to be named for each |
| `cross_domain_rhyme` (3) | PROPOSED | |
| `not_assessed` (3) | null | |

## Claims about this build

Local ids. SUPPORTED means the bounded statement holds; UNVERIFIED names the
missing check.

| id | statement | evidence | refuter | state |
|---|---|---|---|---|
| PRV_001 | Every stored step id equals the sha256 recomputed from the stored step | `provenance_chain.py stale`: 0 flagged | one HASH_MISMATCH on the committed files | SUPPORTED |
| PRV_002 | A second `build` on unchanged entity files appends nothing | second run: appended 0; selftest "build twice" | a second run that appends | SUPPORTED |
| PRV_003 | A changed assumption is found by `trace` and flags downstream steps while old steps stay | selftest planted chain A→B→C | a planted chain where B or C is missed, or a step disappears | SUPPORTED |
| PRV_004 | `declared_pre_run` names a commit made before the build it governs | commit order: `1c31cf8` declares, `9d4b56f` first build; `b8ca746` amends, then the rebuild; `c1eff92` amends, then the v2 rebuild | a live step built before `c1eff92` | SUPPORTED, with two limits: the first declaring commit was amended once before any build, to correct a mistyped commit hash in a source path (that version was not pushed and is not in the history); and the rules were changed after the first and second builds, by order, which the amendments record |
| PRV_005 | The source strings in the chain are correct citations | none: no source was opened by the backfill | — | UNVERIFIED; the check is opening each source |
| PRV_007 | Changing one field of an entity file flags only that field's step, and `build` appends one step | selftest "change one field"; on the live chain, an edit to `coordination.carrier` of ANT gave `stale: 1` (FIELD_CHANGED on that step), then reverted | an edit to one field that flags or appends a second step | SUPPORTED |
| PRV_006 | The void-state mapping reads LID nulls the way the bridge states are meant | none | — | UNVERIFIED; the mapping is a proposal written here |
