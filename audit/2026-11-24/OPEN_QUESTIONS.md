# OPEN_QUESTIONS

Open questions from the 2026-11-24 audit of Living-Intelligence-Database at `63d93c0`. Written in the Simulators `OPEN_QUESTIONS.md` field form, so `tools/gap_index.py` can read this file. Each entry is also recorded as a category weld in `welds/`. A weld is the term. A gap is what is missing to separate it. Status of each entry: PROPOSED by the audit reader (Claude Opus 5.5, Perplexity Computer), not an owner decision.

---

### 1. INSTRUMENT — de_weld's OTHER axis reads as evaluative

**Gap:** `method-layer/de_weld.py` (commit `4636166`) puts every non-descriptive axis, OTHER included, in `EVALUATIVE_AXES`. A weld that joins two descriptive quantities has no axis of its own. Encoded on OTHER, the LID entries W01 and W02 were classed THIN and flagged `ungrounded_evaluation` even though both carry sourced descriptive claims. The weld is inside the instrument: "not descriptive" and "evaluative" share one category.

**Knowledge state:** OBSERVED (encoding control in `reference/lid_welds_results.json`)

**Research question:** Should de_weld carry named descriptive sub-axes, or should descriptive-descriptive welds stay with `category-weld/weld.py`, whose components are not typed as evaluative?

**Disciplines:** Method design

**Data sources:** `reference/lid_welds_results.json` `encoding_control`; `de_weld.py` `EVALUATIVE_AXES`

**Falsifier:** an owner statement that OTHER is meant to be evaluative closes this as intended scope, not a gap.

---

### 2. EVIDENCE — energy a bee gets from honey

**Gap:** The only energy value attached to honey is USDA FDC 169640, 1270 kJ/100 g, derivation "Calculated" from human energy-conversion factors. The energy a bee actually gets from the same honey was not found. Combustion enthalpy was not looked up.

**Knowledge state:** UNKNOWN_ATM (not found in this session; not shown absent)

**Research question:** What is the energy content of honey sugars as used by Apis mellifera, and how far does it differ from the human value?

**Disciplines:** Insect physiology, biochemistry

**Data sources:** bee respirometry and sugar-metabolism literature; bomb-calorimetry of honey

**Falsifier:** a sourced bee value within the human value's rounding would close the weld as harmless for the wax-power chain.

---

### 3. DECISION — mapping D0–D5 to L0–L5

Context: the audit built a D0–D5 dependency stack from the owner's answer without first checking `docs/GROUNDING_LAYERS.md`, which already defines L0–L5 plus the epistemic membrane Lε. The two stacks have the same shape. No mapping between them is declared.

**Fork:** (a) D-labels are aliases of L-labels; (b) D stays a separate stack with a declared crosswalk; (c) D is withdrawn in favour of L.

**Winning condition:** the owner states which branch holds, and where Lε sits relative to D.

**Discriminator:** an owner statement. No source outside the owner can settle it, and the layer names alone do not.

**Blocked by:** owner decision. A mapping inferred from the layer names would be the word-list reading the method refuses.

**Who could run it:** the repository owner.

**If you run it:** the audit's D-labels either become aliases of L-labels or stay a separate stack with a declared crosswalk. Either way, W08 closes.

---

### 4. SCHEMA — a process stored as a static noun

**Gap:** Attributes such as `hexagonal_cell_efficiency` store one value with no time index, no cycle and no rate. The thing they describe is a process: secretion every 12 h, heating, a relaxation of about 6 s. The owner's language has no static nouns, so the schema has no slot for what the source knowledge carries.

**Knowledge state:** OBSERVED (schema); the remedy is NOT_STUDIED

**Research question:** Can an attribute carry the slots the common-denominator rule needs (dimension, interval, time basis on a named cycle, scope, source) as optional additions, so that no existing record has to change?

**Disciplines:** Knowledge representation, schema design

**Data sources:** `schemas/animal.schema.json`; `reference/common_denominator.py`

**Falsifier:** if the slots cannot be added without breaking `scripts/build_index.py` validation of current records, the additive route fails.
