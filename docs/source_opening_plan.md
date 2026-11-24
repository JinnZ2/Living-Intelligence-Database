# Source-opening pass: plan

Status: PROPOSED plan. Nothing was fetched or opened. Written by
`scripts/source_plan.py` from the chain and `registry/sources.json`;
do not edit by hand. Co-authored (JinnZ2 + Claude), 2026-11-24.

Status comes from reading the source, not from its evidence_type. A field
is counted as unblocked by a source when the source is an input of the
field's head step and the field reads NOT_ASSESSED. The count is how many
fields a reading could give a status to. It is not a forecast of what the
source says.

| | |
|---|---|
| sources in the registry | 234 |
| opened (abstract read) | 3 |
| unopened | 231 |
| unopened with a PMID or DOI in the string | 0 |
| NOT_ASSESSED attribute fields behind unopened sources | 225 |
| those behind the top 25 | 25 |

Fields per unopened source: 225 source(s) unblock 1, 6 source(s) unblock 0.

## Top 25

**The rank by fields unblocked is flat.** One source string is one attribute
field: every unopened source unblocks 1 field or 0. So the first key decides
nothing, and the order below comes from the tie-breaks:

1. fields unblocked by the string (1 for all 25);
2. `group`: fields behind the string's near-duplicate candidate group
   (`provenance_chain.py dups`: same first word and same year). A group is
   a candidate that several strings name one work, so one reading may serve
   several fields. Nothing was merged and no candidate was confirmed;
3. `works`: fewer works named in the string first (its `;`-separated parts),
   as fewer things to open per field;
4. source id.

No string carries a PMID or a DOI, so none is listed. `locator` is a
volume:pages pattern found in the string, when there is one.

| # | fields | group | works | source id | PMID | DOI | locator | entities | source string |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 3 | 2 | `7ef3bf63a979` | not in string | not in string | 408:537-538 | HUMPBACK | Noad et al. (2000) 'Cultural revolution in whale songs', Nature 408:537-538; Cerchio et al. (2001) 'Interannual variation in songs of humpback whales', Animal Behaviour 62:943-956. |
| 2 | 1 | 3 | 2 | `82b3eb8372a3` | not in string | not in string | 36:5-69 | BE | Hales (1999) 'Proof of the Honeycomb Conjecture', Discrete & Computational Geometry 36:5-69; engineering measurements confirm wax economy vs. circular and square cells. |
| 3 | 1 | 3 | 2 | `8c71dac0dd49` | not in string | not in string | 408:537 | WH | Noad et al. (2000) 'Cultural revolution in whale songs', Nature 408:537; Garland et al. (2011) 'Dynamic horizontal cultural transmission of humpback whale song', Current Biology 21:687-691. |
| 4 | 1 | 3 | 2 | `a04bc6fa3e69` | not in string | not in string | 25:1-22 | BE | Hales (1999) 'The honeycomb conjecture', Discrete and Computational Geometry 25:1-22 (mathematical proof); Thompson (1917) 'On Growth and Form', Cambridge UP. |
| 5 | 1 | 3 | 2 | `be07fab1f920` | not in string | not in string | 25:1-22 | HEX | Hales (1999) 'The honeycomb conjecture', Discrete and Computational Geometry 25:1-22; Kepler (1611) 'Strena Seu de Nive Sexangula' (on hexagonal snow crystal geometry). |
| 6 | 1 | 3 | 3 | `024bf6ae22e8` | not in string | not in string | none | WHALE | Noad et al. (2000) Pacific Ocean song transmission study; Garland et al. (2011) cultural evolution of song; 20+ years of hydrophone data. |
| 7 | 1 | 2 | 2 | `0f5c97bb9388` | not in string | not in string | 1:53-66 | AN | Dorigo & Gambardella (1997) 'Ant colony system', IEEE Transactions on Evolutionary Computation 1:53-66; Goss et al. (1989) 'Self-organized shortcuts in the Argentine ant', Naturwissenschaften 76:579-581. |
| 8 | 1 | 2 | 2 | `105f0407624a` | not in string | not in string | 1:53-66 | SWARM_AI | Dorigo & Gambardella (1997) 'Ant colony system', IEEE Transactions on Evolutionary Computation 1:53-66; Stützle & Hoos (2000) 'MAX-MIN ant system', Future Generation Computer Systems. |
| 9 | 1 | 2 | 2 | `173b0830c034` | not in string | not in string | none | QUARTZ | Cady (1946) 'Piezoelectricity', McGraw-Hill; Vig (1992) 'Quartz crystal resonators and oscillators', IEEE UFFC-S Tutorial. |
| 10 | 1 | 2 | 2 | `19e955b454a0` | not in string | not in string | none | WOLF_PACK | Mech & Peterson (2003) Yellowstone reintroduction data; 10+ years post-reintroduction observation. |
| 11 | 1 | 2 | 2 | `2db5724365e8` | not in string | not in string | 47:917-949 | BE | von Frisch (1967) 'The Dance Language and Orientation of Bees', Harvard UP (Nobel Prize 1973); Dyer (2002) 'The biology of the dance language', Annual Review of Entomology 47:917-949. |
| 12 | 1 | 2 | 2 | `3f4549e1a138` | not in string | not in string | 173:585-597 | WH | Payne & McVay (1971) 'Songs of Humpback Whales', Science 173:585-597; Watkins et al. (2000) 'Twentieth-century records of 20-Hz signals', Deep-Sea Research 47:1543-1562. |
| 13 | 1 | 2 | 2 | `7cc6491b4502` | not in string | not in string | 293:1845-1848 | OC | Sumbre et al. (2001) 'Control of Octopus Arm Extension by a Peripheral Motor Program', Science 293:1845-1848; Hochner et al. (2006) 'A Unified View of Animal Body Movements', Science. |
| 14 | 1 | 2 | 2 | `aac1e2efe74b` | not in string | not in string | 173:585-597 | HUMPBACK | Payne & McVay (1971) 'Songs of Humpback Whales', Science 173:585-597; Suzuki et al. (2006) 'Information entropy of humpback whale songs', Journal of the Acoustical Society of America 119:1849-1866. |
| 15 | 1 | 2 | 2 | `b77eade4b5c4` | not in string | not in string | 411:595-598 | OC | Sumbre et al. (2001) 'Octopus shows controlled arm coordination despite decentralized neural design', Nature 411:595-598; Hochner (2012) 'An almost infinite behavioral repertoire', Current Biology. |
| 16 | 1 | 2 | 2 | `dc47204c5a2a` | not in string | not in string | 19:780-790 | CU | Packard & Sanders (1971) 'Body patterns of Octopus vulgaris and maturation of the response', Animal Behaviour 19:780-790; Hanlon et al. (2009) dynamic camouflage in cephalopods. |
| 17 | 1 | 2 | 2 | `ef567179407c` | not in string | not in string | 302:207-218 | TOUR | Cady (1946) 'Piezoelectricity', McGraw-Hill; Lang (2004) 'A history of pyroelectricity', Ferroelectrics 302:207-218. |
| 18 | 1 | 2 | 2 | `f3b98e31c42f` | not in string | not in string | none | WOLF | Mech & Boitani (2003) 'Wolves: Behavior, Ecology, and Conservation', Univ. Chicago Press; Peterson & Ciucci (2003) predation success analysis across 3 pack studies. |
| 19 | 1 | 2 | 3 | `2915902723ac` | not in string | not in string | none | BE | von Frisch (1967) 'The Dance Language and Orientation of Bees' (Nobel Prize, 1973); replicated by Seeley (1995) 'The Wisdom of the Hive' and Seeley (2010) 'Honeybee Democracy'; 50+ independent replications. |
| 20 | 1 | 2 | 3 | `b6365f159a5b` | not in string | not in string | none | OC | Packard & Sanders (1971) 'Body patterns of Octopus vulgaris', Animal Behaviour; Langridge (2009) chromatophore response timing studies; Hanlon & Messenger (2018) 'Cephalopod Behaviour', 3rd ed. |
| 21 | 1 | 1 | 1 | `2a89338cf18c` | not in string | not in string | 23:298-300 | BT | Dacke et al. (2013) 'Dung beetles use the Milky Way for orientation', Current Biology 23:298-300. |
| 22 | 1 | 1 | 1 | `3082d6adcd12` | not in string | not in string | 181:169-184 | FIRE_BT | Schmitz & Bleckmann (1997) 'Fine structure and physiology of the infrared receptor of beetles', Journal of Comparative Physiology A 181:169-184. |
| 23 | 1 | 1 | 1 | `40b59501ee54` | not in string | not in string | 21:687-691 | HUMPBACK | Garland et al. (2011) 'Dynamic horizontal cultural transmission of humpback whale song at the ocean-basin scale', Current Biology 21:687-691. |
| 24 | 1 | 1 | 1 | `5765499ac3e3` | not in string | not in string | 7:12808 | TARDI | Hashimoto et al. (2016) 'Extremotolerant tardigrade genome and improved radiotolerance of human cultured cells by tardigrade-unique protein', Nature Communications 7:12808. |
| 25 | 1 | 1 | 1 | `5f78020093f7` | not in string | not in string | 6:6368 | CHAMELEON | Teyssier et al. (2015) 'Photonic crystals cause active colour change in chameleons', Nature Communications 6:6368. |

## Fields behind the top 25

1. `7ef3bf63a979`: HUMPBACK attributes.seasonal_evolution
2. `82b3eb8372a3`: BE attributes.hexagonal_cell_efficiency
3. `8c71dac0dd49`: WH attributes.cultural_song_transmission
4. `a04bc6fa3e69`: BE attributes.hexagonal_tessellation
5. `be07fab1f920`: HEX attributes.isoperimetric_packing_efficiency
6. `024bf6ae22e8`: WHALE attributes.song_coherence_across_pods
7. `0f5c97bb9388`: AN attributes.pheromone_trail_optimization
8. `105f0407624a`: SWARM_AI attributes.ant_colony_optimization
9. `173b0830c034`: QUARTZ attributes.piezoelectric_coefficient
10. `19e955b454a0`: WOLF_PACK attributes.hunt_success_rate
11. `2db5724365e8`: BE attributes.waggle_dance_communication
12. `3f4549e1a138`: WH attributes.long_range_acoustic
13. `7cc6491b4502`: OC attributes.arm_autonomy_fraction
14. `aac1e2efe74b`: HUMPBACK attributes.hierarchical_composition
15. `b77eade4b5c4`: OC attributes.distributed_neural_processing
16. `dc47204c5a2a`: CU attributes.instant_camouflage
17. `ef567179407c`: TOUR attributes.pyroelectric_sensitivity
18. `f3b98e31c42f`: WOLF attributes.coordinated_pursuit
19. `2915902723ac`: BE attributes.waggle_dance_precision
20. `b6365f159a5b`: OC attributes.chromatophore_response_latency
21. `2a89338cf18c`: BT attributes.milky_way_navigation
22. `3082d6adcd12`: FIRE_BT attributes.fire_navigation
23. `40b59501ee54`: HUMPBACK attributes.cultural_wave_propagation
24. `5765499ac3e3`: TARDI attributes.tdp_protein_shielding
25. `5f78020093f7`: CHAMELEON attributes.nanocrystal_structural_color

## What the plan does not settle

- Whether a string names one findable work. "not in string" means the
  string carries no PMID or DOI; the work has to be searched for by author,
  year and topic, and a search can come back empty or ambiguous.
- Whether the source supports the value. A reading can end in OBSERVED,
  DERIVED, PROPOSED, or in the value being withdrawn.
- Order of work. The rank is by count only. It does not weigh how hard a
  source is to obtain or how much the fields matter.
