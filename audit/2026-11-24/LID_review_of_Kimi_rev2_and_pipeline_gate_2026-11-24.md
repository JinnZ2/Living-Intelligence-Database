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
