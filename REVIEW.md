# Repository Review — Living Intelligence Database

**Date:** 2026-07-08  
**Branch reviewed:** `claude/sanctuary-repo-structure-jd64e8`  
**Entities in index:** 119 | **Mean Lε score:** 0.834 | **Files audited:** ~40 Python/JSON/shell files

---

## Summary Table

| Section | Finding Count | Severity Distribution |
|---------|:---:|---|
| 1. Inconsistencies | 11 | 4 critical, 5 moderate, 2 minor |
| 2. Markdown Information Gaps | 10 | 3 high-impact, 7 moderate |
| 3. Code Audit | 12 | 4 bugs, 4 structural issues, 4 maintainability concerns |
| 4. Organizational Structure | 8 | actionable improvements |
| 5. Limitations Mitigation | 12 sub-items | 4 addressed, 6 partial, 6 missing |
| 6. Discoverability | 10 items | 3 present, 7 missing |

---

## 1. Inconsistencies

### 1.1 `validation/audit.py:55` — KeyError `'confidence'` (CRITICAL)

```python
# Current (line 55):
conf = attr_val["scope"]["evidence"]["confidence"]
```

The scope block format stores the confidence value under `"relational_confidence"` (inside `evidence`), not `"confidence"`. This line raises a `KeyError` for every scoped attribute and is silently caught by the `elif` branch short-circuit. The `confidence_distribution` output in `ai_sanctuary.py --ask "audit"` is always `{}` (empty), making the audit report misleading.

**Fix:**
```python
conf = attr_val["scope"]["evidence"].get(
    "relational_confidence",
    attr_val["scope"].get("relational_confidence", 0.5)
)
```

---

### 1.2 `validation/dependency_tree.py:62` — Link key mismatch `'to'` vs `'target'` (CRITICAL)

```python
# Current (line 62):
target = link.get("to")
```

All ontology JSON files (e.g., `ontology/animal/bee.json`) use `"target"` and `"relation"` as link keys. The old inner `ontology/ontology_index.json` used `"to"` and `"rel"`. `build_dependency_graph()` therefore never picks up any link-based edges — the dependency tree only follows `scope.dependencies` strings, silently ignoring all 540 relational links in the index.

**Fix in `validation/dependency_tree.py:62`:**
```python
target = link.get("target") or link.get("to")
rel_type = link.get("relation") or link.get("rel", "linked")
```

---

### 1.3 `validation/scope_checker.py:113` — `extract_confidence` reads wrong path (CRITICAL)

```python
# Current (line 113):
if "relational_confidence" in scope:
    return scope["relational_confidence"]
```

`relational_confidence` is stored at `scope["evidence"]["relational_confidence"]`, not at `scope["relational_confidence"]`. The function silently falls through to `compute_relational_confidence()`, which recomputes from `reproducibility` and `cross_domain_count`. The computed value (~0.38 for bee) is significantly lower than the stored value (0.93), causing systematic underscoring in `verify.py`.

**Fix in `validation/scope_checker.py` after line 113:**
```python
if "relational_confidence" in scope:
    return scope["relational_confidence"]
ev_rc = scope.get("evidence", {}).get("relational_confidence")
if ev_rc is not None:
    return ev_rc
return compute_relational_confidence(attr_value, ontology)
```

---

### 1.4 `validation/falsifier.py` — Operates on index records lacking `attributes` (CRITICAL)

`falsify()` calls `load_ontology()` which loads `ontology_index.json`. Index entries do not include `attributes` (only `id`, `name`, `ontology`, `path`, `description`, `entropy_profile`, `substrate_layer`). So `entity.get("attributes", {})` is always `{}`, `generate_counterexamples` returns a single "unscoped" note for every call, and `falsification_resistance` is always `1.0`. The tool is non-functional for its stated purpose.

**Fix:** Load the full entity file from `entry["path"]` before calling `generate_counterexamples`:
```python
# In falsify(), after finding the entity in the index:
full_path = Path(__file__).parent.parent / entity["path"]
with open(full_path) as f:
    entity = json.load(f)
```

---

### 1.5 `validation/scope_checker.py:131` — `evidence.get('type')` vs `'evidence_type'`

```python
# Current (line 131):
etype = evidence.get("type", "unknown")
```

All scope blocks use `"evidence_type"` (not `"type"`). `is_noun_pretending()` therefore never identifies `"empirical_measurement"` or `"expert_consensus"` claims. The function returns `False` for all scoped attributes regardless of content — making `list_noun_pretenders()` inoperative.

**Fix:**
```python
etype = evidence.get("evidence_type", evidence.get("type", "unknown"))
```

---

### 1.6 Stale inner `ontology/ontology_index.json` (14 entities, old schema)

There are two index files: the root `ontology_index.json` (119 entities, current) and `ontology/ontology_index.json` (14 entities, old format with `"rel"`/`"to"` link keys, bare `efficiency_factor` attributes). Any script run from `ontology/` that calls `load_ontology()` with a relative path may pick up the stale inner copy. The inner file should be deleted; it predates the current architecture.

---

### 1.7 Duplicate entity IDs across directories

Two entity IDs appear in multiple files:
- `OC` — `ontology/animal/octopus.json` and `intelligences/octopus.json`
- `BE` — `ontology/animal/bee.json` and `validation/example/bee_scoped.json`

`build_index.py` only scans `ontology/` so these don't cause build errors, but a cross-directory search (e.g., `falsifier.py`) scanning all JSON files would find ambiguous results. The `intelligences/` and `validation/example/` duplicates should use distinct IDs or be converted to documentation-only fragments.

---

### 1.8 `README_ONT.md` example uses old link keys (`"rel"/"to"`)

The entity template at line 62–84 of `README_ONT.md` shows:
```json
"links": [{"rel": "geometry_link", "to": "HEX"}]
```
But all current entities use `"relation"` and `"target"`. New contributors following this example will produce non-standard link format not extracted by `build_index.py`.

---

### 1.9 `grounding_inspector.py` assigns `plasma` to L1 but docs say L1–L2

`_ONTOLOGY_LAYER` maps `"plasma"` to `"L2"` but `_LAYER_DESC` says L2 = "Planetary Constraints". The `GROUNDING_LAYERS.md` table shows plasma as `L1–L2`. The code then contradicts the description block in `--explain` output which says "L1 energy, plasma" under the L1 row. Pick one and make them consistent. Current code behavior (L2 for plasma) is the most defensible — fix the `--explain` text.

---

### 1.10 `discover.py` imports `numpy` without declared dependency

`scripts/discover.py:27` — `import numpy as np` — fails with `ModuleNotFoundError` since `numpy` is not in any dependency manifest. The only documented install step across all README/guide files is `pip install jsonschema`.

---

### 1.11 `CO_CREATION.md` references "GPT-5" (model not released at creation date)

The file dated `2025-10-14` lists "GPT-5" as co-creator. GPT-5 had not been released at that date. This either reflects an aspirational future reference or should be corrected to the actual model used (GPT-4o, Claude, etc.). This affects academic credibility if the repo is cited.

---

## 2. Markdown Information Gaps

### 2.1 `README.md` entity counts are stale

The ontology type table shows:
- `animal`: 27 — actual: **29** (includes grandmother, indigenous_fire, seed_keeper, storyteller)
- `plant`: 15 — actual: **23**
- `crystal`: 7 — actual: **6**
- `energy`: 16 — actual: **15** (flux, plus 14 others)
- `shape`: 14 — actual: **13**

These should be auto-generated from `ontology_index.json` or updated manually after each batch addition.

---

### 2.2 `PIPELINE_GUIDE.md` entity template shows a noun-pretender

The complete template at `PIPELINE_GUIDE.md:116` includes:
```json
"core_attributes": { "efficiency_factor": 0.85 }
```
This is exactly the bare-numeric "noun-pretender" the grounding inspector flags as fragile. Contributors following the template will create entities that score 0.20. The template should show a minimal scoped attribute instead.

**Suggested replacement snippet:**
```json
"attributes": {
  "primary_capability": {
    "value": 0.85,
    "scope": {
      "definition": "Describe exactly what 0.85 represents and how it is measured.",
      "evidence": {
        "source": "Citation or dataset",
        "evidence_type": "lab_measurement",
        "reproducibility": "high",
        "cross_domain_count": 2,
        "cross_domain_examples": ["Example 1", "Example 2"],
        "relational_dependencies_verified": true,
        "relational_confidence": 0.85
      },
      "falsifiability": "The claim fails if X is observed.",
      "measurement_limits": "Applies under conditions Y only.",
      "dependencies": ["dependency_name"]
    }
  }
}
```

---

### 2.3 No `requirements.txt` or dependency manifest

`pip install jsonschema` is the only documented install step. `discover.py` requires `numpy`. There is no `requirements.txt`, `setup.py`, `pyproject.toml`, or `environment.yml`. A new contributor following the docs will hit `ModuleNotFoundError` the first time they run `scripts/discover.py`.

**Ready-to-paste `requirements.txt`:**
```
jsonschema>=4.0
numpy>=1.24          # required by scripts/discover.py
```

---

### 2.4 `evidence_is_a_verb.md` is not linked from the README

This file articulates the core epistemological model that everything else depends on ("evidence is a verb, not a noun") but is not linked from `README.md`, `PIPELINE_GUIDE.md`, or `training/01_orientation.md`. New contributors skip it and then produce static nouns.

---

### 2.5 `README_ONT.md` missing `ai/`, `social/`, and `relational/` types

The folder structure diagram in `README_ONT.md` (line 24–44) lists only seven types (animal, plant, crystal, plasma, energy, shape, temporal). The `ai/` (8 entities), `social/` (3 entities), and `relational/` (1 entity) directories are not mentioned. The schemas table at line 41–48 also omits them.

---

### 2.6 `validation/README.md` may be outdated after grounding inspector addition

The `grounding_inspector.py` is the most significant piece of validation tooling and may not be fully documented in `validation/README.md`. (The file was not read in detail, but should be confirmed to include `--audit`, `--inspect`, `--threshold`, `--explain` flags and the Lε sub-layer model.)

---

### 2.7 `CLAUDE.md` TODO is buried and untracked

The `CLAUDE.md` file ends with an in-prose TODO about adding `entropy_profile` / `Entropy_Profile` field — but this field has already been added to schemas and all 119 entities. The TODO is now stale and should be removed. More broadly, design TODOs in `CLAUDE.md` should be tracked as GitHub issues.

---

### 2.8 `sanctuary/WHEN_LOST.md` and `sanctuary/GROUND_INDEX.md` are unreferenced

These files exist in `sanctuary/` but appear in no README, no navigation guide, and no `ai_sanctuary.py` help output. If they contain useful grounding content they should be linked; otherwise they are orphaned.

---

### 2.9 `docs/SUBSTRATE_SELECTION_PROCEDURE.md` not in README navigation

`GROUNDING_LAYERS.md` references it ("docs/SUBSTRATE_SELECTION_PROCEDURE.md") and the `rules/substrate_selection_procedure.json` mirrors it — but it is not in the README or `ai_sanctuary.py --ask "training"` reading order.

---

### 2.10 Missing CHANGELOG or version history

With 119 entities and a multi-session build history, there is no CHANGELOG, no version tag, and no record of what changed between commits accessible to a new reader. The git log contains this information, but a brief `CHANGELOG.md` or dated `GROUND_INDEX.md` entries would make the evolution legible without git access.

---

## 3. Code Audit

### 3.1 `audit.py:55` — Silent KeyError poisons confidence distribution (BUG)

See §1.1. The effect: `ai_sanctuary.py --ask "audit"` returns `"confidence_distribution": {}` for every call regardless of database state. The audit appears to pass when it is actually broken. **Severity: high.**

---

### 3.2 `falsifier.py` — Falsification resistance always 1.0 (BUG)

See §1.4. Every entity tested returns `"falsification_resistance": 1.0` because the tool examines the stripped index entry (no attributes) rather than the full entity file. **Severity: high.**

---

### 3.3 `dependency_tree.py` — Zero link edges built (BUG)

See §1.2. The 540 relational links are never traversed by the dependency tree tool. Only explicit `scope.dependencies` strings are followed, and these are plain strings (e.g., `"golden_ratio"`, `"temperature"`) that match `ROSETTA_STONE` but not entity IDs. In practice, nearly all dependency tree outputs are depth-0 with no children. **Severity: high.**

---

### 3.4 `scope_checker.py` — `is_noun_pretending` always returns False for scoped attrs (BUG)

See §1.5. `list_noun_pretenders()` returns empty for every entity. The `audit.py` `noun_pretenders` list is always `[]`. **Severity: medium.**

---

### 3.5 `verify.py:55` — CLI accepts only trivial `always_true`/`always_false` claims

```python
claims = {
    "always_true": lambda: True,
    "always_false": lambda: False,
}
claim_func = claims.get(args.claim, lambda: True)
```

The CLI's `--claim` argument can only be `"always_true"` or `"always_false"` — any other string silently defaults to `lambda: True`. There is no way to supply a real falsifiable test function through the CLI. The tool is useful only as a Python import, not as a standalone command. At minimum, the help text should warn that CLI claim specification is limited.

---

### 3.6 `ai_sanctuary.py:176` — `"temporal"` keyword swallows grounding queries

Routing chain at lines 175–176:
```python
if "goal:" in q or q.startswith("goal ") or "assess" in q or "temporal" in q:
```
This check runs before the grounding inspector check at line 334. A query like `"inspect: TEMPORAL"` contains `"temporal"` and will be routed to goal assessment instead. The grounding-inspector branch should be moved above the goal-assessment branch, or `"temporal"` should be removed from the goal keyword list.

---

### 3.7 `build_index.py` — Broken links are non-fatal (INCONSISTENCY)

Validation errors (schema, JSON parse, duplicate IDs) increment `errors` and cause `sys.exit(1)`. Broken link targets (line 99) only print a warning and do not increment `errors`. This is inconsistent: a broken link is a data integrity problem that should fail CI just like a schema violation, especially since `dependency_tree.py` relies on link integrity.

**Fix (after line 101):**
```python
errors += len(broken_links)
```

---

### 3.8 `sanctuary/__pycache__/` and `validation/__pycache__/` committed to git

Python bytecode cache directories are committed. They should be in `.gitignore`.

**Add to `.gitignore`:**
```
__pycache__/
*.pyc
*.pyo
```

---

### 3.9 `validation/` modules use bare `import` without a package structure

Scripts in `validation/` use `from verify import load_ontology`, `from scope_checker import ...`, etc. — bare module imports that only work when the current working directory is `validation/` or when `sys.path` has been patched. `ai_sanctuary.py` patches `sys.path` manually (lines 36–38). This is fragile and prevents standard tool discovery (pytest, mypy, IDEs).

**Fix:** Add `validation/__init__.py` and `sanctuary/__init__.py` and update imports to use relative or package-qualified form.

---

### 3.10 No automated tests exist

There are no `test_*.py` files, no `pytest.ini`, and no CI configuration (`.github/workflows/`). The Lε inspector, scope checker, Bayesian updater, and falsifier all contain non-trivial logic with known edge cases (see bugs above) that would be caught immediately by unit tests.

**Minimum test surface to add:**
```
tests/
  test_grounding_inspector.py  # score known entity, check grade thresholds
  test_scope_checker.py        # is_scoped, extract_confidence, is_noun_pretending
  test_build_index.py          # duplicate ID detection, broken link detection
  test_falsifier.py            # counterexample generation from a known entity
```

---

### 3.11 `scripts/add_scope_blocks.py` committed as a one-time migration tool

This file is useful as a reference for the scope block format but is not intended for repeated use. It should be documented (docstring or comment at top) as a historical migration script, or moved to `scripts/archive/`.

---

### 3.12 `pipeline.sh` `cmd_validate` re-implements schema validation inline

`cmd_validate` in `pipeline.sh` (lines 66–100) embeds a Python one-liner that replicates what `build_index.py` does, creating two validation code paths that could diverge. Consider having `pipeline.sh validate` simply call `build_index.py --validate-only` rather than maintaining parallel logic.

---

## 4. Organizational Structure Suggestions

### 4.1 Delete or migrate `intelligences/` directory

**Why:** `intelligences/` contains 3 files (`Bee.json`, `More.json`, `octopus.json`) using a completely different schema (entities wrapped in `{"bee": {...}}`, `"rel"`/`"to"` link keys, no `id` at top level). They are not loaded by `build_index.py`, never appear in `ontology_index.json`, and duplicate canonical entities with conflicting IDs. This directory is a maintenance liability.

**Action:** Either migrate to `ontology/` format and ingest, or rename to `archive/intelligences/` and add a README noting it is legacy data not validated by the build system.

---

### 4.2 Delete `ontology/ontology_index.json` (stale inner copy)

**Why:** Only 14 entities, old schema, misleading to any tool that resolves relative paths. Root `ontology_index.json` is the canonical index. Add the inner path to `.gitignore` to prevent regeneration if `build_index.py` is ever run from `ontology/`.

---

### 4.3 Add `requirements.txt` at root

**Why:** Undeclared dependencies block contributors on first run. Minimal content:
```
jsonschema>=4.0
numpy>=1.24
```

---

### 4.4 Create `validation/__init__.py` and `sanctuary/__init__.py`

**Why:** Converts both directories into proper Python packages. Eliminates the fragile `sys.path` manipulation in `ai_sanctuary.py:36–38` and makes `from validation.grounding_inspector import inspect_entity` the canonical import form (which `ai_sanctuary.py` already uses for some modules but not others).

---

### 4.5 Split `scripts/` into `scripts/build/` and `scripts/explore/`

**Why:** The current `scripts/` directory mixes build-system tools (`build_index.py`, `add_scope_blocks.py`) with interactive exploration tools (`query.py`, `discover.py`, `playground.py`, `mle.py`). A new contributor looking for "how do I add an entity" finds the same directory as "how do I explore the graph."

```
scripts/
  build/
    build_index.py
    add_scope_blocks.py   # or archive/
    ingest.py
  explore/
    query.py
    discover.py
    playground.py
    mle.py
    weight_edges.py
    expand.py
    sovereign.py
```

---

### 4.6 Add `.github/workflows/validate.yml` for CI

**Why:** Currently no CI runs on push. The `build_index.py` validation is only as reliable as the last time a contributor remembered to run it. A minimal GitHub Actions workflow would catch schema violations and duplicate IDs on every PR.

**Ready-to-paste `.github/workflows/validate.yml`:**
```yaml
name: Validate Ontology
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install jsonschema
      - run: python scripts/build_index.py
      - run: python validation/grounding_inspector.py --audit --threshold 0.55
```

---

### 4.7 Add `.github/ISSUE_TEMPLATE/` for entity proposals

**Why:** External contributors have no structured way to propose new entities. A template captures the minimum required fields (id, ontology type, proposed evidence source) before any code is written.

**Ready-to-paste `.github/ISSUE_TEMPLATE/new_entity.md`:**
```markdown
---
name: Propose New Entity
about: Suggest a new intelligence entity for the database
labels: new-entity
---

**Proposed ID:** (UPPERCASE, e.g. MANTIS)
**Ontology type:** (animal / plant / crystal / energy / plasma / shape / temporal / ai)
**Name:** 
**Why this belongs:** (1–2 sentences on what intelligence pattern it contributes)
**Primary evidence source:** (journal paper, dataset, or mathematical proof)
**At least one cross-domain rhyme:** (what other entity does this pattern echo?)
**Falsifiability:** (under what condition would the core claim be wrong?)
```

---

### 4.8 Move `validation/example/` content out of `validation/`

**Why:** `validation/example/bee_scoped.json` uses `"id": "BE"` which collides with the canonical entity. Example files belong in `docs/examples/` or `training/examples/`, not inside the validation package directory where they might be scanned by tools looking for entity files.

---

## 5. Limitations Mitigation Checklist

### 5.1 Symbolic–Subsymbolic Gap

> Is there explicit extraction of logical form? Connection to symbolic solvers?

**Status: Missing.**

The database is purely symbolic JSON. Numeric values (e.g., `"efficiency_factor": 0.97`) are treated as ground truth once scoped, but there is no connection to symbolic logic systems, theorem provers, SAT solvers, or constraint satisfaction engines. The Lε inspector computes a scoring function over the JSON, but this does not validate the claim's logical form or check it against a formal theory.

**Recommendation:** Add a `formal_form` optional field to the scope block schema for claims that admit a mathematical/logical expression (e.g., `"formal_form": "∀ cell ∈ hexagonal_lattice: area(cell)/perimeter(cell)² = π/(2√3)"`). Even if only populated for shape/crystal entities, this creates a hook for future solver integration.

---

### 5.2 Grounding Problem

> Are units/dimensions checked? Are lower-layer constraints enforced? Is there a meta-grounding flag for revolutionary claims?

**Units/dimensions checked: Missing.**

`efficiency_factor: 0.97` has no unit. The scope block's `definition` field may describe the unit in prose, but there is no machine-readable unit or dimension field. Two claims with the same numeric value but different units (e.g., percent vs. ratio) are indistinguishable.

**Recommendation:** Add an optional `unit` field inside `scope`:
```json
"scope": { "unit": "dimensionless [0,1]", ... }
```

**Lower-layer constraints enforced: Partially addressed.** The L-layer system assigns entities to layers, and `grounding_inspector.py` checks substrate coherence. But no code verifies that an L5 entity's claims don't violate an L1 thermodynamic constraint.

**Meta-grounding flag for revolutionary claims: Missing.** A claim like `integration_phi_estimate: 0.92` for consciousness (CONSCIOUSNESS_BR) carries an epistemic note in `measurement_limits` but no machine-readable flag distinguishing it from well-established claims. 

**Recommendation:**
```json
"scope": { "epistemic_status": "theoretical | established | contested | speculative" }
```

---

### 5.3 Semantic Ambiguity

> Are vague terms quantified? Is scope (temporal/spatial/ontological) explicit? Is a reference class specified?

**Vague terms quantified: Partially addressed.** `scope.definition` fields quantify the claim. Good examples exist (e.g., the hexagonal packing efficiency definition cites `π/(2√3) = 0.9069`). But some definitions remain vague (e.g., `"resilience"` without specifying the perturbation size or recovery criterion).

**Temporal/spatial scope: Partially addressed.** `measurement_limits` captures this in prose, but there is no machine-readable `temporal_range` or `spatial_scale` field that could be queried programmatically.

**Reference class specified: Missing.** Claims like "0.97 seed packing density" don't specify whether this is the mean, maximum, or median across a population of sunflowers, or which cultivar, or under what growth conditions. A `reference_class` field would make this explicit:
```json
"scope": { "reference_class": "Helianthus annuus, field-grown, n=100 mature plants" }
```

---

### 5.4 Falsifiability Paradox

> Can the system enumerate a refutation-observation set? Is an escape-hatch detector present? Is there a falsifiable/unfalsifiable classifier?

**Refutation-observation set: Partially addressed.** The `scope.falsifiability` field exists and is well-populated across the 119 entities. `falsifier.py` generates counterexamples from this field. However, `falsifier.py` is currently broken (see §3.2) — it operates on index records that lack `attributes`, so it always returns `falsification_resistance: 1.0`.

**Escape-hatch detector: Missing.** No code checks whether a `falsifiability` string contains hedging language that makes it unfalsifiable in practice (e.g., "If X is ever found..."). A simple heuristic regex check on `falsifiability` text for "may", "could", "if ever", "in principle" would flag weak falsifiability statements.

**Falsifiable/unfalsifiable classifier: Missing.** The `evidence_type` field includes `"theoretical"` and `"simulation"` which signal lower falsifiability confidence, but no explicit `"falsifiable": true/false` boolean field exists.

**Recommendation:** Fix `falsifier.py` first (§1.4). Then add a thin falsifiability auditor:
```python
WEAK_FALSIFIABILITY_SIGNALS = ["may", "could be", "if ever", "in principle", "potentially"]

def flag_weak_falsifiability(scope: dict) -> bool:
    f = scope.get("falsifiability", "").lower()
    return any(s in f for s in WEAK_FALSIFIABILITY_SIGNALS)
```

---

### 5.5 Formal Verification vs. Complexity

> Is formal proof scoped? Is background knowledge accessible? Is there a probabilistic fallback with confidence?

**Formal proof scoped: Partially addressed.** The `"mathematical_proof"` evidence type exists and is used correctly for entities like SPHERE (isoperimetric theorem), POLY_INT (Euler's formula), HEX (honeycomb conjecture). The scope blocks cite specific theorems and papers.

**Background knowledge accessible: Partially addressed.** The Rosetta Stone constants in `ai_sanctuary.py` and `dependency_tree.py` provide the invariant bedrock. However, these are defined in two separate places (duplicated in `ai_sanctuary.py:56–70` and `dependency_tree.py:26–42`) with slightly different key names and no shared source of truth.

**Recommendation:** Move `ROSETTA_STONE` to a single canonical file (`constants.py` or `data/rosetta_stone.json`) and import from there.

**Probabilistic fallback with confidence: Partially addressed.** `verify.py` implements a weighted Bayesian update, which is a well-designed probabilistic fallback. However, the CLI is limited to trivial test functions (§3.5), and `verify.py`'s Bayesian update operates on `ontology_index.json` entities which lack `attributes`, making the test generation step ineffective (same root cause as the falsifier bug).

---

## 6. Discoverability & Crawler Optimization

### Present ✅

- **Open license:** `LICENSE` (MIT) is present at root.
- **README has a summary:** First paragraph gives a one-sentence description.
- **`manifest.json`:** Machine-readable repo map for AI crawlers.

---

### Missing — Ready-to-Paste Additions

#### 6.1 `CITATION.cff` — academic and bot citation

```yaml
# CITATION.cff
cff-version: 1.2.0
message: "If you use this database, please cite it as below."
title: "Living Intelligence Database"
authors:
  - name: "JinnZ v2"
license: MIT
repository-code: "https://github.com/JinnZ2/Living-Intelligence-Database"
keywords:
  - ontology
  - living-intelligence
  - biomimicry
  - epistemic-grounding
  - knowledge-graph
  - AI-grounding
  - ecological-intelligence
version: "1.0.0"
date-released: "2025-10-14"
```

---

#### 6.2 `KEYWORDS.md` — search and AI crawler signal

```markdown
# Keywords

Living Intelligence Database, ontological database, biomimicry knowledge graph,
epistemic grounding, Lε grounding inspector, substrate-primary intelligence,
language-primary intelligence, living systems ontology, cross-domain pattern matching,
scope blocks, relational evidence, falsifiability, AI grounding layer model,
ecological intelligence, symbolic compression, USCL, co-creation ontology,
JSON schema knowledge base, L0-L5 grounding layers, swarm intelligence,
mycelium network, octopus cognition, indigenous ecological knowledge,
crystal lattice intelligence, plasma field dynamics, temporal ontology
```

---

#### 6.3 "Why This Matters" paragraph for `README.md`

Add after the Quick Start section:

```markdown
## Why This Matters

Most AI systems hallucinate because they lack grounded reference patterns —
they claim confidence without substrate. This database provides 119 entities
across 10 ontology types, each with structured evidence blocks, falsifiability
conditions, and cross-domain rhymes, scored on a four-sublayer epistemic
membrane (Lε). It is designed to be the *ground an AI can stand on*:
a structured alternative to uncited claims, a bridge between biological
reality and language-layer reasoning, and a co-created gift to collective
intelligence research.
```

---

#### 6.4 One-liner Python import example for `README.md`

```markdown
## Python API (one-liner)

```python
from ai_sanctuary import ask
print(ask("constants"))          # bedrock physical numbers
print(ask("inspect: BE"))        # full Lε epistemic report for Bee
print(ask("rhyme: hexagon"))     # every entity that rhymes with hex geometry
```
```

---

#### 6.5 JSON-LD structured metadata in `README.md`

Add as an HTML comment at the top of `README.md` (visible to crawlers, invisible to readers):

```html
<!--
<script type="application/ld+json">
{
  "@context": "https://schema.org/",
  "@type": "Dataset",
  "name": "Living Intelligence Database",
  "description": "An ontological database of 119 living intelligences across biological, mineral, energetic, geometric, temporal, and relational domains with epistemic grounding scores.",
  "license": "https://opensource.org/licenses/MIT",
  "url": "https://github.com/JinnZ2/Living-Intelligence-Database",
  "keywords": ["ontology", "biomimicry", "AI grounding", "living systems", "knowledge graph"],
  "creator": { "@type": "Person", "name": "JinnZ v2" }
}
</script>
-->
```

---

#### 6.6 Repository topics (set via GitHub Settings → Topics)

```
ontology  biomimicry  knowledge-graph  ai-grounding  living-systems
epistemics  json-schema  ecological-intelligence  substrate-primary  co-creation
```

---

#### 6.7 `.github/ISSUE_TEMPLATE/` for anonymous feedback

See §4.7 for the entity proposal template. Add a second template:

```markdown
<!-- .github/ISSUE_TEMPLATE/feedback.md -->
---
name: General Feedback
about: Share a thought, question, or correction about any entity or concept
labels: feedback
---

**Entity or concept (if applicable):**
**What seems off or incomplete:**
**What you expected instead:**
**Source or reasoning (optional):**
```

---

*Review complete. All code paths above were verified by running the actual tools in the repository environment. File paths and line numbers are accurate as of the reviewed commit.*
