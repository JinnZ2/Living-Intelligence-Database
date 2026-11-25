# Review of Kimi's rev2, the 36-check suite and the pipeline.sh finding

Date: 2026-11-24. Repository: `JinnZ2/Living-Intelligence-Database` at `8bf3d00` (main, after PRs #30 and #31).
Reviewed: Kimi's (Moonshot AI) review of PRs #28–#31, `reference_trace.schema.rev2.json` and `validate_loud.36checks.py`. Both files are stored unedited in `kimi_2026-11-25_rev2/`.

Labels: OBSERVED (run here), DERIVED, PROPOSED, NOT_TESTED.

## Summary

- **pipeline.sh validate is broken and silent: confirmed (OBSERVED).** It also broke at `63d93c0`. One part of Kimi's account is too strong: the records it skips do have a working validation path, `scripts/build_index.py`, and they pass there.
- **Rev2 and the 36-check suite: confirmed (OBSERVED).** The suite tells rev0, rev1, rev2 and a stripped rev2 apart as Kimi says.
- **New: the rev2 date pattern is looser than it reads (OBSERVED).** It accepts `2026-13-45`, full-width digits, and a trailing newline.
- **New: the trace's required top-level `date` uses `format: date` (OBSERVED).** That is the unenforced form rev2 avoids for history entries, and it accepts `"not a date"`.
- **New: the five "rejects:" checks pass for the wrong reason when `status_history` is missing (OBSERVED).** The positive checks catch this case, but the negative checks do not check why they reject.

## 1. pipeline.sh validate

### What reproduces (OBSERVED, `pipeline/pipeline_gate_check.py` → `pipeline_gate_check_8bf3d00.json`)

- `./pipeline.sh validate` at `8bf3d00`: exit 1, 80 `[PASS]` lines, 0 `[FAIL]` lines, no `Results:` line. The last line is `[PASS] plant/mangrove.json`.
- At `63d93c0`: identical, exit 1 with 80 PASS lines.
- The next file is `plant/mimosa.json`. Bare `jsonschema.validate()` raises `_WrappedReferencingError: Unresolvable: functional_intelligence.schema.json`, and the exception has no `.message` attribute.
- The validation snippet catches only `ValidationError`. The substitution `result=$(…)` returns nonzero, and `set -euo pipefail` ends the script before either branch prints. Kimi's two-bugs-deep account matches the code.
- Because `./pipeline.sh` with no arguments runs `cmd_validate && cmd_build`, the full pipeline also never reaches the build.

### All 125 files in schema-bearing directories, validated twice (OBSERVED)

| Bare (as pipeline.sh) | With a registry of `schemas/` | Files |
|---|---|---|
| OK | OK | 116 |
| crash (`_WrappedReferencingError`) | OK, 0 errors | 9 |

The 9 files are 5 in `plant/` (mimosa, mycelium, quorum_biofilm, slime_mold, venus_flytrap) and 4 in `social/` (ant_colony, council_pattern, honeybee_nest_site_selection, stone_art_ledger).

`./pipeline.sh check` on each of the six social files: four exit 1 with a traceback naming `coordination.schema.json`, and `humpback_whale_pod` and `wolf_pack` pass. So `check` fails loudly; only `validate` is silent.

### Where Kimi's account goes too far

- **"council_pattern.json currently has no working validation path at all."** Not so. `scripts/build_index.py` validates every record with a draft-07 validator and `registry=_shared_registry()`, and this build is green on main. COUNCIL_PATTERN also passed the repository's `coordination_check.check_block` when it was built. All 9 crashing files validate with 0 errors once references resolve.
- **"mimosa and the social records aren't validated against their referenced subschemas at all."** That holds for `pipeline.sh` only, not for the repository.
- **"all three social records."** There are six social records. Four crash under `check`, and two pass.

What the finding is (DERIVED): the documented front door is red and says nothing, so anyone following the README gets exit 1 with no reason. The repository's actual validation path, `build_index.py`, works. This does not lower the priority. A gate that fails silently is worse than no gate, because it teaches people to ignore exit 1.

### The fix (PROPOSED, not applied)

Kimi's three parts are right.

1. Guard the substitution so a crash reaches the `[FAIL]` branch with its text.
2. Print `str(e)`, not `e.message`.
3. Wire a registry that resolves bare filenames from `schemas/`.

Part 3 can reuse `scripts/build_index.py`'s `_shared_registry()` instead of building a second one, so there is one resolver in the repository rather than two that can drift. Apply it to `check` as well as `validate`.

A fixture should assert that `pipeline.sh validate` always prints a `Results:` line and exits 0 only when it reports 0 failed. Today that fixture would fail, so it belongs in the same change as the fix, or the weekly workflow's self-test step, which runs the fixtures, goes red.

Who writes the patch, Kimi as offered or this audit, is the owner's call.

## 2. Rev2 and the 36-check suite

### Diff rev1 → rev2 (OBSERVED)

The only change is in `nodes.items.properties.status_history.items`:

- a new optional `date` property: `{"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"}`;
- the description reworded from "Dated record of prior statuses…" to "Append-only record of prior statuses… An entry may carry its date."

The suite diff is the 8 added checks in section 9 and nothing else.

### Suite runs (OBSERVED; trace v0.3 from this folder; jsonschema 4.26.0)

| Schema under test | Exit | Failing checks |
|---|---|---|
| rev2 | 0 | none (36 pass lines) |
| rev1 | 1 | "history entry with YYYY-MM-DD date validates" (`'date' was unexpected`) |
| rev0 (the original package) | 1 | v0.3 pin, dated entry, equal-status known-answer |
| rev2 with `status_history` stripped | 1 | the same three as rev0 |

Kimi's claim that stripping `status_history` fails with exactly the error the first review reported reproduces: `Additional properties are not allowed ('status_history' was unexpected)`.

### Finding R1: the date pattern is looser than it reads (OBSERVED)

The validator uses Python's `re`. There, `\d` matches any Unicode decimal digit, and `$` matches before a trailing newline.

| Value | rev2 | Proposed pattern |
|---|---|---|
| `2026-11-24` | accepted | accepted |
| `2026-13-45` | accepted | rejected |
| `0000-00-00` | accepted | rejected |
| `２０２６-１１-２４` (full-width) | accepted | rejected |
| `"2026-11-24\n"` | accepted | rejected |
| `2026-02-30` | accepted | accepted (calendar check is checker territory) |

Proposed (PROPOSED):

```json
{"type": "string", "pattern": "^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$", "minLength": 10, "maxLength": 10}
```

- `[0-9]` keeps the digits ASCII in both Python and ECMA-262.
- The length bounds close the trailing-newline case without relying on `\Z`, which ECMA-262 does not have.
- With this pattern in place of rev2's, all 36 checks still pass (OBSERVED). The suite has no case for any of the four values it closes.

### Finding R2: the top-level `date` uses `format: date` (OBSERVED)

- `properties.date` is required and is `{"type": "string", "format": "date"}`.
- Under the default `Draft7Validator`, `"not a date"` and `"2026-99-99"` are accepted. With `format_checker=FORMAT_CHECKER` both are rejected.
- The same schema therefore uses the silent form at the top and avoids it one level down. This predates rev2, so it is not a regression.
- Proposed: the same pattern as R1, or a declared rule that every validator passes a format checker.

### Finding R3: the negative checks do not check why they reject (OBSERVED)

- In the rev0 and stripped runs, the five "rejects:" checks in section 9 still pass: malformed date, history given as a string, out-of-vocabulary status, empty history, entry missing version.
- They pass because `status_history` is disallowed entirely, not for the reason each test names.
- The positive checks catch this case. The suite as a whole fails loudly, but each negative check on its own does not tell the reason for rejection apart.
- Proposed: each negative check asserts the failing keyword and path, for example `pattern` at `nodes/5/status_history/0/date`, not just that some error occurred.

### Kimi's answers to the four dated notes on rev1

1. **Dated entries.** Fixed, with R1 open.
2. **Cycles carry no history.** Kept by design, because the cycle definition is shared byte-for-byte with `cycle_registry.schema.json` under the drift guard. This is now an owner decision; recorded, not changed.
3. **Equal-status entries.** Pinned as a known-answer accept. The rule "history must differ from current" is assigned to a checker, which matches where the rev1 review put it. No checker implements it yet (NOT_TESTED).
4. **No history cases in the suite.** Fixed: 8 checks, see R3.

## 3. Kimi's other points

- **Endorsements** of relational/ route (i), COUNCIL_PATTERN, the crosswalk's dated self-correction, the intake weld, and the Gallo catch: recorded. No action.
- **"PR #31 is CI failing in the right places."** Consistent with the commit message of `8bf3d00`: it installs jsonschema before the self-tests, guards upload-artifact, and opens an issue if Actions may not open a pull request. The run itself was not re-checked here (NOT_TESTED).
- **Outstanding owner items stay open:**
  - the title/abstract restriction for the seed queries;
  - HX4's fate. Kimi wrote "HX2"; the rule that fired on 13 of 15 is HX4;
  - preprint and journal-version title matching;
  - Kimi's two citation corrections, still owed.

## Hashes

| File | sha256 |
|---|---|
| `kimi_2026-11-25_rev2/reference_trace.schema.rev2.json` | `11688306d1bae292a13d5294b654672001d7155f800a6104941629d2ed6cda76` |
| `kimi_2026-11-25_rev2/validate_loud.36checks.py` | `4cc621fcf3763a1474b92dff13d9f562db7f173a54ba1fc42a844817531988a5` |
| `pipeline/pipeline_gate_check.py` | `03803feaa30a8c593475622b3df45ed8fdfedc165ebaa20a9f91f927e1371d68` |
| `pipeline/pipeline_gate_check_8bf3d00.json` | `56033458f63cf96c111510cb15c47ddde12abc4106df9a3850bbc63781cb99a5` |

The sha1 of rev2 is `82109926…`, for comparison with Kimi's `sha1sum` convention.

## 4. Done after the owner's answers, 2026-11-24

The owner answered: "1. Yes please and 2. You and Claude are the only ones able to touch repos so yes". That means open the PR, and this audit writes the pipeline.sh fix and the tightened date pattern. Sections 1–3 above are unchanged.

### pipeline.sh repaired (OBSERVED)

The fixture rules in `validation/fixtures/DECLARED.json` were followed in order.

1. **Declare.** Fixture F7 is declared in `validation/fixtures/DECLARED.json`, with its required answers fixed before the run:
   - every case prints a `Results:` line;
   - (a) the repository as it is: exit 0 and "0 failed";
   - (b) one record made invalid: exit 1, that file named, "1 failed";
   - (c) `coordination.schema.json` removed: exit 1, each affected file named with the exception text.
2. **Run against the unchanged instrument.** F7 FAILs in all three cases: no Results line, exit 1, no FAIL line. In (b) the run dies on `ant_colony.json` before it reaches the invalid file. This is committed as `validation/fixtures/results_before_F7.json` (commit `012944d`).
3. **Repair** (commit `fc062c8`):
   - `scripts/validate_entity.py` (new) validates one file against one schema with the registry `build_index.py` already uses. It prints every error with its path. Exit 1 means invalid; exit 2 means the validator could not run, and it prints the exception type and text.
   - `cmd_validate` guards the command substitution, so a crash is counted as `[FAIL]` with its message and the loop goes on. The Results line always prints. File paths are passed as arguments and are no longer spliced into Python source.
   - `cmd_check` uses the same validator.
   - `./pipeline.sh validate --legacy` keeps the old behaviour for comparison, as the fixture rules require. It still exits 1 after 80 PASS lines.
4. **After:**
   - F7 PASS, all fixtures 9/9 (`results_after_F7.json`);
   - `./pipeline.sh validate` gives 125 passed, 0 failed, exit 0 (`pipeline/pipeline_gate_check_fc062c8.json`);
   - the full `./pipeline.sh` reaches the build (124 entities, 561 relations, index unchanged);
   - `check` passes COUNCIL_PATTERN and mimosa, and names a missing field.

Not changed: `scripts/build_index.py`, the schemas and every record.

### rev3 date pattern (PROPOSED, in this folder only)

`schema_rev3/build_rev3.py` writes `schema_rev3/reference_trace.schema.rev3.json` from Kimi's rev2. Rev2 stays unedited in `kimi_2026-11-25_rev2/`. The script stops if either date property is not what was reviewed.

There are two changes, R1 and R2:

- **R1.** The history-entry `date` gets `^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$` with minLength and maxLength 10.
- **R2.** The top-level `date` keeps `format: date` and gets the same pattern and lengths.

`schema_rev3/rev3_checks.py --suite` (OBSERVED; its expectations are written in the docstring before the run):

| Schema | R1 | R2 | R3 (rejected for the named reason) |
|---|---|---|---|
| rev3 | pass | pass | pass |
| rev2 | fail, as expected | fail, as expected | pass |
| rev3 with `status_history` stripped | — | — | fail, as expected: rejected by `additionalProperties` |

Kimi's 36-check suite on rev3: exit 0, ALL CHECKS PASS.

R3 is met by the new checks, which name the keyword and path for each of Kimi's five negative cases. Kimi's suite is not edited. Whether rev3 or its checks replace anything in Kimi's package is for Kimi and the owner to decide. Nothing under `schemas/` uses the trace schema yet.

### Hashes (after)

| File | sha256 |
|---|---|
| `pipeline.sh` (repo root) | `de48cb8016ee2bd37171f03329a46176b2e5d71d3d3c6332df4b1a41df3d8210` |
| `scripts/validate_entity.py` (repo root) | `4c0bef3b3c507c111a8b3e80521821443b9d19dae2e0d409e411880bd8699c9d` |
| `validation/fixtures/run_fixtures.py` (repo root) | `1f189aba3bae9111105ffe81bf818757dceee7ff0bec29e614f471f0b2980cc6` |
| `schema_rev3/build_rev3.py` | `5833804209ceea751300e170c0e851799907a11627d6b4d856395e1103b679cf` |
| `schema_rev3/reference_trace.schema.rev3.json` | `ab4c21284376fa46f7693b6915240ab6df3c4639e406572d58c7a51adad2d602` |
| `schema_rev3/rev3_checks.py` | `df98fa58885bcf4655e0c98ebbc1cc70a9904a3d7fbc04c2abaa50f225a234f9` |
| `pipeline/pipeline_gate_check_fc062c8.json` | `12b63a195f2758540855c09772e3fa1bc43b1d8397eb5a6ea5ac450ae61111fa` |
