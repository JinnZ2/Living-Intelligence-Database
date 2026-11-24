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

### 5. EVIDENCE — a kangaroo attribute cites a penguin paper

**Gap:** The KA `pendulum_gait` attribute cites PMID 11140670, Griffin & Kram 2000. That record is "Penguin waddling is not wasteful" (Nature), which has no abstract. The cited work is about penguins, not kangaroos.

**Knowledge state:** OBSERVED (title, Europe PMC); whether the citation is a slip or deliberate is UNKNOWN

**Research question:** Which source supports the kangaroo pendulum-gait claim, and was this PMID meant for a different attribute?

**Disciplines:** Biomechanics, bibliographic provenance

**Data sources:** `ontology/` KA record; Europe PMC record for PMID 11140670

**Falsifier:** if the full text of PMID 11140670 contains kangaroo gait measurements that the attribute uses, the mismatch is only apparent.

### 6. SCHEMA — outside readings have no way in, and the proposed schema cannot carry history

**Gap:** No script reads `registry/attribute_readings.json`. `reading_queue.py --check` checks only the queue document. So the completed readings from an outside reader (Kimi, 2026-11-25) cannot yet reach any record. Separately, the proposed `reference_trace.schema.json` is closed (`additionalProperties: false`). It rejects the v0.3 trace because v0.3 carries `status_history`, the dated record of a status change. As drafted, the schema cannot hold the repository's own rule that corrections are added and never overwritten.

**Knowledge state:** OBSERVED (no consumer; v0.3 fails validation on `nodes[5].status_history`); the remedy is NOT_STUDIED

**Research question:** What ingest path should outside readings use, and which fields should a trace schema reserve for dated history (status_history, dated notes) so that adding corrections never fails validation?

**Disciplines:** Knowledge representation, schema design, provenance

**Data sources:** `audit/2026-11-24/kimi_2026-11-25/` (proposed schemas and readings); `reference/reference_trace_BE_hex_v0.3.json`

**Falsifier:** if a history field can be added to the proposed schema and all 28 of Kimi's checks still pass, the second half of this gap closes.

**Dated note, 2026-11-24 (#6, second half):** Kimi submitted a revised `reference_trace.schema.json`, stored unedited in `kimi_2026-11-25_rev1/`; the original is unchanged. The only change is an optional `status_history` on nodes (OBSERVED by diff). The falsifier was met: v0.1, v0.2 and v0.3 all validate, and Kimi's suite, run with the revised schema, still passes 28/28 (OBSERVED). The schema half of this gap is therefore closed. The ingest half stays open: nothing reads the readings file yet.

### 7. INSTRUMENT — the falsifier searches records that carry no attributes

**Gap:** After the 2026-11-24 repair, all 601 counterexamples read NOT_TESTED. The label is honest, but `check_counterexample` still searches the thin index entries, and those carry no attributes. When the same counterexamples are searched against the full records, 360 come back RISK_FLAGGED and 241 NOT_TESTED, identically on `63d93c0` and `906e86a`. So the NOT_TESTED reading comes from where the instrument looks, not from the database having nothing to say.

**Knowledge state:** OBSERVED (`recheck_results_906e86a.json`, F1 and F1b); whether the 360 text matches bear on the claims is NOT_TESTED

**Research question:** Should the falsifier search the full records? If so, how should a RISK_FLAGGED text match be read by a person, so that a match is not taken as a refutation?

**Disciplines:** Method design, falsification practice

**Data sources:** `validation/falsifier.py`; `recheck_main.py`; `recheck_results_906e86a.json`

**Falsifier:** if a reading of the 360 matches finds none relevant to its claim, then searching the full records adds nothing beyond the thin search, and the gap closes as harmless.
