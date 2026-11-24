"""v0.2 of the BE reference trace: adds the sunlight chain (energy + information roles),
a sourced circadian cycle, and an environment differential (manuka vs wildflower forage).
Reads v0.1 unchanged and writes a new file. Values are copied from fetched/searched sources."""
import json, copy
v1 = json.load(open("reference_trace_BE_hex.json"))
R = copy.deepcopy(v1); R["version"] = "0.2"; R["supersedes_note"] = "v0.1 file kept unchanged beside this one"
S = {
 "sfc_irr": "https://en.wikipedia.org/wiki/Solar_irradiance",
 "sfc_range": "https://delftxdownloads.tudelft.nl/solar/week1/ET3034TUx-1.7-subtitles.pdf",
 "zhu2008": "https://pubmed.ncbi.nlm.nih.gov/18374559/",
 "zhu_par": "https://ripe.illinois.edu/sites/ripe.illinois.edu/files/2018-06/Photosynthetic.pdf",
 "compass": "https://pmc.ncbi.nlm.nih.gov/articles/PMC4667876/",
 "beling": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10995049/",
 "timehoney": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5647282/",
 "clearwater21": "https://onlinelibrary.wiley.com/doi/full/10.1111/nph.17632",
 "annals18": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5838834/",
 "noe19": "https://agupubs.onlinelibrary.wiley.com/doi/10.1080/01140671.2019.1670681",
 "williams14": "https://pubs.acs.org/doi/pdf/10.1021/jf5045958",
 "thesis": "https://mro.massey.ac.nz/server/api/core/bitstreams/cd6d5182-ce92-4c2d-aad1-a272b46343e7/content",
 "mpi_pgp": "https://www.mpi.govt.nz/dmsdocument/37392/direct",
 "adams09": "https://pubmed.ncbi.nlm.nih.gov/19368902/",
 "review_mh": "https://onlinelibrary.wiley.com/doi/full/10.1002/nzb2.70185",
 "atrott12": "https://europepmc.org/article/MED/22960208",
 "grainger16": "https://europepmc.org/article/MED/26920322",
 "inhive": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6963415/",
 "mpi2018": "https://www.mpi.govt.nz/dmsdocument/34329/direct",
 "landcare": "https://pnrp.gw.govt.nz/assets/Documents/2021/07/Manuka-plantation-guide-landcare-April2017.pdf",
 "ijfst": "https://academic.oup.com/ijfst/article/54/12/3185/7805247",
 "multi_es": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11395089/",
 "multi_it": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9407073/",
 "nectar": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9058545/",
}
def node(id, layer, role, claim, status, src=None, **kw):
    d = dict(id=id, layer=layer, role=role, claim=claim, status=status, source=[S[s] for s in (src or [])] or None, **kw)
    R["nodes"].append({k: v for k, v in d.items() if v not in (None, [])})
def get(i): return next(n for n in R["nodes"] if n["id"] == i)

# --- Sunlight: energy role -------------------------------------------------
node("E_SURFACE", "D1_energy", "energy_source",
     "Atmospheric attenuation leaves ≈1000 W/m² maximum normal irradiance at sea level on a clear day; clear-sky noon values range ≈700–1300 W/m² with latitude, altitude and time of year.",
     "TRACED", ["sfc_irr", "sfc_range"], value={"y": 1000, "unit": "W/m²", "deviation": "range 700–1300 (regime-dependent)"},
     regime={"vars": ["solar_zenith_angle (air mass)", "cloud", "altitude", "season"]}, depends_on=["E_SUN"])
node("E_PHOTO_MAX", "D1_energy", "conversion_bound",
     "Theoretical maximum conversion of solar energy to biomass: 4.6% (C3) / 6% (C4) at 30 °C and 380 ppm CO2; 9.4% / 12.3% of photosynthetically active radiation. Field values are much lower.",
     "TRACED", ["zhu2008", "zhu_par"], value={"y": 0.046, "unit": "fraction (C3, full spectrum)", "deviation": "upper bound, not a typical value"},
     regime={"leaf_T_C": 30, "CO2_ppm": 380}, depends_on=["E_SURFACE"])
get("E_NECTAR")["depends_on"] = sorted(set(get("E_NECTAR")["depends_on"] + ["E_PHOTO_MAX"]))
get("D4_FLOWERS")["note"] = get("D4_FLOWERS")["note"] + " v0.2 (2026-11-24): split into D4_MANUKA and D4_WILDFLOWER in the environment differential."

# --- Sunlight: information role (same Sun, different dependency role) -------
node("I_SUNCOMPASS", "D2_condition", "information_source",
     "Honeybees use solar azimuth and the sky polarization pattern (produced by atmospheric scattering of sunlight) as a compass; the sun's movement is compensated by an internal circadian clock.",
     "TRACED", ["compass", "beling", "timehoney"], links_repo="BE.waggle_dance_communication",
     note="Role is information, not energy: the dependency is on the geometry of sunlight, not its power. Repo dependency string 'time_of_day' binds here (PROPOSED).",
     depends_on=["E_SUN", "L_SCATTER"])
node("L_SCATTER", "D0_law", "governing_law",
     "Scattering of sunlight in the atmosphere produces a regular pattern of E-vectors tangential to concentric circles around the sun.",
     "TRACED", ["compass"], note="Named as stated by source; the scattering theory itself (e.g., Rayleigh) is not cited here -> UNCHECKED beyond the source's statement.")

# --- Cycles ---------------------------------------------------------------
for c in R["cycles"]:
    if c["id"] == "CY_DAY":
        c.update(status="TRACED", source=[S["beling"], S["compass"]],
                 period_text="≈24 h endogenous; free-runs slightly off 24 h in constant conditions; entrains to light–dark cycles; period ≈24 h at both 23 °C and 31 °C (temperature-compensated)",
                 note="v0.2 (2026-11-24): sourced. The same clock drives time memory and sun-compass compensation (Beier & Lindauer 1970 as reported). External driver: the light–dark cycle.")
R["cycles"] += [
 {"id": "CY_MANUKA_BLOOM", "name": "mānuka flowering window", "kind": "seasonal_window", "period_s": 8*7*86400,
  "period_text": "usual 10–12 weeks; 4 weeks in a short season (MPI 2018); 6–12 weeks, often less, Sept–March, <6 weeks in Taranaki (Landcare)",
  "context": "New Zealand, region- and year-dependent", "parent": "CY_YEAR", "source": [S["mpi2018"], S["landcare"]], "status": "TRACED",
  "note": "period_s set to 8 weeks as a midpoint for ordering only; the record keeps the range."},
 {"id": "CY_FLOWER_AGE", "name": "mānuka flower nectar stages", "kind": "developmental_window", "period_s": None,
  "period_text": "opening → end of nectar flow; >2-fold changes in sugar, DHA and DHA:sugar across stages", "context": "single flower",
  "parent": "CY_MANUKA_BLOOM", "source": [S["clearwater21"], S["annals18"]], "status": "TRACED", "note": "Duration in days not given by these sources."},
 {"id": "CY_WILDFLOWER", "name": "multifloral forage season", "kind": "superposition", "period_s": None,
  "period_text": "union of many species' flowering windows", "context": "site- and year-dependent", "parent": "CY_YEAR",
  "source": None, "status": "PROPOSED_UNSOURCED", "note": "No source describes the combined window; kept as a structural placeholder."},
]

# --- Environment differential -------------------------------------------
node("D4_MANUKA", "D4_entity", "entity", "Mānuka (Leptospermum scoparium): green, photosynthetic nectaries; nectar dominated by fructose and glucose with small, variable sucrose and dihydroxyacetone (DHA), usually <2% each.",
     "TRACED", ["clearwater21", "annals18"], note="GAP: no repository entity for mānuka.", depends_on=["E_NECTARY_PHOTO", "E_PHOTO_MAX"])
node("E_NECTARY_PHOTO", "D1_energy", "energy_source",
     "Nectary photosynthesis contributes a measurable share of mānuka nectar sugars (¹³CO₂ label appears in nectar sugars incl. DHA); the rest is phloem import. Nectar DHA derives from triose-phosphate (DHAP) pools.",
     "TRACED", ["clearwater21"], depends_on=["E_SURFACE"])
node("D4_WILDFLOWER", "D4_entity", "entity", "Multifloral forage: many species; honey composition reflects the botanical mix and is more variable than monofloral honey.",
     "TRACED", ["multi_es", "multi_it"], links_repo="candidates: DANDELION, SUN, ORCHID (owner decision)", depends_on=["E_PHOTO_MAX"])
node("H_DHA_MGO", "D3_material", "transformation",
     "In honey, nectar-derived DHA converts non-enzymatically to methylglyoxal (MGO): overall first-order, studied 4–37 °C. Fresh comb honey DHA 1192–5099 mg/kg vs MGO 139–491 mg/kg; DHA falls and MGO rises in storage. Commercial mānuka: mean DHA:MGO ≈2:1, MGO 70–700 mg/kg.",
     "TRACED", ["adams09", "grainger16", "review_mh", "atrott12"],
     note="Control: DHA added to clover honey produced MGO at mānuka-like levels (Adams 2009). The chemistry is set by the nectar input, not the bee.", depends_on=["D4_MANUKA"])

R["environment_differential"] = {
 "question": "Same bee, same physics, different forage environment: which parts of the trace change?",
 "regimes": ["MANUKA", "WILDFLOWER"],
 "invariant_nodes": {
   "G2D_HALES": "mathematical; independent of forage", "G3D_FEJES": "mathematical; independent of forage",
   "C_BROOD_T": "colony-regulated 33–36 °C; no forage dependence reported in cited sources (ASSUMED invariant, NOT_TESTED)",
   "C_FLOW_T": "wax physics; forage dependence UNKNOWN", "E_SUN": "same star", "L_CONSERVE": "law"},
 "unknown_dependence": {
   "M_WAX": "Whether wax composition differs by forage: no source found -> UNKNOWN",
   "E_WAX_COST": "Honey-per-wax ratio not reported by forage type -> UNKNOWN"},
 "variant_nodes": [
   {"node": "nectar_sugar_total", "MANUKA": "per-flower yield varies with genotype, flower age, temperature", "WILDFLOWER": "species mix",
    "shared_observation": "Total sugar, fructose and glucose not significantly different between mānuka (59.11 ± 0.36 g/100 g) and two multifloral honeys (56.02 ± 2.02; 56.56 ± 1.06), n = 3 each",
    "source": [S["ijfst"]], "status": "TRACED", "implication": "At the energy layer (sugar), the two regimes look alike in this study."},
   {"node": "honey_bioactive_chemistry", "MANUKA": "DHA → MGO pathway present (H_DHA_MGO)", "WILDFLOWER": "no DHA-derived MGO pathway reported; clover control lacks it until DHA is added",
    "source": [S["adams09"]], "status": "TRACED", "implication": "Divergence enters at the material/chemistry layer, not the energy layer."},
   {"node": "antioxidant_capacity", "MANUKA": "ORAC 103.55 ± 9.41", "WILDFLOWER": "ORAC 19.25 ± 2.24 and 49.38 ± 0.18 (two multifloral sources)",
    "unit": "Trolox equivalent, as reported", "source": [S["ijfst"]], "status": "TRACED"},
   {"node": "forage_season", "MANUKA": "CY_MANUKA_BLOOM (4–12 weeks)", "WILDFLOWER": "CY_WILDFLOWER (unsourced superposition)",
    "source": [S["mpi2018"], S["landcare"]], "status": "PARTIAL"}],
 "sensitivities": [
   {"of": "mānuka nectar DHA per flower", "to": "light on nectary", "sign": "+",
    "magnitude": "shaded flowers produced less sugar and DHA; DHA reduction proportionally larger (DHA:sugar fell)",
    "scope": "attached flowers, shading treatment", "source": [S["clearwater21"]], "status": "TRACED"},
   {"of": "mānuka total nectar sugar", "to": "temperature", "sign": "+ (small)",
    "magnitude": "less important than light exposure of the nectary", "scope": "Clearwater 2021 treatments", "source": [S["clearwater21"]], "status": "TRACED"},
   {"of": "mānuka nectar yield", "to": "daytime temperature of the previous day", "sign": "+",
    "magnitude": "P < 0.001 cross-correlation; lag of 1 day", "scope": "controlled water-stress trial; drying soil had no effect",
    "source": [S["annals18"]], "status": "TRACED", "cycle_link": "CY_DAY (lagged by one period)"},
   {"of": "mānuka DHA:total sugar", "to": "temperature", "sign": "GENOTYPE-DEPENDENT",
    "magnitude": "significant clone × temperature × time-of-day interaction; some clones increase DHA:TS under sustained warmth",
    "scope": "controlled-environment clones", "source": [S["thesis"], S["mpi_pgp"]], "status": "TRACED",
    "implication": "The sign of the sensitivity is itself scoped by genotype. A single ∂/∂T for 'mānuka' would be unsupported."},
   {"of": "between-site variation (wild mānuka)", "to": "radiation; night-time temperature", "sign": "NONE (variance share, not a direction)",
    "magnitude": "radiation ≈80% of between-site variation in mean total sugar per flower; night-time temperature ≈80% of between-site variation in DHA:total sugar; but plant-to-plant variation within sites is the largest source (40–70%)",
    "scope": "wild plants across sites", "source": [S["noe19"]], "status": "TRACED"}],
 "scope_dependent_divergence": {
   "claim_a": "Temporal variation in DHA:sugar was not related to any environmental variable (controlled trial, within genotype).", "source_a": S["annals18"],
   "claim_b": "Night-time temperature accounted for ≈80% of between-site variation in DHA:total sugar (wild plants).", "source_b": S["noe19"],
   "classification": "NOT a contradiction once scoped: within-genotype temporal variance vs between-site variance of means. Both kept."},
 "classification_scheme": {"DHA:Tsugar low": "<0.001 mg/mg", "moderate": "0.001–0.002", "high": ">0.002", "source": S["williams14"],
   "note": "Inter-annual shifts low→moderate and inter-regional low→high observed (Williams 2014)."},
}

# --- Bindings: repository dependency strings -> trace nodes (PROPOSED, read-only) ---
R["repo_bindings"] = [
 {"attribute": "hexagonal_tessellation", "repo_dependency": "construction_temperature", "binds_to": ["C_FLOW_T", "REGIME_HEX"], "status": "PROPOSED"},
 {"attribute": "hexagonal_tessellation", "repo_dependency": "wax_purity", "binds_to": ["M_WAX"], "status": "PROPOSED"},
 {"attribute": "hexagonal_tessellation", "repo_dependency": "cell_type", "binds_to": [], "status": "UNKNOWN", "note": "worker vs drone cell size; no node yet"},
 {"attribute": "waggle_dance_communication", "repo_dependency": "time_of_day", "binds_to": ["CY_DAY", "I_SUNCOMPASS"], "status": "PROPOSED"},
 {"attribute": "collective_thermoregulation", "repo_dependency": "ambient_temperature", "binds_to": ["C_BROOD_T"], "status": "PROPOSED", "note": "C_BROOD_T regime: ambient 13–41 °C"},
 {"attribute": "collective_thermoregulation", "repo_dependency": "food_stores", "binds_to": ["E_BODY_HEAT", "E_NECTAR"], "status": "PROPOSED"},
 {"attribute": "swarm_coordination", "repo_dependency": "weather_window", "binds_to": ["E_SURFACE"], "status": "PROPOSED", "note": "partial; weather is more than irradiance"},
 {"attribute": "hexagonal_cell_efficiency", "repo_dependency": "golden_ratio", "binds_to": [], "status": "UNCHECKED", "note": "no trace node uses it"},
 {"attribute": "hexagonal_cell_efficiency", "repo_dependency": "pi", "binds_to": [], "status": "UNCHECKED"},
]
json.dump(R, open("reference_trace_BE_hex_v0.2.json", "w"), indent=1, ensure_ascii=False)
print(len(R["nodes"]), "nodes;", len(R["cycles"]), "cycles;", len(R["environment_differential"]["sensitivities"]), "sensitivities;", len(R["repo_bindings"]), "bindings")
