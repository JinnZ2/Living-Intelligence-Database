# Living Intelligence Database — Translation-Loss Ledger

Version: 0.4 (v0.4 additions 2026-11-24; earlier text kept unchanged)
Date: 2026-11-24
Status: PROPOSED. No repository files modified.
Baseline commit: `63d93c00951b14ed7352891747468c9b65cca146`
Companion: `LID_execution_results_2026-11-24.md` (instrument execution record)

## Purpose

This ledger records where the implementation replaced the source knowledge system's frame with the default frame of English-language code. It keeps three kinds of defect apart:

| Class | Meaning |
|---|---|
| BUG | Wrong under any ontology. Fix it directly. |
| SUBSTITUTION | The code's frame replaced the source frame. Fixing it changes what the code can represent. |
| UNTRANSLATED | The knowledge exists (in prose, in the owner's account, or in the data) but has no computational form yet. |
| FRAME_CONFLICT | Two parts of the repository encode different frames for the same construct. The owner decides. |

A ledger entry is not a verdict that the source frame is empirically correct. Preserving a frame and verifying its claims are separate operations.

## Source-frame statements used as reference

| ID | Statement | Source | Type |
|---|---|---|---|
| S1 | "Every noun is a verb in our language, in our culture. There is no static noun." | Owner statement, 2026-11-24 | Cultural source (owner) |
| S2 | "The relationships are, like, differential equations, and the whole thing acts like differential equations with a clear scope. If the scope is clearly defined, then you know what condition you're operating in." | Owner statement, 2026-11-24 | Cultural source (owner) |
| S3 | "A number by itself is a noun. It sits still." / "Efficiency is not a property a bee *has*; it is a pattern a bee *does*." | `evidence_is_a_verb.md` | Repository text |
| S4 | A claim is trusted when "it repeats across cycles … over seasons, generations, oscillations, winters." | `evidence_is_a_verb.md` | Repository text |
| S5 | "A claim depends on other entities; those entities must themselves be observed and verified." | `evidence_is_a_verb.md` | Repository text |
| S6 | Reciprocity is functional and can travel through a network: a return to the lake goes through the watershed, not necessarily as a direct exchange. | Owner account (prior session, recorded in attached transcript) | Cultural source (owner) |

## Ledger

### L01 — Attribute stored as a static number

- **Class:** SUBSTITUTION
- **Construct:** `attributes.<name>.value` in all entity files
- **Code frame:** An attribute is a property the entity has, recorded as one number.
- **Source frame:** S1, S3. An attribute is something the entity does, under conditions, over time.
- **Evidence (OBSERVED):** 225 of 228 scoped attributes hold a single `float`. Another 254 numeric values sit in `core_attributes` and `patterns` with no scope at all. For example, the bee's `0.97` appears three times (`core_attributes.efficiency_factor`, `patterns[0].efficiency_factor`, `attributes.hexagonal_cell_efficiency.value`), and only one of those copies is scoped.
- **Consequence:** The number is detached from the regime, timescale and cycle that produced it. The repository text names exactly this failure as a "noun pretending to be a verb" (S3).
- **Proposed form:** Treat the value as the output of a process under a declared regime: `{observed_output, regime_ref, timescale, cycle_basis}`. Keep `value` as-is for history.
- **Residual (UNTRANSLATED):** Where no state variable or rate is known, the "doing" has no computational form yet. Record it as `process_form: UNRESOLVED` rather than inventing one.

### L02 — Relationship stored as a static labelled arrow

- **Class:** SUBSTITUTION
- **Construct:** `links[]` → `ontology_index.json.relations`
- **Code frame:** A relationship is a fixed, directed, labelled edge. Its direction and existence are set when it is written.
- **Source frame:** S2. A relationship behaves like a differential equation. Direction, strength and whether it is active come out of evaluating it under conditions.
- **Evidence (OBSERVED):** 542 links have only `relation` and `target`. 13 have `rel`, `to` and `note`, and one has `status`. No link carries a condition, timescale, regime or functional form. Direction is strongly structured at authoring: 27.4% directed reachability, against 68.3–79.5% for degree-preserving rewired graphs.
- **Consequence:** Graph measurements (reachability, reciprocity, ablation) measure the storage format, not the relationships. The Stage 06 result, where reciprocating geometry can't be told apart from reciprocating random edges, is partly a symptom of this.
- **Proposed form:** A coupling record: `{source, target, relation, regimes:[{bounds, form|null}], couples:{source_state → target_rate}}`. Direction becomes an evaluated output (see the prototype below).
- **Residual:** The functional forms are UNKNOWN for every current link. The original edge list stays as the structural map.

### L03 — Scope written in prose, not as an operating regime

- **Class:** UNTRANSLATED
- **Construct:** `attributes.<name>.scope`
- **Code frame:** The instruments read scope as text, compared by word overlap.
- **Source frame:** S2. Scope defines the operating condition. Inside it, the relationship holds and can be evaluated. Outside it, the relationship doesn't apply.
- **Evidence (OBSERVED):** `definition`, `falsifiability` and `measurement_limits` are present in 228 of 228 attributes, so the knowledge is there. A machine-readable `condition` block is present in only 10 of 228 (4.4%), all of them in `social/`. `scope_checker.py` reads a `temporal_range` field that exists in 0 files.
- **Consequence:** No instrument can tell which regime a query is in. That is why instruments fall back to defaults (L04).
- **Proposed form:** A regime block per attribute: `{variables, bounds or predicates, timescale}`. The `condition_variables` from L06 are the raw material for its axes.
- **Residual:** Some constraints have no operational test yet, such as "pack is socially cohesive" or "terrain allows encirclement." Keep these as prose with `status: UNOPERATIONALIZED`. Don't force numeric bounds onto them.

### L04 — "Outside scope" and "unknown" turned into numbers

- **Class:** SUBSTITUTION
- **Construct:** `falsifier.py`, `scope_checker.py`, `audit.py`, `verify.py`
- **Code frame:** Closed world. Every query returns a value, and absence gets a default.
- **Source frame:** S2. Outside the scope, the equation doesn't apply. That is neither true nor false, and not a midpoint.
- **Evidence (OBSERVED, executed):**
  - 601 of 601 unmatched counterexamples were scored "survived."
  - Zero tests performed gives a resistance of 1.0.
  - An attribute with no confidence information gets a default of 0.5.
  - Empty scope text gets an overlap of 0.5.
  - An empty denominator gives `scoped_ratio` 1.0.
- **Consequence:** These instruments can't express the state that the source frame treats as essential.
- **Proposed form:** Outcome states `IN_REGIME`, `NOT_IN_SCOPE`, `CONDITION_UNKNOWN`, `UNRESOLVED_FORM` and `NOT_EXAMINED`, and no numeric output for the last four. The prototype below demonstrates this.
- **Residual:** None expected. This is the cleanest correction in the ledger.

### L05 — "Repeats across cycles" reduced to a keyword search

- **Class:** SUBSTITUTION, plus a data drift
- **Construct:** `scope.evidence.reproducibility`; `compute_relational_confidence()`
- **Code frame:** Recurrence is found by searching the reproducibility text for "cycle," "season," "generation" and similar words.
- **Source frame:** S4. Recurrence means the pattern held across counted cycles: seasons, generations, oscillations.
- **Evidence (OBSERVED):**
  - The reproducibility field holds grades: `high` (151), `medium` (50), `certain` (23), `not_assessed` (3), `low` (1).
  - None of the 228 entries contain a cycle term, so the cycle weight is always its 0.5 floor.
  - With that floor, the repository's own formula can produce at most 0.38.
  - Every stored `relational_confidence` is higher than the formula yields from the same evidence fields: mean difference +0.54 (range +0.26 to +0.65, n = 225).
- **Consequence:** The stored confidences weren't produced by the method the repository describes. The confidences have become nouns: asserted numbers.
- **Proposed form:** A cycle record: `{cycle_type, period, cycles_observed, span, source}`. Confidence is derived from it, and the stored numbers are kept as dated historical values.
- **Residual:** Who or what set the explicit confidences is UNKNOWN (C12 in the roadmap). Don't attribute them to a model without provenance.

- **Resolution (2026-11-24, owner):** Confidence means: what is the scope, what is the deviation within that scope, and how certain are you — "like the scientific method, variation plus or minus." So the stored 0–1 `relational_confidence` is neither of those quantities. It is reclassified as a historical value. See "Confidence as scoped deviation" below. Recurrence across cycles (S4) stays a separate measurement from deviation.

### L06 — "Dependencies" means two different things

- **Class:** FRAME_CONFLICT (owner decision)
- **Construct:** `scope.dependencies`
- **Frame A:** S5 (`evidence_is_a_verb.md`), plus `dependency_tree.py` and `audit.py`. A dependency is another entity.
- **Frame B:** The data. 646 of 651 entries are condition or state variables, such as `compression_ratio`, `dataset_complexity`, `architecture_depth` and `problem_dimensionality`. Only 5 resolve to an entity or a constant.
- **Evidence (OBSERVED):** The tracer silently drops the 646, while `audit.py` reports 651 as "missing."
- **Observation:** Under S2, the data's reading (variables the relationship depends on) is closer to the owner's frame than the code's reading. That is an inference, not a decision.
- **Proposed form:** Split the field into `entity_dependencies` and `condition_variables`, keep the original list unchanged, and add an adapter. `condition_variables` become regime axes for L03.
- **Owner decision needed:** Is S5 meant literally, or was "entities" a translation of something broader?

- **Resolution (2026-11-24, owner):** Dependencies are actual dependencies: trace "all the way down to physics, to the conditions, to the environment." What does this depend on? What energy? Which equations, as we currently understand Earth and the cosmos, make the bee exist? Neither Frame A (other entities) nor Frame B (condition variables) is complete. Each is one layer of a dependency stack, and the code reads only one layer. Class changes from FRAME_CONFLICT to SUBSTITUTION, because the code flattened a vertical chain into a single list. See "Dependency stack" below.

### L07 — Reciprocity given a single meaning

- **Class:** SUBSTITUTION
- **Construct:** Graph tests (Stages 04–06); the absence of any reciprocity field
- **Code frame:** Reciprocity means a reverse edge exists.
- **Source frame:** S6. Return can be functional, delayed, through other systems, and in a different form.
- **Evidence (OBSERVED):** Stage 06 could only measure structural reverse edges. No field records any other kind.
- **Proposed form:** `reciprocity: {structural, physical, functional}`, each with a regime and timescale. Functional reciprocity can name a pathway, for example `via: WATERSHED`.
- **Residual (UNTRANSLATED):** Network-level return over long timescales may not reduce to pairwise edges at all. It may need a flow or cycle representation over subgraphs.

### L08 — Entities filed by what they are, not what they do

- **Class:** SUBSTITUTION candidate (owner decision)
- **Construct:** The `ontology` field and the directory taxonomy
- **Code frame:** An entity is identified by its kind (animal, plant, crystal).
- **Source frame:** S1, and the functional definition of intelligence in the experiment protocol.
- **Evidence (OBSERVED):** GRANDMOTHER, STORYTELLER, INDIG_FIRE and SEED_KEEPER are filed as `animal`. Their own descriptions call them a "transmission intelligence," a "human practice" and "multi-generational … landscape management knowledge."
- **Proposed form:** Add a functional or process classification alongside the kind. Don't move or rename anything.
- **Owner decision needed:** Is filing these under `animal` intended, as in humans being animals, or did the taxonomy force a practice into a kingdom bin?

- **Resolution (2026-11-24, owner):** Intended. "We consider ourselves animals, part of the creature, other biological beings. We do not need to separate ourselves above or below or put status on us." **L08 is withdrawn as a defect.**
- **Correction to this ledger:** The v0.1 entry assumed that human practices belong in a separate category. That assumption came from the auditing instrument (this model), not from the repository. It is recorded under "Assumptions introduced by the auditor."

### L09 — Stability recorded as a fixed trait

- **Class:** PARTIAL translation
- **Construct:** `entropy_profile.stability`, `entropy_profile.adaptability` (120 entities)
- **Code frame:** A fixed qualitative trait (`high`, `medium` or `low`).
- **Source frame:** Under S2, stability is a property of a state within a regime and depends on the timescale.
- **Proposed form:** Stability per regime and timescale. Low priority. Keep the current values as defaults labelled `regime: unspecified`.

### L10 — Audit coverage gap

- **Class:** BUG
- **Construct:** `audit.py`
- **Evidence (OBSERVED):** The audit reports 0 unscoped numerics and `scoped_ratio` 1.0, while 254 numeric values in `core_attributes` and `patterns` are unscoped and unexamined.
- **Fix:** Walk every numeric leaf, or declare which fields are excluded and why.

### L11–L15 — Plain bugs (from the execution record)

| ID | Defect | Evidence |
|---|---|---|
| L11 | `verify.py`: the claim function receives no entity, and an unknown claim defaults to True | 228 identical calls → 1.0 |
| L12 | `build_index.py`: exit code 0 with a broken link; the index is written before error exit | Rebuild run |
| L13 | COUNCIL sits in `validation/example/`, outside the indexed tree | WOLF_PACK edge unresolved |
| L14 | `ontology/relational/` skipped; the `OC → EL` edge exists only there | Build log |
| L15 | Manifest drift: 4 IDs missing, 1 obsolete, `social` and `energy_exchange` missing, co-creators incomplete | Stage 01 |

## Dual-vocabulary map (PROPOSED)

| Source term | Computational term | Classification |
|---|---|---|
| Entity (verb: what it does) | Process with state x(t) and evolution dx/dt = F(x, e, p, t) | PARTIAL_TRANSLATION. The process form is unknown for most entities. |
| Relationship | Coupling term: the contribution of one process's state to another's rate | PARTIAL_TRANSLATION |
| Scope | Domain of validity: the operating regime (a region in condition space where F is defined) | Candidate EQUIVALENT_WITHIN_SCOPE (owner to confirm) |
| Outside scope | F not defined there. The result is "not applicable," not zero or 0.5. | Candidate EQUIVALENT_WITHIN_SCOPE |
| Direction of a relationship | Sign of the coupling term evaluated at the current state and conditions | PARTIAL_TRANSLATION |
| Repeats across cycles | Recurrence: the pattern observed over N periods (periodic or limit-cycle behavior) | PARTIAL_TRANSLATION |
| Reciprocity (functional, via the network) | Flow or cycle over a subgraph, possibly time-lagged | UNTRANSLATED. No current computational form. |
| Glyph as reasoning instrument | Condition-dependent dynamical system | PARTIAL_TRANSLATION, per roadmap Stage 07. The residual has not been characterized. |

## Prototype: scope as operating regime (PROPOSED, synthetic)

`regime_eval.py` (standard library only; results in `regime_eval_results.json`) applies the L02, L03 and L04 forms to a synthetic coupling. Its sign reverses at e = 0.5, and scope ends at e = 1.0. All six known-answer cases pass (OBSERVED):

| Case | Outcome |
|---|---|
| e = 0.2 | IN_REGIME, rate +0.6, direction source → target |
| e = 0.9 | IN_REGIME, rate −0.8, direction target → source |
| e = 0.5 | IN_REGIME, rate 0, inactive |
| e = 1.7 | NOT_IN_SCOPE (no number returned) |
| e not supplied | CONDITION_UNKNOWN, missing `e` |
| Regime declared with no form | UNRESOLVED_FORM (no form invented) |

In the drift run, the environment ramps from 0 to 1.6. The system enters `low_e` at t = 0, crosses into `high_e` at t = 1.26, and leaves scope at t = 2.51, after which evaluation stops. The final y = 0 is the expected analytic result, because the fixture's two regimes are symmetric.

What this shows: the same relationship can drive, reverse and switch off depending only on the conditions, and outside the declared scope the code returns a state instead of a value. What it doesn't show: that any repository relationship has this form. No repository equation was supplied or inferred.

## Owner decisions needed (v0.1 — resolved 2026-11-24 except item 4)

1. **L06:** Does "dependencies" mean entities, condition variables, or both?
2. **L08:** Is the `animal` filing of the practice entities intended?
3. **L05:** Should the stored confidences be kept as dated historical values and derived anew from cycle records, or kept as primary?
4. **Dual-vocabulary map:** Is "scope = domain of validity / operating regime" equivalent within scope, or does it leave a residual?

## Not tested

- Whether any real relationship has a known functional form (Stage 07, T07.6).
- Parsing the 10 existing `condition` blocks into regime bounds. Some are numeric ("pack size 4–8", "20–30 °C"), and some are not operationalized.
- Whether the dual vocabulary changes how other AI instruments interpret the material (Stage 10, condition D).

---

# v0.2 additions (2026-11-24)

## Dependency stack (PROPOSED, from the L06 resolution)

What the owner described is a vertical chain: pattern → what it is made of → the conditions it needs → the energy it runs on → the physical law that governs it. The code holds a flat list, and in practice reads only the top layer.

| Layer | Question it answers | Example kinds | Present in data now (OBSERVED) |
|---|---|---|---|
| D5 Pattern | What is being done? | The attribute itself | 228 scoped attributes |
| D4 Entity | Which other beings or processes must exist? | Flowers, colony, mycorrhizal partner | 0 dependencies point to an entity |
| D3 Substrate / material | What is it made of, and where does that come from? | Wax, calcium carbonate, lattice | Mixed into the 567 dependency strings, untyped |
| D2 Environment / boundary conditions | Under what conditions does it hold? | Temperature range, pressure, gravity, water | 49 of 567 distinct dependency strings name temperature, pressure, solar, water, flux or similar |
| D1 Energy source and flow | What energy runs it, and from where? | Sunlight → chemical energy; thermal gradient | Entities exist (THERMAL, PRESSURE, GRAV, EM_FIELD, FLUX, SOLAR_WIND, CYANO, LEAF_TESS), but 0 dependencies point to them. There is no entity for solar radiation as an energy source. |
| D0 Law / equation / constant | Which equation governs it? | Energy conservation, Carnot bound, isoperimetric theorem, c, h, k_B | Rosetta Stone has 13 constants. 5 dependencies reach them, all mathematical (golden_ratio ×3, pi ×2). **0 attributes trace to a physical law.** |

### Proposed dependency record

```json
{
  "target": "THERMAL",
  "layer": "D1_energy",
  "role": "energy_source | material | boundary_condition | governing_law | entity",
  "required_in_regime": "regime_id or 'all'",
  "equation_ref": "optional pointer to a D0 record",
  "status": "TRACED | PROPOSED | UNKNOWN",
  "source": "citation or 'owner account' or 'not sourced'"
}
```

The existing `dependencies` list is kept unchanged. The new records sit beside it. A string from the old list can be promoted into a typed record only when someone has examined it.

### Proposed measurement: trace completeness

For each attribute, check whether at least one path reaches D0, and which layers it skips. Report the result as a profile, for example `D5 → D2 → (gap D1) → D0`, not as a score. Current state (DERIVED): no attribute reaches a physical law. The five that reach anything at D0 reach mathematical constants by skipping every layer between.

### Gaps this exposes

- There is no entity for incoming solar radiation, even though the database describes a living Earth that runs on it. SOLAR_WIND is a plasma flow, not the light that drives photosynthesis. CYANO and LEAF_TESS describe solar energy conversion, but nothing names the source they convert.
- The Rosetta Stone lists universal constants only. Earth-system quantities, such as incoming solar flux or surface gravity, would be the natural D1–D2 floor for terrestrial entities. Values must be sourced, not recalled.

## Worked trace: BE `hexagonal_cell_efficiency` (current record, examined)

| Layer | Current record | Examination |
|---|---|---|
| D5 | value 0.97, "ratio of honey volume stored per unit wax mass … compared to the next-best regular tessellation" | — |
| D0 claimed | Hales honeycomb conjecture; dependencies `golden_ratio`, `pi` | **Citation mismatch (OBSERVED):** The record cites "Hales (1999) … Discrete & Computational Geometry 36:5-69." The published paper is [Discrete Comput Geom 25, 1–22 (2001)](https://link.springer.com/article/10.1007/s004540010071); a 1999 [arXiv preprint](https://arxiv.org/abs/math/9906042) exists. |
| D0 scope | — | **Scope mismatch (DERIVED):** Hales proves that "any partition of the plane into regions of equal area has perimeter at least that of the regular hexagonal honeycomb tiling" ([Springer abstract](https://link.springer.com/article/10.1007/s004540010071)). That is a two-dimensional perimeter result. The attribute claims a three-dimensional storage-per-wax-mass ratio. Whether the theorem transfers to real 3D cells is UNCHECKED. |
| D0 dependency | `golden_ratio` | **UNCHECKED:** The theorem's statement doesn't involve the golden ratio. The dependency may be a carry-over from another pattern. |
| D1–D4 | Not recorded | Energy (wax is secreted from sugar the bees collect), material (wax properties), conditions (comb temperature) and entities (flowers) are all absent. Each must be sourced before it is entered. |

This one record shows the general shape. The pattern is real and the mathematics behind it exists, but the chain between them is missing, and the one link that is recorded points at a neighbouring result rather than the exact one.

## Confidence as scoped deviation (PROPOSED, from the L05 resolution)

The owner's definition (scope, deviation within scope, certainty) corresponds closely to the established metrology form. The Guide to the Expression of Uncertainty in Measurement writes a result as Y = y ± U: y is the best estimate, and y − U to y + U is an interval expected to contain a large fraction of the values reasonably attributable to the quantity ([BIPM, JCGM 100:2008](https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf)). The interval comes with a stated coverage probability, or level of confidence ([NIST coverage-interval review](https://nvlpubs.nist.gov/nistpubs/jres/126/jres.126.004.pdf)).

| Owner term | Metrology term | Proposed field |
|---|---|---|
| Scope | Measurand definition and conditions of measurement | `scope_ref` → the regime block (L03) |
| Deviation | Standard uncertainty u, or expanded uncertainty U | `deviation: {value, kind: standard / expanded / range / percent, asymmetric?}` |
| How certain | Coverage probability or level of confidence | `certainty: {coverage, basis}` |
| (separate) Repeats across cycles | Repeatability or reproducibility across occasions | `recurrence: {cycle_type, cycles_observed, span}` |

Current state (OBSERVED): 0 of 228 attributes have a deviation field. In 92 of 228, the `measurement_limits` prose already contains a deviation or range expression: a numeric range (55), a percentage (26), "varies" (23), and an explicit ± (6), for example BE "Varies ±0.01 with cell aspect ratio" and SPIRAL "±5–10% deviation." So 40% of the confidence information exists and needs extracting, not inventing. The other 60% are UNKNOWN until examined.

Candidate classification for the dual-vocabulary map: EQUIVALENT_WITHIN_SCOPE, pending your check. One possible residual: metrology treats certainty as probability over repeated measurement, while the owner's frame may include certainty earned across generations of observation. If so, `certainty.basis` must be able to say so.

## Vocabulary map — suggestions for the ongoing experiment

These are offered as test candidates. None has been applied.

1. **Entity ↔ dissipative structure (living systems).** Prigogine's dissipative structures are ordered states maintained by continuous exchanges of energy and matter with the environment, and they disappear if that exchange stops ([UT Physics History](https://www.utphysicshistory.net/IlyaPrigogine.html); [Prigogine Nobel lecture](https://www.nobelprize.org/uploads/2018/06/prigogine-lecture.pdf)). This is close to "there is no static noun" in physics' own words: a bee or a whirlpool exists only as long as its energy flow continues. It also ties directly to D1, because every dissipative structure has an energy-source dependency by definition. Candidate: EQUIVALENT_WITHIN_SCOPE for living and weather systems.
2. **Entity ↔ process with a characteristic timescale (all domains).** The dissipative-structure term fits crystals poorly, because a quartz lattice persists near equilibrium without throughput. A translation that covers every domain: something looks like a noun when it is observed over a window much shorter than its own characteristic time τ. Quartz is a verb with a very long τ. Add `characteristic_timescale` to every entity. Then "static" stops being a property of the thing and becomes a relation between the thing and the observer's window. This is testable: flag every attribute whose evidence window is shorter than the entity's τ.
3. **Dependency ↔ existence conditions with an energy budget.** Use the D0–D5 stack above, and give each layer its physics name: governing equation, constants, energy source, boundary conditions, material inputs, coupled processes.
4. **Confidence ↔ y ± U with a coverage probability, within scope.** As above. Keep recurrence as its own field.
5. **A test for every row.** Translate in both directions. Give the computational term to a fresh instrument and see whether it reconstructs the owner's meaning. Whatever fails to come back is the residual, and it is recorded rather than smoothed over.

## Assumptions introduced by the auditor

| Entry | Assumption | Source of the assumption | Status |
|---|---|---|---|
| L08 (v0.1) | Human practices may need a category separate from animals | This model's default frame, not the repository | Withdrawn 2026-11-24 after owner correction |
| L06 (v0.1) | Dependencies must be either entities or conditions | This model's binary framing | Superseded by the layered stack |

## Still open

- Vocabulary map: in progress (owner). The suggestions above are candidates.
- A sourced D1–D4 trace for one entity end to end, as a known-answer reference record.
- Extracting the 92 prose deviations into fields, with the original prose preserved.
- Characteristic timescales: needed for every entity, unsourced so far.

# v0.3 additions (2026-11-24)

## L05 second resolution: cycles (owner, 2026-11-24)

- **Owner statement:** A cycle is a cycle of whatever is in context. It is a differential equation. Every cycle has to be named: sleep, circadian, seasonal, compute. There are cycles within cycles. AI compute cycles run on a much faster gradient than human or fruit-fly cycles, and they are still cycles.
- **Consequence for L05 (DERIVED):** The keyword search for "cycle" can't be repaired by adding words, because a bare word doesn't say which cycle is meant. The proposed `recurrence` field becomes a reference into a named cycle registry.
- **Proposed cycle record:** `{id, name, kind, period_s, period_text, context, parent, source, status}`. `kind` keeps oscillation, developmental window, production cycle and a transient inside a cycle apart without ranking them. `parent` encodes nesting.
- **Physics name for "cycles within cycles" (PROPOSED, EQUIVALENT_WITHIN_SCOPE pending your check):** a multiple-timescale system. Seen from a fast cycle, the phase of a slower cycle acts as a fixed parameter. That phase belongs to the fast cycle's operating regime (L03). Seen from a slow cycle, a fast cycle shows up only through its average. The ratio of periods tells you how well that separation holds. So naming the cycle and naming the scope are the same act.
- **Worked example (OBSERVED in sources):** The wax-gland age window governs which workers make wax. In the swarm regime (a phase of the colony's annual cycle), bees of all ages build comb ([FAO](https://www.fao.org/4/i0842e/i0842e12.pdf)). A phase of the slower cycle changed the rule for the faster one.
- **AI cycles:** These use the same schema in their own domain: clock cycle, forward pass, token step, training step, session. No periods are entered, because none have been sourced here. Each instrument should declare its own periods (NOT_TESTED).

## Reference trace built

Files: `reference/reference_trace_BE_hex.json`, `reference/trace_check.py`, `reference/trace_check_results.json`, and the narrative `LID_reference_trace_BE_2026-11-24.md`.

- 18 nodes across D0–D5. 14 are TRACED, 1 DERIVED, 1 CONTESTED, 1 PROPOSED, and 1 is the current record, kept as RECORDED_UNVERIFIED.
- 13 of 14 dependency paths end at a D0 governing result. One path ends at a boundary condition, wall thickness, which is a legitimate terminal.
- 6 paths pass through a PROPOSED node: which repository plant entity stands for "flowers" is still an owner decision.
- 9 named cycles span about 11 orders of magnitude in period, from wingbeat (about 4 ms) to the solar cycle (about 11 years). The worker adult-life period is UNKNOWN, and the circadian cycle is unsourced.

## Proposed dated corrections for `ontology/animal/bee.json` (not applied)

These are notes to sit beside the existing claims. Nothing is overwritten or removed.

1. **Citation (2026-11-24):** The cited "Discrete & Computational Geometry 36:5-69 (1999)" does not match. The published reference is DCG 25:1–22 (2001), and arXiv math/9906042 (1999) is the preprint.
2. **Scope (2026-11-24):** Hales covers 2D perimeter. The 3D cell base is not surface-minimizing in the idealized case: Fejes Tóth (1964) gives a saving of less than 0.35% of the opening area. Whether the base is optimal depends on wall thickness. The value 0.97 is RECORDED_UNVERIFIED, since no source for it has been found.
3. **Dependency `golden_ratio` (2026-11-24):** UNCHECKED. No source in the trace uses it.
4. **Formation mechanism (2026-11-24):** CONTESTED. Three accounts are preserved side by side: surface-tension wax flow, thermal expansion, and self-organized angular redistribution.

## Still open (v0.3)

- Characteristic timescales for every entity. Cycle periods now give part of this.
- Which repository plant entities stand for nectar sources.
- Whether a transient, such as the circle-to-hexagon change, counts as a cycle in its own right or as a phase inside one. This is the owner's call.
- AI compute-cycle periods. Each instrument should declare its own.

# v0.4 additions (2026-11-24)

- **Sunlight added in two roles (OBSERVED in sources):** energy (irradiance → photosynthesis → nectar) and information (sun compass, time-compensated by the circadian clock). Proposed vocabulary row: one entity can sit under one dependency with two roles, `energy_source` and `information_source`. The current dependency field can't express this (L06).
- **Environment differential (PROPOSED form):** For each regime pair, the record lists invariant nodes, variant nodes, nodes with unknown dependence, and signed sensitivities, each with its own scope. Mānuka vs wildflower diverge at the chemistry layer, not the energy or geometry layers.
- **New L03 evidence:** A sensitivity's sign can depend on genotype (mānuka DHA:sugar vs temperature). So scope has to include the identity of the system, not only external conditions.
- **New L05/cycle evidence:** The mānuka flowering window sits about 6.5× inside the year. That is the weakest separation in the ladder, and the slow cycle's phase decides whether the regime exists at all.
- **Binding test:** 9 repository dependency strings were checked against `bee.json`. All 9 exist; 6 bind to sourced nodes, 3 are UNKNOWN or UNCHECKED. No repository files were modified.

## v0.5 note (2026-11-24): welds and the common denominator

Added beside v0.4 without changing it. The ledger's double-meaning rows (two 0.97 attributes with different definitions, two 0.89 waggle attributes with different radii, "cycle", "confidence", "dependency", the Sun in two roles) are now recorded as welds W01–W10 in `LID_weld_register_and_common_denominator_2026-11-24.md`. The register is built with the owner's method-layer `de_weld.py` at commit `4636166`.

- Instrument fit (OBSERVED): de_weld counts the OTHER axis as evaluative. Named descriptive sub-quantities are therefore encoded on DESCRIPTIVE, and the OTHER encoding is kept as a control.
- New weld found while tracing energy: the USDA honey energy value is human metabolizable energy, used as a PROXY for bee-usable energy (W07).
- New weld found in this audit's own work: the D0–D5 stack was built without first checking the repository's `docs/GROUNDING_LAYERS.md` (L0–L5 + Lε). The mapping is left to the owner (W08).
- Common denominator (PROPOSED): a rate together with its named cycle, carried as dimension, interval, time basis, scope and source. Units alone were not enough. The time basis is where the combinations failed.
