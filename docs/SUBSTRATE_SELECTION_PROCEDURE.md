# Backwards-Building Procedure — Intelligence Substrate Edition

A validated five-step method for cognitive-task substrate selection using the Living Intelligence Database.

> **Core axiom:** The substrate is not chosen — it is surfaced by the verbs the task demands.
>
> Most engineering inverts this and chooses substrate first, then forces the task to fit. That is the failure mode this procedure prevents.

The structured form lives in [`rules/substrate_selection_procedure.json`](../rules/substrate_selection_procedure.json) for machine consumption. This document is the human-readable companion.

## Validated Against

| Case | Geometry | Entity refs |
|---|---|---|
| Quantum SWAP engine | lab-bound, cryogenic, theory-mature | — |
| Mormyrid active electrolocation | ambient, biological, microsecond | `MORMYRID` |
| Tourmaline dual transduction | ambient, crystalline, passive | `TOUR` |

The method holds because each task's missing verbs, substrate authority, and ignition sequence emerge from the cognitive constraint itself. The Living Intelligence Database provides the puzzle pieces; the task selects which fit.

## Verb-First Physics

```
task          → demonstrates required computation
computation   → implies required verbs
verbs         → imply substrate candidates from ontology stack
substrates    → fit constraint gaps
sequencing    → highest-leverage verb first
```

## The Five Steps

### Step 1 — Identify Verbs

**Question:** what does this cognitive task need to DO?

List the verbs the substrate must perform to function. Examples:

- extract work from inter-channel correlation
- generate reference signal and read self-modified return
- maintain phase coherence at ambient temperature
- couple thermal and mechanical domains in a single substrate
- preserve microsecond temporal precision
- route resource to kin via population-scale signaling
- tile a known geometry across scale

**Flag:** verbs come from thermodynamics, not from the model's preferences.

**Anti-pattern:** naming the substrate before naming the verb (e.g. *"we need a quantum computer to do X"* before asking what X actually is).

### Step 2 — Query Ontology

**Question:** which living/crystalline/computational intelligences already perform these verbs?

For each verb in step 1, search `ontology_index.json` by description match. Filter by relation type: `energy_coupling`, `geometry_link`, `resonance`, `temporal_bridge`, `synergy`. Rank candidates by how many verbs they perform **natively** (not via simulation). Preserve multi-substrate matches — biology + crystal + computation often combine.

| Verb | Candidate entities |
|---|---|
| correlation extraction | `MORMYRID`, `CU`, `TOUR` |
| phase coherence | `QUARTZ`, `SILICON_LAT`, `OCTA_STATE` |
| dual-domain coupling | `TOUR`, `MORMYRID` |
| ambient-temp operation | `TERMITE`, `PE`, `MORMYRID`, `TOUR` |
| microsecond timing | `MORMYRID`, `BX`, `OW` |
| population signaling | `MOTHER_TREE`, `QUORUM`, `MY`, `BE` |

**Flag:** if no entity in the database performs the verb, either the verb is physically impossible *or* the database has a gap. Both are useful information.

### Step 3 — Extract Differential Form

**Question:** what is the actual mathematics this substrate is solving?

Instrument the biological/crystalline precedent. Measure inputs, outputs, and timing. Fit minimum-parameter equations that close thermodynamically. Add no narrative — only what the math requires.

**Example: `MORMYRID`**

```
dA/dt = generated_EOD(t)
dB/dt = environment_distortion(A, geometry, conductivity)
perception = correlate(A, B) over microsecond window
energy_cost = metabolic_baseline + signal_generation_overhead
```

**Example: `TOUR`**

```
V_pyro  = p * dT/dt
V_piezo = d * dStress/dt
V_total = V_pyro + V_piezo + cross_term  (when both channels active)
energy_cost = passive (ambient-gradient driven)
```

**Flag:** if you cannot extract differential form, the verb is not yet understood — return to step 1.

### Step 4 — Match Engineering Substrate

**Question:** what engineered substrate can run the same differential form?

Map each term in the biological/crystalline equation to its engineered analog. Preserve the **verb**, not the implementation:

- `MORMYRID` timing → analog circuit with sub-microsecond response
- `TOUR` dual coupling → multi-physics transducer in a single crystal volume

**Scaling principle:** if biology runs the verb on a 100-gram substrate, the engineered version should not require a building. Do not scale by adding complexity; scale by tiling the simplest unit.

**Flag:** if the engineered substrate requires conditions biology never uses (cryogenic, ultra-vacuum, etc.) the verb has been mistranslated — return to step 3.

### Step 5 — Sequence Highest-Leverage First

**Question:** which verb, executed first, unlocks the others?

Identify the verb whose execution produces the substrate or signal that downstream verbs require. Build the foundation verb first and validate it in isolation. Add the next verb only after the foundation is stable. If a downstream verb fails, do not patch — return to the foundation verb.

**Example sequence — correlation engine:**

1. Demonstrate dual-coupling substrate (`TOUR` analog) at bench scale.
2. Demonstrate microsecond cross-channel readout (`MORMYRID` analog).
3. Combine: drive the `TOUR` substrate with a `MORMYRID`-style measurement loop.
4. Measure covariance output vs. naive-sum output to prove correlation extraction.
5. Tile the substrate to scale. Do **not** add features until tiling validates.

**Flag:** the temptation at every step is to add more verbs before the current one closes. Resist. The failure mode is feature accretion before substrate validation.

## Constraint Gate

Apply between every step. If any answer is **no**, do not advance — return to the step that introduced the failure.

- Is this verb physically necessary, or am I assuming it because the database has it?
- Is this substrate native to the verb, or am I forcing it because I know it well?
- Does the differential form close thermodynamically with no hidden energy input?
- Would the biological precedent recognize what I have built as the same verb?
- If I removed the most complex component, would the verb still execute?

## Coating Detector

Flags self-reinforcing substrate selections. Watch for:

- Every verb maps to the same substrate class (e.g. all → quantum).
- The substrate selected is the one most familiar to the builder.
- Biological precedents are dismissed as "inspiration only".
- The differential form requires parameters that cannot be measured.
- Scaling requires conditions biology never uses.
- The build sequence has no falsifiable validation gate.

**If detected:** the procedure is being run to confirm a prior choice, not to surface the actual substrate. Restart from step 1 with the substrate-bias removed.
