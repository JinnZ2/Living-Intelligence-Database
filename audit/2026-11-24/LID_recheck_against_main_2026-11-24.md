# Re-check: Do the 2026-11-24 Audit Findings Hold on Current Main?

Run on 2026-11-24 (America/Chicago). Both runs used the same probe script, `recheck_main.py`, on throwaway copies of the repository:

- **Baseline:** `63d93c0`, the commit the audit was run against.
- **Current main:** `906e86a`, which includes the instrument repairs merged in PRs #25–27.

Raw outputs are in `recheck_results_63d93c0.json` and `recheck_results_906e86a.json`. Both copies were left clean (`git status` empty), and the index file was restored byte-for-byte after each build probe. The repository was not written to.

The probes use the real ontology data plus the same fixtures as `instrument_tests.py`. They are independent of the repair's own fixtures. Separately, the repair's fixture suite, `validation/fixtures/run_fixtures.py`, reproduces 8/8 PASS (OBSERVED).

Labels:
- **REPAIRED:** the finding no longer holds on main.
- **HOLDS:** unchanged.
- **NARROWED:** partly repaired.
- **NEW:** not in the original audit.

Every row is OBSERVED unless marked otherwise.

## Instruments

| Finding (execution results, Stage 03) | 63d93c0 | 906e86a (default) | State |
|---|---|---|---|
| verify: an unknown claim name runs as True | exit 0, posterior 0.5, no verdict | verdict UNKNOWN, posterior null, exit 2 | REPAIRED |
| verify: README example `hex_efficiency` | silently becomes True | UNKNOWN, exit 2 | REPAIRED |
| verify: posterior rises with attribute count (N = 0, 1, 2, 5, 10, 20) | 0.5, 0.79, 0.934, 0.9987, 1.0, 1.0 | 0.5, then 0.79 for every N ≥ 1; the claim runs once | REPAIRED |
| verify: hydrated real index, `always_true` | 228 calls, posterior 1.0 | 1 call, evidence_count 1, posterior 0.8111 | REPAIRED |
| verify: the CLI on the shipped index gathers no evidence | 0 tests, 0.5 | 0 tests, 0.5, now labelled NOT_TESTED | HOLDS (now labelled) |
| verify: empty scope text counts as 0.5 overlap | 0.5 | 0.5 | HOLDS |
| falsifier: all 601 counterexamples "survived"; 120 entities score 1.0 | 601 survived; 120 × 1.0 | 601 NOT_TESTED; 120 × null | REPAIRED |
| falsifier: empty scope scores 1.0 | 1.0 | null, "no counterexample was tested: no score" | REPAIRED |
| falsifier: a missing file falls back silently to the thin entry | "No scoped attributes" | LOAD_FAILED, with reason | REPAIRED |
| falsifier: the search runs on the thin index, not the full records | thin | still thin (see N1) | HOLDS |
| falsifier / dependency_tree: README examples using COUNCIL | not found | not found; the link is listed KNOWN_HELD in `registry/known_held_links.json` | HOLDS (declared) |
| dependency_tree: `WOLF_PACK → COUNCIL` dropped silently | 554 of 555 edges | 555 of 555; COUNCIL appears as an `unresolved` node | REPAIRED |
| dependency_tree: 646 scope dependencies dropped silently | 0 listed | 646 listed under `non_entity_scope_dependencies` | REPAIRED |
| audit vs tracer disagree on the same field | audit 651 vs tracer 0 | audit 651 vs tracer 646. The remaining 5 are `golden_ratio` and `pi`: audit counts them as missing, while the tracer resolves them as constants. | NARROWED |
| audit: confidence fallback (scope_checker 0.06 vs audit 0.5) | 3 attributes | 3 attributes | HOLDS |
| audit: missing file still reports scoped_ratio 1.0 | 1.0, no warning | LOAD_FAILED; scoped_ratio null | REPAIRED |
| audit: no numerics gives a ratio of 1.0 | 1.0 | null, with a reason | REPAIRED |
| build_index: an extra broken link still gives exit 0 and writes the index | exit 0, written | exit 1, not written | REPAIRED |
| build_index: index written before `exit(1)` on a validation error (duplicate ID) | written | not written ("ontology_index.json was NOT written") | REPAIRED |
| build_index: `relational/` is skipped without failing | skipped, exit 0 | skipped, exit 0 | HOLDS (see N2) |

**Legacy switch.** With `--legacy` / `legacy=True`, main reproduces the baseline readings exactly: the posterior curve 0.5 → 1.0, 228 calls giving 1.0, 601 "survived" giving 120 × 1.0, and a broken link giving exit 0 with the index written. The repair kept the old behaviour available for comparison, as its docstrings say.

## Data and graph

| Item | 63d93c0 | 906e86a | State |
|---|---|---|---|
| Scoped attributes / holding a single float | 228 / 225 | 228 / 225 | HOLDS |
| Machine-readable `condition` blocks | 10 | 10 | HOLDS |
| `deviation` fields | 0 | 0 | HOLDS |
| Files containing `temporal_range` | 0 | 0 | HOLDS |
| `ontology_index.json` | | byte-identical (`git diff` empty) | HOLDS |
| Graph topology and ablation (Stages 04–05) | | same index, so same results | HOLDS (DERIVED from the identical index; not re-run) |

The translation-loss ledger's findings are about the data: single floats, missing condition, cycle and deviation slots, and process stored as noun. The repair did not touch the data, so all of them hold.

## New findings

- **N1. The falsifier reads NOT_TESTED because of where it searches.** It still searches the thin index entries, which carry no attributes. As a control, I searched the full records with the same 601 counterexamples. **360 are RISK_FLAGGED and 241 are NOT_TESTED** (OBSERVED; identical on both commits). The repaired label is honest: nothing was tested. But the cause is the search target, not an absence of matches. A RISK_FLAGGED result is a text match for a person to read, not a refutation. Recorded as OPEN_QUESTIONS #7.
- **N2. The new biosphere record is neither validated nor indexed.** `ontology/relational/biosphere_reference.json` (id BIOSPHERE, status PROPOSED) sits in `relational/`, which has no schema. The build skips that folder with a warning and exits 0, so the file is not in the index. Whether it is meant to be indexed is UNKNOWN; its `record_kind` field suggests it may be a different kind of record.
- **N3. A record with no `id` disappears from the index, and the build still passes.** In the probe I removed `id` from `ontology/ai/autoencoder.json`. On both commits the build printed "Skipping … missing required 'id' or 'name' field", wrote an index with 121 entities, and exited 0. That record has no inbound links, so the broken-link rule did not catch it. With an inbound link, the result is NOT_TESTED.

## Scope

- This re-check covers the probes listed above. It does not judge whether the repair's design choices are the right ones. Examples: weighting by the best-matching attribute, and `tests_survived` being 0 by construction.
- I did not re-run the reference-trace work: `bee.json` is unchanged between the two commits.
