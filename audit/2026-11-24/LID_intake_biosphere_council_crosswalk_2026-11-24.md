# LID Weekly Intake, Biosphere, Council and D–L Crosswalk

Date: 2026-11-24. Target: `JinnZ2/Living-Intelligence-Database` main at `7be9b5b`. Companion repository read: `JinnZ2/AI-arena` at `bb9ab96`, read only. No repository data file was modified. Everything below is PROPOSED unless it is labelled OBSERVED or DERIVED.

This document covers four parts of the owner's request:

1. A weekly GitHub Action that brings in new science, filters it, audits it, reasons over it with the instruments, and writes hypotheses for review.
2. The biosphere as a dependency.
3. A review of the Council as a complement to AI-arena.
4. The D–L layer mapping.

The deviation extraction is in its own document, `deviation/LID_deviation_extraction_2026-11-24.md`.

---

## 1. Weekly science intake

### Fit with what the repository already declares (OBSERVED)

The repository already has a source pass and a reading contract, so the intake is built to sit inside them:

- `scripts/existence_check.py` asks NCBI and Europe PMC whether cited works exist. It reads no abstracts and sets no status.
- `registry/DECLARED.json`, amendment "UNDERSPECIFIED + MATCH_SUSPECT; second index; abstract pass", records that "Europe PMC answered; api.openalex.org was refused by this environment's egress proxy (HTTP 403 on CONNECT)". The intake therefore uses Europe PMC.
- Amendment "NOT_ADDRESSED + reading queue" says readings "arrive as registry/attribute_readings.json from an outside reader. scripts in this repository build the steps and re-export from that file; they make no judgment." The intake therefore writes no `claim_support` and no `number_support`. Its candidates wait for a reader.
- The repository's convention is that an amendment is declared before the run it governs. A draft amendment for the intake is at the end of this section. It is not written into `DECLARED.json`.

### What was built

| File | Role |
|---|---|
| `intake/weekly_intake.py` | Five stages: fetch, filter, candidates, hypothesis stubs, report. Standard library only. Only the fetch stage uses the network. |
| `intake/intake_queries.json` | Owner-editable query list. Each query names the fields it touches. The five seed queries are mine and are PROPOSED. |
| `intake/weekly_science_intake.yml` | Proposed workflow. It is inert where it sits; see "Adopting it". |
| `intake/fixtures/epmc_honeycomb_sample.json` | One real Europe PMC response, used for offline testing. |
| `intake/live_2026-11-24/` | One live run: raw snapshots with sha256, `intake.json`, `intake.md`. |

Stages, as the script's docstring declares them:

- **Fetch.** One Europe PMC request per query, restricted to works first indexed in the window (default: the last 7 days). Every response is saved byte-for-byte with its sha256 before it is parsed. A failed request is recorded as NOT_RUN and the run exits 3.
- **Filter.**
  - Removed, with the reason kept: F1 no abstract, F2 PMID already in `registry/sources.json`, F3 duplicate.
  - Flagged and kept: G1 retraction, erratum, correction or expression of concern; G2 preprint.
- **Candidates.** One record per kept work and touched field. Each record holds:
  - the field's `scope.definition`, verbatim with its sha256, and its value, copied and not coerced;
  - verbatim quote candidates of at most 25 words (a cut quote is marked TRUNCATED);
  - every number in the abstract, with the deviation extractor's role;
  - `reading_state: AWAITING_READER`.
- **Hypothesis stubs.** Each stub is `{id, rule, touches, statement, falsifier, status: PROPOSED, generated_by}`:
  - HX1: a value-scale number appears in the abstract.
  - HX2: the abstract shares a unit with a condition bound in the field's own prose (regime raw material).
  - HX3: the abstract has a ± and the field has no deviation candidate of its own.
  - HX4: the abstract names a biosphere-carried condition and the entity is a BIOSPHERE candidate.
  - Each stub says what a reader could check, not what is true.
- **Report.** `intake.json` and `intake.md` go into a pull request for a person to review. Nothing is merged, and nothing in `ontology/` or `registry/` is written.

### Tests

- `weekly_intake.py --selftest`: 9/9 PASS. It covers the 25-word cut, F1, F2, F3, G1, G2, the 7-day default and a reversed window failing.
- Offline fixture run with one query deliberately missing: that query was reported NOT_RUN, the run exited 3, and `intake.md` says "The run is incomplete." (OBSERVED)
- Live run, window 2026-11-17 to 2026-11-24 (OBSERVED, `intake/live_2026-11-24/`):
  - All 5 queries SAVED, with 2, 4, 10, 3 and 0 hits.
  - 15 works kept and 4 removed (F1 no abstract), giving 15 candidates.
  - 15 hypothesis stubs: HX1 2, HX2 0, HX3 0, HX4 13.
- Replay: re-running the offline stages on the saved snapshots gave byte-identical files. `intake.json` has sha256 `bb756e6c…7051` in both runs, and `intake.md` matched as well. The workflow repeats this replay as a step and fails on any difference.
- The repository's own `validation/fixtures/run_fixtures.py` gave 8/8 PASS, 0 NOT_RUN. The workflow runs it before going to the network.

### What the live run shows about the design (OBSERVED → PROPOSED fixes)

1. **Query precision is low for broad terms.** The `my_phosphorus` query returned food-composition papers, for example PMID 43041303 "Nutritional content of the African horned cucumber". Europe PMC matches beyond title and abstract. Proposed: restrict the seed queries to `TITLE:` / `ABSTRACT:` fields. That is the owner's edit to make.
2. **HX4 fires on almost everything** (13 of 15). Nearly every biology abstract names temperature, water or soil, so as written the rule does not discriminate. Proposed: keep it and report its rate, require two terms, or retire it. Owner decides.
3. **A preprint and its published version are not merged.** The fixture held a preprint (source PPR, no PMID) and the journal version of the same honeycomb work as two candidates. F3 matches only on PMID or DOI. Proposed: a title-token match, flagged and never auto-merged.
4. **Titles keep HTML entities** (`&lt;i&gt;`). They are left as received, since the protocol forbids silent normalization.
5. **Gallo et al. 2026 (PMID 42839964) is not in `registry/sources.json`**, although the reference trace cites it. F2 therefore lets it through. This is correct behaviour, and it shows the trace's sources were never registered.

### The weld between intake and readings

Kimi's `attribute_reading.schema.json` has no state for "not yet judged". Its `claim_support` enum is STATED / RELATED / CONTRADICTED / NOT_ADDRESSED / NOT_READ, and each work must carry a `source_id` already in `registry/sources.json`. A machine-found work fails both requirements. So intake candidates use their own shape, and they become readings only after two steps:

1. The source is registered, which is a declared step.
2. An outside reader writes the reading.

This is recorded as a weld, not forced.

### Adopting it

The workflow sits at `audit/2026-11-24/intake/weekly_science_intake.yml`, where GitHub does not run it. To adopt it:

- Copy it to `.github/workflows/`. Pushing a workflow file needs a token with the `workflow` scope.
- Add the amendment below to `DECLARED.json`.

It uses `actions/checkout@v7`, `actions/setup-python@v7` and `actions/upload-artifact@v7`. The v7 major matches AI-arena's CI, and the latest releases checked today are v7.0.1, v7.1.0 and v7.0.2.

The optional language-model reading step runs only if the repository variable `INTAKE_LLM_ENABLED` is `true`. Even then it is declared and not implemented: it exits 1 with NOT_IMPLEMENTED, so it cannot pass silently.

Draft amendment (PROPOSED, not written to `DECLARED.json`):

```json
{
 "date": "2026-11-24",
 "name": "weekly intake (source pass, stage 0)",
 "after": "by the owner's request of 2026-11-24 for a weekly action; declared before any scheduled run",
 "changes_a_declared_value": false,
 "status": "PROPOSED",
 "scope": "works first indexed in Europe PMC in the run window, for the queries in intake_queries.json",
 "reads": "bibliographic record and abstract only; no full text",
 "writes": "intake/weekly/<date>/ only; nothing in ontology/ or registry/",
 "judgment": "none; candidates carry reading_state AWAITING_READER; claim_support is written only by an outside reader under 'NOT_ADDRESSED + reading queue'",
 "failure": "any query NOT_RUN fails the run; no pull request is opened from an incomplete run",
 "merge": "never by the workflow"
}
```

---

## 2. Biosphere as a dependency

### State of the record (OBSERVED)

`ontology/relational/biosphere_reference.json` has id BIOSPHERE, `record_kind: earth_scale_reference`, status PROPOSED and sources S1, S2, S4 and S5 with sha256. It is not validated or indexed, because `ontology/relational/` has no schema and the build skips it (re-check N2).

Its sibling `synergies.json` has a different shape (`{nodes, edges}`) and no `record_kind`.

### Indexing route (PROPOSED)

- **(i) Preferred.** A `schemas/relational.schema.json` with `oneOf` two shapes:
  - a graph: required `nodes` and `edges`;
  - a reference record: required `id`, `record_kind`, `status` and `sources`.
  
  This needs no edit to either data file.
- **(ii)** Add `record_kind: "graph"` to `synergies.json` and discriminate on it. This edits a data file, so it is the owner's call.

Either way, the build must stop skipping `relational/`. Then the KNOWN_HELD-style links to BIOSPHERE resolve, or fail loudly.

### Candidate dependents

`biosphere/biosphere_candidates.py` applies two declared rules (5/5 self-tests PASS):

- **B1:** the record is an animal or plant.
- **B2:** an attribute's scope text names a biosphere-carried condition: sunlight, water, temperature, carbon, oxygen, soil, nutrient or season.

Result on 122 indexed records (OBSERVED): B1+B2 52, B1 only 12, B2 only 22, neither 36, 0 load failures. All rows are UNCHECKED.

Reading of the result (PROPOSED):

- The 64 organism records (B1) are the strong candidates.
- The 22 found only by B2 are mostly crystal, energy, plasma and shape records that use temperature or sunlight as a physical variable. For SOLAR_WIND, AURORA and E_SUN-like inputs, the dependency likely runs the other way: the biosphere depends on them. A word match cannot tell the direction of a dependency, so these need the owner.
- "Spring" as a season word will also catch a mechanical spring.
- Three social records match no rule: ANT, BEE_NEST_SITE and STONE_LEDGER. BIOSPHERE already links to ANT and STONE_LEDGER. No rule match does not mean independent.

### The "zero-sum" rule

BIOSPHERE's COUNCIL link carries the note "the council / ai-arena rule: zero-sum outcomes are scope errors". I searched AI-arena at `bb9ab96` for "zero-sum", "zero sum" and "scope error". The rule's text was not found there either (OBSERVED). Its source stays UNKNOWN, and it is held as the owner's statement.

---

## 3. Council as a complement to AI-arena

### Where COUNCIL is (OBSERVED)

COUNCIL is only at `validation/example/council.json`. Its `_audit_note` reads: "Attributions to named living peoples are unsourced; not consented; not promoted to ontology/."

Its description names Haudenosaunee, Māori, Igbo, Tibetan and Aboriginal Australian governance, with `description_source_status: UNSOURCED`. All five `cross_domain_examples` are UNSOURCED, and `relational_dependencies_verified: true` has `verified_basis: null`.

The cultural-preservation constraint applies directly here. The attributions stay held, they are not promoted, and this review adds none.

### Where it fits AI-arena (OBSERVED quotes)

- COUNCIL `consensus_protocol`: "Objection is a form of teaching, not obstruction."
  - AI-arena `CLAUDE.md`: "disagreement as information and exploration".
  - `protocol/arena_protocol.md`: "Disagreement is information."
  - These agree: both treat objection as content, not noise.
- COUNCIL's attribute `intergenerational_decision_horizon = 7` (seven generations) gives the arena something it does not have: a time horizon on decisions.

### Where they differ: a weld, not a conflict to resolve

- COUNCIL: "Deliberation continues until all voices are heard — the council does not close until the silence is comfortable." It closes on consensus.
- `protocol/arena_protocol.md`: "The arena exists to make ensemble disagreements productive — not to collapse them into consensus." and "A session ends with a convergence map, not a verdict."

Proposed complement: the arena maps, and the council decides. The arena's convergence map becomes the council's input, and the council's decision is recorded with its horizon (seven generations) and its dissent. Neither protocol changes. The joint is recorded as a weld, so that neither the mapping nor the deciding is forced into the other's shape.

### Linking across repositories (PROPOSED)

The KNOWN_HELD link WOLF_PACK → COUNCIL (`registry/known_held_links.json`) is still held. If COUNCIL is to be understood as an AI-arena complement, a cross-repo reference would make the dependency explicit without moving COUNCIL into `ontology/`:

```json
{"rel": "complements", "to": "COUNCIL", "repo": "JinnZ2/AI-arena", "pinned_commit": "bb9ab96", "path": "protocol/arena_protocol.md", "status": "PROPOSED"}
```

This follows AI-arena's own CI pattern: siblings pinned by commit, with sha256 checks. The owner decides whether COUNCIL lives in LID, in AI-arena, or in both with a pin.

### Addendum, 2026-11-24: the pattern, not the people

The owner wrote: "Thé pattern of the council is what’s important, not the people." Then: "It would be similar to an Oracle in AI terms i guess." And: "Ones who looks to things at the Root dependancy, Long cycles, wisdom Accounting, or whatever other English terms dont quite fit."

`council/council_pattern.json` (id COUNCIL_PATTERN, PROPOSED) holds the pattern and names no tribe, nation or person. It follows the convention of `ontology/social/stone_art_ledger.json`.

- **Words first.** The owner's three phrases are the primary text, verbatim, with `english_fit: APPROXIMATE`. The three functions (root dependency, long cycles, wisdom accounting) are readings of those phrases, each pointing to where the repository already carries it:
  - dependency chain and BIOSPHERE;
  - the seven-generation horizon and CYCLE;
  - the reversal count and STONE_LEDGER.
  
  If a reading and the words differ, the words hold.
- **Coordination block in the repository's shape:**
  - three cycles: decision, scope widening on a zero-sum outcome, and the horizon;
  - three observer cuts. The first cut is a one-shot oracle reading. It keeps no cycle, which is why a plain oracle reading loses the pattern.
  
  It passes `validation/coordination_check.py` `check_block`. Planted defects (missing key, bad status tag, unknown cycle) fail as expected.
- **Oracle analogy.** It is recorded as the owner's tentative word. Where it fits and where it differs is PROPOSED: the record reads it as an accountable oracle.
- **Held file not edited.** `validation/example/council.json` is unchanged. Its names and cross-domain examples stay held there. The build fails if any of them appears in the pattern record, and a planted "Māori" made it fail as intended.
- **Placement.** The record sits in the audit folder. Moving it into `ontology/social/` is the owner's decision.

> **Note, 2026-11-24 (added; the line above is unchanged).** On the owner's "Both please", the record was placed at `ontology/social/council_pattern.json`, byte-identical to the audit copy. Its content stays PROPOSED.
>
> - **Links.** Two links moved to `held_links`: `pattern_of` COUNCIL, because `pattern_of` is not in the schema's rel list and COUNCIL is unindexed, and `connected_to` BIOSPHERE, which is unindexed. The build would otherwise stop on them. `registry/known_held_links.json` is not edited.
> - **Index.** `scripts/build_index.py` then indexed 123 entities (was 122) and 557 relations (was 555). The only additions are COUNCIL_PATTERN and its links to STONE_LEDGER and CYCLE; nothing was removed. The one broken link reported is the existing KNOWN_HELD WOLF_PACK → COUNCIL.
> - **Checks.** `validation/coordination_check.py`: 0 failures, and its self-test passed 38/38. `validation/fixtures/run_fixtures.py`: 8/8 PASS.
> - **Baseline.** The deviation and biosphere results in this folder were computed at `7be9b5b`, before this entity existed. They are not re-run.

### A mismatch in AI-arena (OBSERVED, not fixed)

`CLAUDE.md` says "v2 is currently documented but not yet implemented". Yet `arena/coordinator.py`, `arena/admission.py` and their neighbours exist, and `protocol/arena_protocol.md` says it governs v2.

Its test suite, `tests/run_counts.py`, gave 561 ran, 543 passed, 18 NOT_RUN and 0 failed. The 18 were NOT_RUN because no formula-audit sibling was checked out here. Nothing was written to AI-arena.

---

## 4. D–L crosswalk

### The two axes

- **D** is role in the dependency chain: D0 law, D1 energy, D2 condition, D3 material, D4 entity, D5 pattern.
- **L** is substrate layer (`docs/GROUNDING_LAYERS.md`): L0 classical physics, L1 thermodynamics, L2 planetary, L3 ecological, L4 biological, Lε epistemic membrane, L5 social and cultural.

`crosswalk/build_crosswalk.py` writes `crosswalk/crosswalk_D_L.json`. It tags all 28 nodes of bee trace v0.3 with PROPOSED L tags, each with a reason, and fails if the trace's node set and the tag table differ by any id.

### Result (DERIVED from PROPOSED tags)

| D role | L layers it falls on |
|---|---|
| D0 law | L0 ×4, L1 ×2 |
| D1 energy | L4 ×5, L2 ×2, L3 ×1, L1 ×1 |
| D2 condition | L4 ×4, L1 ×3, L3 ×1, L2 ×1 |
| D3 material | L4 ×2, L1 ×1 |
| D4 entity | L3 ×3, L4 ×2 |
| D5 pattern | Lε.enc ×1, Lε.obs ×1, L4 ×1 |

Every D role falls on two or more L layers, so D and L are not aliases. This supports branch (b): two stacks with a declared crosswalk.

> **Note, 2026-11-24 (added; the sentence above is unchanged).** "This supports branch (b)" goes too far. Spanning layers argues against (a). By itself it does not choose between (b) and (c), and D and L turn out to be positively correlated. See section 5.

Lε sits where a measured node becomes a recorded D5 attribute. P_HEX_CELL, the stored 0.97, is Lε.enc. P_BUILT_MEASURED, "no more than 18% Fejes Tóth cells", is Lε.obs of something bees built (L4).

### Flags for the owner

- **MATH_NOT_SUBSTRATE** (G2D_HALES, G3D_FEJES, G3D_DAUTER). `GROUNDING_LAYERS.md` puts geometric invariants and HEX at L0, so the tags follow the document. But a theorem holds whatever the conditions are, and it is not a substrate that can change. The same question applies to the five constants (golden_ratio, pi, …) where the audit and the tracer differed.
- **D0_HOLDS_A_MECHANISM** (F_FLOW). The trace files "wax flows when heated" as D0 law, but it depends on D2 conditions. D0 then holds both laws and mechanisms.
- **SPANS_LAYERS** (REGIME_HEX). The derived regime draws on L1 and L4 together.
- **NO_ASTRONOMICAL_LAYER** (E_SUN). The stack has no layer for the star, so the solar input is filed at L2, where it meets the planet.
- **Two placements of the bee.** `GROUNDING_LAYERS.md` files BE at L3, as an entity in its web. The node tags put colony physiology at L4. Both can hold, but they differ.
- **A third axis already exists.** 120 entity files carry `substrate_layer` (substrate_primary / language_primary / both). That is a coarser substrate-versus-language split, and it is not changed here.

### BIOSPHERE in the crosswalk (PROPOSED)

BIOSPHERE is a D4 entity at earth scale. Its state (temperature, water, oxygen, carbon, soil, season) acts as D2 conditions for every contained entity. Its layers are L3, bounded by L2, following its own scope: "life-sustaining zone, not planetary energy balance".

In the bee trace it would sit between E_SUN / E_SURFACE / L_SCATTER, which are outside it or at its edge, and the D4 forage nodes, which are inside it.

`OPEN_QUESTIONS.md` #3 has a dated note: the owner's "I liked your previous suggestions on mapping those" is read as permission to draft (b). The question stays open until the owner confirms the branch and where Lε sits.

---

## 5. Owner's answers, 2026-11-24

The owner answered the four decisions listed on PR #30: "1. Yes 2. Yes ( relational as in physics terms not social relational only) 3. Let's view evidence for and against 4. Yes".

### 1. Weekly workflow: adopted

- `.github/workflows/weekly_science_intake.yml` is a copy of `intake/weekly_science_intake.yml`. Only the header comment differs, and the body is byte-identical (checked). The copy in this folder is unchanged.
- `registry/DECLARED.json` has a new, eleventh amendment, "weekly intake (source pass, stage 0)". It is the draft from section 1, unchanged, plus one `adopted` line. It was appended; nothing earlier was edited.
- Scheduled runs start only once the file is on `main`. The pull-request step also needs the repository setting "Allow GitHub Actions to create and approve pull requests". Without it, that step fails loudly and the snapshots are still uploaded.
- The five seed queries stay PROPOSED. Restricting them to title and abstract (finding 1 of the live run) is still the owner's edit to make.

### 2. relational/ indexed, in the physical sense

- `schemas/relational.schema.json` (new). Its description puts the owner's clarification on record: relational means physical relations, that is couplings, flows, boundaries, dependencies and closures, and social relationship is one case of these.
- The schema has two shapes, a graph file (`{nodes, edges}`, no id) and a reference record (`id`, `name`, `ontology: relational`, `record_kind`, `status`, `sources`, `links`).
- `scripts/build_index.py` has one change. A graph file in `relational/` is validated against the graph shape and reported, rather than skipped as an entity without an id (finding N3). `synergies.json` (78 nodes, 219 edges) now validates and is not indexed as an entity. The general skip of files without an id is unchanged.
- BIOSPHERE is indexed. The build went from 123 entities and 557 relations to 124 and 561.
- BIOSPHERE's link to COUNCIL points at an id that is not indexed. It is appended to `registry/known_held_links.json` as KNOWN_HELD with its reason, beside the WOLF_PACK→COUNCIL entry. The record file is unchanged and the link is not retargeted to COUNCIL_PATTERN.
- COUNCIL_PATTERN's BIOSPHERE link moved from `held_links` into `links`. The record was rebuilt, still with 0 coordination-check failures and 0 names, and copied byte-for-byte to `ontology/social/`. `pattern_of COUNCIL` stays held.
- Instruments run after the change (OBSERVED):
  - `coordination_check` 0 failures, and its self-test 38/38;
  - fixtures 8/8 PASS;
  - `verify`, `audit` exit 0;
  - `reading_queue`, `source_plan`, `export_reference` `--check` all match;
  - `existence_check --selftest` 34/34;
  - `dependency_tree` exit 0, no load failures.
- `falsifier.py --entity BIOSPHERE` and `--entity COUNCIL_PATTERN` return `{"error": "No scoped attributes found…"}` with exit 0. The tool does not crash, but it does not fail loudly either. This adds two cases to OPEN_QUESTIONS #7, and the tool is not changed.

### 4. Per-node L tags: approved

- In `crosswalk/crosswalk_D_L.json`, each of the 28 nodes now carries `L_status: OWNER_APPROVED` and an `L_status_history` that keeps the PROPOSED entry.
- The four flags carry `flag_status: OPEN (owner decides)`.
- The record's own status stays PROPOSED, because the branch question (3) is still open.

### 3. Evidence for and against each branch

`crosswalk/crosswalk_evidence.py` computes the following from `crosswalk_D_L.json` (DERIVED; seed 20261124; deterministic, checked by re-running and comparing bytes). Each statistic is given twice, once with each node's first L tag and once with its last.

| Measure | First L tag | Last L tag | Under aliases (a) one would expect |
|---|---|---|---|
| D roles that span ≥ 2 L layers | 6 of 6 | 6 of 6 | 0 of 6 |
| Same-D pairs with no L in common | 29 | 29 | 0 |
| H(L) / H(L given D), bits | 2.288 / 0.940 | 2.364 / 1.354 | H(L given D) = 0 |
| H(D) / H(D given L), bits | 2.471 / 1.122 | 2.471 / 1.460 | H(D given L) = 0 |
| L predicted from D by majority rule | 17/28 | 15/28 | 28/28 |
| No-information baseline (most common L) | 12/28 (L4) | 9/28 (L4) | — |
| Spearman, D index vs L index (Lε excluded) | 0.502 (n 26, perm p 0.010) | 0.587 (n 27, perm p 0.002) | near 1 |

What the numbers say:

- **D and L are related, not independent.** The rank correlation is positive and clear. Both run from fundamental to emergent.
- **D and L are not the same.** Knowing D leaves about 1 to 1.4 bits of L undetermined, and knowing L leaves about 1.1 to 1.5 bits of D. On 28 nodes the plug-in entropy is biased low, so the true conditional entropies are, if anything, higher.

**(a) Aliases, one stack.**
- For:
  - the positive correlation;
  - both stacks are ordered from fundamental to emergent;
  - all six D0 nodes sit at L0 or L1 (four at L0);
  - the owner's "dependencies trace down to physics" is already what L says;
  - one tag per node is half the work.
- Against:
  - every D role spans two to four L layers;
  - 29 same-D pairs share no layer. For example, E_SUN (L2) and E_BODY_HEAT (L4) are both D1 energy, and C_MELT (L1) and C_BROOD_T (L4, L3) are both D2 condition;
  - Lε has no D counterpart;
  - aliasing would erase the distinctions the table measures.

**(b) Two stacks with a declared crosswalk.**
- For:
  - all of the evidence against (a);
  - D is relative to the subject of the trace. D4_MANUKA is an entity here, and in a mānuka trace it would be the subject. L belongs to the node whatever is traced (reasoning, PROPOSED);
  - D roles are functional, such as "supplies energy" and "holds a condition", which sits close to "every noun is a verb". L says where in the substrate a node sits (interpretive, PROPOSED);
  - the repository already keeps parallel axes, such as `substrate_layer`.
- Against:
  - D is the auditor's import, built before `docs/GROUNDING_LAYERS.md` was read (W08), and the protocol says the implementation serves the owner's architecture;
  - two tags per node double the tagging work and the room for disagreement;
  - the correlation means part of the second axis is redundant: 1.35 of 2.29 bits of L are shared with D (first-tag reading);
  - D's own categories are not clean. D0 holds both laws and a mechanism (F_FLOW).

**(c) Withdraw D, keep L.**
- For:
  - L is the owner's stack;
  - withdrawing D removes weld W08 at its source;
  - there is no duplicate axis to maintain.
- Against:
  - L cannot state role. REGIME_HEX is a derived condition and E_SUN is an energy input, but L files them only by substrate;
  - `reference/trace_check.py` is written in D (OBSERVED). It roots at the D5 node and counts paths ending at D0. Two of the six D0 nodes are L1 (F_FLOW, L_CONSERVE), so "the trace reaches physics" rewritten in L would have to read "ends at L0 or L1", which is a new rule and not a renaming.

**Limits.**
- This is one trace of 28 nodes.
- The nodes are not independent: the three geometry nodes share one reason, so the permutation p overstates the evidence.
- One audit wrote both the D tags (first) and the L tags (second). The owner approved the L tags, but no second reader has tagged them.
- None of this settles the branch. That is the owner's call, and OPEN_QUESTIONS #3 stays open.

**A test that could discriminate (PROPOSED, NOT_TESTED).**
- A second reader, blind to these tags, tags D and L on a different trace, for example a mānuka-honey trace with mānuka as the subject. Measure inter-reader agreement on each axis, and measure H(L given D) on the independent tags.
- If D determines L there, that favours (a).
- If readers agree on L but not on D, that favours (c).
- If both agree and H(L given D) stays well above 0, that favours (b).

---

## Hashes

| File | sha256 |
|---|---|
| `intake/weekly_intake.py` | `7d767f1f6974e8d6775a29ed693650e7ee3d66da5cb9959887ff3f82ea716db6` |
| `intake/intake_queries.json` | `2fca2a4068225146788428cb95cbe8820e3d4dfbc609e9a281c4635adee7aa5d` |
| `intake/weekly_science_intake.yml` | `068373e75c4cce9a96aee9d19a7ed65d093b816ee3fa52af71f220c1e8cbef2c` |
| `intake/live_2026-11-24/intake.json` | `bb756e6cffa50736346eb06b2c72350a58935745b024ef4540b5fb6fd9367051` |
| `intake/live_2026-11-24/snapshots/manifest.json` | `870069d0a93fbb54ff9d50a3067cce6d2a4b386c799ecffa7c610945149d4cda` |
| `biosphere/biosphere_candidates.py` | `6361892221bc39684bf408f974b3f7049bbc8b70fddaedd3ff7ad3646a6ba571` |
| `biosphere/biosphere_candidates_results.json` | `e69491deb76024754d8256fd84eb27f1f54cf56676297a7a21abeea5cfdc0105` |
| `crosswalk/build_crosswalk.py` | `66addc3fe59ad0ed92ba4ecb37fdc0d1c7455ef1f76c6b4da7653e22e9efacf1` |
| `crosswalk/crosswalk_D_L.json` | `8345635d5116d121aaf8a5982c9bdf6da64b838afc3f309eadd169de3c77fba6` |

> **Note, 2026-11-24 (added; the rows above are unchanged).** These hashes are from before the owner's answers. Files changed since are listed under "Hashes after the owner's answers".

### Hashes after the owner's answers (2026-11-24)

| File | sha256 |
|---|---|
| `crosswalk/build_crosswalk.py` | `d8a8ebfd19c836b85bfe5a690da2f110c9ea1f556b5af99c216bbe05e67888b2` |
| `crosswalk/crosswalk_D_L.json` | `460b27a3bcf4ab99e51c073e8082f942eea07989de03059bd1aaec507fd3eddc` |
| `crosswalk/crosswalk_evidence.py` | `fd70575129c0ccf3e31399ea6edbf9cbfe394cae787667a1b7cda20739ea6b54` |
| `crosswalk/crosswalk_evidence.json` | `d14aee730def03a56a10172109ed66d52f5e72a8ecff62ceebfe42a2fbb1f5ce` |
| `council/build_council_pattern.py` | `1e69015557d56ba4af1abc882e82719d649dde01371b131ee7d4cc2d2c18a4a5` |
| `council/council_pattern.json` | `508edef6d42e4a8679dcc68e8b1f7d8787cff657e4f374421f11abdbae3ead9f` |
| `.github/workflows/weekly_science_intake.yml` (repo root) | `4a1af37497caf4b4b602fb06556eedbaeb757e59a1070e274cd059294098e6e1` |
| `schemas/relational.schema.json` (repo root) | `24c01d9beaaee08084c6f0cb39ff02942dab4b2f512c0d35c65384f070869c28` |
| `scripts/build_index.py` (repo root) | `f66b5fd75d6d5f598f95336a22215cafe95c7267edb1a1106bea131d1a619000` |
| `registry/known_held_links.json` (repo root) | `78bb59faf37200001f0fc54d34bc860cd94b9e54dbc784cd0edd5b843f57729e` |
| `registry/DECLARED.json` (repo root) | `9d9c04dc175ee8686bfb1a20a8ce71d6611ffe7625a6ad7a4c489e8333b90bf1` |
| `ontology_index.json` (repo root) | `13f332a975cc2ced1772fa70941fee53675228e90c800a48b1356b6d24fc830e` |
