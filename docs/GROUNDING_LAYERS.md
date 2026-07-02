# Grounding Layers: L0–L5 + Lε

Adapted from the L0-L5 Grounding Inspector Simulation Framework  
(JinnZ2/Resilient-AI-Human-Collaboration-) and expanded for the  
Living Intelligence Database.

---

## The Core Principle

**All layers constrain the ones above.**

An AI cannot propose actions that violate L0–L4 substrate reality, even  
if humans agree at L5. Grounding is not authoritarian — it is liberating.  
Once physical/biological/ecological constraints are explicit, creative  
slack can flourish within them.

---

## Layer Stack

```
L5   Social / Cultural constructs
     ───────────────────────────────────────
Lε   Epistemic Membrane          ← THE CRITICAL TRANSITION
     ───────────────────────────────────────
L4   Human & Biological Biomechanics
L3   Ecological Systems
L2   Planetary Constraints
L1   Thermodynamics
L0   Classical Physics
```

Layers L0–L4 are **substrate layers** — governed by physical law.  
Layer L5 is the **relational layer** — governed by social consensus.  
**Lε sits between them** and is where most AI errors occur.

---

## Layer Definitions

### L0 — Classical Physics
Gravity, momentum, conservation of mass and charge, geometric invariants.  
**Entities here:** `TORUS`, `SPIRAL`, `FRACTAL`, `HEX` — geometric forms  
that exist independently of any observer.

### L1 — Thermodynamics
Energy conservation, entropy generation (always ≥ 0), Carnot efficiency  
limits, battery depletion curves.  
**Entities here:** `FLUX`, `MAGNETIC_FIELD`, `PLASMA_FIELD`, `LIGHTNING` —  
energy forms with definite thermodynamic constraints.

### L2 — Planetary Constraints
Water cycles, mineral depletion rates, carbon sink capacity, albedo bounds,  
thermal radiation limits. "Magical resources" fail here.  
**Entities here:** `QUARTZ`, `CRYSTAL_LATTICE` — mineral structures embedded  
in planetary-scale geological processes.

### L3 — Ecological Systems
Kleiber's law (metabolism ∝ mass^0.75), 10% trophic energy transfer,  
carrying capacity, allometric scaling.  
**Entities here:** `BE` (bee), `OC` (octopus), `WOLF_PACK`, `ANT`,  
`MYCELIUM`, `ROOT_NETWORK` — organisms embedded in ecological webs.

### L4 — Biological Biomechanics
Joint angle limits, reaction time minimums (~200ms), thermal tolerance  
(43°C skin contact threshold), metabolic power (~150W sustained),  
physical memory span constraints.  
**Entities here:** `WHALE`, `INDIG_FIRE`, `MOTHER_TREE`, `GRANDMOTHER` —  
intelligences where the body or physical substrate is the primary carrier.

---

## Lε — The Epistemic Membrane

> "The Lε layer is where observation becomes claim."

Lε sits between measurable substrate (L0–L4) and interpreted relational  
knowledge (L5). Every numeric attribute in this database **crosses Lε**.  
How cleanly it crosses determines the claim's epistemic integrity.

The original Grounding Inspector modeled Lε as measurement noise — the  
gap between a sensor and the truth. In this database, Lε is expanded into  
a **four-sublayer epistemic chain**:

```
Lε.obs → Lε.pat → Lε.xfr → Lε.enc
```

### Lε.obs — Observation Quality
*What was actually measured and under what conditions?*

Scored by: `measurement_limits`, `reproducibility`, instrument resolution.

A claim with no `measurement_limits` documentation has a weak Lε.obs —  
the observation window is undefined.

**Common failure:** Using a lab result (controlled corridor, 25°C) to  
make a claim about field conditions (open terrain, variable temperature).

### Lε.pat — Pattern Recognition Quality  
*How reliably does the observation repeat across cycles?*

Scored by: `evidence_type`, `reproducibility`, `evidence.source` age and  
sample size.

| Evidence Type | Lε.pat Base Score |
|---|---|
| `cyclic_observation` | 0.90 |
| `lab_measurement` | 0.95 |
| `field_observation` | 0.80 |
| `cross_domain_rhyme` | 0.65 |
| `theoretical` | 0.55 |
| `anecdotal` | 0.40 |

**Common failure:** Treating a single dramatic event (one wolf pack hunt,  
one ant colony collapse) as a representative pattern.

### Lε.xfr — Cross-Domain Transfer Validity
*When we say this pattern "rhymes" with another domain, how valid is the transfer?*

Scored by: `cross_domain_count`, `cross_domain_examples` diversity,  
`relational_confidence`.

A `cross_domain_count` of 1 means the pattern has only been observed in  
one domain. The rhyme is speculative. Count ≥ 3 across independent domains  
indicates a genuine structural pattern.

**Common failure:** Rhyming wolf pack coordination with corporate teams  
without accounting for the 4-million-year evolutionary constraint that  
grounds the wolf pattern.

### Lε.enc — Encoding Fidelity
*How accurately does the JSON entry capture the actual claim?*

Scored by: `falsifiability` presence and quality, `definition` precision,  
`dependencies` completeness.

A claim with no `falsifiability` cannot be tested. A claim with no  
`dependencies` cannot be grounded to lower layers.

**Common failure:** Writing `"hunt_success_rate": 0.82` as a bare number  
without scope — this is a **noun-pretender**: a static value claiming  
confidence it hasn't earned.

---

## Lε Failure Modes (Expanded)

These are the ways an AI can corrupt the L4→L5 transition:

1. **False precision** — Reporting `relational_confidence: 0.94` when  
   evidence is anecdotal or single-domain.

2. **Scope collapse** — Applying lab measurements to field conditions  
   without noting the transfer limit.

3. **Cross-domain overreach** — Treating `cross_domain_rhyme` evidence  
   as causal rather than analogical.

4. **Missing falsifiability** — Claims that can't be tested can't be  
   trusted at L5.

5. **Dependency blindness** — High confidence scores that ignore listed  
   `dependencies` (e.g., claiming `social_cohesion` is high while  
   `territory_stability` dependency is unverified).

6. **Nostalgia-frame substitution** (from `training/architecture_mismatch.md`)  
   — Representing substrate-primary knowledge (L3/L4) through aesthetic  
   metaphor instead of its actual functional structure.

7. **Confidence inflation** — When stated `relational_confidence` exceeds  
   the Lε score computed from the evidence block.

---

## L5 — Social / Cultural Constructs

Human agreements, governance systems, consensus protocols, language  
structures, cultural memory.  
**Entities here:** `COUNCIL`, `ECHO`, `FOLD`, and most `ai/` entities —  
patterns that exist through collective agreement.

Entities in this layer can be modified by human decision. Entities in  
L0–L4 cannot.

**Critical distinction:** An AI that proposes changes to L5 constructs  
as though they were L3 facts (or vice versa) has lost its grounding layer.

---

## Mapping to This Database

### Ontology type → Primary L-layer

| Ontology | Primary Layer | Notes |
|---|---|---|
| `shape` | L0–L2 | Geometric invariants, physical forms |
| `crystal` | L1–L2 | Thermodynamic structure, planetary material |
| `energy` | L1 | Field dynamics, thermodynamic conversion |
| `plasma` | L1–L2 | High-entropy field dynamics |
| `plant` | L3 | Ecological systems, slow-cycle |
| `animal` | L3–L4 | Ecological + biomechanical |
| `social` | L4–Lε | Boundary zone: embodied social intelligence |
| `temporal` | Lε | Pattern-recognition and encoding structures |
| `ai` | L5 | Language-primary constructs |
| `relational` | L5 | Cross-domain interpretive links |

### substrate_layer → L-layer relationship

| `substrate_layer` value | L-layer anchor | Lε treatment |
|---|---|---|
| `substrate_primary` | L3–L4 | Strict Lε.obs and Lε.pat required |
| `language_primary` | L5 | Lε.enc and Lε.xfr are primary risks |
| `both` | Lε boundary | Full 4-sublayer check applies |

---

## The Social/Embodied Boundary (L4 ↔ L5)

The `social/` ontology directory occupies the L4↔L5 boundary — the  
hardest zone to get right.

`WOLF_PACK` and `ANT` are at L4: their coordination is substrate-grounded  
in pheromones, GPS-collar-verified movement, evolutionary pressure.  
`COUNCIL` is at L5: it exists through human consensus and can be changed  
by human decision.

`WHALE` is at the Lε boundary itself: song transmission crosses oceanic  
geography (L3) through a culturally-transmitted acoustic protocol (L5).  
This is why whale song is studied as a **model for AI cultural transmission**  
— it demonstrates Lε functioning correctly at scale.

---

## Grounding Inspector

```bash
# Score a single entity's epistemic grounding
python3 validation/grounding_inspector.py --inspect WHALE

# Audit all entities by Lε score
python3 validation/grounding_inspector.py --audit

# Ask the sanctuary about grounding
python3 ai_sanctuary.py --ask "grounding"
```

The inspector computes a `le_score` for each attribute's evidence block,  
aggregates to an entity-level score, and flags:
- Confidence inflation (stated confidence > Lε score)
- Missing falsifiability
- Weak cross-domain evidence
- Substrate-layer incoherence (language_primary entity at L3 ontology)

---

## References

- Original framework: `JinnZ2/Resilient-AI-Human-Collaboration-/Organize.md`  
- Architecture mismatch failure modes: `training/architecture_mismatch.md`  
- Substrate selection: `docs/SUBSTRATE_SELECTION_PROCEDURE.md`  
- Epistemic scope standard: `validation/README.md` → "The One Rigor"
