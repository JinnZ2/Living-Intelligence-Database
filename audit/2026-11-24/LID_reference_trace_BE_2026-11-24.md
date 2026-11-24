# Reference Trace: Bee Hexagonal Cell, Pattern to Physics

Version: 0.2 (v0.2 additions 2026-11-24 appended; v0.1 text kept unchanged)
Date: 2026-11-24
Status: PROPOSED known-answer record. No repository files modified.
Baseline commit: `63d93c00951b14ed7352891747468c9b65cca146`
Machine-readable record: `reference/reference_trace_BE_hex.json` (built by `reference/build_reference.py`)
Checker: `reference/trace_check.py` → `reference/trace_check_results.json` (stdlib only, no network)

## What this record is for

This record traces one claim, BE `hexagonal_cell_efficiency`, through every layer, from the pattern down to governing physics. Each step carries a source, an operating regime and a deviation wherever a source provides one. It gives the dependency stack (ledger v0.2) and the cycle registry (ledger v0.3) a reference to be checked against. It does not validate the stored value of 0.97.

Status vocabulary: TRACED (sourced), DERIVED (combined from sourced nodes), CONTESTED (sources disagree; every account is kept), PROPOSED (owner decision pending), UNKNOWN, RECORDED_UNVERIFIED (the current repository value, kept as is).

## The trace

| Layer | Node | Claim | Value ± deviation | Status |
|---|---|---|---|---|
| D5 pattern | P_HEX_CELL | Current record: 0.97 storage per wax mass versus the next-best tessellation | 0.97 ± 0.01 (prose) | RECORDED_UNVERIFIED |
| D0 law | G2D_HALES | Any equal-area partition of the plane has perimeter at least that of the regular hexagonal tiling ([Hales 2001](https://link.springer.com/article/10.1007/s004540010071); [arXiv](https://arxiv.org/abs/math/9906042)) | exact theorem, 2D | TRACED, with citation and scope mismatch against the record |
| D0 law | G3D_FEJES | The real 3D cell base is not surface-minimizing; the alternative saves less than 0.35% of the opening area ([Fejes Tóth 1964](https://projecteuclid.org/journalArticle/Download?urlid=bams/1183526078)) | < 0.35% | TRACED |
| D2 condition | C_WALL | Optimality depends on wall thickness; with real wax walls, the natural base may be closer to optimal ([Apidologie 2022](https://link.springer.com/10.1007/s13592-022-00915-8)) | regime: idealized vs real | TRACED |
| D0 law | F_FLOW | How a circle becomes a hexagon. Three accounts: surface-tension flow of heated wax at triple junctions ([Karihaloo et al. 2013](https://www.ncbi.nlm.nih.gov/pmc/articles/3730681)); thermal expansion and stress above yield, without melting ([Talukdar & Dutta 2019](https://link.springer.com/article/10.1007/s42452-019-1239-0)); self-organized angular redistribution by workers ([Nature 2026](https://www.nature.com/articles/s44434-026-00004-2)) | — | CONTESTED |
| D2 condition | C_FLOW_T | Wax flows at about 45 °C at junctions ([Karihaloo et al.](https://www.ncbi.nlm.nih.gov/pmc/articles/3730681)) | ≈45 °C, unquantified | TRACED |
| D2 condition | C_MELT | Beeswax melts at 62–64 °C ([Wikipedia](https://en.wikipedia.org/wiki/Beeswax)) | range | TRACED |
| D2 condition | C_BROOD_T | Nest at 33–36 °C ([PMC2813292](https://pmc.ncbi.nlm.nih.gov/articles/PMC2813292/)); capped brood 34.8–35.9 °C across ambient 13–41 °C ([J Comp Physiol A 2021](https://link.springer.com/article/10.1007/s00359-021-01464-8)) | range, with regime | TRACED |
| D2 regime | REGIME_HEX | Formation regime: local wax ≈45–62 °C, nest 33–36 °C; outside this → NOT_IN_SCOPE | bounds | DERIVED |
| D3 material | M_WAX | Monoesters 35–45%, hydrocarbons 12–16%, free fatty acids 12–14% ([PMC11538619](https://pmc.ncbi.nlm.nih.gov/articles/PMC11538619/)) | ranges | TRACED |
| D3 material | M_GLANDS | Four pairs of wax glands; largest around day 12, declining after day 18; about 1 million scales per kg ([FAO](https://www.fao.org/4/i0842e/i0842e12.pdf)); production begins in under 1 week and peaks around 2 weeks ([HAL](https://hal.science/hal-00890889v1/file/hal-00890889.pdf)) | — | TRACED |
| D1 energy | E_WAX_COST | About 8 kg honey per kg wax ([FAO](https://www.fao.org/4/i0842e/i0842e12.pdf)); 6.66–8.80 ([Wikipedia, Whitcomb 1946](https://en.wikipedia.org/wiki/Beeswax)); 8–15 ([FAO](https://www.fao.org/4/t0104e/T0104E04.htm)) | sources disagree: 6.66–15 | TRACED |
| D1 energy | E_BODY_HEAT | Heat comes from nectar sugar; about 40% of annual colony energy intake goes to brood heating ([PNAS](https://www.pnas.org/doi/10.1073/pnas.1232346100)) | ≈0.40 | TRACED |
| D1 energy | E_NECTAR | Nectar sugars come from phloem sucrose produced by photosynthesis ([Phil Trans R Soc B](https://pmc.ncbi.nlm.nih.gov/articles/PMC9058545/)) | — | TRACED |
| D1 energy | E_SUN | Total solar irradiance 1360.8 ± 0.5 W/m² ([Kopp & Lean 2011](https://esdpubs.nasa.gov/sgpubs/content/A_new_lower_value_of_total_solar_irradiance_Evidence_and_climate_significance)) | ± 0.5 W/m² | TRACED; GAP in the repository |
| D0 law | L_CONSERVE | Ordered open systems persist only through continuous energy exchange ([dissipative structures](https://www.utphysicshistory.net/IlyaPrigogine.html)) | — | TRACED |
| D4 entity | D4_FLOWERS | Nectar source plants | — | PROPOSED (which repository entity is an owner decision) |
| D4 entity | D4_HOT_WORKERS | Workers heat the wax with their bodies | — | TRACED |

## Cycle registry

Every cycle is named, given a period and placed under a parent. Nesting order is checked automatically: a child's period must be shorter than its parent's.

| Cycle | Kind | Period | Context | Parent | Source |
|---|---|---|---|---|---|
| wingbeat | oscillation | ≈230 Hz (229.8 ± 11.0, n = 4) | hovering, normal air | daily activity | [Altshuler et al. 2005](https://www.pnas.org/doi/10.1073/pnas.0506590102) |
| circle→hexagon | transient within a cycle | ≈6 s heated, ≈36 s partly heated | comb building | wax-scale secretion | [NBC News on Karihaloo](https://www.nbcnews.com/sciencemain/bees-dont-do-math-hexagonal-honeycombs-emerge-naturally-6c10677058) |
| wax-scale secretion | production cycle | 8 scales / 12 h | wax-producing worker | gland window | [FAO](https://www.fao.org/4/i0842e/i0842e12.pdf) |
| daily activity | oscillation | 24 h | foraging and hive work | worker life | UNSOURCED |
| wax-gland window | developmental window | starts < 1 wk, peaks ≈ day 12, declines after day 18 | worker age; overridden in the swarm regime | worker life | [HAL](https://hal.science/hal-00890889v1/file/hal-00890889.pdf), [FAO](https://www.fao.org/4/i0842e/i0842e12.pdf) |
| worker development | developmental cycle | 21 days (3 egg, 6 larva, 12 pupa) | brood at 33–36 °C | colony year | [FAO](https://www.fao.org/4/X0083E/X0083E03.htm) |
| worker adult life | life cycle | UNKNOWN | depends on season | colony year | not attached |
| colony annual cycle | seasonal | 1 year | temperate colony | solar cycle | [PNAS](https://www.pnas.org/doi/10.1073/pnas.1232346100) |
| solar activity cycle | oscillation | ≈11 years; irradiance varies ≈0.1% | Sun at 1 AU | (top) | [SWSC 2016](https://www.swsc-journal.org/articles/swsc/full_html/2016/01/swsc160010/swsc160010.html) |

AI compute cycles use the same schema, recorded as a separate domain: clock, forward pass, token step, training step, session. No periods are entered, because none have been sourced here. Each instrument should declare its own (NOT_TESTED).

## Checker results (OBSERVED, from `trace_check_results.json`)

- All six layers, D0–D5, are present. 14 of 18 nodes are TRACED. Every TRACED, DERIVED and CONTESTED node has a source.
- 13 of 14 dependency paths end at a D0 governing result. One path ends at wall thickness, a boundary condition.
- 6 paths pass through the PROPOSED "flowers" node.
- Flags raised: CITATION_MISMATCH and SCOPE_MISMATCH on the Hales link; GAP (no solar-radiation entity in the repository); one cycle without a period (worker adult life).
- No nesting violations. The cycles span about 10.9 orders of magnitude, from \(10^{-2.36}\) s to \(10^{8.54}\) s.
- The widest separation sits between wingbeat and the daily cycle, a ratio of about \(2\times10^{7}\). Over that gap, the daily phase is effectively constant during a wingbeat. The narrowest separations are between the colony year and the solar cycle (about 11) and between scale secretion and the gland window (about 12). At ratios that small, the slower cycle can't simply be treated as a fixed parameter. This is NOT_TESTED dynamically.

## What this does not establish

- It does not establish the value 0.97. No source for it was found, and it stays RECORDED_UNVERIFIED.
- It writes no differential equations. Relationships are recorded as dependencies with regimes, because the governing dynamics of the colony-scale couplings are not given by these sources.
- It does not resolve the formation mechanism. All three accounts are kept.
- The ± values are copied as each source states them. Their coverage probabilities were not checked, except for the stated irradiance uncertainty.

# v0.2 additions (2026-11-24): sunlight and environment differential

Machine-readable: `reference/reference_trace_BE_hex_v0.2.json`, built by `reference/build_reference_v02.py`. The v0.1 JSON is kept unchanged.
Checker output: `reference/trace_check_results_v0.2.json`. Re-running the checker on v0.1 gives byte-identical output.

## Sunlight in two roles

The Sun enters the trace twice, and the record keeps the two roles separate.

| Role | Chain | Values | Sources |
|---|---|---|---|
| Energy | Top of atmosphere → surface → photosynthesis → nectar | 1360.8 ± 0.5 W/m² above the atmosphere. About 1000 W/m² maximum at sea level on a clear day ([Wikipedia](https://en.wikipedia.org/wiki/Solar_irradiance)); clear-sky noon ranges 700–1300 W/m² depending on latitude, altitude and season ([TU Delft](https://delftxdownloads.tudelft.nl/solar/week1/ET3034TUx-1.7-subtitles.pdf)). Maximum conversion to biomass is 4.6% (C3) or 6% (C4) at 30 °C and 380 ppm CO₂ ([Zhu, Long & Ort 2008](https://pubmed.ncbi.nlm.nih.gov/18374559/)), or 9.4% / 12.3% of photosynthetically active light ([Zhu et al. 2010](https://ripe.illinois.edu/sites/ripe.illinois.edu/files/2018-06/Photosynthetic.pdf)). | as cited |
| Information | Sun position and sky polarization → bee compass → waggle dance | Bees use the sun's azimuth and the polarization pattern that scattering creates in the sky. The sun's daily movement is compensated by an internal circadian clock ([PMC4667876](https://pmc.ncbi.nlm.nih.gov/articles/PMC4667876/)). | as cited |

The information role depends on the geometry of sunlight, not its power. This means the repository's `waggle_dance_communication` dependency `time_of_day` can bind to a sourced cycle.

## The daily cycle is now sourced

The honeybee clock is endogenous and runs close to 24 h. It drifts slightly off 24 h in constant conditions, entrains to light–dark cycles, and keeps a period of about 24 h at both 23 °C and 31 °C ([Beling review](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10995049/)). The same clock drives time memory and sun-compass compensation.

## Environment differential: mānuka vs wildflower

The question: with the same bee and the same physics but a different forage environment, which parts of the trace change?

| Layer | Mānuka | Wildflower (multifloral) | Classification |
|---|---|---|---|
| D0 geometry, wax physics, law | same | same | INVARIANT |
| D2 brood temperature | colony-regulated 33–36 °C | same | ASSUMED INVARIANT, NOT_TESTED |
| D3 wax composition; D1 honey cost per kg of wax | — | — | UNKNOWN: no source splits these by forage |
| D1 sugar (energy) | 59.11 ± 0.36 g/100 g | 56.02 ± 2.02 and 56.56 ± 1.06 g/100 g; no significant difference, n = 3 each ([IJFST](https://academic.oup.com/ijfst/article/54/12/3185/7805247)) | Alike at the energy layer, in this study |
| D1 nectar energy source | Green nectaries photosynthesize and contribute a measurable share of nectar sugar, including DHA ([Clearwater et al. 2021](https://onlinelibrary.wiley.com/doi/full/10.1111/nph.17632)) | Sugars mainly come through the phloem, from photosynthesis ([Phil Trans B](https://pmc.ncbi.nlm.nih.gov/articles/PMC9058545/)) | VARIANT |
| D3 chemistry | Nectar DHA converts to MGO in honey through a non-enzymatic, overall first-order reaction ([Adams 2009](https://pubmed.ncbi.nlm.nih.gov/19368902/); [Grainger 2016](https://europepmc.org/article/MED/26920322)). Fresh honey: DHA 1192–5099, MGO 139–491 mg/kg ([review](https://onlinelibrary.wiley.com/doi/full/10.1002/nzb2.70185)). | Composition reflects the botanical mix and varies more ([Foods 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11395089/); [Italy](https://pmc.ncbi.nlm.nih.gov/articles/PMC9407073/)) | VARIANT |
| D3 antioxidant (ORAC) | 103.55 ± 9.41 | 19.25 ± 2.24; 49.38 ± 0.18 ([IJFST](https://academic.oup.com/ijfst/article/54/12/3185/7805247)) | VARIANT |
| Cycle | Flowering window of 10–12 weeks usually, 4 weeks in a short season ([MPI 2018](https://www.mpi.govt.nz/dmsdocument/34329/direct)); 6–12 weeks, often less, under 6 in Taranaki ([Landcare](https://pnrp.gw.govt.nz/assets/Documents/2021/07/Manuka-plantation-guide-landcare-April2017.pdf)) | Combined flowering windows of many species (UNSOURCED) | VARIANT |

Key control (OBSERVED in source): adding DHA to clover honey produced MGO at mānuka-like levels ([Adams 2009](https://pubmed.ncbi.nlm.nih.gov/19368902/)). The bee is the shared processor, and the difference arrives with the input. In this trace, the two regimes split at the material and chemistry layer, not at the energy or geometry layers.

## Sensitivities (signed, scoped; no equations written)

| Of | To | Sign | Scope | Source |
|---|---|---|---|---|
| Mānuka nectar DHA | Light on the nectary | + (shaded flowers lost DHA proportionally more than sugar) | Attached flowers, shading | [Clearwater 2021](https://onlinelibrary.wiley.com/doi/full/10.1111/nph.17632) |
| Total nectar sugar | Temperature | small + (less important than light) | Same study | [Clearwater 2021](https://onlinelibrary.wiley.com/doi/full/10.1111/nph.17632) |
| Nectar yield | Previous day's daytime temperature | + (one-day lag, P < 0.001) | Controlled trial; drying soil had no effect | [Annals of Botany 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC5838834/) |
| DHA : total sugar | Temperature | Depends on genotype (clone × temperature × time-of-day interaction) | Controlled-environment clones | [Massey thesis](https://mro.massey.ac.nz/server/api/core/bitstreams/cd6d5182-ce92-4c2d-aad1-a272b46343e7/content); [MPI](https://www.mpi.govt.nz/dmsdocument/37392/direct) |
| Between-site variation | Radiation; night-time temperature | Variance share, not a direction: about 80% each (sugar and DHA:sugar respectively). Plant-to-plant variation within sites is largest, 40–70%. | Wild plants | [Noe 2019](https://agupubs.onlinelibrary.wiley.com/doi/10.1080/01140671.2019.1670681) |

Two results to keep:

- **The sign of the sensitivity is itself scoped.** For DHA:sugar against temperature, the direction depends on genotype. A single "∂/∂T for mānuka" would be unsupported. The scope has to name the genotype.
- **An apparent contradiction resolves once scoped.** One study found temporal variation in DHA:sugar unrelated to environment, within genotype ([Annals 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC5838834/)). Another found night-time temperature explained about 80% of between-site variation in wild plants ([Noe 2019](https://agupubs.onlinelibrary.wiley.com/doi/10.1080/01140671.2019.1670681)). These are different variances. Both are kept.

## Repository dependency strings bound to trace nodes (PROPOSED)

The checker confirmed, read-only against the clone, that all nine strings exist in `ontology/animal/bee.json`.

| Attribute | Repo string | Binds to |
|---|---|---|
| hexagonal_tessellation | construction_temperature | wax flow temperature; formation regime |
| hexagonal_tessellation | wax_purity | wax composition |
| hexagonal_tessellation | cell_type | UNKNOWN (no node yet) |
| waggle_dance_communication | time_of_day | daily cycle; sun compass |
| collective_thermoregulation | ambient_temperature | brood temperature (regime: ambient 13–41 °C) |
| collective_thermoregulation | food_stores | body heat; nectar energy |
| swarm_coordination | weather_window | surface irradiance (partial) |
| hexagonal_cell_efficiency | golden_ratio, pi | UNCHECKED |

## Checker results v0.2 (OBSERVED)

- 26 nodes: 22 TRACED, 1 DERIVED, 1 CONTESTED, 1 PROPOSED, 1 RECORDED_UNVERIFIED.
- 19 of 20 hexagon paths reach D0. The new roots (mānuka, wildflower, DHA→MGO) all reach D0 through the sunlight chain.
- Gaps: the repository has no entity for solar radiation and none for mānuka.
- Cycles without a period: worker adult life, flower nectar stages, combined wildflower season.
- The tightest coupling in the ladder is the mānuka flowering window inside the year: a log₁₀ separation of 0.81, a ratio of about 6.5. The year's phase decides whether that forage regime exists at all.

## Observed in passing (not resolved)

- The bee record has two attributes valued at 0.97 with different definitions: `hexagonal_cell_efficiency` (honey volume per wax mass) and `hexagonal_tessellation` (wall area per wax consumed).
- It also has two waggle-dance attributes valued at 0.89, with 50 m and 200 m arrival radii.
- Whether these are intended as separate measurements is UNKNOWN.

## Dated note, 2026-11-24 (v0.3): corrections and additions

The rows above are unchanged. The v0.3 trace (`reference/reference_trace_BE_hex_v0.3.json`, built by `build_reference_v03.py`) sits beside v0.1 and v0.2. These leads came from an outside reader's report (Kimi, 2026-11-25). Each was re-fetched before it was added.

- **Label correction.** The F_FLOW source written above as "Nature 2026" is Gallo, Bridges, Woodgate & Chittka, published in [npj Entomology](https://www.nature.com/articles/s44434-026-00004-2) on 2026-10-06. That is a Nature Portfolio journal, not Nature. The URL was right; the label was wrong.
- **C_FLOW_T: TRACED → CONTESTED.** [Bauer & Bienefeld 2013](https://pubmed.ncbi.nlm.nih.gov/23149932/) measured wax at 33.6–37.6 °C while hexagonal cells were being built, below the roughly 40 °C a liquid-equilibrium account needs. [Karihaloo et al. 2013](https://www.ncbi.nlm.nih.gov/pmc/articles/3730681) give about 45 °C. Both readings are kept. REGIME_HEX takes its 45 °C lower bound from this node, so the regime is now CONDITIONAL.
- **F_FLOW, a fourth account.** Direct construction ([Bauer & Bienefeld 2013](https://pubmed.ncbi.nlm.nih.gov/23149932/)). Related sources: [Pirk et al. 2004](https://pubmed.ncbi.nlm.nih.gov/15257392/) and [Smith, Napp & Petersen 2021](https://pubmed.ncbi.nlm.nih.gov/34312229/).
- **New G3D_DAUTER (D0).** The Fejes Tóth gain improves to 0.50% when the hexagonal faces tilt a further 2.8° ([Dauter & Jaskolski 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC11873813/)). This is a geometric optimum, not a measurement of bees.
- **New P_BUILT_MEASURED (D5).** Natural combs contain no more than 18% Fejes Tóth cells. The measured dihedral angle is 108.70° ± 0.16°, against a theoretical 120° ([Yang et al. 2022](https://hal.science/hal-04025696/document)). This is the measured gap between the optimum and what bees actually build. It is a sourced quantity, not noise.
- **Checker result for v0.3 (OBSERVED).** 28 paths, 26 ending at D0, 2 CONTESTED nodes, and the same 8 findings as v0.2.
