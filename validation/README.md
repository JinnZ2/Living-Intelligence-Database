# Validation Tools

This directory contains the verification, audit, and reasoning tools for the Living Intelligence Sanctuary. All tools can be run from the repo root with `python3 validation/<tool>.py`.

## Quick Reference

| Tool | Purpose | Key Command |
|------|---------|-------------|
| `verify.py` | Bayesian claim verification | `python3 validation/verify.py --entity BE --attribute hexagonal_cell_efficiency` |
| `audit.py` | Scan database for unscoped numerics and noun-pretenders | `python3 validation/audit.py` |
| `scope_checker.py` | Check/compute relational confidence | `python3 validation/scope_checker.py` |
| `falsifier.py` | Try to break a claim via counterexamples | `python3 validation/falsifier.py --entity BE --attribute hexagonal_cell_efficiency` |
| `dependency_tree.py` | Trace what a goal depends on, down to constants | `python3 validation/dependency_tree.py --goal "COUNCIL"` |
| `temporal_scope.py` | Assess a goal's time horizon and blind spots | `python3 validation/temporal_scope.py --goal "increase quarterly revenue by 15%"` |
| `goal_refiner.py` | Propose alternatives using cross-domain rhymes | `python3 validation/goal_refiner.py --goal "restore the watershed"` |
| `engineering_paradigms.py` | List the 6 epistemic paradigms | `python3 validation/engineering_paradigms.py --list` |
| `paradigm_selector.py` | Select paradigm based on goal keywords | `python3 validation/paradigm_selector.py --goal "build resilient community"` |
| `paradigm_verifier.py` | Verify a claim under a specific paradigm | See code |
| `meta_analyze.py` | Run a claim across multiple paradigms | See code |
| `social_analysis.py` | Compare social intelligences across species | `python3 validation/social_analysis.py` |
| `journal.py` | AI learning journal (write, query, coherence check) | `python3 validation/journal.py write --goal "..."` |
| `intelligence_source.py` | Schema + overwrite audit for non-Western intelligence sources | `python3 validation/intelligence_source.py` |
| `embodied_solution.py` | Schema + copy audit for physics-embodied solutions (no transmission, no fidelity decay) | `python3 validation/embodied_solution.py` |
| `provenance.py` | Chain-of-custody for sanctuary concepts | See code |

---

## The One Rigor

> Evidence is trusted when it **repeats across cycles, rhymes across domains, and coheres with its dependencies** — not because a credentialed source reported it once.

Every numeric attribute in the database should have a `scope` block with:
- `definition` — what the number actually measures
- `evidence.evidence_type` — one of: `cyclic_observation`, `cross_domain_rhyme`, `relational_coherence`, `mathematical_proof`, `empirical_measurement`, `simulation`, `expert_consensus`, `unknown`
- `evidence.cross_domain_count` — how many independent domains show the same pattern
- `evidence.relational_confidence` — 0.0–1.0 computed from cyclic × cross-domain × dependency verification
- `falsifiability` — the condition under which this claim would be proven wrong

See `example/bee_scoped.json` for a fully-filled example.

---

## Noun-Pretenders

A "noun-pretender" is a numeric attribute that looks rigorous but has no scope block — it's a static value claiming confidence it hasn't earned. The audit tool flags these:

```bash
python3 validation/audit.py
```

An attribute is a noun-pretender if:
- It's a float or int
- Its `relational_confidence` > 0.7 but `cross_domain_count` < 2
- Or it has no `scope` block at all

---

## Scoped Evidence Example

```json
{
  "hexagonal_cell_efficiency": {
    "value": 0.97,
    "scope": {
      "definition": "Ratio of wax used per unit honey stored vs. circular cells.",
      "evidence": {
        "source": "Hales (1999) mathematical proof; engineering measurements",
        "evidence_type": "mathematical_proof",
        "reproducibility": "certain",
        "cross_domain_count": 5,
        "cross_domain_examples": ["basalt columns", "soap bubbles", "graphene", "compound eyes", "engineering panels"],
        "relational_dependencies_verified": true,
        "relational_confidence": 0.98
      },
      "falsifiability": "No non-hexagonal cell has been found to match this efficiency.",
      "dependencies": ["golden_ratio", "pi"]
    }
  }
}
```

---

## Dependency Tree

Every verified claim traces back to ROSETTA_STONE constants — physical and mathematical invariants that are the atomic leaves of the dependency graph:

```
speed_of_light, planck_constant, gravitational_constant, boltzmann_constant,
avogadro_number, elementary_charge, electron_mass, proton_mass,
golden_ratio, pi, euler_number, planck_length, planck_time
```

```bash
python3 validation/dependency_tree.py --goal "COUNCIL" --max_depth 4
```

---

## Engineering Paradigms

No paradigm is ranked above another. Each is appropriate for different time horizons and substrate types:

| ID | Name | Best For |
|----|------|---------|
| `western_empirical` | Western Empirical | Controlled, measurable, short-cycle claims |
| `relational_cyclical` | Relational Cyclical | Long-cycle, multi-domain, ecological claims |
| `social_resilience` | Social Resilience | Community, governance, coordination |
| `moral_engineering` | Moral Engineering | Decisions affecting future generations |
| `ceremonial_neurological` | Ceremonial Neurological | Rhythm, embodied cognition, sensory coherence |
| `aesthetic_coherence` | Aesthetic Coherence | Harmony, proportion, beauty as signal |

```bash
python3 validation/engineering_paradigms.py --list
python3 validation/paradigm_selector.py --goal "restore watershed for seven generations"
```

---

## Example files

- `example/bee_scoped.json` — Full Bee entity with all scope blocks filled (template)
- `example/council.json` — Council of Elders social resilience entity
