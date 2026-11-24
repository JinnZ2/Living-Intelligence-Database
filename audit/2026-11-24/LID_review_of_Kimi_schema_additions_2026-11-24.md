# Review of the Outside-Reader Package: LID Schema Additions (Kimi, 2026-11-25)

Reviewed 2026-11-24 (America/Chicago) against repository `main` at `f9ce766` (data baseline `63d93c0`). The package was written by Kimi (Moonshot AI), as the owner stated and as the readings file's own `reader` field records. It is kept byte-for-byte in `kimi_2026-11-25/` and is not edited here. Everything in it is PROPOSED. Nothing in it has been moved into `schemas/` or `registry/`.

Labels used here: OBSERVED / DERIVED / PROPOSED / UNKNOWN / NOT_TESTED.

## What was reproduced

| Claim in the package | Result | Label |
|---|---|---|
| `tests/validate_loud.py` runs 28 checks and exits 0 | Reproduced: 28/28, exit 0. Fixtures were placed at the path the suite expects. | OBSERVED |
| `registry/DECLARED.json` has 10 amendments, and amendment 10 introduces NOT_ADDRESSED and the reading queue | Confirmed | OBSERVED |
| `docs/reading_queue.md` has 12 rows across 11 fields | Confirmed | OBSERVED |
| 17 schemas; 124 entity files | 17 confirmed. `find ontology -name '*.json'` gives 124, so Kimi's figure is right. My shallower count of 123 was wrong. | OBSERVED |
| `baseline_commit` is a 40-hex git SHA-1 | Confirmed | OBSERVED |
| `trace_check.py` exits 0 even when it has findings | Confirmed. An opt-in fix was added (see below). | OBSERVED |
| The repo's validator is `jsonschema` | Confirmed: `pipeline.sh` installs it with pip if it is missing. Note: that is a non-stdlib, network-time dependency, which the audit protocol's implementation rule excludes for audit code. | OBSERVED |

## The 12 readings

All 11 quoted works were fetched from Europe PMC. Every quote appears word for word in its abstract, every `source_id` matches the queue, and the longest quote is 25 words (OBSERVED). The `claim_support` values (STATED / RELATED / etc.) are Kimi's judgments and were not re-judged here (NOT_TESTED).

**A finding the package missed.** The 12th row, KA `pendulum_gait`, cites PMID 11140670, Griffin & Kram 2000. Kimi marked it NOT_READ because it has no abstract, which is correct under the abstract rules. But that record's title is "Penguin waddling is not wasteful" (Nature, DOI 10.1038/35050167). The cited work is about penguins. `docs/existence_check.md` already lists this PMID, and existence is all that check tests: the record resolves, but whether it matches the claim's topic was never checked. This is recorded as OPEN_QUESTIONS #5. Whether it is a slip or deliberate is UNKNOWN.

**Nothing consumes the readings yet.** No script reads `registry/attribute_readings.json`; `reading_queue.py --check` checks only the queue document. The completed readings therefore have no path into any record (OBSERVED). See OPEN_QUESTIONS #6.

## The new sources

Each source was re-fetched before it was used.

| Source | What it says | Note |
|---|---|---|
| [Dauter & Jaskolski 2025, Acta Cryst. A](https://pmc.ncbi.nlm.nih.gov/articles/PMC11873813/) | The Fejes Tóth gain can be improved to 0.50% by tilting the hexagonal faces a further 2.8°. | Kimi calls it a "review". It presents new analysis. |
| [Yang et al. 2022, Apidologie 53:6](https://hal.science/hal-04025696/document) | Natural combs contain no more than 18% Fejes Tóth cells; dihedral angle 108.70° ± 0.16° against 120°. | Which species each sample came from was not checked. |
| [Yang et al. 2021, J. Insect Sci.](https://pmc.ncbi.nlm.nih.gov/articles/PMC8253300/) | Cell structure and dimensions by species | Not used in the trace |
| [Bauer & Bienefeld 2013, Naturwissenschaften 100:45–49](https://pubmed.ncbi.nlm.nih.gov/23149932/) | Wax measured at 33.6–37.6 °C during hexagon construction; direct construction | Contradicts the ~45 °C condition node. See below. |
| [Smith, Napp & Petersen 2021, PNAS](https://pubmed.ncbi.nlm.nih.gov/34312229/) | Irregular building under constraint | |
| [Pirk et al. 2004](https://pubmed.ncbi.nlm.nih.gov/15257392/) | Liquid-equilibrium account | Seen in search results only |
| [Gallo, Bridges, Woodgate & Chittka 2026](https://www.nature.com/articles/s44434-026-00004-2) | Published in npj Entomology on 2026-10-06 | My trace mislabelled it "Nature 2026". Corrected by dated note. |
| Fejes Tóth "<0.35%" (DOI 10.1090/S0002-9904-1964-11155-1) | | NOT_TESTED |

## What changed in the audit (all additive)

- `reference/reference_trace_BE_hex_v0.3.json` and `build_reference_v03.py` were added beside v0.1 and v0.2. The v0.2 file's SHA-1 is unchanged.
  - **C_FLOW_T: TRACED → CONTESTED.** The trace's own data put about 45 °C ([Karihaloo 2013](https://www.ncbi.nlm.nih.gov/pmc/articles/3730681)) against 33.6–37.6 °C measured ([Bauer & Bienefeld 2013](https://pubmed.ncbi.nlm.nih.gov/23149932/)). The earlier status is kept in `status_history`.
  - **REGIME_HEX** is now CONDITIONAL, because its lower bound comes from C_FLOW_T.
  - **F_FLOW** gains a fourth account, direct construction, and the label correction.
  - Two new nodes: **G3D_DAUTER** (D0, the optimum) and **P_BUILT_MEASURED** (D5, what bees actually build). The gap between them is a sourced quantity.
  - Checker result: 28 paths, 26 ending at D0, 2 CONTESTED nodes, the same 8 findings as before (OBSERVED).
- `trace_check.py`: `LID_STRICT=1` now exits 1 when there are findings. The default exit and the output bytes are unchanged, so earlier results still reproduce (OBSERVED: the v0.2 output is byte-identical).
- Dated notes were appended to the reference trace and to the weld register (W01). No earlier row was edited.
- OPEN_QUESTIONS #5 (the penguin citation) and #6 (the readings have no ingest path; the schema has no history field). All six entries parse as complete under `Simulators/tools/gap_index.py`.

## A test the proposed schema fails

Kimi's `reference_trace.schema.json` is closed (`additionalProperties: false`). It validates v0.1 and v0.2, but it **rejects v0.3**: `nodes[5]` has `'status_history'`, which was unexpected (OBSERVED). The rejection is caused by the dated record of a status change, which is exactly what the repository's correction practice produces. The data was not changed to fit the schema. Under the protocol, the implementation serves the knowledge. Whether the schema should reserve fields for history is left to the owner (OPEN_QUESTIONS #6).

## Open decisions Kimi raised, left with the owner

These are listed as PROPOSED and not decided here:

1. Whether cycles use `PROPOSED_UNSOURCED` and nodes use `PROPOSED`, or both use one shared vocabulary.
2. Whether a top-level `registry/cycles.json` exists.
3. Whether `depends_on` becomes typed (for example, energy vs constraint vs information).
4. Whether Gallo et al. 2026 joins the CONTESTED F_FLOW node as its own account. In v0.3 it stays as account (c), with the label corrected.
5. Where the four schemas go, if anywhere. They stay under `audit/` for now.
