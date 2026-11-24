# Reading queue

Status: waiting for readings. Written by `scripts/reading_queue.py`; do not edit
by hand. Co-authored (JinnZ2 + Claude).

One row per attribute field and found work: 12 rows, 11 fields. No abstract text
and no judgment is in this file. The readings arrive from an outside reader as
`registry/attribute_readings.json`; the scripts here then build the steps and
re-export. Rules: `registry/DECLARED.json`, amendments "claim/number split" and
"NOT_ADDRESSED + reading queue".

| entity | field | value | field definition text | PMID | DOI |
|---|---|---|---|---|---|
| AN | attributes.stigmergic_construction | 0.93 | Structural precision of ant-built tunnel branching angles and pillar spacing relative to computationally optimal ventilation geometry (as a fraction of theoretical optimum) in fire ant and army ant studies. | 10633572 | 10.1162/106454699568700 |
| AN | attributes.distributed_task_allocation | 0.94 | Efficiency of colony-level response rebalancing after 20% of workers in one task category are removed — measured as time to return to optimal task distribution divided by time for human-managed rebalancing of equivalent work unit. | 11112175 | 10.1146/annurev.ento.46.1.413 |
| BE | attributes.waggle_dance_communication | 0.89 | Information transfer accuracy of honeybee waggle dance — fraction of recruited foragers that arrive within 200 m of the communicated food source after following dance instructions. | 11729095 | 10.1146/annurev.ento.47.091201.145306 |
| KA | attributes.elastic_energy_storage | 0.93 | Fraction of mechanical energy recovered from tendon elastic storage during each hopping stride, compared to equivalent muscle-powered stride without tendon recoil contribution. | 9319738 | 10.1242/jeb.198.9.1829 |
| KA | attributes.pendulum_gait | 0.91 | Inverted pendulum mechanical efficiency of kangaroo slow quadrupedal gait (pentapedal walk) — fraction of gravitational potential energy recovered as forward kinetic energy per stride. | 11140670 | 10.1038/35050167 |
| KA | attributes.dynamic_counterbalance | 0.92 | Contribution of tail inertia to angular momentum balance during rapid acceleration — measured as fraction of whole-body angular momentum change absorbed by tail during stride initiation. | 24990111 | 10.1098/rsbl.2014.0381 |
| MORMYRID | attributes.active_electrolocation | 0.96 | Spatial resolution of mormyrid active electrolocation — minimum distinguishable object separation at 10 cm range, expressed as fraction of body length. | 10210662 | 10.1242/jeb.202.10.1205 |
| OC | attributes.arm_autonomy_fraction | 0.64 | Proportion of octopus arm motor commands executed by arm-local ganglia without involving the central brain, measured by comparing coordinated arm movements in intact vs. decerebrate preparations. | 11546877 | 10.1126/science.1060976 |
| OC | attributes.chromatophore_camouflage | 0.89 | Spectral match quality of octopus camouflage against novel substrates — cosine similarity of octopus skin reflectance spectrum to background substrate reflectance, averaged across 20 novel substrates. | 20392722 | 10.1098/rsbl.2010.0223 |
| TU | attributes.magnetic_field_navigation | 0.96 | Accuracy of loggerhead sea turtle magnetic navigation — fraction of hatchlings swimming in magnetically appropriate direction when total darkness eliminates wave-following as cue, in rotating-coil experiments. | 9317267 | 10.1242/jeb.194.1.23 |
| TU | attributes.magnetic_field_navigation | 0.96 | Accuracy of loggerhead sea turtle magnetic navigation — fraction of hatchlings swimming in magnetically appropriate direction when total darkness eliminates wave-following as cue, in rotating-coil experiments. | 11598298 | 10.1126/science.1064557 |
| TU | attributes.magnetic_storm_compensation | 0.88 | Proportion of sea turtle navigational error introduced by moderate geomagnetic storms (Kp index 5-7) that is actively compensated vs persistent as navigational deviation over 48-hour tracking periods. | 19060188 | 10.1073/pnas.0801859105 |

## Keys for the readings file

| entity | field | cited as | existence state | source id | head step id |
|---|---|---|---|---|---|
| AN | attributes.stigmergic_construction | Theraulaz & Bonabeau (1999) | FOUND_AS_CITED | `bb2a3794dfe471be58df0dad8365368c370bf7837f0c3c4cb358e0668a2279b7` | `20d746be60ce6a38fe009584246b3f04b76dd0a7f0da30833bea788fc1ee44b4` |
| AN | attributes.distributed_task_allocation | Beshers & Fewell (2001) | FOUND_AS_CITED | `eefbde78a7620ac42c7f3e4926bed5db0797ab8c2252ea3586f10c7d0e9a11d4` | `191e749dfa7f621b3d961ae20f632bbd3b14f88dd9748cd05180624a9d0e3106` |
| BE | attributes.waggle_dance_communication | Dyer (2002) | FOUND_AS_CITED | `2db5724365e8cb113486295c886588ff5b44683d2f9e650a843bff2ed80a1dea` | `ba5fad31de4dc374c21ae8910b1208641ea7703d799d6c20b5096dadd51e2ac1` |
| KA | attributes.elastic_energy_storage | Biewener & Baudinette (1995) | FOUND_DIFFERS | `60703e1d04e75c1471b3b22d04014e17b666d2038c830bbd4a1b457dfb458c57` | `f794c267802ebadc899771a8601dc200d03617821177d466dc0fd6e845876bd6` |
| KA | attributes.pendulum_gait | Griffin & Kram (2000) | FOUND_AS_CITED | `dd03a167489cf1847f7aa6134bc576dc86f54d7530f9741b9c5fb8cbac824c5c` | `7cffda2e6a2ae3c68dc9db204ea14b3ebdffc2546cd27935f9729089e7018c53` |
| KA | attributes.dynamic_counterbalance | Askew et al. (2014) | FOUND_DIFFERS | `6bc5a082a849fb666bdaa1911b150a24e51687d4b79632ae3664f70ed96a1378` | `da9c3b85c029d82a58f467934b036149723c0199b6daa864ec2599fde0e960ca` |
| MORMYRID | attributes.active_electrolocation | von der Emde (1999) | FOUND_AS_CITED | `5bea5baaff13b5cdcd038840e71f43a49f99ea5ae990f486f03c77c9a98d6815` | `2b7402908cf5884b3f20f9d43fc2af88bac0b1f603509253109a6a965aef988a` |
| OC | attributes.arm_autonomy_fraction | Sumbre et al. (2001) | FOUND_AS_CITED | `7cc6491b4502b695a6e79005cb46ff48c4478a991a65e2c457f3e4bf00ea704b` | `4e99ab6eb84512051258643fe3528d67db75564974518ca103f8fcd52f54f7a9` |
| OC | attributes.chromatophore_camouflage | Mäthger et al. (2008) | FOUND_DIFFERS | `8ae2d41bffc93805877011ca044061374c561c858f791deea49f90d79901586f` | `efa8a874a0789b55343b5b00a4eca1d767aa8ae1f9650d6071f232db7d00a441` |
| TU | attributes.magnetic_field_navigation | Lohmann & Lohmann (1994) | FOUND_DIFFERS | `7828b8676f0416c92bdfcb68e487d443765539db9c3b1f6bbc6b1bcfd5fc4668` | `4d0c1e58b4d994858ec25bb74dd74819866101adaecd9dbe5788124f74456137` |
| TU | attributes.magnetic_field_navigation | Lohmann et al. (2001) | FOUND_AS_CITED | `7828b8676f0416c92bdfcb68e487d443765539db9c3b1f6bbc6b1bcfd5fc4668` | `4d0c1e58b4d994858ec25bb74dd74819866101adaecd9dbe5788124f74456137` |
| TU | attributes.magnetic_storm_compensation | Lohmann et al. (2008) | FOUND_AS_CITED | `bca0d1caa4e9b98a742327b64a1732e58e71b1804f7f8510fb04e6bed6416495` | `7f46624dc5efdb75e17686aa9c58d539e9bb4c9fc3f0a30207577b713a306804` |

## Values a reading may take

- `claim_support`: STATED, RELATED, CONTRADICTED, NOT_ADDRESSED, NOT_READ
- `number_support`: STATED, NOT_STATED
- a quote of at most 25 words per field and work
