# LID Weld Register and Common Denominator

Date: 2026-11-24. Repository: JinnZ2/Living-Intelligence-Database at commit `63d93c0`. Status of everything in this file: PROPOSED unless a line says otherwise. Nothing here changes a repository file, and no record is renamed or removed.

Reader: Claude Opus 5.5, working in Perplexity Computer. I read the assessor key earlier in this session, so I am not a blind participant.

## What a weld is here

A weld is one word, field or number that carries several independent quantities as if they were one. The term comes from the owner's category-weld work. The register below is built with the owner's own instrument, `de_weld.py` from [JinnZ2/method-layer](https://github.com/JinnZ2/method-layer), pinned at commit `4636166`. de_weld computes the class, the cross-axis pairs, the flag and the void slots from the axes the caller declares. This audit declares the axes. It does not decide what the words mean.

Run: `METHOD_LAYER=/path/to/method-layer python3 reference/lid_welds.py`. Outputs: `reference/lid_welds_results.json` and `reference/lid_welds_render.txt`. The run is deterministic (byte-identical across two runs).

## Instrument-fit finding

OBSERVED: de_weld counts every axis other than DESCRIPTIVE as evaluative, OTHER included (`EVALUATIVE_AXES` in `de_weld.py`). The LID welds mostly join descriptive quantities to each other, such as a 2D proof and a 3D cell. My first encoding put each named sub-quantity on OTHER. Under that encoding all ten entries classed as THIN, and W01 and W02 were flagged `ungrounded_evaluation`. That reading is wrong: both have sourced descriptive content.

The primary encoding now puts sub-quantities on DESCRIPTIVE, with the name in the claim text (for example `[geometry_2d] …`). The OTHER encoding is kept in the JSON as `encoding_control`. This is a scope note about the instrument, not a defect report. de_weld was built for welds between description and evaluation, and these welds are between descriptions. Whether method-layer should gain a descriptive sub-axis is the owner's decision and is not proposed as a change here.

## The register

| ID | Weld | Quantities it carries | de_weld class | Declared pairs | Open question |
|---|---|---|---|---|---|
| W01 | `hexagonal_cell_efficiency = 0.97` | 2D perimeter proof ([Hales](https://link.springer.com/article/10.1007/s004540010071)); 3D cell closure ([Fejes Tóth](https://projecteuclid.org/journalArticle/Download?urlid=bams/1183526078)); wax cost in honey ([FAO](https://www.fao.org/4/i0842e/i0842e12.pdf)); contested formation process ([Karihaloo](https://www.ncbi.nlm.nih.gov/pmc/articles/3730681), [Nature 2026](https://www.nature.com/articles/s44434-026-00004-2)); abundance; quality | thick | 1 coupled, 1 conflicting, 13 undeclared | Which ratio 0.97 is, over which boundary |
| W02 | `relational_confidence = 0.98` | scope; deviation ±U and coverage ([GUM](https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf)); recurrence (kept separate by the owner); a 0–1 trust score | thick | 1 coupled, 9 undeclared | Which of the four the 0.98 encodes |
| W03 | `dependencies` field | D0 constants (pi); D2 conditions (construction_temperature); D3 material (wax_purity); D4 state (swarm_hunger_state); sign of effect (not stated) | descriptive | 10 undeclared | Layer and signed effect of each string |
| W04 | "cycle" | oscillation ([wingbeat](https://www.pnas.org/doi/10.1073/pnas.0506590102)); developmental window ([FAO](https://www.fao.org/4/X0083E/X0083E03.htm)); transient (≈6 s hexagon relaxation); superposition (unsourced); nesting (owner) | descriptive | 1 coupled, 9 undeclared | Which cycle, at what period, inside which parent |
| W05 | sunlight | energy source ([1360.8 W/m²](https://esdpubs.nasa.gov/sgpubs/content/A_new_lower_value_of_total_solar_irradiance_Evidence_and_climate_significance)); information source ([sun compass](https://pmc.ncbi.nlm.nih.gov/articles/PMC4667876/)); cycle driver | descriptive | 1 independent (PROPOSED, NOT_TESTED), 2 undeclared | No repository entity for incoming solar radiation |
| W06 | honey, mānuka vs wildflower | energy layer, where sugar is alike ([IJFST](https://academic.oup.com/ijfst/article/54/12/3185/7805247)); chemistry layer, DHA→MGO ([Adams 2009](https://pubmed.ncbi.nlm.nih.gov/19368902/)); market grade | thick | 1 independent, 2 undeclared | Wax composition by forage: no source |
| W07 | honey energy, 1270 kJ/100 g | human metabolizable energy ([USDA FDC 169640](https://fdc.nal.usda.gov/portal-data/external/169640), derivation "Calculated"); bee-usable energy (not found); combustion enthalpy (not looked up) | descriptive | 3 undeclared | Which one the wax-power figure should use |
| W08 | layer stacks | the repository's L0–L5 + Lε (`docs/GROUNDING_LAYERS.md`); this audit's D0–D5 | descriptive | 1 undeclared | Whether D-n maps to L-n; not declared by the owner |
| W09 | verb → noun | the building process (secretion every 12 h, heating, relaxation); a stored attribute with no time index | descriptive | 1 conflicting | How the schema carries a process without forcing a static noun |
| W10 | the common denominator itself | the 12 h cycle average; the phase profile inside the cycle (not sourced) | descriptive | 1 undeclared | Averaging over a cycle hides its phases |

Undeclared pairs stay UNDECLARED. They are not read as independent.

W08 is a weld this audit nearly made. It built D0–D5 from the owner's dependency answer without first checking `docs/GROUNDING_LAYERS.md`, which already defines L0–L5 with an epistemic membrane. The two stacks have the same shape. Mapping them is left to the owner.

## Common denominator

Question: what lets the welded quantities be compared without collapsing them into one?

### Rule tested (PROPOSED)

A quantity can be compared with another only when each carries four things:

1. an SI dimension vector (kg, m, s, K, mol);
2. the value interval the source states;
3. a time basis: `INSTANT`, `AVERAGE_OVER:<named cycle>`, `PER_EVENT:<event>`, or `NONE`;
4. a scope and a source.

Addition and ratio comparison need identical dimensions and identical time bases. Multiplication and division combine dimensions. When the time bases differ, the operation is flagged `DENOMINATOR_MISMATCH` instead of being computed silently. The one allowed conversion is a per-event quantity multiplied by the rate of that same event. That conversion is how "mass per scale" becomes "mass per second".

Tool: `reference/common_denominator.py` (standard library only, deterministic). Output: `reference/common_denominator_results.json`.

### Worked chain: wax-producing worker (DERIVED)

| Step | Value [interval] | Dimension | Time basis | Inputs |
|---|---|---|---|---|
| Scale rate | 1.85×10⁻⁴ scales/s | s⁻¹ | average over CY_SCALE | 8 scales / 12 h ([FAO](https://www.fao.org/4/i0842e/i0842e12.pdf)) |
| Wax mass rate | 1.85×10⁻¹⁰ kg/s | kg·s⁻¹ | average over CY_SCALE | × 10⁻⁶ kg/scale ("about 1 million scales per kg", [FAO](https://www.fao.org/4/i0842e/i0842e12.pdf); no ± stated, none invented) |
| Honey energy per scale | 102 J [85, 190] | J | per scale | × 6.66–15 kg honey/kg wax ([Wikipedia](https://en.wikipedia.org/wiki/Beeswax), [FAO T0104E](https://www.fao.org/4/t0104e/T0104E04.htm)) × 12.7 MJ/kg (PROXY, W07) |
| Honey energy per 12 h cycle | 813 J [677, 1524] | J | per CY_SCALE | × 8 scales |
| Throughput into wax | 0.0188 W [0.0157, 0.0353] | W | average over CY_SCALE | chain above |
| Max biomass flux, clear noon | 46 W/m² [32, 60] | W·m⁻² | instant | 700–1300 W/m² ([Wikipedia](https://en.wikipedia.org/wiki/Solar_irradiance)) × 4.6% C3 upper bound ([Zhu, Long & Ort](https://pubmed.ncbi.nlm.nih.gov/18374559/)) |
| Leaf area to match | 4.1 cm² [2.6, 11] | m² | MIXED, flagged | a 12 h average divided by a noon peak |

The last row is shown only to demonstrate the flag. Dividing a cycle average by an instant peak understates the area. No day-average irradiance is sourced here, so no corrected value is given.

### Comparisons the rule allows and refuses

| Pair | Result | Reason |
|---|---|---|
| mānuka sugar vs multifloral sugar | COMPARABLE, ratio 1.055 | same dimension (mass fraction), same basis ([IJFST](https://academic.oup.com/ijfst/article/54/12/3185/7805247)) |
| wax power vs biomass flux | REFUSED | W vs W/m² |
| wax power vs any instant power | REFUSED | time basis: cycle average vs instant |
| mānuka DHA vs multifloral DHA | REFUSED | no counterpart quantity: presence vs absence, not a ratio ([Adams 2009](https://pubmed.ncbi.nlm.nih.gov/19368902/)) |

### What this run supports (DERIVED)

1. One dimension vector held every sourced energy quantity. The chain from scale rate to watts closed with one unsourced link: the human-nutrition honey energy, marked PROXY.
2. Combinations failed at the time basis, not the unit. The common denominator is not joules or watts alone. It is the rate together with the named cycle it is averaged over.
3. Energy works as a common denominator for the sugar layer only. The chemistry layer (DHA/MGO) has no counterpart in one regime, so the denominator leaves it as a difference in kind, which is the environment differential the owner asked about.
4. Time on a named cycle is the one denominator every node in the trace shares. The cycle ladder already spans 10^-2.36 to 10^8.54 s. Time is necessary but not sufficient, because a cycle average hides that cycle's phases (W10).

### What this run does not establish

- The honey energy figure is human metabolizable energy. Bee-usable energy was not found (W07).
- "About 1 million scales per kg" carries no stated interval, so the wax-rate interval reflects only the spread in honey per kg of wax.
- No phase profile is sourced for CY_SCALE, CY_DAY or CY_YEAR, so no within-cycle rate is computed.
- No equation is proposed for any relationship. Every derived value is a product or quotient of sourced values.
- The comparison set is small and hand-chosen. It tests the rule's behaviour. It does not validate the rule.

## Connection to the owner's framing

The owner's statement "every noun is a verb" corresponds to the rule's insistence on rates. "What cycle are we talking?" corresponds to the time-basis slot. The rule does not translate the knowledge architecture into the code's terms. It adds the slots the code was missing, so that no quantity is stored without its cycle. Whether these slots are the right ones is an owner decision. The rule stays PROPOSED until then.

## Files in this posting

- `reference/lid_welds.py`, `reference/lid_welds_results.json`, `reference/lid_welds_render.txt`: the weld register on de_weld.
- `reference/common_denominator.py`, `reference/common_denominator_results.json`: the time-basis rule and the worked chain.
- `reference/trace_check.py`: dated 2026-11-24 note added. The script now also looks for `bee.json` three levels up, so it runs in place in the repository. Both earlier result files reproduce byte-for-byte.
