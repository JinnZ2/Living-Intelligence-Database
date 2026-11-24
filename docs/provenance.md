# Provenance chain

Status: PROPOSED. The chain is built and its selftest passes. What is **not**
established: that any source string in it is correct. The backfill copies
what the entity files say; it opens no source and adds no claim. Co-authored
(JinnZ2 + Claude), 2026-11-24. Stdlib only.

Not the same thing as `validation/provenance.py`, which is a hand-written
lineage table for concepts and carries no hashes.

## Purpose

Any later experiment, physics revision or scope change can be traced back
through the chain and re-run. Old versions are kept and never overwritten.

## Where things live

| path | holds |
|---|---|
| `registry/DECLARED.json` | the rules, committed before the tool existed (commit `1c31cf8`) |
| `registry/assumptions.json` | one entry per assumption: `id`, `statement`, `domain`, `status`, `sources`, `supersedes` |
| `registry/sources.json` | one entry per distinct source string: `id`, `text`, `form`, `used_by` |
| `provenance/<entity_id>.json` | the steps of one entity |
| `provenance/INDEX.json` | per-entity counts; `snapshot_class: SUMMARY_ONLY` |
| `provenance/as_received/MANIFEST.json` | sha256 of specimens as received |
| `schemas/provenance.schema.json` | the block shape, referenced from every per-type schema; block nullable |
| `scripts/provenance.py` | `build`, `trace`, `stale`, `--selftest` |

Entity files are not changed by the chain. The `provenance` key is legal in
an entity file (object, null or absent) but no entity carries it.

## Step

| key | meaning |
|---|---|
| `id` | sha256 of the canonical JSON of `{inputs, method, params, value}` |
| `inputs` | parent step ids or source ids (`S-…`); `[]` when the field has no source |
| `method` | `{name, version}`; the backfill is `manual_entry`, version `1` |
| `params` | always `entity` and `field`; for attributes also `evidence_type` and `reproducibility` as found |
| `value` | the field's value as found |
| `assumptions` | assumption ids (`A-…`) |
| `scope` | conditions the value holds under, as recorded; null = none recorded |
| `status` | the field's existing tag (OBSERVED / DERIVED (basis: …) / PROPOSED), or null when it has none |
| `supersedes` | prior step id, or null |
| `declared_pre_run` | the commit that added `registry/DECLARED.json` |
| `claim` | null, or `{statement, evidence, refuter, state}` with state SUPPORTED / UNVERIFIED |
| `void` | null, or `{state, reason}` |
| `snapshot_class` | null, or one of the four classes below |

Canonical JSON: UTF-8, keys sorted, separators `,` and `:` with no spaces,
non-ASCII characters written as themselves.

`assumptions`, `scope`, `status` and the last five keys are not part of the
id. Two steps that differ only in those have the same id, and the second is
refused. A revision must differ in `inputs`, `method`, `params` or `value`.

## Conventions copied from the bridge experiment

Copied from `JinnZ2/Geometric-to-Binary-Computational-Bridge`,
`experiments/experiment_bridge/`. Conventions only; no code was imported.

| convention | here | source path |
|---|---|---|
| declared before run | `registry/DECLARED.json` in its own commit; every step cites it as `declared_pre_run`; a change is a dated entry under `amendments`, never an edit | `eqsearch/DECLARED.json`, `eqsearch/README.md` at main `e8b7d12` |
| as received | `provenance/as_received/` with a sha256 `MANIFEST.json`; a correction goes beside a specimen, never in place | `evidence/kimi_round2_as_received/MANIFEST.json`, `evidence/equation_search_as_received/MANIFEST.json`, `raw/manifest.json` at main `e8b7d12` |
| claim table | `claim` on a step and the table below: statement, evidence, refuter, state. Separate from `status` | `CLAIM_TABLE.md` at main `e8b7d12` |
| void states | `void.state`: REJECTED, UNMAPPED, LEXICAL_VOID, VOID, all four kept | `v1/README.md` lines 16-20, `v1/semantics.py`, `eqsearch/exact.py` at main `e8b7d12` |
| snapshot classes | `snapshot_class` on a summarized or coarse record | `snapshot/README.md`, `snapshot/snapshot_class.py` on branch `claude/snapshot-class` at `baa114e`; not on main at `e8b7d12` |

### Void states mapped to an LID null

The mapping is PROPOSED; it was written here, not taken from the bridge.

| state | LID condition | in the backfill |
|---|---|---|
| LEXICAL_VOID | the field is null and the record states the gap in words (`unmeasured`, or a note for the field) | 9 |
| VOID | the field is null and no reason is recorded | 31 |
| UNMAPPED | the field has a value and no source | 12 |
| REJECTED | a value was offered and refused by a gate | 0; the backfill produces none |

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
python3 scripts/provenance.py build        # backfill; append steps for changed fields
python3 scripts/provenance.py trace <id>   # assumption id, source id or step id
python3 scripts/provenance.py stale        # exit 1 when anything is flagged
python3 scripts/provenance.py --selftest
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
- When an entity field changes, `build` appends a new step whose `supersedes`
  is the prior step id. The prior step stays in the file.
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
  `reproducibility`, not a status tag, so their step status is null.
- `assumptions` is filled only on the `coordination.assumption_trace` step.
- `claim` is null on every backfilled step.
- Every chain in the backfill is one step long: no field names another
  field as its input. Longer chains exist only in the selftest so far.
- Source ids are per string. Two spellings of one work are two sources.
  Nothing was merged.

## Claims about this build

Local ids. SUPPORTED means the bounded statement holds; UNVERIFIED names the
missing check.

| id | statement | evidence | refuter | state |
|---|---|---|---|---|
| PRV_001 | Every stored step id equals the sha256 recomputed from the stored step | `provenance.py stale`: 0 flagged | one HASH_MISMATCH on the committed files | SUPPORTED |
| PRV_002 | A second `build` on unchanged entity files appends nothing | second run: appended 0; selftest "build twice" | a second run that appends | SUPPORTED |
| PRV_003 | A changed assumption is found by `trace` and flags downstream steps while old steps stay | selftest planted chain A→B→C | a planted chain where B or C is missed, or a step disappears | SUPPORTED |
| PRV_004 | `declared_pre_run` names a commit made before the tool ran | commit order: `1c31cf8` adds only `registry/DECLARED.json`; the tool arrives in the next commit | a step built before that commit | SUPPORTED, with a limit: the declaring commit was amended once before any build, to correct a mistyped commit hash in a source path; the first version was not pushed and is not in the history |
| PRV_005 | The source strings in the chain are correct citations | none: no source was opened by the backfill | — | UNVERIFIED; the check is opening each source |
| PRV_006 | The void-state mapping reads LID nulls the way the bridge states are meant | none | — | UNVERIFIED; the mapping is a proposal written here |
