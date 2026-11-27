# Reading prompt (machine reading of weekly intake 2026-11-24)

This is the instruction the machine reader followed. Its sha256 is recorded in `machine_reading.json` as `prompt_sha256`.

For each candidate in `../intake.json`:

1. Read the abstract from the saved Europe PMC snapshot in `../snapshots/`. Confirm its sha256 equals the candidate's `abstract_sha256`.
2. If the work is open access, fetch the Europe PMC full text (`/rest/<PMCID>/fullTextXML`), record the sha256 of the bytes received, and do not commit the text. Note where each query term occurs (abstract, body, reference list).
3. Compare what the work measured (organism, conditions, method, n, effect) with the touched field's `scope.definition`, `value` and `dependencies` in the entity file.
4. Say whether the work bears on that field: RELEVANT, PARTIAL or NOT_RELEVANT, with a reason. This is a machine relevance call. It is not `claim_support` and must not be copied into `claim_support`.
5. For each hypothesis stub, say whether its falsifier is met: FALSIFIER_MET, FALSIFIER_PARTLY_MET, FALSIFIER_NOT_MET, or NOT_TESTABLE (the work does not study the touched entity).
6. Name lexical false positives: a term that matched without the work bearing on the field.
7. Recommend one disposition: ACCEPT_FOR_LEDGER_CANDIDACY, NEEDS_FULL_TEXT_READER or REJECT, with a reason.
8. Quote at most 25 words, verbatim, and say whether the quote comes from the abstract or the full text.
9. Mark anything not read as UNCHECKED.

Write `reading_state: MACHINE_READ_NOT_REVIEWED` with the model name and this prompt's sha256 on every record. Do not write `claim_support` or `number_support`. Do not set any status beyond PROPOSED. Edit nothing in `ontology/`, `registry/` or the intake's own files. The owner decides what is reviewed.
