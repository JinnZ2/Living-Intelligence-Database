"""Builds the BE hexagonal_cell_efficiency reference trace (PROPOSED known-answer record).
Every TRACED node carries a source URL. Values are copied from sources, not recalled."""
import json
S = {
 "hales": "https://link.springer.com/article/10.1007/s004540010071",
 "hales_arxiv": "https://arxiv.org/abs/math/9906042",
 "fejes": "https://projecteuclid.org/journalArticle/Download?urlid=bams/1183526078",
 "apidologie": "https://link.springer.com/10.1007/s13592-022-00915-8",
 "karihaloo": "https://www.ncbi.nlm.nih.gov/pmc/articles/3730681",
 "karihaloo_times": "https://www.nbcnews.com/sciencemain/bees-dont-do-math-hexagonal-honeycombs-emerge-naturally-6c10677058",
 "thermo_alt": "https://link.springer.com/article/10.1007/s42452-019-1239-0",
 "nature2026": "https://www.nature.com/articles/s44434-026-00004-2",
 "fao_wax": "https://www.fao.org/4/i0842e/i0842e12.pdf",
 "fao_wax_hi": "https://www.fao.org/4/t0104e/T0104E04.htm",
 "wiki_wax": "https://en.wikipedia.org/wiki/Beeswax",
 "wax_comp": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11538619/",
 "hal_wax": "https://hal.science/hal-00890889v1/file/hal-00890889.pdf",
 "brood_T": "https://pmc.ncbi.nlm.nih.gov/articles/PMC2813292/",
 "comb_T": "https://link.springer.com/article/10.1007/s00359-021-01464-8",
 "pnas_energy": "https://www.pnas.org/doi/10.1073/pnas.1232346100",
 "nectar": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9058545/",
 "tsi": "https://esdpubs.nasa.gov/sgpubs/content/A_new_lower_value_of_total_solar_irradiance_Evidence_and_climate_significance",
 "tsi_cycle": "https://www.swsc-journal.org/articles/swsc/full_html/2016/01/swsc160010/swsc160010.html",
 "wingbeat": "https://www.pnas.org/doi/10.1073/pnas.0506590102",
 "fao_dev": "https://www.fao.org/4/X0083E/X0083E03.htm",
 "prigogine": "https://www.utphysicshistory.net/IlyaPrigogine.html",
}
N = []
def node(id, layer, role, claim, status, src=None, value=None, regime=None, links_repo=None, note=None, depends_on=()):
    N.append({k: v for k, v in dict(id=id, layer=layer, role=role, claim=claim, status=status,
              source=[S[s] for s in (src or [])] or None, value=value, regime=regime,
              repo_entity=links_repo, note=note, depends_on=list(depends_on)).items() if v not in (None, [])})

# D5 — the pattern as recorded today (kept verbatim-in-meaning; not altered)
node("P_HEX_CELL", "D5_pattern", "pattern",
     "Record: hexagonal_cell_efficiency = 0.97, 'ratio of honey volume stored per unit wax mass ... vs next-best regular tessellation'",
     "RECORDED_UNVERIFIED", value={"y": 0.97, "deviation": "±0.01 (prose in measurement_limits)"},
     links_repo="BE", depends_on=["G2D_HALES", "G3D_FEJES", "F_FLOW", "E_WAX_COST", "M_WAX", "C_BROOD_T", "C_FLOW_T"])

# D0 — governing results
node("G2D_HALES", "D0_law", "governing_law",
     "Any partition of the plane into regions of equal area has perimeter at least that of the regular hexagonal tiling (2D).",
     "TRACED", ["hales", "hales_arxiv"], links_repo="HEX",
     note="Published Discrete Comput Geom 25:1-22 (2001); repo cites '36:5-69 (1999)' -> CITATION_MISMATCH. Theorem is 2D perimeter; record claims 3D volume per wax mass -> SCOPE_MISMATCH.")
node("G3D_FEJES", "D0_law", "governing_law",
     "The 3D bee cell (three-rhombus base) is not surface-minimizing; two hexagons + two rhombi is more economical, saving <0.35% of the opening area.",
     "TRACED", ["fejes"], value={"y": "<0.35% of opening area", "deviation": "upper bound stated by source"},
     note="With non-zero wall thickness the three-rhombus base may be closer to optimum (Weaire & Phelan, as reported in Apidologie 2022). Optimality in 3D is regime-dependent on wall thickness.",
     depends_on=["C_WALL"])
node("C_WALL", "D2_condition", "boundary_condition", "Wall thickness: zero (idealized) vs real non-uniform beeswax walls.",
     "TRACED", ["fejes", "apidologie"], regime={"var": "wall_thickness", "kinds": ["idealized_zero", "real_nonuniform"]})
node("F_FLOW", "D0_law", "governing_law",
     "Cells are built circular; visco-elastic wax heated by workers flows near triple junctions; surface-energy minimization straightens walls into rounded hexagons.",
     "CONTESTED", ["karihaloo", "thermo_alt", "nature2026"],
     note="Three accounts preserved, not reconciled: (a) surface-tension wax flow (Karihaloo 2013); (b) thermal expansion and stress above yield under a temperature gradient, without melting (Talukdar & Dutta, SN Appl Sci 2019); (c) workers iteratively equalising angular space at junctions, self-organised (npj/Nature 2026). Divergence is retained as data.",
     depends_on=["C_FLOW_T", "E_BODY_HEAT"])

# D2 — conditions / regime bounds
node("C_FLOW_T", "D2_condition", "boundary_condition", "Wax flows visco-elastically at about 45 °C at the triple junction.",
     "TRACED", ["karihaloo"], value={"y": 45, "unit": "°C", "deviation": "'about' — not quantified by source"}, depends_on=["E_BODY_HEAT"])
node("C_MELT", "D2_condition", "boundary_condition", "Beeswax melts at 62–64 °C (upper regime bound: comb structure fails).",
     "TRACED", ["wiki_wax"], value={"y": [62, 64], "unit": "°C", "deviation": "range"})
node("C_BROOD_T", "D2_condition", "boundary_condition", "Brood nest regulated at 33–36 °C; capped brood 34.8–35.9 °C across ambient 13–41 °C.",
     "TRACED", ["brood_T", "comb_T"], value={"y": [34.8, 35.9], "unit": "°C", "regime": "ambient 13–41 °C"}, depends_on=["E_BODY_HEAT"])
node("REGIME_HEX", "D2_condition", "regime",
     "Derived operating regime for hexagon formation: local wax ~45 °C, nest ~33–36 °C, below melt 62–64 °C.",
     "DERIVED", ["karihaloo", "brood_T", "wiki_wax"],
     regime={"bounds": {"wax_local_T_C": [45, 62], "nest_T_C": [33, 36]}, "outside": "NOT_IN_SCOPE"},
     note="Lower bound 45 °C is 'about'; treat as CONDITIONAL until a source gives a range.")

# D3 — material
node("M_WAX", "D3_material", "material",
     "Beeswax composition: monoesters 35–45%, hydrocarbons 12–16%, free fatty acids 12–14%; hydrocarbons probably from oenocytes.",
     "TRACED", ["wax_comp", "hal_wax"], depends_on=["M_GLANDS"])
node("M_GLANDS", "D3_material", "material",
     "Secreted as liquid by four pairs of wax glands on young workers; glands largest ~day 12, decline after day 18; ~1 million scales per kg.",
     "TRACED", ["fao_wax", "hal_wax"], depends_on=["E_WAX_COST"])

# D1 — energy chain
node("E_WAX_COST", "D1_energy", "energy_source", "Wax is synthesised from sugar: ~8 kg honey consumed per kg wax.",
     "TRACED", ["fao_wax", "wiki_wax", "fao_wax_hi"],
     value={"y": 8, "unit": "kg honey / kg wax", "deviation": "sources span 6.66–8.80 (Whitcomb 1946, via Wikipedia) to 8–15 (FAO T0104E)"}, depends_on=["E_NECTAR"])
node("E_BODY_HEAT", "D1_energy", "energy_source",
     "Heat for wax working and brood comes from worker thoracic muscle metabolism fuelled by nectar sugar; ~40% of the colony's annual energy intake goes to brood-nest heating.",
     "TRACED", ["pnas_energy", "karihaloo"], value={"y": 0.40, "unit": "fraction of annual energy", "deviation": "'≈' estimate"},
     depends_on=["E_NECTAR"])
node("E_NECTAR", "D1_energy", "energy_source",
     "Nectar sugars originate from sucrose loaded from phloem, produced by photosynthesis.",
     "TRACED", ["nectar"], links_repo="PHLOEM_XYLEM", depends_on=["D4_FLOWERS", "E_SUN"])
node("E_SUN", "D1_energy", "energy_source",
     "Total solar irradiance at 1 AU: 1360.8 ± 0.5 W/m² (2008 solar minimum).",
     "TRACED", ["tsi"], value={"y": 1360.8, "unit": "W/m²", "deviation": "±0.5"},
     note="GAP: no repository entity represents incoming solar radiation. SOLAR_WIND is a plasma flow.",
     depends_on=["L_CONSERVE"])
node("L_CONSERVE", "D0_law", "governing_law",
     "Open, far-from-equilibrium systems maintain ordered structure only through continuous energy/matter exchange and disappear if it ceases (dissipative structures).",
     "TRACED", ["prigogine"], note="Energy conservation is assumed as the accounting law for the chain; no repository equation reference exists for it.")

# D4 — entities
node("D4_FLOWERS", "D4_entity", "entity", "Flowering plants supplying nectar.", "PROPOSED",
     links_repo="SUN (Sunflower) / LEAF_TESS", note="Which repository plant entities stand for nectar sources is an owner decision.", depends_on=["E_SUN"])
node("D4_HOT_WORKERS", "D4_entity", "entity", "Workers heat the wax with their bodies during comb building.", "TRACED", ["karihaloo"], links_repo="BE")

# Cycles — named, with period, context, nesting. Periods in seconds where a source gives them.
C = []
def cyc(id, name, kind, period_s, period_text, context, parent, src, status="TRACED", note=None):
    C.append({k: v for k, v in dict(id=id, name=name, kind=kind, period_s=period_s, period_text=period_text, context=context,
              parent=parent, source=[S[s] for s in src] if src else None, status=status, note=note).items() if v is not None})
cyc("CY_WING", "wingbeat", "oscillation", 1/230, "≈230 Hz (229.8 ± 11.0 Hz, n=4, hovering)", "hovering flight, normal air", "CY_DAY", ["wingbeat"])
cyc("CY_HEXFORM", "circle→hexagon transition", "transient_within_cycle", 6, "≈6 s fully heated; ≈36 s partially heated", "comb building, wax ~45 °C", "CY_SCALE", ["karihaloo_times"],
    note="A relaxation, not a repeat. Recorded as a transient phase inside the comb-building cycle; whether it counts as a cycle in its own right is an owner call.")
cyc("CY_SCALE", "wax-scale secretion", "production_cycle", 12*3600, "8 scales every 12 h", "wax-producing worker", "CY_GLAND", ["fao_wax"])
cyc("CY_DAY", "daily activity (circadian)", "oscillation", 86400, "24 h", "foraging / in-hive activity", "CY_LIFE", [], status="PROPOSED_UNSOURCED",
    note="Nesting position is assumed; a honeybee circadian source has not been attached.")
cyc("CY_GLAND", "wax-gland age window", "developmental_window", 6*86400, "begins <1 wk, peaks ≈2 wk (≈day 12), declines after day 18", "worker life stage; swarm regime overrides (all ages build)", "CY_LIFE", ["hal_wax", "fao_wax"])
cyc("CY_DEV", "worker development", "developmental_cycle", 21*86400, "21 days (3 egg, 6 larva, 12 pupa)", "brood at 33–36 °C", "CY_YEAR", ["fao_dev"])
cyc("CY_LIFE", "worker adult life", "life_cycle", None, "not attached", "season-dependent", "CY_YEAR", [], status="UNKNOWN")
cyc("CY_YEAR", "colony annual cycle", "seasonal_cycle", 365.25*86400, "1 year (winter cluster vs summer energy partition)", "temperate colony", "CY_SOLAR", ["pnas_energy"])
cyc("CY_SOLAR", "solar activity cycle", "oscillation", 11*365.25*86400, "≈11 years; TSI varies ≈0.1% min→max", "Sun at 1 AU", None, ["tsi_cycle"])

REC = {"record": "REFERENCE_TRACE_BE_HEXAGONAL_CELL", "version": "0.1", "date": "2026-11-24", "status": "PROPOSED",
       "baseline_commit": "63d93c00951b14ed7352891747468c9b65cca146",
       "subject": {"entity": "BE", "attribute": "hexagonal_cell_efficiency"},
       "rule": "TRACED nodes require a source. PROPOSED/UNKNOWN nodes carry no confidence. CONTESTED nodes preserve all accounts.",
       "nodes": N, "cycles": C}
json.dump(REC, open("reference_trace_BE_hex.json", "w"), indent=1, ensure_ascii=False)
print(len(N), "nodes;", len(C), "cycles")
