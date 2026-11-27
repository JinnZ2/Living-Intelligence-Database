# Weekly intake 2026-11-03 to 2026-11-10

Status: PROPOSED. Machine output; nothing in this file has been read or judged by a person.

Queries file sha256 `6800a68886ded85dd5f224acb80971e134ca68f61d5d0327136ba85c974f3f9c`. Source: Europe PMC REST.

| Query | State | Hits | Snapshot sha256 |
|---|---|---|---|
| be_comb_geometry | SAVED | 2 | 56f8f989484da9ccc33961c30cc722dfc934f8051c0c02e2fbf0f2c62cfc5094 |
| be_thermoregulation | SAVED | 1 | 40ac0e32bc1d70a434d65708e3c41b14509dd812597bb4e0612c7b6cf8dd8b46 |
| my_phosphorus | SAVED | 2 | b5282c3ab2be5db005c96625241aa5cf4f38e23f9cc04fb2ef9bd35ef0a7c4f0 |
| root_water_uptake | SAVED | 3 | 7caf36dbb54babc338322b012bab325e3a79008948450c47c93f9711a412a6a1 |
| biosphere_recycling | SAVED | 0 | 468910355eb01b924a315ac3b3db547b8a9fb39c9a84d5d3a75f0e040c855816 |

Kept 7, removed 1 {"F1 NO_ABSTRACT": 1}, candidates 7, hypotheses 6 {"HX1": 1, "HX2": 0, "HX3": 0, "HX4": 5}

## Candidates awaiting a reader

| Work | Flags | Touches | Value | First quote candidate |
|---|---|---|---|---|
| PMID 42982737: Wearable E-Textiles for Cardiovascular Monitoring: Materials, Devices, and Integrated Syst | - | BE.hexagonal_cell_efficiency | 0.97 | Smart textiles have emerged as a promising platform for personalized cardiovascular healthcare by combining wearability, mechanical comfort, and seamless integration into everyday garments. |
| PMID 42996216: Functional analyses of &lt;i&gt;Apis cerana cerana DnaJC28&lt;/i&gt;: a new biomarker for  | - | BE.collective_thermoregulation | 0.94 | (no sentence contains a query term) |
| PMID 42985422: Rhizophagus clarus and phosphorus co-regulate oat rhizosphere metabolome-microbiome under  | - | MY.phosphorus_transfer_efficiency | 0.85 | The interaction between arbuscular mycorrhizal fungi (AMF) and phosphorus (P) availability could enhance plant drought tolerance. |
| PMID 42979373: Mast fruiting in a large tropical African legume tree species and the mineral nutrient lim | - | MY.phosphorus_transfer_efficiency | 0.85 | The large grove-forming ectomycorrhizal tropical tree Microberlinia bisulcata displays strong mast fruiting on poor soils. |
| PMID 42973534: Combined application of salicylic acid and silicon enhances photosynthetic capacity and yi | - | ROOT_NET.water_uptake_efficiency | 0.93 | This finding suggests that drought-resistant varieties may require greater accumulation of osmotic adjustment substances to alleviate drought stress. |
| PMID 42984748: Plant physiological control of root microbiome assembly and feedback under environmental s | - | ROOT_NET.water_uptake_efficiency | 0.93 | (no sentence contains a query term) |
| PMID 42989086: Effects of physiological integration on water use patterns and adaptation strategies in ty | - | ROOT_NET.water_uptake_efficiency | 0.93 | Understanding plant water uptakes in alpine wetlands are pivotal for sustaining water conservation and maintaining ecological safety of the lower reaches under continuous wetland degradation. |

## Hypothesis stubs (rule-generated, PROPOSED)

| Rule | Touches | Statement | Falsifier |
|---|---|---|---|
| HX4 | BE.collective_thermoregulation | The abstract names biosphere-carried conditions (temperature) for BE, a BIOSPHERE dependency candidate. | A reader finds the condition is not one the entity depends on, or the dependency runs the other way. |
| HX1 | MY.phosphorus_transfer_efficiency | The abstract gives numbers on a value-like scale; one may bear on MY.phosphorus_transfer_efficiency = 0.85. | A reader finds each number measures a different quantity from the field's scope.definition. |
| HX4 | MY.phosphorus_transfer_efficiency | The abstract names biosphere-carried conditions (nutrient, soil) for MY, a BIOSPHERE dependency candidate. | A reader finds the condition is not one the entity depends on, or the dependency runs the other way. |
| HX4 | MY.phosphorus_transfer_efficiency | The abstract names biosphere-carried conditions (nutrient, soil) for MY, a BIOSPHERE dependency candidate. | A reader finds the condition is not one the entity depends on, or the dependency runs the other way. |
| HX4 | ROOT_NET.water_uptake_efficiency | The abstract names biosphere-carried conditions (water) for ROOT_NET, a BIOSPHERE dependency candidate. | A reader finds the condition is not one the entity depends on, or the dependency runs the other way. |
| HX4 | ROOT_NET.water_uptake_efficiency | The abstract names biosphere-carried conditions (soil, water) for ROOT_NET, a BIOSPHERE dependency candidate. | A reader finds the condition is not one the entity depends on, or the dependency runs the other way. |
