#!/usr/bin/env python3
"""
build_machine_reading.py -- writes machine_reading.json and MACHINE_READING.md for the weekly
intake of 2026-11-24 from the judgments entered by hand in READINGS below.

Python standard library only. No network.

  python3 build_machine_reading.py [FULLTEXT_DIR]

The script makes no judgment. The judgments in READINGS were entered by the machine reader
(Claude Opus 5.5 working in Perplexity Computer) and are MACHINE_READ_NOT_REVIEWED.

What the script checks, and fails on:
  - every snapshot's bytes hash to the sha256 in ../snapshots/manifest.json;
  - every candidate's abstract hashes to its abstract_sha256 in ../intake.json;
  - every quote has at most 25 words and occurs verbatim in the abstract (tags removed,
    whitespace collapsed) or, for a full-text quote, in the full-text body;
  - every candidate in ../intake.json has exactly one reading, and every stub one verdict;
  - no record carries claim_support or number_support.

FULLTEXT_DIR, when given, holds the Europe PMC fullTextXML files <PMCID>.xml that were read.
Their text is not committed. Their sha256 must equal fulltext_MANIFEST.json; the query-term
locations below are recomputed from them. Without FULLTEXT_DIR the locations are taken from
the existing machine_reading.json and full-text quotes are not re-checked (reported).
"""
import hashlib
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
INTAKE = HERE.parent
MODEL = "Claude Opus 5.5 (Anthropic), working in Perplexity Computer"
DATE = "2026-11-27"
STATE = "MACHINE_READ_NOT_REVIEWED"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def clean(s):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", s)).split())


# Query clause groups, copied from audit/2026-11-24/intake/intake_queries.json. Each group must
# match for Europe PMC to return the work; the script reports where each group matched.
GROUPS = {
    "be_comb_geometry": [r"honeycomb|comb building|comb cell", r"\bbee\b|\bApis\b"],
    "be_thermoregulation": [r"thermoregulation|brood temperature|nest temperature", r"\bApis\b|honeybee"],
    "my_phosphorus": [r"mycorrhiz", r"phosphorus", r"\btransfer"],
    "root_water_uptake": [r"root water uptake", r"soil water potential|drought"],
}

# ----------------------------------------------------------------------------- readings
# relevance: RELEVANT | PARTIAL | NOT_RELEVANT  (a machine relevance call on the touched field;
#            it is not claim_support and is not to be copied into claim_support)
# stub verdicts: FALSIFIER_MET | FALSIFIER_PARTLY_MET | FALSIFIER_NOT_MET | NOT_TESTABLE
# disposition: ACCEPT_FOR_LEDGER_CANDIDACY | NEEDS_FULL_TEXT_READER | REJECT
READINGS = {
    "43058457": dict(
        read=["abstract", "full_text"],
        measured="Apis mellifera foragers from high-propolis vs ordinary colonies (hives of about 3,000-3,500 workers, per methods). Antennal morphology, antennal RNA-seq, qRT-PCR of 58 genes in three olfactory gene families (6 CSPs, 19 OBPs, 34 ORs). Effect: antennae and flagellomeres FL7, FL10 shorter in high-propolis colonies.",
        field_claim="Wax economy of hexagonal cells relative to the next-best regular tessellation (honeycomb conjecture).",
        relevance="NOT_RELEVANT",
        reason="Olfaction and propolis foraging. Nothing on comb geometry, cell shape or wax. The word 'honeycomb' occurs once, in a rearing sentence in the methods.",
        lexical=["'honeycomb' (one rearing sentence in the methods: pupae placed on comb to emerge)",
                 "numbers '7' and '10' extracted by the deviation extractor are flagellomere names FL7 and FL10, not quantities"],
        quotes=[("abstract", "We compared the antennal morphology and RNA-seq profiles of foragers from high propolis-producing and ordinary colonies of A. mellifera worker bees")],
        stubs={},
        disposition="REJECT",
        disposition_reason="Does not bear on BE.hexagonal_cell_efficiency. The query matched on full text only.",
    ),
    "43056305": dict(
        read=["abstract", "full_text"],
        measured="Apis mellifera ligustica colonies moved between low and high altitude (554 m to 3,637 m) on the Tibetan Plateau, 2023-2024, plus low-altitude colonies held under hypoxia. Varroa destructor fecundity and offspring development, e.g. no mated adult female mite offspring in n = 178 infested cells at high altitude. Full text only: brood-nest temperature and humidity were logged every 5 min in 3 colonies at each of 2 sites as a confound check. Site means were 34.1-34.2 C and 34.4-34.6 C. Worker brood development was not delayed (about 21 days egg to adult).",
        field_claim="Precision (SD) of honeybee brood-nest temperature about a 35 C target across ambient -30 C to +45 C.",
        relevance="PARTIAL",
        reason="The abstract does not address thermoregulation: its subject is mite reproduction under hypoxia. The full text has a small side measurement of brood-nest temperature at two very different sites. It reports means only. The SD the field defines is not given in the text, and the 5-min series are in S1/S2 Data, which were not read. This is a lead for the field, not a reading of it.",
        lexical=["the query's 'nest temperature' matched only the full text's confound-check section, not the abstract"],
        quotes=[("abstract", "highlights a previously unrecognized sensitivity of this mite to reduced oxygen availability"),
                ("full_text", "ranging from 34.1 to 34.2 °C in Lhasa and 34.4 to 34.6 °C in Xishuangbanna")],
        stubs={"HX4": ("FALSIFIER_MET", "Oxygen acts on the mite, not on the colony's thermoregulation. BE.collective_thermoregulation lists colony_size, ambient_temperature and food_stores, not oxygen. The full text reports that worker development was not delayed under hypoxia.")},
        disposition="NEEDS_FULL_TEXT_READER",
        disposition_reason="An abstract-only reading would find nothing for this field. Any use of the brood-nest series needs S1/S2 Data and a full-text reading, which the declared pass ('reads: abstract only') does not cover. That is the owner's decision. Reject the HX4 stub either way.",
    ),
    "43048754": dict(
        read=["abstract", "full_text"],
        measured="Bombus impatiens lab-reared incipient nests: 75 queens in four configurations (queen alone n = 29; +1 male n = 18; +3 males n = 15; +5 males n = 13), colonies at about 24-27 C. FLIR T650sc thermal imaging (stated accuracy +/-1 C) over 28 days. Males incubate brood, nest development improves with males present, and males keep a larger thorax-abdomen temperature differential than queens.",
        field_claim="Precision (SD) of honeybee (Apis) cluster brood-nest temperature about 35 C across ambient -30 C to +45 C.",
        relevance="PARTIAL",
        reason="Brood incubation in a social bee is on the same subject. But the genus differs (Bombus, not Apis), the measure is individual body-surface temperature, not colony brood-nest precision, and ambient temperature was held constant, so precision across ambient was not tested.",
        lexical=["the query's '(Apis OR honeybee)' clause matched only 'honeybee-collected pollen' and 'honeybee wax' in the methods; the study organism is Bombus",
                 "'temperature' (HX4) here is heat produced by incubating bees, not an ambient condition"],
        quotes=[("abstract", "males maintain a greater heat differential between the thorax and abdomen during incubation, suggesting sex-specific differences in thermal regulation")],
        stubs={"HX4": ("FALSIFIER_MET", "The dependency runs the other way. The temperatures named are produced by the insects (thorax heat), while ambient was held near 27 C. The field's dependency, ambient_temperature, was not varied.")},
        disposition="REJECT",
        disposition_reason="Does not bear on the Apis field as defined. Using it as a cross-taxon example (cross_domain_examples) would be the owner's call. It is not evidence for the value.",
    ),
    "43050400": dict(
        read=["abstract", "full_text"],
        measured="Vespa mandarinia (giant hornet) gynes, workers and males across life stages. Brain biogenic amines (dopamine-, serotonin-related) by HPLC-type quantification, ovarian development and lipid storage. Dopamine was higher in gynes and serotonin higher in workers.",
        field_claim="Precision of honeybee brood-nest temperature maintenance.",
        relevance="NOT_RELEVANT",
        reason="Hornet neurochemistry, with no thermoregulation measured. The query matched 'thermoregulation' in one introduction sentence about honey bees, and 'honeybee' in an author affiliation ('Honeybee Science Research Center').",
        lexical=["'thermoregulation' in one citation sentence of the introduction",
                 "'honeybee' in an author affiliation"],
        quotes=[("abstract", "we investigated levels of biogenic amines in the brain, lipid storage and ovarian development in the abdomen at different life stages")],
        stubs={},
        disposition="REJECT",
        disposition_reason="Off-organism and off-subject. A full-text-only match.",
    ),
    "43041999": dict(
        read=["abstract", "full_text"],
        measured="Narrative review (no new data) of arbuscular mycorrhizal fungi in maize: diversity, arbuscule-mediated exchange, host genotype, P availability, field reliability. Proposes a six-stage 'Maize-Soil-AMF Fit Framework'. The full text cites a 33P-uptake result for a ZmPT6 transporter mutant but gives no transfer fraction.",
        field_claim="Fraction of radiotracer-labelled P mobilised by mycorrhizal hyphae that reaches host roots within 72 h under field-comparable pot conditions. The value 0.85 'represents ectomycorrhizal networks in temperate forest soils'.",
        relevance="PARTIAL",
        reason="On the subject of mycorrhizal P exchange and its dependence on soil P availability. But it is a review of AMF in maize, not ECM in temperate forest; there is no radiotracer fraction and no 72 h window. Its own caveat is that colonisation does not establish transfer.",
        lexical=[],
        quotes=[("abstract", "Root colonization alone does not establish effective nutrient transfer or net crop benefit."),
                ("abstract", "It is a conceptual decision aid, not a validated predictive model.")],
        stubs={"HX4": ("FALSIFIER_NOT_MET", "Soil phosphorus availability is named as a condition of AMF benefit, and the field lists soil_phosphorus_availability as a dependency. The direction is condition to entity.")},
        disposition="ACCEPT_FOR_LEDGER_CANDIDACY",
        disposition_reason="Worth a reading-ledger entry once the owner registers the source. An outside reader would decide claim_support; this reading assigns none. It does not state the field's number, and its fungal group (AMF) is outside the value's stated ECM scope.",
    ),
    "43041303": dict(
        read=["abstract", "full_text"],
        measured="Cucumis metuliferus fruit grown in greenhouse vs shade net with organic vs chemical fertiliser. Fruit mineral and phytochemical content, e.g. P 577.7 mg/100 g DW under shade net plus chemical fertiliser.",
        field_claim="Mycorrhizal hyphal P transfer fraction to host roots.",
        relevance="NOT_RELEVANT",
        reason="Fruit tissue P concentration under fertiliser treatments. No mycorrhizal treatment or measure. 'Mycorrhiza' occurs once, in the discussion, and 'transfer' refers to transplanting seedlings and phloem nutrient transfer.",
        lexical=["'phosphorus' = fruit mineral content", "'transfer' = seedlings transferred to containers; leaf-to-fruit transfer",
                 "'mycorrhiza' once in the discussion"],
        quotes=[("abstract", "increased phosphorus (577.7 mg/100g DW) and potassium (1074 mg/100g DW) compared to other treatments")],
        stubs={"HX4": ("NOT_TESTABLE", "The work does not study MY. 'Nutrient' is fruit nutritional content, not a condition of a mycorrhizal network.")},
        disposition="REJECT",
        disposition_reason="Food composition work. The intake design document already named it as a broad-term false positive.",
    ),
    "43062778": dict(
        read=["abstract", "full_text"],
        measured="Literature review of the composition of tomato plants and by-products as sheep feed (proximate, fibre, minerals, bioactives; intake, digestibility).",
        field_claim="Mycorrhizal hyphal P transfer fraction to host roots.",
        relevance="NOT_RELEVANT",
        reason="Ruminant nutrition. 'Mycorrhizal' occurs once (amino-acid content as affected by AM status), and 'transfer' occurs once ('lipid transfer protein').",
        lexical=["'transfer' in 'lipid transfer protein'", "'phosphorus' as a feed mineral", "'mycorrhizal' once"],
        quotes=[("abstract", "This review evaluated the nutritional composition and feeding potential of S. lycopersicum-derived materials in sheep nutrition")],
        stubs={"HX4": ("NOT_TESTABLE", "The work does not study MY. 'Nutrient' means feed nutrients.")},
        disposition="REJECT",
        disposition_reason="Off-subject. A full-text-only match.",
    ),
    "43061600": dict(
        read=["abstract", "full_text"],
        measured="Review (no new data) of ectomycorrhizal fungi in deep forest soil horizons: vertical community turnover, methods (long-read metabarcoding, isotopes), and possible roles in carbon translocation, N and P mobilisation, and hydraulic redistribution. There is no P transfer fraction and no 32P/33P tracer result.",
        field_claim="Fraction of radiotracer-labelled P reaching host roots within 72 h. The value 0.85 'represents ectomycorrhizal networks in temperate forest soils'.",
        relevance="PARTIAL",
        reason="The same fungal group and ecosystem as the value's stated scope, and it names P mobilisation. The language is hedged ('might contribute'), it gives no fraction and no time window, and it states that deep-soil ECM function is under-measured.",
        lexical=["'oxygen', 'water', 'carbon' (HX4) refer to deep-soil gradients and network outputs, not to the P-transfer field"],
        quotes=[("abstract", "the mobilization of nitrogen and phosphorus pools that are otherwise poorly accessible"),
                ("abstract", "deep-soil ECM fungi remain underrepresented in experimental studies and ecosystem models")],
        stubs={"HX4": ("FALSIFIER_PARTLY_MET", "Nutrient and soil hold: they are conditions the field depends on (soil_phosphorus_availability). Oxygen is named as a driver of ECM community turnover, which is not a declared dependency of this field. Carbon and water are what the network moves (translocation, hydraulic redistribution), so for them the dependency runs the other way.")},
        disposition="ACCEPT_FOR_LEDGER_CANDIDACY",
        disposition_reason="Worth a reading-ledger entry once the owner registers the source. It may also inform the field's measurement_limits (depth). This reading assigns no claim_support and does not state the number.",
    ),
    "43043610": dict(
        read=["abstract", "full_text"],
        measured="Rhizopus sp. TYR1 (a non-mycorrhizal rhizosphere fungus) on fragrant rice, in field trials (2023, 2024), pots, hydroponics and plates. Grain 2-AP +38.04% and +48.37%. Tolerance to five stresses including P deficiency (shoot fresh weight +25-62%). A JA-proline mechanism (JA x2.8, proline x2.1).",
        field_claim="Mycorrhizal hyphal P transfer fraction to host roots.",
        relevance="NOT_RELEVANT",
        reason="The fungus is not mycorrhizal, P deficiency is one of five stress treatments, and no P transfer is measured. 'Mycorrhiz' occurs only in discussion citations (Laccaria, AMF signalling).",
        lexical=["'phosphorus' as a stress treatment", "'transfer' = seedlings/soil transferred (methods)",
                 "'mycorrhiz' in discussion citations"],
        quotes=[("abstract", "enhancing tolerance to five abiotic stresses (phosphorus deficiency, iron deficiency, cadmium toxicity, salt, and drought)")],
        stubs={"HX4": ("NOT_TESTABLE", "The work does not study MY (Rhizopus is not mycorrhizal).")},
        disposition="REJECT",
        disposition_reason="Off-entity. A full-text-only match on the conjunction of terms.",
    ),
    "43047453": dict(
        read=["abstract", "full_text"],
        measured="Grass-alone vs grass-legume Urochloa pastures on seven farms in Colombian Amazonia, with biomass over six harvests and 15N natural abundance. Biomass benefit of 1.6 t/ha, and more than 70% of legume N from the atmosphere.",
        field_claim="Mycorrhizal hyphal P transfer fraction to host roots.",
        relevance="NOT_RELEVANT",
        reason="Nitrogen fixation and nitrification inhibition. AM colonisation is mentioned once in the discussion, and 'transfer' means legume-to-grass N transfer.",
        lexical=["'transfer' = legume N transfer", "'phosphorus' = soil P pool (background)", "'mycorrhiza' once in the discussion"],
        quotes=[("abstract", "More than 70% of the legume N was derived from atmosphere")],
        stubs={"HX4": ("NOT_TESTABLE", "The work does not study MY. The nutrient is N.")},
        disposition="REJECT",
        disposition_reason="Off-subject. A full-text-only match.",
    ),
    "43061529": dict(
        read=["abstract", "full_text"],
        measured="Review of rapid food-composition methods (NIR, Raman, hyperspectral, ML) and their link to human nutrient bioavailability.",
        field_claim="Mycorrhizal hyphal P transfer fraction to host roots.",
        relevance="NOT_RELEVANT",
        reason="Human nutrition methods. One sentence on mycorrhizal association and soil micronutrients. 'Transfer' means intestinal transfer and model transferability.",
        lexical=["'transfer' = lumen-to-body transfer; calibration-model transfer", "'phosphorus' = predicted by NIR",
                 "'mycorrhizal' once"],
        quotes=[("abstract", "these techniques alone do not determine biological availability")],
        stubs={"HX4": ("NOT_TESTABLE", "The work does not study MY.")},
        disposition="REJECT",
        disposition_reason="Off-subject. A full-text-only match.",
    ),
    "43041360": dict(
        read=["abstract", "full_text"],
        measured="Cacao soil microbiome (16S/ITS amplicons) in a multi-location Brazilian breeding trial (4 regions, 2 scions, drip-irrigated vs rainfed). Irrigation and nutrient management explained 13% of fungal beta diversity. No AM genera were identified in the scion analysis; one putative AM ASV was less abundant under drip irrigation (full text).",
        field_claim="Mycorrhizal hyphal P transfer fraction to host roots.",
        relevance="NOT_RELEVANT",
        reason="Community composition only, with no P transfer or mycorrhizal function measured. 'Phosphorus' appears as a soil-test method and 'transfer' as sample handling.",
        lexical=["'phosphorus' = soil available-P method", "'transfer' = soil aliquot transferred; carbon transfer in discussion"],
        quotes=[("abstract", "Irrigation and nutrient management explained 13% of fungal beta diversity")],
        stubs={"HX4": ("NOT_TESTABLE", "The work does not study MY. The conditions act on the bulk soil microbiome.")},
        disposition="REJECT",
        disposition_reason="Off-subject for this field. A full-text-only match.",
    ),
    "43061155": dict(
        read=["abstract", "full_text"],
        measured="Five Populus taxa compared by transcriptomics, then PtrERF54 and PtrERD7 overexpression in poplar 84K under drought. Leaf wilting, electrolyte leakage, antioxidant enzymes, gas exchange (stomatal conductance, transpiration, instantaneous WUE). Soil water potential was measured as the treatment condition.",
        field_claim="Fraction of available soil water extracted per unit root length per day at field capacity, relative to the theoretical maximum.",
        relevance="NOT_RELEVANT",
        reason="Leaf-level drought tolerance and gene regulation. Root water extraction and root architecture were not measured. 'Root water uptake' occurs once, in the introduction.",
        lexical=["'water-use efficiency' (leaf C gain per water transpired) is not 'water_uptake_efficiency'",
                 "'sunlight' (HX4) matched 'photosynthetic' via the photosynth* pattern",
                 "numbers '54', '7', '84K' are gene and clone names"],
        quotes=[("abstract", "PtrERF54-OE lines maintained reduced stomatal conductance and transpiration rates without compromising photosynthetic carbon assimilation, thereby increasing instantaneous water-use efficiency.")],
        stubs={"HX4": ("FALSIFIER_PARTLY_MET", "Water (drought / soil water potential) holds as a condition the field depends on (soil_water_potential). Carbon (leaf assimilation, an output) and sunlight (lexical: 'photosynthetic') do not.")},
        disposition="REJECT",
        disposition_reason="Does not bear on root water uptake efficiency.",
    ),
    "43047459": dict(
        read=["abstract", "full_text"],
        measured="Factorial warming x drought on six temperate grassland species in soils from intensively vs extensively managed grasslands (240 pots, n = 10 per cell). N content and biomass in soil, microbes, roots and shoots. Drought cut plant biomass by about 40%; warming cut microbial biomass by up to 30%.",
        field_claim="Fraction of available soil water extracted per unit root length per day at field capacity.",
        relevance="NOT_RELEVANT",
        reason="Nitrogen flows and biomass under drought. Root water uptake is not measured; the phrase occurs once, in the discussion.",
        lexical=["'drought' is the treatment; it satisfied the query's OR-clause without any water-uptake measurement"],
        quotes=[("abstract", "this advantage disappeared under drought, reducing plant biomass by\u2009~\u200940%")],
        stubs={"HX1": ("FALSIFIER_MET", "'~40%' is the reduction in plant biomass under drought, and '~20%' is the increase in microbial biomass in Ext soils. Neither is the field's water-extraction fraction."),
               "HX4": ("FALSIFIER_PARTLY_MET", "Water (drought) and soil hold as conditions the field depends on. Nutrient (N) is the response studied, not a condition of water uptake.")},
        disposition="REJECT",
        disposition_reason="Off-subject for this field.",
    ),
    "43045997": dict(
        read=["abstract", "full_text"],
        measured="Three Pelargonium graveolens cultivars at 0-200 mM NaCl in a greenhouse. Biomass (-26.8% to -37.3% at 200 mM), K+/Na+ ratio, antioxidant enzymes, anatomy, essential-oil yield and composition.",
        field_claim="Fraction of available soil water extracted per unit root length per day at field capacity.",
        relevance="NOT_RELEVANT",
        reason="Salinity tolerance, with no water-uptake measurement. 'Root water uptake' occurs once and 'drought' once, both in introduction or discussion prose.",
        lexical=["'sunlight' (HX4) matched 'photosynthetic'",
                 "K+/Na+ ratios 0.68 / 0.56 / 0.38 were tagged DEVIATION_CANDIDATE by the extractor; they are ion ratios between cultivars"],
        quotes=[("abstract", "maintaining a higher K⁺/Na⁺ ratio (0.68) than CIM Bio-171 (0.56) and CIM Bharat (0.38)")],
        stubs={"HX1": ("FALSIFIER_MET", "0.68, 0.56 and 0.38 are K+/Na+ ion ratios, not a water-extraction fraction."),
               "HX4": ("FALSIFIER_MET", "The only term found, 'sunlight', is a lexical match on 'photosynthetic'. The work's actual condition, salinity (osmotic stress), is not in the term list.")},
        disposition="REJECT",
        disposition_reason="Off-subject. A full-text-only match.",
    ),
}

# Observed outside the 15, while testing query proposals on 2026-11-27 (read-only searches).
LATE_INDEXED = {
    "note": "Re-running the unchanged seed queries for the same window on 2026-11-27 returned more works than the snapshot: root_water_uptake 5 (snapshot 3), my_phosphorus 14 (snapshot 10). The extra works have FIRST_IDATE 2026-11-23 or 2026-11-24, so they were indexed after the run. They are not candidates here. One abstract was read (below); the others are UNCHECKED.",
    "read": {"pmid": "43069007", "title": "Combined Rhizophagus irregularis and Bacillus megaterium inoculation e[...] (title cut by the reader)",
             "first_index_date": "2026-11-23", "read": "abstract",
             "note": "Maize with an AM fungus plus a PGPR under K deficiency and drought. The abstract names enhanced root hydraulic conductivities. A plausible PARTIAL for ROOT_NET.water_uptake_efficiency and MY, which the run missed because of the window edge."},
    "unchecked_pmids": ["43075482", "43071297", "43073734", "43062364"],
}


def main():
    ftdir = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    intake = json.loads((INTAKE / "intake.json").read_text(encoding="utf-8"))
    man = json.loads((INTAKE / "snapshots" / "manifest.json").read_text(encoding="utf-8"))
    ftman = json.loads((HERE / "fulltext_MANIFEST.json").read_text(encoding="utf-8"))
    prompt_sha = sha((HERE / "reading_prompt.md").read_bytes())
    fails = []

    abstracts, pmcids, titles = {}, {}, {}
    for e in man["entries"]:
        b = (INTAKE / "snapshots" / e["file"]).read_bytes()
        if sha(b) != e["sha256"]:
            fails.append(f"snapshot {e['file']} sha256 differs from manifest")
        for r in json.loads(b)["resultList"]["result"]:
            if r.get("pmid"):
                abstracts[r["pmid"]] = r.get("abstractText", "")
                pmcids[r["pmid"]] = r.get("pmcid")
                titles[r["pmid"]] = r.get("title", "")

    prev = {}
    if (HERE / "machine_reading.json").exists():
        prev = {c["pmid"]: c for c in json.loads((HERE / "machine_reading.json").read_text(encoding="utf-8"))["candidates"]}

    out = []
    stub_by_cand = {}
    for h in intake["hypotheses"]:
        stub_by_cand.setdefault(h["touches"]["candidate"], []).append(h)
    seen = set()
    for c in intake["candidates"]:
        p = c["work"]["pmid"]
        R = READINGS.get(p)
        if R is None:
            fails.append(f"no reading for candidate {c['id']}")
            continue
        seen.add(p)
        a = abstracts[p]
        if sha(a.encode()) != c["work"]["abstract_sha256"]:
            fails.append(f"{p}: abstract sha256 differs from intake.json")
        ta = clean(titles[p] + " " + a)
        pmc = pmcids[p]
        ft_body = None
        if ftdir:
            fb = (ftdir / f"{pmc}.xml").read_bytes()
            if sha(fb) != ftman["files"][pmc]["sha256"]:
                fails.append(f"{pmc}: full text sha256 differs from fulltext_MANIFEST.json")
            x = fb.decode("utf-8")
            ft_refs = clean(" ".join(re.findall(r"<ref-list.*?</ref-list>", x, re.S)))
            ft_body = clean(re.sub(r"<ref-list.*?</ref-list>", "", x, flags=re.S))
            locs = []
            for g in GROUPS[c["query_id"]]:
                locs.append({"pattern": g,
                             "title_or_abstract": len(re.findall(g, ta, re.I)),
                             "full_text_body": len(re.findall(g, ft_body, re.I)),
                             "full_text_reference_list": len(re.findall(g, ft_refs, re.I))})
        else:
            locs = prev.get(p, {}).get("query_clause_locations")
            if locs is None:
                fails.append(f"{p}: no FULLTEXT_DIR and no earlier locations")
        all_in_ta = all(l["title_or_abstract"] > 0 for l in (locs or []))
        qs = []
        for src, q in R["quotes"]:
            n = len(q.split())
            if n > 25:
                fails.append(f"{p}: quote over 25 words ({n})")
            hay = clean(a) if src == "abstract" else ft_body
            if hay is None:
                print(f"NOTE {p}: full-text quote not re-checked (no FULLTEXT_DIR)")
            elif clean(q) not in hay:
                fails.append(f"{p}: quote not verbatim in {src}: {q[:60]}")
            qs.append({"source": src, "quote": q, "words": n})
        stubs = []
        for h in stub_by_cand.get(c["id"], []):
            v = R["stubs"].get(h["rule"])
            if v is None:
                fails.append(f"{p}: no verdict for stub {h['id']}")
                continue
            stubs.append({"stub_id": h["id"], "rule": h["rule"], "evidence_spans": h["evidence_spans"],
                          "verdict": v[0], "reason": v[1]})
        if len(stubs) != len(R["stubs"]):
            fails.append(f"{p}: verdict count differs from stub count")
        out.append({
            "candidate_id": c["id"], "pmid": p, "pmcid": pmc, "doi": c["work"]["doi"],
            "title": c["work"]["title"], "query_id": c["query_id"],
            "touches": {"entity": c["touches"]["entity"], "field": c["touches"]["field"],
                        "value": c["touches"]["value"], "claim_sha256": c["touches"]["claim_sha256"]},
            "read": R["read"], "abstract_sha256": c["work"]["abstract_sha256"],
            "fulltext_sha256": ftman["files"][pmc]["sha256"],
            "query_clause_locations": locs, "all_query_clauses_in_title_or_abstract": all_in_ta,
            "measured": R["measured"], "field_claim_paraphrase": R["field_claim"],
            "relevance": R["relevance"], "relevance_reason": R["reason"],
            "lexical_false_positives": R["lexical"], "quotes": qs, "stub_verdicts": stubs,
            "disposition": R["disposition"], "disposition_reason": R["disposition_reason"],
            "reading_state": STATE, "reader": MODEL, "prompt_sha256": prompt_sha, "date": DATE,
            "status": "PROPOSED",
        })
    for p in READINGS:
        if p not in seen:
            fails.append(f"reading for {p} has no candidate")
    def keys(o):
        if isinstance(o, dict):
            for k, v in o.items():
                yield k
                yield from keys(v)
        elif isinstance(o, list):
            for v in o:
                yield from keys(v)
    for rec in out:
        bad = {"claim_support", "number_support"} & set(keys(rec))
        if bad:
            fails.append(f"{rec['pmid']}: record carries {sorted(bad)}")

    rel = {k: sum(1 for r in out if r["relevance"] == k) for k in ("RELEVANT", "PARTIAL", "NOT_RELEVANT")}
    disp = {k: sum(1 for r in out if r["disposition"] == k) for k in ("ACCEPT_FOR_LEDGER_CANDIDACY", "NEEDS_FULL_TEXT_READER", "REJECT")}
    sv = {}
    for r in out:
        for s in r["stub_verdicts"]:
            sv.setdefault(s["rule"], {}).setdefault(s["verdict"], 0)
            sv[s["rule"]][s["verdict"]] += 1
    by_q = {}
    for r in out:
        d = by_q.setdefault(r["query_id"], {"candidates": 0, "RELEVANT": 0, "PARTIAL": 0, "NOT_RELEVANT": 0, "all_clauses_in_title_or_abstract": 0})
        d["candidates"] += 1
        d[r["relevance"]] += 1
        d["all_clauses_in_title_or_abstract"] += int(r["all_query_clauses_in_title_or_abstract"])
    summary = {
        "candidates": len(out), "relevance": rel, "dispositions": disp,
        "precision_strict": f"{rel['RELEVANT']}/{len(out)}",
        "precision_lenient_relevant_or_partial": f"{rel['RELEVANT'] + rel['PARTIAL']}/{len(out)}",
        "ledger_worthy": f"{disp['ACCEPT_FOR_LEDGER_CANDIDACY']}/{len(out)}",
        "all_query_clauses_in_title_or_abstract": sum(int(r["all_query_clauses_in_title_or_abstract"]) for r in out),
        "by_query": by_q, "stub_verdicts": sv,
    }
    doc = {
        "record": "WEEKLY_INTAKE_MACHINE_READING",
        "status": "PROPOSED; MACHINE_READ_NOT_REVIEWED. Not an owner decision; no claim_support or number_support is written.",
        "intake": "intake/weekly/2026-11-24/intake.json",
        "intake_sha256": sha((INTAKE / "intake.json").read_bytes()),
        "reader": MODEL, "prompt": "reading_prompt.md", "prompt_sha256": prompt_sha, "date": DATE,
        "reading_state": STATE,
        "vocabulary": {
            "relevance": "RELEVANT | PARTIAL | NOT_RELEVANT: a machine relevance call on the touched field's scope.definition. Not claim_support; it does not map onto claim_support.",
            "stub_verdict": "FALSIFIER_MET | FALSIFIER_PARTLY_MET | FALSIFIER_NOT_MET | NOT_TESTABLE (the work does not study the touched entity)",
            "disposition": "ACCEPT_FOR_LEDGER_CANDIDACY (worth an outside reader's reading-ledger entry once the source is registered) | NEEDS_FULL_TEXT_READER | REJECT",
        },
        "limits": "One machine reader, no second reading. Full texts were read to locate query terms and to check the abstract's scope. No supplementary data were read. Full-text text is not committed; its sha256 is in fulltext_MANIFEST.json.",
        "summary": summary, "candidates": out, "outside_the_15": LATE_INDEXED,
    }
    if fails:
        for f in fails:
            print("FAIL", f)
        raise SystemExit(1)
    (HERE / "machine_reading.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
