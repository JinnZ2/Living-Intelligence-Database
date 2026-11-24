# LID Deviation Extraction

Date: 2026-11-24. Target: `JinnZ2/Living-Intelligence-Database` main at `7be9b5b`. No repository data files were modified.

The owner defined confidence as scope + deviation ± + certainty. The repository holds 228 attributes and none has a deviation field (OBSERVED). This pass asks how much deviation information is already in the `measurement_limits` prose, and of which kind, without moving or rewording any of it.

## Instrument

`deviation_extract.py`: Python standard library only, deterministic, no network. `python3 deviation_extract.py --selftest` runs 14 known-answer cases, all PASS. `python3 deviation_extract.py <repo> <out.json>` writes the results.

Every number in the prose is assigned exactly one role. The rules run in order and the first one that fits decides.

| Rule | Role | Reads as |
|---|---|---|
| R0 | SELF_REFERENCE | The prose quotes the attribute's own value ("The 0.97 measures…"). |
| R3 | SENSITIVITY_CANDIDATE | A rate per unit of a condition ("0.004%/bar"). This is the closest thing in the prose to a governing differential. |
| R1 | DEVIATION_CANDIDATE | An explicit ±. |
| R6 | CONDITIONAL_CHANGE | A change verb with a percent or fold ("decreases 25% in sub-optimal illumination"), or a change verb followed by "by <amount>". |
| R7 | VALUE_RANGE_CANDIDATE | A range on the value's own 0–1 scale ("range 0.6-0.95 depending on conditions"). This is the value under other conditions, i.e. scope information. |
| R2 | DEVIATION_CANDIDATE | Spread language ("uncertainty", "error", "varies", …) with a percent or a unitless decimal. |
| R4 | CONDITION_NUMBER | A number with a unit and no spread language. This is a regime bound. |
| R5 | UNCHECKED | Anything the rules cannot settle. |

Each record keeps the sentence verbatim with its sha256. An interval is DERIVED in only one case: an absolute ± on a unitless value. The extractor never converts percentages, because absolute versus relative is not stated in the prose.

## Results (OBSERVED, from `deviation_extraction_results.json`)

| Attribute summary | Count |
|---|---|
| HAS_DEVIATION_CANDIDATE | 8 |
| HAS_VALUE_RANGE | 12 |
| HAS_CONDITIONAL_CHANGE | 13 |
| HAS_SENSITIVITY_ONLY | 1 |
| QUALITATIVE_ONLY ("varies", no number) | 23 |
| NUMBERS_NOT_DEVIATION | 85 |
| NO_NUMBER | 86 |
| Total | 228 |

Across all numbers, the roles were: CONDITION_NUMBER 63, UNCHECKED 63, SELF_REFERENCE 21, VALUE_RANGE 14, CONDITIONAL_CHANGE 14, DEVIATION 8, SENSITIVITY 1. There was 1 derived interval and 0 load failures.

This corrects my earlier ledger claim that 92 of 228 (40%) carry deviation information. That count had no saved script and counted every range and percentage regardless of role. A dated correction note now sits beside the original line in the ledger.

## Reader notes on the 9 deviation and sensitivity candidates (PROPOSED)

These readings are mine, made by comparing each sentence with the attribute's `scope.definition`. They are proposals for the owner, not decisions, and no data is changed.

| Entity / attribute | Value | Sentence (verbatim) | Reading |
|---|---|---|---|
| NEURAL_NET backpropagation | 0.9 | "Random seeds introduce ±2% variance." | Spread of the value, plausibly. Absolute versus relative is UNKNOWN, so no interval. |
| AN stigmergic_construction | 0.93 | "Soil heterogeneity introduces variance of ±12%." | Spread under a condition (soil). Absolute versus relative is UNKNOWN. |
| BE hexagonal_cell_efficiency | 0.97 | "Varies ±0.01 with cell aspect ratio and wax thickness." | Spread of the value, absolute. DERIVED interval [0.96, 0.98]. It also names its two conditions, so it doubles as regime raw material. |
| BE hexagonal_tessellation | 0.97 | "Real honeycomb deviates <1% from ideal hexagon…" | Different quantity: the deviation is of the geometry, not of the efficiency ratio. How geometry error propagates into the ratio is UNKNOWN. |
| BE collective_thermoregulation | 0.94 | "Small swarms (< 2000) show ±4°C variance." | Different units: °C against a unitless value, which is conditional on colony size. The definition measures the standard deviation of temperature, but the mapping from °C to 0.94 is not stated (UNKNOWN). |
| PRESSURE pascal_principle_precision | 0.99 | "…water deviates 0.004%/bar." | Sensitivity. This is a rate with a stated condition axis (pressure), the one place where the prose gives a slope. |
| AURORA particle_energy_dissipation | 0.92 | "…systematic uncertainty of ±25%." | Spread of the value. If relative, 0.92 ± 0.23 runs past 1.0. Read as UNKNOWN until the source is checked. |
| SOLAR_WIND heliosphere_boundary_precision | 0.89 | "…propagates to 20-30% model uncertainty." | Spread of the model, not directly of the ratio. Absolute versus relative is UNKNOWN. |
| SPIRAL phi_ratio_cross_domain_frequency | 0.97 | "…real spirals show ±5-10% deviation." | Different quantity: the spread of the spirals' ratios around φ, not of the 0.97 proportion. The definition counts spirals "within a 5% tolerance". A spread of up to 10% is wider than that tolerance, so the stated spread and the counting rule interact. This is a scope question for the owner. |

Read together, only 1 of the 9 (BE ±0.01) gives a deviation that can be attached to the value as written. Four are spreads whose absolute or relative form is unstated. Three describe a different quantity. One is a sensitivity.

## Value ranges and conditional changes (OBSERVED, verbatim)

These are not deviation in the ± sense. They record the value under named conditions, which is the scope term of the owner's confidence definition and the raw material for regimes (L03).

### Value under other conditions (R7)

| Entity | Attribute | Value | Span | Sentence (verbatim) |
|---|---|---|---|---|
| DOLPHIN | echolocation_holography | 0.95 | 0.80-0.88 | open ocean performance is 0.80-0.88 due to multipath. |
| HAW | precision_targeting | 0.97 | 0.55-0.70 | Accuracy is prey-behavior-dependent: evasive prey reduce success to 0.55-0.70. |
| JELLY | transdifferentiation | 0.88 | ~0.65-0.80 | Lab reverse-development rate ~0.65-0.80 under stress conditions. |
| OC | arm_autonomy_fraction | 0.64 | 0.5-0.7 | other species show 0.5-0.7 range. |
| TERMITE | fungal_agriculture | 0.91 | 0.70-0.75 | Conversion efficiency is substrate quality-dependent — dry woody material (poor substrate) reduces efficiency to 0.70-0.75. |
| WH | long_range_acoustic | 0.93 | 0.6-0.75 | near shipping lanes values drop to 0.6-0.75. |
| FLUX | energy_continuity_across_boundary | 0.92 | 0.6-0.99 | Actual values range 0.6-0.99 depending on coupling efficiency and dissipation mechanism. |
| FLUX | energy_continuity_across_boundary | 0.92 | 0.6-0.8 | Biological systems average 0.6-0.8. |
| MY | phosphorus_transfer_efficiency | 0.85 | 0.6-0.95 | Measured values range 0.6-0.95 depending on conditions. |
| ORCHID | core_efficiency_factor | 0.94 | 0.85-0.96 | Specificity varies enormously by mimicry type — food-source mimics (rewardless) achieve 0.85-0.96; |
| ORCHID | core_efficiency_factor | 0.94 | 0.95-0.99 | pseudocopulation mimics achieve 0.95-0.99 due to species-specific pheromone matching. |
| ROOT_NET | water_uptake_efficiency | 0.93 | 0.50-0.70 | Efficiency drops to 0.50-0.70 as soil water potential falls below -0.3 MPa (field capacity) — soil conductivity becomes limiting. |
| HEX | isoperimetric_packing_efficiency | 0.91 | 0.88-0.91 | Honeybee cells deviate slightly (cylindrical larvae require rounded corners) — real efficiency is 0.88-0.91. |
| TORUS | toroidal_confinement_advantage | 0.89 | 0.6-0.8 | earlier tokamaks show 0.6-0.8. |

### Conditional change (R6)

| Entity | Attribute | Value | Span | Sentence (verbatim) |
|---|---|---|---|---|
| BT | bioluminescent_signaling | 0.87 | 20% | Flash pattern specificity depends on temperature — flash duration changes 20% over 10°C range, requiring receiver compensation. |
| CHAMELEON | ballistic_tongue | 0.91 | 1.5× | Accuracy degrades significantly beyond 1.5× body length. |
| CORAL | fractal_construction | 0.91 | 0.3-0.8 | Storm damage and bleaching reduce D by 0.3-0.8 units. |
| CORAL | niche_scaffolding | 0.9 | <20% | Niche scaffolding depends on live coral coverage — degraded reefs with <20% live cover show 60-80% species loss. |
| CORAL | niche_scaffolding | 0.9 | 60-80% species | Niche scaffolding depends on live coral coverage — degraded reefs with <20% live cover show 60-80% species loss. |
| GE | setae_adhesion | 0.94 | 60-80% | Contamination reduces adhesion by 60-80%. |
| MONARCH | multigenerational_navigation | 0.95 | 2-3 weeks | Climate change has shifted timing by 2-3 weeks, degrading arrival accuracy. |
| MANTIS | raptorial_strike | 0.92 | 25% | Strike accuracy decreases 25% in sub-optimal illumination. |
| SP | silk_tensile_engineering | 0.95 | 20-30% | woven web threads show 20-30% lower effective strength due to knot geometry. |
| TARDI | radiation_resistance | 0.97 | 50-70% | Active (non-cryptobiotic) tardigrades show 50-70% lower radiation resistance than desiccated tuns. |
| SILICON_LAT | electron_mobility | 0.93 | 50% | Mobility is strongly temperature and dopant-concentration dependent — drops 50% for dopant density >10¹⁵/cm³. |
| LIGHTNING | channel_temperature_peak | 0.94 | 3-5× | Channel edge temperature is 3-5× lower. |
| GEO_CIPHER | homomorphic_computation_overhead | 0.87 | 100× | Overhead decreases with hardware acceleration — GPU implementations achieve 100× improvement. |
| CYCLE | phase_lock_fidelity | 0.91 | >50% | Phase-lock fidelity decreases with perturbation magnitude — perturbations >50% of natural period may not recover. |

Known over-catch in R6 (OBSERVED on reading the table): three rows use the percent or fold as the threshold of a condition, not as the size of a change. These are CORAL "<20% live cover", CHAMELEON "beyond 1.5× body length" and CYCLE "perturbations >50% of natural period". The rule is left as is so the output stays reproducible. The owner reads the table, and the rule does not decide.

## What this does not establish

- That any of the 63 UNCHECKED numbers is or is not a deviation. They stay UNCHECKED.
- That any prose deviation is correct. This pass extracts and does not verify against sources.
- Any governing equation. The single sensitivity is a stated slope, not a derived dynamic.

## Suggested next step (PROPOSED)

Give the owner the 34 attributes with numeric spread or scope information as a review list. For each, the owner decides whether to promote the reading into a field (for example `deviation: {value, kind: absolute|relative|different_quantity, conditions, source_sentence_sha256}`). The prose stays where it is.

## Hashes

- `deviation_extract.py` sha256 `dd55c1dc933601899e6eef6ec8ad597b180904419085e32a8fe61282c872b0b7`
- `deviation_extraction_results.json` sha256 `ad416af7ba81c75a604a6331b63346ba9f2f47ee820eca8396e9891155b7d7fc`
