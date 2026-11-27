# Reading prompt (dated note, 2026-11-27: full text and supplementary data of PMID 43056305)

This is the instruction the machine reader followed for the dated note on 43056305. Its sha256 is recorded on the note as `prompt_sha256`. It was written after the owner's decisions on PR #34 (registry/DECLARED.json, amendment of 2026-11-27) and adds to `reading_prompt.md`; it does not replace it.

1. Read the open-access full text (Europe PMC fullTextXML, sha256 in `fulltext_MANIFEST.json`) and the open-access supplementary files from the publisher. Record each file's URL, bytes and sha256 in `supplementary_MANIFEST.json`. Do not commit the bytes.
2. Find every brood-nest temperature series. Report what it is (hives, sites, dates, interval, n) as OBSERVED, labelled as full-text and supplementary observation.
3. From the raw series compute, per hive and pooled: mean, population SD, and RMS deviation about 35 C. Label these DERIVED and give the sheet and column. Check them against any summary the authors give.
4. Say what the series cannot show against the touched field's `scope.definition` (ambient range, ambient recorded or not, duration). Do not compare with the field's value when its unit or form is not stated.
5. Quote at most 25 words, verbatim, and name the file the quote is from.
6. PROPOSE a disposition after the note. Leave the earlier reading's fields as written; the note is added beside them, dated.

Write `reading_state: MACHINE_READ_NOT_REVIEWED` with the model name and this prompt's sha256. Do not write `claim_support` or `number_support`. Do not register the source; that is the owner's call.
