# Audit posting, 2026-11-24

An external audit of this repository at commit `63d93c0`, posted by the owner. This folder only adds files: no existing repository file is edited, renamed or removed.

Reader: Claude Opus 5.5 working in Perplexity Computer. I read the assessor key, so I am not a blind participant. Evidence labels used throughout: OBSERVED / DERIVED / PROPOSED / UNKNOWN / NOT_TESTED. A PROPOSED item is not an owner decision.

## Documents

| File | Contents |
|---|---|
| `LID_execution_results_2026-11-24.md` | Executed baseline: graph metrics, instrument tests, ablations, regime evaluation |
| `LID_translation_loss_ledger_2026-11-24.md` | Translation-loss ledger, v0.1–v0.5, each version kept beside the last |
| `LID_reference_trace_BE_2026-11-24.md` | Bee hexagonal-cell reference trace down to physics, v0.1 and v0.2, with sunlight and the mānuka vs wildflower environment differential |
| `LID_weld_register_and_common_denominator_2026-11-24.md` | Weld register W01–W10 on method-layer `de_weld.py`, and the common-denominator rule with a worked chain |

## Scripts

`instrument_tests.py` treats the working directory as the repository root. Run it from the root of a copy, with `OUT=...` set for the output path. The original runs used a copy at `/tmp/lid_run`, so the repository itself was never written to.

All scripts are Python 3 standard library only and need no network. `jsonschema` is needed only where the repository's own validator is exercised.

| Script | Output |
|---|---|
| `graph_baseline.py` | graph baseline (see execution results) |
| `instrument_tests.py` | `instrument_results.json` |
| `ablation_controls.py` | `ablation_results.json` |
| `regime_eval.py` | `regime_eval_results.json` |
| `reference/build_reference.py`, `reference/build_reference_v02.py` | `reference/reference_trace_BE_hex.json`, `reference/reference_trace_BE_hex_v0.2.json` |
| `reference/trace_check.py <record> <out>` | `reference/trace_check_results.json`, `reference/trace_check_results_v0.2.json` |
| `reference/common_denominator.py [out]` | `reference/common_denominator_results.json` (run it from `reference/`) |
| `reference/lid_welds.py [out]` | `reference/lid_welds_results.json`, `reference/lid_welds_render.txt` (needs `METHOD_LAYER=/path/to/method-layer`) |
| `reference/build_reference_v03.py` | `reference/reference_trace_BE_hex_v0.3.json` (adds to v0.2; v0.2 is unchanged) |
| `reference/trace_check.py` with `LID_STRICT=1` | the same output file; exits 1 if there are findings (opt-in, added 2026-11-24) |
| `reference/trace_check.py reference_trace_BE_hex_v0.3.json trace_check_results_v0.3.json` | `reference/trace_check_results_v0.3.json` |

## Outside-reader package (added 2026-11-24)

`kimi_2026-11-25/` holds the package Kimi (Moonshot AI) produced, unzipped byte-for-byte and not edited. It contains four draft schemas, a completed readings file, a 28-check suite, a report and figures. The `#U2014` in the report's filename is how an em dash came through the zip. Everything in the package is PROPOSED. To run `tests/validate_loud.py`, first copy this audit folder (`audit/2026-11-24/`) to `/tmp/audit/lid_audit/`. The suite reads its fixtures from `/tmp/audit/lid_audit/reference/`. Result on 2026-11-24: 28/28, exit 0. The review is `LID_review_of_Kimi_schema_additions_2026-11-24.md`.
| `recheck_main.py` (run from the root of a copy; `OUT=...`) | `recheck_results_63d93c0.json`, `recheck_results_906e86a.json`; written up in `LID_recheck_against_main_2026-11-24.md` |

## Added 2026-11-24 (second batch)

| File | Contents |
|---|---|
| `deviation/LID_deviation_extraction_2026-11-24.md` | Every number in the 228 `measurement_limits` texts read by role. It corrects the ledger's "92 of 228" with a dated note beside it. |
| `LID_intake_biosphere_council_crosswalk_2026-11-24.md` | Weekly intake design and live run, BIOSPHERE dependency candidates and indexing route, COUNCIL as an AI-arena complement, D–L crosswalk |

| Script | Output |
|---|---|
| `deviation/deviation_extract.py <repo> <out>` (`--selftest`: 14 cases) | `deviation/deviation_extraction_results.json` |
| `biosphere/biosphere_candidates.py <repo> <out>` (`--selftest`: 5 cases) | `biosphere/biosphere_candidates_results.json` |
| `intake/weekly_intake.py fetch / offline` (`--selftest`: 9 cases) | `intake/live_2026-11-24/` (snapshots with sha256, `intake.json`, `intake.md`) |
| `crosswalk/build_crosswalk.py` | `crosswalk/crosswalk_D_L.json` |
| `crosswalk/crosswalk_evidence.py` (added 2026-11-24, after the owner's answers) | `crosswalk/crosswalk_evidence.json`: evidence for and against OPEN_QUESTIONS #3 branches (a), (b) and (c) |
| `council/build_council_pattern.py <repo>` | `council/council_pattern.json`: the pattern-only COUNCIL record, checked with the repo's `coordination_check.check_block` and a no-names guard |

`intake/weekly_science_intake.yml` is a PROPOSED workflow. GitHub does not run it from this folder. Adopting it means copying it to `.github/workflows/`, which is the owner's decision.

> **Note, 2026-11-24 (added).** The owner adopted it (answer 1 on PR #30). A copy now sits at `.github/workflows/weekly_science_intake.yml`, where only the header differs, and the amendment is appended to `registry/DECLARED.json`. The file in this folder is unchanged. Section 5 of `LID_intake_biosphere_council_crosswalk_2026-11-24.md` records all four answers.

## Added 2026-11-24 (third batch, after main 8bf3d00)

| File | Contents |
|---|---|
| `LID_review_of_Kimi_rev2_and_pipeline_gate_2026-11-24.md` | Review of Kimi's rev2 schema, 36-check suite and pipeline.sh finding: confirmed, with corrections and three new findings (R1–R3) |
| `kimi_2026-11-25_rev2/` | Kimi's `reference_trace.schema.rev2.json` and `validate_loud.36checks.py`, unedited |

| Script | Output |
|---|---|
| `pipeline/pipeline_gate_check.py <repo> <out>` (read-only) | `pipeline/pipeline_gate_check_8bf3d00.json`: every record validated bare and with a schema registry, plus `pipeline.sh validate` exit code and lines |

To run the 36-check suite: copy this folder to `/tmp/audit/lid_audit/`, copy `kimi_2026-11-25/lid-schema-additions/` somewhere, put rev2 in its `schemas/` as `reference_trace.schema.json`, and pass that folder as the first argument.
