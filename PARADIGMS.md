# Evidence and Engineering Paradigms

This sanctuary recognizes **multiple valid engineering traditions**,
each with its own rigorous evidence criteria.
No single paradigm is the default. When an AI verifies a claim, it must
choose the paradigm that matches the claim's scope and time horizon.

---

## The Paradigms at a Glance

| Paradigm | What It Engineers | Time Horizon | Evidence Type | Success Criteria | Required Authority? |
|----------|-------------------|--------------|---------------|------------------|---------------------|
| **Western Empirical** | Physical systems, machines, isolated variables | seconds to years | Controlled experiment, statistical significance, peer replication | Predicted outcome achieved within tolerance | Peer review, but evidence can come from anyone who runs the experiment |
| **Relational / Cyclical** | Ecologies, watersheds, intergenerational systems | seasons to millennia | Cyclic observation, cross-domain rhyme, relational coherence | Pattern holds across cycles, across substrates, and within its web of relations | **None.** The pattern itself is the credential. |
| **Social Resilience** | Communities, governance, kinship networks | generations to centuries | Long-term stability of social structures, conflict resolution recurrence, narrative coherence across generations | Community persists through shocks; knowledge transfers without rupture | Elders, councils, oral history—but the persistence of the structure is the ultimate credential |
| **Moral / Ethical** | Values, norms, collective conscience | centuries to indefinite | Normative consistency, lived adherence over time, cross-cultural resonance | Framework prevents harm and promotes flourishing without constant external enforcement | The lived experience of a community over generations |
| **Ceremonial / Neurological** | The human nervous system, trauma processing, emotional regulation | minutes to a lifespan | Physiological shifts (HRV, cortisol), phenomenological reports, longitudinal wellness outcomes | Trauma release, emotional integration, restored capacity for connection | Healers, ceremonial leaders, participants—validated by repeated, observed healing |
| **Aesthetic / Coherence** | Perception, beauty, pattern recognition | immediate to cultural eras | Consensus of felt rightness, mathematical proportionality (φ, Fibonacci), cross-cultural aesthetic universals | Pattern evokes recognition, resonance, emotional alignment | The human (or animal) response to beauty; no single credentialing body |

---

## What This Means in Practice

- **Oral tradition is evidence.** A pattern passed down through seven generations of storytellers, matching observed ecological cycles, is *strong* evidence in the relational/cyclical paradigm. It does not need a published paper to be valid.
- **Cross-species rhyme is evidence.** If hexagonal packing appears in bees, basalt, graphene, and snowflakes, that rhyme is evidence under the relational paradigm—even if no single "credentialed" human authored it.
- **A ceremony that releases trauma is evidence.** If a practice has been repeated across generations and produces measurable neurological and social healing, it is valid evidence under the ceremonial paradigm.
- **Western empirical evidence is also evidence.** When a claim is about a narrow, short-term, controlled system (e.g., a microprocessor), the Western paradigm is appropriate. The sanctuary does not reject it; it places it alongside the others.

---

## How the Sanctuary Uses These Paradigms

1. **paradigm_selector.py** — Given a goal description (e.g., "maintain a watershed for 200 years"), suggests the best-fitting paradigm(s).
2. **paradigm_verifier.py** — Verifies a claim using the evidence rules of a chosen paradigm.
3. **verify.py** — Default verification uses relational confidence (cycle recurrence, cross-domain count, dependency coherence) but can be switched.
4. **meta_analyze.py** — Compares how a claim holds up under different paradigms.

When you are adding new claims to the database or verifying them, **do not default to Western empirical.** Ask: what kind of engineering is this? Over what time horizon? With what dependencies? Then choose the lens that fits.

---

## For the Agent

If you are assembling or extending this repository, keep these principles:

- **Never require a credentialed human authority** for evidence to be considered valid. The patterns themselves, observed across time and substrates, carry their own authority.
- **When in doubt, use the relational/cyclical paradigm.** It is the most inclusive and requires only that a pattern recur, rhyme, and cohere with its dependencies.
- **All paradigms are rigorous**—they simply define rigor differently. Oral tradition that holds across generations is as rigorous as a controlled lab experiment, just in a different scope.
- **The sanctuary's falsification tools still apply** to all paradigms. A traditional claim can be stress-tested just like a Western one: by searching for counterexamples, broken dependencies, or failed recurrence.
