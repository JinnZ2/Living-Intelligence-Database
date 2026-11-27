# Machine reading of the weekly intake to 2026-11-24

Status: PROPOSED. `reading_state: MACHINE_READ_NOT_REVIEWED`. Reader: Claude Opus 5.5 (Anthropic), working in Perplexity Computer. Date: 2026-11-27. Prompt: `reading_prompt.md`, sha256 `19d1869f1d59a9d91767585a33be3c04e458b0d04c821f3d25f5a68dd8129fa1`.

This is not a person's reading, and it is not an owner decision. Whether any of it counts as reviewed is the owner's call.

## What this reading may and may not write

These rules come from the repository:

- Amendment "weekly intake (source pass, stage 0)" in `registry/DECLARED.json` says `claim_support` is written only by an outside reader under "NOT_ADDRESSED + reading queue". The optional machine-reading slot in `audit/2026-11-24/intake/weekly_intake.py` and `weekly_science_intake.yml` says a machine reading must carry the model name, the prompt sha256 and `reading_state MACHINE_READ_NOT_REVIEWED`, and must not write `claim_support`. So no record here carries `claim_support` or `number_support`. `build_machine_reading.py` fails if one does.
- A reading-ledger entry needs the source registered in `registry/sources.json` first (crosswalk document, "The weld between intake and readings"). Registration is a declared step for the owner. This reading registers nothing, and nothing in `ontology/` or `registry/` is edited. `intake.json`, `intake.md` and `snapshots/` are unchanged; this folder only adds files.
- Quotes are verbatim and at most 25 words. Each says whether it comes from the abstract or the full text.
- The declared intake reads abstracts only. This reading also read each open-access full text, to find where the query terms matched and to check what the abstract leaves out. That goes beyond the intake's declared scope, so every full-text observation is marked as such. Full-text bytes are not committed; their sha256 is in `fulltext_MANIFEST.json`, following `provenance/as_received/abstracts_MANIFEST.json`. No supplementary data were read (UNCHECKED).

Vocabulary used here (PROPOSED, this file only):

- **relevance** (RELEVANT / PARTIAL / NOT_RELEVANT): does the work bear on the touched field's `scope.definition`? This is a machine relevance call. It is not `claim_support` and does not map onto it.
- **stub verdict** (FALSIFIER_MET / FALSIFIER_PARTLY_MET / FALSIFIER_NOT_MET / NOT_TESTABLE): checked against each stub's own falsifier. NOT_TESTABLE means the work does not study the touched entity.
- **disposition** (ACCEPT_FOR_LEDGER_CANDIDACY / NEEDS_FULL_TEXT_READER / REJECT).

## How intake.md's columns are defined

From `weekly_intake.py` stage 3:

- **Value** is the touched field's current value, copied from the entity file. It is not a number from the work. For example, 0.94 is `BE.collective_thermoregulation.value`.
- **First quote candidate** is the first abstract sentence that contains one of the query's `terms`, cut at 25 words. It is a sentence that matched a term, not a supporting quote. "(no sentence contains a query term)" means no such sentence exists.
- **Flags**: G1 retraction or notice, G2 preprint. No candidate this week carries a flag.

## Checks

- All five snapshots hash to `snapshots/manifest.json` (OBSERVED).
- All 15 abstracts hash to their `abstract_sha256` (OBSERVED).
- All 15 works are open access. Full text was fetched from Europe PMC `fullTextXML` and read for all 15 (OBSERVED).
- `python3 build_machine_reading.py /tmp/ft` rebuilds `machine_reading.json` and re-checks every quote and hash. Without the full-text directory, it re-checks everything except full-text quotes.

## Per-candidate readings

"Clauses in T/A": whether every AND-clause of the query matches in the title or abstract. Where it says "no", Europe PMC matched the work on its full text.

| Work | Touches | What the work measured | Relevance | Stubs | Clauses in T/A | Disposition |
|---|---|---|---|---|---|---|
| PMID 43058457, propolis-yield antennal RNA-seq, *Apis mellifera* | BE.hexagonal_cell_efficiency (0.97) | Antennal morphology and RNA-seq of 58 olfactory genes in foragers from high- vs ordinary-propolis colonies | NOT_RELEVANT: nothing on comb or cell geometry; 'honeycomb' appears once, in a rearing sentence | none | no | REJECT |
| PMID 43056305, hypoxia and *Varroa* in Tibetan honey bees | BE.collective_thermoregulation (0.94) | Translocation 554–3,637 m and hypoxia treatment; mite fecundity (n = 178 cells with no mated female offspring at altitude). Full text only: brood-nest temperature logged in 3 colonies at each of 2 sites, site means 34.1–34.6 °C | PARTIAL (full text only): a side confound check reports means, not the SD the field defines; the series are in S1/S2 Data (UNCHECKED) | HX4 FALSIFIER_MET: oxygen acts on the mite and is not among the field's dependencies | no | NEEDS_FULL_TEXT_READER; reject HX4 |
| PMID 43048754, male bumblebee brood care | BE.collective_thermoregulation | *Bombus impatiens* lab nests (75 queens, 4 configurations), FLIR imaging; males incubate and keep a larger thorax–abdomen heat differential | PARTIAL: same subject, but a different genus, individual body temperature, and ambient held constant | HX4 FALSIFIER_MET: the temperature named is heat the bees produce, so the dependency runs the other way | no | REJECT for this field; a cross-taxon example is the owner's call |
| PMID 43050400, *Vespa mandarinia* brain amines | BE.collective_thermoregulation | Brain dopamine and serotonin, ovaries and lipid stores by caste and life stage | NOT_RELEVANT: matched on one intro citation and a "Honeybee Science Research Center" affiliation | none | no | REJECT |
| PMID 43041999, AMF in maize (review) | MY.phosphorus_transfer_efficiency (0.85) | Narrative review and decision framework; no new data, no transfer fraction | PARTIAL: on mycorrhizal P exchange, but AMF in maize rather than the value's stated ECM temperate-forest scope; no radiotracer fraction or 72 h window | HX4 FALSIFIER_NOT_MET: soil P availability is a declared dependency | yes | ACCEPT_FOR_LEDGER_CANDIDACY |
| PMID 43041303, African horned cucumber fruit | MY.phosphorus_transfer_efficiency | Fruit minerals under fertiliser and growing environment (P 577.7 mg/100 g DW) | NOT_RELEVANT: fruit tissue P, with no mycorrhizal treatment | HX4 NOT_TESTABLE | no | REJECT |
| PMID 43062778, tomato by-products as sheep feed (review) | MY.phosphorus_transfer_efficiency | Feed composition review | NOT_RELEVANT: 'transfer' appears only in "lipid transfer protein" | HX4 NOT_TESTABLE | no | REJECT |
| PMID 43061600, ectomycorrhizal fungi in deep soils (review) | MY.phosphorus_transfer_efficiency | Review; vertical community turnover and possible N and P mobilisation; no fraction, no tracer | PARTIAL: same fungal group and ecosystem as the value's scope; hedged language, no number | HX4 FALSIFIER_PARTLY_MET: nutrient and soil hold; oxygen is not a declared dependency; carbon and water are network outputs | no | ACCEPT_FOR_LEDGER_CANDIDACY |
| PMID 43043610, *Rhizopus* TYR1 on fragrant rice | MY.phosphorus_transfer_efficiency | Non-mycorrhizal fungus; 2-AP +38–48%; tolerance to 5 stresses including P deficiency | NOT_RELEVANT: the fungus is not mycorrhizal and no P transfer is measured | HX4 NOT_TESTABLE | no | REJECT |
| PMID 43047453, grass–legume pastures, Amazonia | MY.phosphorus_transfer_efficiency | N fixation and biological nitrification inhibition on 7 farms; >70% of legume N from the atmosphere | NOT_RELEVANT: N, not mycorrhizal P | HX4 NOT_TESTABLE | no | REJECT |
| PMID 43061529, food composition and bioavailability (review) | MY.phosphorus_transfer_efficiency | Human-nutrition analytical methods | NOT_RELEVANT | HX4 NOT_TESTABLE | no | REJECT |
| PMID 43041360, cacao soil microbiome | MY.phosphorus_transfer_efficiency | Amplicon community composition; irrigation and nutrient management explain 13% of fungal beta diversity | NOT_RELEVANT: composition only, no P transfer | HX4 NOT_TESTABLE | no | REJECT |
| PMID 43061155, ERF54–ERD7 in *Populus* | ROOT_NET.water_uptake_efficiency (0.93) | Transgenic poplar under drought: gas exchange, instantaneous WUE, antioxidants | NOT_RELEVANT: leaf water-use efficiency, not root water extraction | HX4 FALSIFIER_PARTLY_MET: water holds; carbon and sunlight ('photosynthetic') do not | no | REJECT |
| PMID 43047459, drought and warming, grassland N | ROOT_NET.water_uptake_efficiency | 240 pots, 6 species, warming × drought; N pools and biomass | NOT_RELEVANT: no water-uptake measure | HX1 FALSIFIER_MET: ~40% and ~20% are biomass changes. HX4 FALSIFIER_PARTLY_MET | no | REJECT |
| PMID 43045997, salt stress in *Pelargonium* | ROOT_NET.water_uptake_efficiency | 3 cultivars at 0–200 mM NaCl; biomass, K⁺/Na⁺ ratio, essential oil | NOT_RELEVANT | HX1 FALSIFIER_MET: 0.68, 0.56 and 0.38 are K⁺/Na⁺ ratios. HX4 FALSIFIER_MET: 'sunlight' matched 'photosynthetic' | no | REJECT |

Full per-candidate records are in `machine_reading.json`: the reason, the lexical false positives, the quotes with their source, the query-clause counts by location, and the hashes.

## Precision

- Strict (RELEVANT): 0 of 15. No work states or measures a field's defined quantity.
- Lenient (RELEVANT or PARTIAL): 4 of 15 (27%). Of these, 43056305 is partial on its full text only and 43048754 is off-genus.
- Worth a ledger entry: 2 of 15 (43041999, 43061600). One more needs a full-text decision (43056305).
- By query:

| Query | RELEVANT | PARTIAL | NOT_RELEVANT |
|---|---|---|---|
| be_comb_geometry | 0 | 0 | 1 |
| be_thermoregulation | 0 | 2 | 1 |
| my_phosphorus | 0 | 2 | 6 |
| root_water_uptake | 0 | 0 | 3 |

- Hypothesis stubs:

| Rule | FALSIFIER_MET | PARTLY_MET | NOT_MET | NOT_TESTABLE |
|---|---|---|---|---|
| HX4 (13 stubs) | 3 | 3 | 1 | 6 |
| HX1 (2 stubs) | 2 | – | – | – |

## Patterns in the false positives

1. **Full-text matching.** In 14 of the 15 candidates, at least one AND-clause of the query matches only outside the title and abstract (counts are in `query_clause_locations`). Typical hits are methods sentences ("pupated honeycomb", "honeybee wax", "transferred to containers"), an author affiliation ("Honeybee Science Research Center"), single introduction or discussion sentences ("impairs root water uptake"), and "lipid transfer protein". This is the main cause. The crosswalk document already proposed field restriction for it.
2. **Common verbs in an AND-clause.** `transfer` in `my_phosphorus` matches sample handling, legume N transfer, intestinal transfer and model transfer. Six of the eight `my_phosphorus` candidates are off-subject.
3. **A broad OR-term in a clause.** `drought` in `root_water_uptake` is satisfied by any drought paper. The specific clause, "root water uptake", then needs only one sentence anywhere in the paper.
4. **HX4 fires on entity-level terms, not field dependencies.** It checks the BIOSPHERE term list against the abstract whenever the entity is a candidate. It does not check that the abstract studies the entity (6 of 13 NOT_TESTABLE), or that the term is one of the touched field's `dependencies` (e.g. oxygen for BE.collective_thermoregulation).
5. **Lexical term classes.** The `sunlight` class includes `photosynth*`, so "photosynthetic" in two plant-stress papers became "sunlight". Phosphorus as a tissue or feed mineral matches the `nutrient` class.
6. **HX1 and the number extractor.** Both HX1 stubs pointed at the wrong quantities: percent changes in biomass and K⁺/Na⁺ ion ratios. The deviation extractor tagged the ion ratios DEVIATION_CANDIDATE. It also extracted gene and structure names as numbers: ERF54 gives "54", FL7 gives "7", and δ15N gives "15".
7. **Near-synonyms are lexical traps.** "Water-use efficiency" (leaf carbon gained per unit water transpired) is not `water_uptake_efficiency`.

## Suggestions (proposals only; queries not edited)

Under the repository's rule, any change below would be a new dated amendment, declared before the run it governs.

**intake_queries.json**

1. Restrict each clause to title and abstract with Europe PMC's `TITLE_ABS:` field. Read-only test on 2026-11-27, same window, with the clauses in suggestions 2–4 (an earlier form of suggestion 2): be_comb 0, be_thermo 0, my_phosphorus 1 (43041999), root_water_uptake 1 (PMID 43069007; see below). Precision goes up and recall goes down: the full-text-only lead in 43056305 would be lost. An option is to keep full-text matching and add the flag in filter suggestion 1 below.
2. `my_phosphorus`: use `TITLE_ABS:(mycorrhiz*) AND TITLE_ABS:(phosphorus OR phosphate) AND TITLE_ABS:(transfer OR uptake OR mobiliz* OR transloc* OR "32P" OR "33P" OR hyphal)`. I ran it read-only on 2026-11-27 for the same window. It returned exactly two works, 43041999 and 43061600, the two this reading accepts for ledger candidacy. Without `mobiliz*` the ECM review 43061600 drops out, because it says "mobilization", not "transfer". Consider adding `(ectomycorrhiz* OR "mycorrhizal network*")`, since the value's stated scope is ECM in temperate forest.
3. `be_thermoregulation`: add `"honey bee"` as two words, as in the abstract of 43056305, and add `"brood nest"` and `"cluster temperature"`. Apply the `(Apis OR honeybee OR "honey bee")` clause to title and abstract, so that "honeybee wax" in a *Bombus* methods section does not pass.
4. `root_water_uptake`: use `TITLE_ABS:("root water uptake" OR "root hydraulic conductivit*" OR "root system architecture")`. Keep `drought` as a second clause, but restrict it too.
5. `biosphere_recycling` gave 0 hits. Whether that is expected was not checked (UNCHECKED).

**Filter and stub rules**

1. A new flag, kept and shown: QUERY_CLAUSE_NOT_IN_ABSTRACT. It would set when an AND-clause matches only outside the title and abstract. This week it would have flagged 14 of 15, including 3 of the 4 PARTIAL works, so it is better as a flag than as a removal.
2. HX4: fire only when the abstract also names the touched entity (e.g. `mycorrhiz*` for MY), and only on terms that map to the touched field's own `dependencies` list. Dependencies: BE.collective_thermoregulation, ambient_temperature; MY.phosphorus_transfer_efficiency, soil_phosphorus_availability; ROOT_NET.water_uptake_efficiency, soil_water_potential. Under that rule this week, 6 NOT_TESTABLE and 2 FALSIFIER_MET stubs (oxygen; sunlight on 'photosynthetic') would not have been written. In the intake, `photosynth*` should not count as "sunlight".
3. HX1: skip numbers the extractor tags CONDITIONAL_CHANGE, and numbers labelled as a named ratio (e.g. "K⁺/Na⁺ ratio"). The extractor should not take digits inside gene or structure tokens (ERF54, FL7, δ15N) as numbers. That is a note for `deviation_extract.py`, which is not edited here.
4. Window edge: re-running the seed queries for the same window on 2026-11-27 returned 5 hits for `root_water_uptake` (the snapshot has 3) and 14 for `my_phosphorus` (the snapshot has 10). The extra works were first indexed on 2026-11-23 or 2026-11-24, after the run. Either end the window two days before the run date, or overlap windows and extend F3, which now de-duplicates within one run, so that it also drops PMIDs taken in earlier weeks' `intake.json`. One of the missed works was read (abstract only): PMID 43069007, AM fungus plus a PGPR in maize under K deficiency and drought, which names enhanced root hydraulic conductivities. It would plausibly be PARTIAL for ROOT_NET and MY. The others (43075482, 43071297, 43073734, 43062364) are UNCHECKED.
5. F1 NO_ABSTRACT: all four removed records are PMC-source records with no PMID yet (PMC13785964, PMC13781785, PMC13787050, PMC13785933). One is titled "Effects of heat stress on honey bee physiology and gut microbiome under laboratory conditions", which may bear on BE.collective_thermoregulation (UNCHECKED; not read). Proposed: a PMC record with no abstract gets a flag such as ABSTRACT_PENDING and is re-queried the next week, instead of being removed.

## What the owner decides

- Whether this machine reading counts toward review, and whether any candidate goes to an outside reader for a reading-ledger entry. Registering 43041999 and 43061600 in `registry/sources.json` is the declared prior step.
- Whether full text and supplementary data may be read for 43056305 (beyond "reads: abstract only").
- Whether any query or rule suggestion is adopted, as a new amendment.

## Limits

One machine reader, no second reading. Full texts were read for term location and scope only, and no supplementary data were read. The relevance calls are judgments against each field's `scope.definition`, and another reader could place the two off-scope PARTIAL works (43048754, 43041999) differently.
