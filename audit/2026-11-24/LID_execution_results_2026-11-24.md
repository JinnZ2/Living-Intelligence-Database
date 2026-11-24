# Living Intelligence Database — Executed Baseline and Instrument Tests

Date: 2026-11-24
Status: Stages 00 (partial), 01, 03, 04, 05, 06 executed. No repository files modified.
Executor: Claude Opus 5.5 (Anthropic) via Perplexity Computer. Not a blind participant: this instrument read the assessor-only baseline before testing. Do not count this run in Stage 11.

## Frozen reference (T00.1)

| Item | Value | Basis |
|---|---|---|
| Repository commit | `63d93c00951b14ed7352891747468c9b65cca146` (2026-11-24 11:38 -0600, "Merge pull request #21 from JinnZ2/physics-usage") | OBSERVED |
| Commits in history | 188 | OBSERVED |
| Tracked files | 635 | OBSERVED |
| `ontology_index.json` blob | `21edd46b1e51fee3e8153d84b9dc1f16fa2d43cc` — matches the assessor baseline | OBSERVED |
| Execution environment | Python 3.14, jsonschema installed; all runs on a copy at `/tmp/lid_run` | OBSERVED |

Because the blob matches, the earlier graph measurements and this run describe the same index.

## Stage 01 — Structural integrity

### Reproduced exactly (OBSERVED)

- 122 entities, 122 unique IDs, 555 relations, 554 with resolved endpoints.
- Unresolved: `WOLF_PACK → COUNCIL` (synergy).
- 0 isolated entities, 1 weakly connected component.
- Manifest missing: `BEE_NEST_SITE`, `MIMOSA`, `STONE_LEDGER`, `WHALE`. Obsolete: `WHALE_POD`.
- Manifest `ontology_types` omits `social` (the index holds 5 social entities). Manifest `relation_types` omits `energy_exchange` (4 records).
- Manifest `co_creators`: `["JinnZ v2", "GPT-5", "Collective Living Systems"]`. No GPT-3 or GPT-4 entry, which matches the "outdated attribution" finding.

### New findings

| ID | Finding | Basis |
|---|---|---|
| N01 | A second file, `ontology/ontology_index.json`, is **not valid JSON**. It is a 14-entity v1.1 index followed by an appended "version 1.2" fragment containing `// ... existing 14 entities unchanged ...` comments. History: created 2025-10-14, last edited 2026-07-04 (commit b891732). No `.py` file references it. | OBSERVED |
| N02 | Classification of N01: probably a historical specimen (a pasted model-suggested diff), not an active defect, because nothing loads it. Whether to keep it as a specimen is your decision. | PROPOSED |
| N03 | COUNCIL exists only at `validation/example/council.json`, outside `ontology/`, so `build_index.py` never indexes it. This is the mechanism behind the unresolved WOLF_PACK edge. | OBSERVED |
| N04 | `ontology/relational/` has no schema, so `build_index.py` prints "No schema for 'relational', skipping" and skips the directory. Its `synergies.json` (78 nodes, 219 edges) is a different shape (`nodes`/`edges`). 218 of its 219 edges are already in the index. `OC → EL` (synergy, weight 0.94) appears only there. | OBSERVED |
| N05 | One `(source, target)` pair has two relation records with different types. There are no exact duplicates and no self-loops. | OBSERVED |
| N06 | Reciprocity count conflict. The baseline reports 46 "explicitly reciprocated relationship records." This run counts 62 directed edges (31 unordered pairs) whose reverse edge exists, and 48 edges whose reverse exists with the **same** relation type. Neither count is 46. The method behind 46 is not recorded. | UNRESOLVED |

## Stage 03 — Validation instruments (executed)

Harness: `instrument_tests.py`. Raw output: `instrument_results.json`.

### Entity loading

- All 122 index paths load. No load fails at this commit (OBSERVED). So the silent-substitution defects below are **latent**: they don't change current outputs, but they would hide a future failure.
- 120 of 122 full entity files contain scoped attributes, 228 scoped attributes in total. Thin index entries carry none (OBSERVED).

### verify.py

| Test | Result | Basis |
|---|---|---|
| `--claim no_such_claim` on the real index | 0 tests gathered; posterior = prior (0.5). The index entries are thin, so `generate_tests` finds no attributes. The CLI as documented can't gather evidence at all. | OBSERVED |
| README example `--claim hex_efficiency --domain hex` | `hex_efficiency` isn't a registered claim, so it silently becomes `lambda: True`. 4 entities consulted, 0 tests, posterior 0.5. | OBSERVED |
| Fixture: one entity, N scoped attributes, one claim function | The claim runs N times. Posterior climbs 0.5 → 0.79 → 0.934 → 0.9987 → 1.0 for N = 0, 1, 2, 5, 10. The rise comes only from how many attributes exist. | OBSERVED |
| Hydrated real index, `always_true` | 228 calls of the same constant function; posterior 1.0. | OBSERVED |
| Hydrated real index, `always_false` | posterior 0.0. | OBSERVED |
| Root cause | `generate_tests` builds `test_func = lambda: claim()`. The claim takes no entity or attribute argument, so it can't test anything about the record it is weighted against. | OBSERVED (source) |
| Empty claim scope text | `jaccard_overlap('', x)` returns 0.5, so a missing scope counts as half overlap instead of unknown. | OBSERVED |

### falsifier.py

| Test | Result | Basis |
|---|---|---|
| All 122 entities | 120 ran and 2 returned "No scoped attributes." **All 120 got falsification_resistance = 1.0.** All 601 generated counterexamples were scored "survived," and every one of them had zero database matches. | OBSERVED |
| Cause | `check_counterexample` searches the **thin** index text, not the full records. No match is read as risk "low," and "low" is counted as survived. An unexamined condition becomes a pass. | OBSERVED (source + execution) |
| Fixture: scoped attribute with an empty scope | 0 counterexamples, 0 survived, resistance **1.0** (`score = ... else 1.0`). | OBSERVED |
| Fixture: missing entity file | Falls back silently to the thin entry and reports "No scoped attributes," so the load failure is hidden. | OBSERVED |
| Documented example `--entity COUNCIL` | "Entity COUNCIL not found." (see N03) | OBSERVED |

The falsifier's output at this commit has no information content: every entity it can test scores the maximum.

### dependency_tree.py

| Test | Result | Basis |
|---|---|---|
| Link edges vs index | The tracer keeps 554 of 555 relations and drops `WOLF_PACK → COUNCIL` silently. Nothing extra appears. | OBSERVED |
| Scope `dependencies` | 646 scope dependency strings resolve to neither an entity ID nor a Rosetta constant, and all of them are dropped silently. Samples: `compression_ratio`, `dataset_complexity`, `problem_dimensionality`. Only 5 resolve. | OBSERVED |
| Interpretation | The `dependencies` field mostly holds condition or variable names, while the tracer expects entity IDs. This looks like a schema-semantics mismatch, not 646 missing entities. | PROPOSED |
| Instrument disagreement | `audit.py` reports 651 "missing dependencies" on the same field, while the tracer reports 0. Two instruments read one field and disagree with no shared definition. | OBSERVED |
| Documented examples `--goal COUNCIL` and `--goal "maintain a watershed for 7 generations"` | Both return "No matching entity found." | OBSERVED |

### audit.py and confidence fallback

| Test | Result | Basis |
|---|---|---|
| Real run | 122 entities, 0 unscoped numerics, 0 noun-pretenders, 2 possible contradictions, 651 missing deps, scoped_ratio 1.0. | OBSERVED |
| Fallback mismatch | For a scoped attribute with no explicit confidence, `scope_checker.extract_confidence` computes 0.06, while `audit.py` buckets it as 0.5. This affects 3 real attributes (the "0.5: 3" bucket). | OBSERVED |
| Fixture: missing entity file | `total_entities 1`, `scoped_ratio 1.0`, no load warning. A record that couldn't be read still reports a perfect scoped ratio. | OBSERVED |
| `scoped_ratio` when no numeric attributes exist | Returns 1.0 (no evidence becomes the maximum). | OBSERVED (source) |

### scripts/build_index.py

| Test | Result | Basis |
|---|---|---|
| Rebuild in copy | Exit code **0**. The rebuilt index matches the committed one in content (122 / 555, identical entity and relation sets). | OBSERVED |
| Broken link | Printed as a warning. The index is written anyway and the exit code stays 0, because broken links don't count toward `errors`. | OBSERVED |
| Write order | The index is written **before** `sys.exit(1)`, even when validation errors occur. | OBSERVED (source) |
| Skipped directory | `relational/` is skipped with a warning and doesn't fail the build (N04). | OBSERVED |

## Stage 04 — Graph topology

Reproduced (OBSERVED/DERIVED): directed reachability 4,046 / 14,762 = 27.4%; undirected 100%; 86 strongly connected components, the largest with 19 entities; geometry reciprocal 88.6%; geometry + synergy + resonance reciprocal 98.4%.

Geometry targets are heavily fan-in: SPIRAL (33 in / 2 out), FRACTAL (26 / 3), TORUS (21 / 2), HEX (9 / 3), SPHERE (10 / 3).

## Stage 05 — Relationship-type ablation (executed)

Each type removed alone (script: `ablation_controls.py`):

| Removed type | Edges | Directed % | Undirected % | Weak components |
|---|---|---|---|---|
| synergy | 184 | 15.8 | 98.4 | 2 |
| resonance | 124 | 19.8 | 100 | 1 |
| connected_to | 50 | 23.2 | 98.4 | 2 |
| geometry_link | 78 | 24.4 | 100 | 1 |
| energy_coupling | 53 | 25.7 | 100 | 1 |
| temporal_bridge | 59 | 25.9 | 100 | 1 |
| energy_mode | 2 | 26.7 | 100 | 1 |
| energy_exchange | 4 | 27.0 | 100 | 1 |

Removing geometry doesn't disconnect the graph and costs 3.0 points of directed reachability. Only synergy and connected_to removal split off a component. (OBSERVED)

## Stage 06 — Randomized controls (executed, seed 20261124)

| Control | Observed | Null | Result |
|---|---|---|---|
| T06.4: reciprocate 78 random existing edges vs the 78 geometry edges (500 trials) | 88.6% | mean 86.6%, SD 3.4, 95% range 78.1–91.8 | p ≈ 0.25. **Not distinguishable from random.** |
| Same control for every type (200 trials each) | resonance 97.5 vs 92.5 (p ≈ 0.005); temporal_bridge 90.2 vs 83.2 (p ≈ 0.03); geometry p ≈ 0.24; synergy p ≈ 0.57; connected_to below null | — | Only resonance stays below 0.05/8 after a Bonferroni correction. These are exploratory. |
| T06.2: degree-preserving directed rewiring (100 trials) | directed 27.4% | rewired 68.3–79.5% | The stored edge **directions** are strongly non-random: far less reachable than chance at the same degrees. |
| T06.2 with geometry reciprocated after rewiring | 88.6% | 89.4–93.4% | The observed value is below the null range. |

### What this changes (DERIVED / PROPOSED)

- The earlier claim "treating geometry as reciprocal raises reachability from 27.4% to 88.6%" is reproduced. But reciprocating **any** 78 edges does about the same. The jump measures how few reverse paths the directed graph has. It isn't evidence that geometry specifically is the connective layer.
- Where geometry does stand out is **cross-domain placement**. 92% of geometry edges join entities in different ontology categories, the highest of any type with more than 2 edges (temporal_bridge 86%, energy_coupling 77%, resonance 72%, synergy 21%). That is a separate structural measurement and a better test of your cultural account (geometry as a cross-domain connector) than reachability. A domain-preserving null (T06.3) is the next test it needs.
- The low directed reachability (27.4% vs about 74% for degree-matched random) reflects how edges were authored: many entities point into a few shape and energy hubs that have little fan-out. Whether that direction carries meaning (C05) is still UNKNOWN until you define relationship semantics.

## Repair register (PROPOSED, not applied)

| # | File | Defect | Evidence | Correction | Regression test | Information loss |
|---|---|---|---|---|---|---|
| R1 | verify.py | Same claim counted as N independent tests; unknown claim → True | Fixture curve; 228 calls → 1.0 | The claim signature takes `(entity, attr)`. Unknown claim → error. Weight is counted per independent source, not per attribute. | Constant claim × N attributes must leave the posterior at the prior, or report "non-discriminating". | None |
| R2 | verify.py | Thin entries → 0 tests, so the posterior silently equals the prior | Real-index run | Hydrate from `path`; report `tests_gathered = 0` as `NOT_TESTED`, not as a posterior. | Real index gathers more than 0 tests | None |
| R3 | falsifier.py | No match = survived; 0 tests = 1.0 | 601 / 601; fixture | Three-state outcome: `matched`, `no_match_within_scope`, `not_examined`. Resistance is `null` when no test ran. Search full records. | Empty-scope fixture → `null`; real index not uniformly 1.0 | None |
| R4 | falsifier.py, audit.py, dependency_tree.py | Silent fallback to thin entry on load failure | Missing-file fixtures | Record the failure in a `load_failures` list in every report. | Ghost-path fixture appears in the output | None |
| R5 | dependency_tree.py | Unresolved link and scope deps dropped silently | WOLF_PACK; 646 deps | Emit `unresolved` nodes, with types `entity_missing` and `non_entity_dependency`. | WOLF_PACK tree shows COUNCIL as unresolved | None |
| R6 | scope schema | `dependencies` mixes entity IDs and condition variables | 646 vs 5 | Split into `entity_dependencies` and `condition_variables`. Keep the original field and add an adapter. | Audit and tracer counts agree | Ordering of the mixed list (keep the original) |
| R7 | audit.py / scope_checker.py | Two confidence fallbacks (0.5 vs computed 0.06) | 3 real attributes | One shared function; label each value `explicit`, `computed`, or `absent`. | The 3 attributes report the same value in both tools | None |
| R8 | audit.py | scoped_ratio 1.0 with no evidence | Ghost fixture | Return `null` when the denominator is 0 | Ghost fixture → `null` | None |
| R9 | scripts/build_index.py | Broken links and errors still write the index; exit 0 | Rebuild run | Write to a temp file and promote it only on success. Add a `--strict` option where broken links make the exit code nonzero. Keep the default behavior behind a flag so the history stays reproducible. | WOLF_PACK fixture → nonzero exit under `--strict` | None |
| R10 | build_index / layout | `relational/` skipped; COUNCIL outside `ontology/` | N03, N04 | Your decision: add COUNCIL to `ontology/social/` **or** record the edge as intentionally pointing to an example. Add a schema for, or an explicit exclusion of, `relational/`. Carry `OC → EL` across if it is intended. | Unresolved count = 0, or documented | None, if done as an addition |
| R11 | manifest.json | 4 missing IDs, 1 obsolete, `social` and `energy_exchange` missing, co-creators | Stage 01 | Regenerate `id_map` from the index. Record WHALE_POD → WHALE as a dated rename note, not a deletion. | Manifest/index diff = empty | None, if the rename is noted |

Per your convention, corrections go in as dated notes beside the original claims, and historical specimens (REVIEW.md, `ontology/ontology_index.json`) are left alone.

## Still not tested

- T00.2 / T00.3: per-model provenance attribution and a full historical-specimen inventory (needs your input).
- T06.3: domain-preserving null for geometry's cross-ontology share (the next test).
- Stages 07–12. Stage 11 needs fresh blind sessions. This run is contaminated by the answer key.
- The other validation modules (`coordination_check.py`, `paradigm_verifier.py`, and the rest), `resilience_lab.py`, and `perturbation_boosted_coherence.py`.
- The method behind the baseline's "46 reciprocated records" (N06).

## Artifacts

- `graph_baseline.py`: Stage 01/04 measurements
- `instrument_tests.py` → `instrument_results.json`: Stage 03 execution
- `ablation_controls.py` → `ablation_results.json`: Stages 05–06

Every script uses only the standard library and runs offline against a repository copy. To reproduce, run each one from a copy of the repository root at commit `63d93c0`.
