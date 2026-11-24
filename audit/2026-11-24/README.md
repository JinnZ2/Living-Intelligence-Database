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
