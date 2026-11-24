# Existence check, top 10 entities (source pass, stage 1)

Status: PROPOSED. Written by `scripts/existence_check.py report` from
`registry/sources.json`; do not edit by hand. Co-authored (JinnZ2 + Claude).

What was checked: whether each cited work can be found in PubMed as cited,
through NCBI esearch and esummary (bibliographic records). No abstract and
no full text was read, so **no field gained a status** and no source is
marked opened. A found record shows the work exists and how it is indexed.
It does not show that the work supports the value it is cited for.

No state means "does not exist".

| state | meaning |
|---|---|
| FOUND_AS_CITED | a record is identified and every compared item agrees |
| FOUND_DIFFERS | a record is identified and at least one item differs |
| MATCH_SUSPECT | a record by the same first author was returned, but it may be a different work; not counted as found |
| NOT_FOUND_INDEXED | a titled work was searched and no record identified |
| NOT_INDEXED | a book, a chapter or a non-biomedical venue: PubMed is the wrong place to look |
| UNDERSPECIFIED | no title and no venue in the string, or the string names no work: not searchable, so not a miss |

A string's state is the weakest among the works it names
(UNDERSPECIFIED, NOT_FOUND_INDEXED, NOT_INDEXED, MATCH_SUSPECT, FOUND_DIFFERS, FOUND_AS_CITED).

## Per entity

| entity | attribute fields | sources | FOUND_AS_CITED | FOUND_DIFFERS | MATCH_SUSPECT | NOT_FOUND_INDEXED | NOT_INDEXED | UNDERSPECIFIED |
|---|---|---|---|---|---|---|---|---|
| ANT | 6 | 3 | 0 | 0 | 0 | 0 | 0 | 3 |
| BE | 6 | 6 | 0 | 0 | 0 | 2 | 3 | 1 |
| WHALE | 6 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| WOLF_PACK | 6 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| OC | 5 | 5 | 0 | 0 | 0 | 3 | 0 | 2 |
| KA | 4 | 4 | 0 | 1 | 0 | 3 | 0 | 0 |
| LLM | 4 | 4 | 0 | 0 | 0 | 0 | 4 | 0 |
| MORMYRID | 4 | 4 | 0 | 0 | 0 | 0 | 1 | 3 |
| TU | 4 | 4 | 1 | 1 | 0 | 0 | 0 | 2 |
| AN | 3 | 3 | 0 | 0 | 0 | 1 | 2 | 0 |
| total | 48 | 37 | 1 | 2 | 0 | 9 | 10 | 15 |

Per work (a string may name several): 65 works in 37 strings. FOUND_AS_CITED 8, FOUND_DIFFERS 4, MATCH_SUSPECT 1, NOT_FOUND_INDEXED 16, NOT_INDEXED 20, UNDERSPECIFIED 16.

## Before and after the re-sort

The re-sort (amendment "UNDERSPECIFIED + MATCH_SUSPECT") searched nothing. It
relabeled stored results: a miss with no title and no venue became
UNDERSPECIFIED, the string naming no work became UNDERSPECIFIED, and a match
that may be a different work by the same author became MATCH_SUSPECT.

| state | strings before | strings after | works before | works after |
|---|---|---|---|---|
| FOUND_AS_CITED | 1 | 1 | 8 | 8 |
| FOUND_DIFFERS | 2 | 2 | 5 | 4 |
| MATCH_SUSPECT | 0 | 0 | 0 | 1 |
| NOT_FOUND_INDEXED | 23 | 9 | 32 | 16 |
| NOT_INDEXED | 11 | 10 | 20 | 20 |
| UNDERSPECIFIED | 0 | 15 | 0 | 16 |
| total | 37 | 37 | 65 | 65 |

## MATCH_SUSPECT

- **AN** `0f5c97bb9388` Dorigo & Gambardella (1997) 'Ant colony system'
  - record returned: PMID 18263004. Dorigo M (1996) Ant system: optimization by a colony of cooperating agents. IEEE transactions on systems, man, and cybernetics. Part B, Cybernetics : a publication of the IEEE Systems, Man, and Cybernetics Society 26:29-41
  - differs in: year, title, venue, volume, pages
  - lead: 1997 IEEE TEC 1:53-66 may exist as cited outside PubMed (recall, unverified)

## FOUND_DIFFERS

Each line: the work as cited, the record identified, and every item that
differs. The source strings are unchanged; these are records of a
difference, not corrections applied.

- **OC** `8ae2d41bffc9` Mäthger et al. (2008) 'Evidence for distributed light-sensing in the skin of cuttlefish'
  - record: PMID 20392722, DOI 10.1098/rsbl.2010.0223. Mäthger LM (2010) Evidence for distributed light sensing in the skin of cuttlefish, Sepia officinalis. Biology letters 6:600-3
  - year: cited "2008"; record "2010"
  - title: cited "Evidence for distributed light-sensing in the skin of cuttlefish"; record "Evidence for distributed light sensing in the skin of cuttlefish, Sepia officinalis"
  - venue: cited "Journal of Experimental Biology"; record "Biology letters"
  - volume: cited "211"; record "6"
  - pages: cited "2203-2212"; record "600-3"
- **KA** `60703e1d04e7` Biewener & Baudinette (1995) 'In vivo muscle force and elastic energy storage during steady-speed hopping'
  - record: PMID 9319738, DOI 10.1242/jeb.198.9.1829. Biewener A (1995) In vivo muscle force and elastic energy storage during steady-speed hopping of tammar wallabies (Macropus eugenii). The Journal of experimental biology 198:1829-41
  - title: cited "In vivo muscle force and elastic energy storage during steady-speed hopping"; record "In vivo muscle force and elastic energy storage during steady-speed hopping of tammar wallabies (Macropus eugenii)"
- **KA** `6bc5a082a849` Askew et al. (2014) 'The kangaroo's tail propels and powers pentapedal locomotion'
  - record: PMID 24990111, DOI 10.1098/rsbl.2014.0381. O'Connor SM (2014) The kangaroo's tail propels and powers pentapedal locomotion. Biology letters 10:[no pages in the record]
  - author: cited "Askew et al."; record "O'Connor SM"
- **TU** `7828b8676f04` Lohmann & Lohmann (1994) 'Detection of magnetic inclination angle by sea turtles: a possible mechanism for determining latitude'
  - record: PMID 9317267, DOI 10.1242/jeb.194.1.23. Lohmann K (1994) DETECTION OF MAGNETIC INCLINATION ANGLE BY SEA TURTLES: A POSSIBLE MECHANISM FOR DETERMINING LATITUDE. The Journal of experimental biology 194:23-32
  - volume: cited "190"; record "194"
  - pages: cited "69-78"; record "23-32"

## Found as cited

- BE `2db5724365e8` Dyer (2002): PMID 11729095, DOI 10.1146/annurev.ento.47.091201.145306
- OC `7cc6491b4502` Sumbre et al. (2001): PMID 11546877, DOI 10.1126/science.1060976
- KA `dd03a167489c` Griffin & Kram (2000): PMID 11140670, DOI 10.1038/35050167
- MORMYRID `5bea5baaff13` von der Emde (1999): PMID 10210662, DOI 10.1242/jeb.202.10.1205
- TU `7828b8676f04` Lohmann et al. (2001): PMID 11598298, DOI 10.1126/science.1064557
- TU `bca0d1caa4e9` Lohmann et al. (2008): PMID 19060188, DOI 10.1073/pnas.0801859105
- AN `bb2a3794dfe4` Theraulaz & Bonabeau (1999): PMID 10633572, DOI 10.1162/106454699568700
- AN `eefbde78a762` Beshers & Fewell (2001): PMID 11112175, DOI 10.1146/annurev.ento.46.1.413

## Not identified

- UNDERSPECIFIED ANT `ad120380ae74` Deneubourg et al. (1990) [no title and no venue in the string: not searchable]
- UNDERSPECIFIED ANT `3786c807f671` Pratt et al. (2002) [no title and no venue in the string: not searchable]
- UNDERSPECIFIED ANT `cf5d62eb0710` Gordon (1999) [no title and no venue in the string: not searchable]
- NOT_INDEXED BE `82b3eb8372a3` Hales (1999) 'Proof of the Honeycomb Conjecture' [book, chapter or non-biomedical venue marker in the string; searched, no record identified]
- NOT_FOUND_INDEXED BE `2915902723ac` von Frisch (1967) 'The Dance Language and Orientation of Bees'
- NOT_FOUND_INDEXED BE `2915902723ac` Seeley (1995) 'The Wisdom of the Hive'
- NOT_FOUND_INDEXED BE `2915902723ac` Seeley (2010) 'Honeybee Democracy'
- NOT_INDEXED BE `a04bc6fa3e69` Hales (1999) 'The honeycomb conjecture' [book, chapter or non-biomedical venue marker in the string; searched, no record identified]
- NOT_INDEXED BE `a04bc6fa3e69` Thompson (1917) 'On Growth and Form' [book, chapter or non-biomedical venue marker in the string; searched, no record identified]
- NOT_INDEXED BE `2db5724365e8` von Frisch (1967) 'The Dance Language and Orientation of Bees' [book, chapter or non-biomedical venue marker in the string; searched, no record identified]
- NOT_FOUND_INDEXED BE `23dd81e2d056` Seeley & Visscher (2004) 'Group decision making in nest-site selection by honey bees'
- NOT_INDEXED BE `23dd81e2d056` Seeley (2010) 'Honeybee Democracy' [book, chapter or non-biomedical venue marker in the string; searched, no record identified]
- NOT_FOUND_INDEXED BE `a67ce7406a52` Fahrenholz et al. (1989) 'Thermal analysis of a honey bee colony'
- UNDERSPECIFIED BE `a67ce7406a52` Stabentheiner et al. (2010) [no title and no venue in the string: not searchable]
- UNDERSPECIFIED WHALE `024bf6ae22e8` Noad et al. (2000) [no title and no venue in the string: not searchable]
- UNDERSPECIFIED WHALE `024bf6ae22e8` Garland et al. (2011) [no title and no venue in the string: not searchable]
- UNDERSPECIFIED WHALE `4bbe1c474bd2` Wiley et al. (2011) [no title and no venue in the string: not searchable]
- UNDERSPECIFIED WOLF_PACK `19e955b454a0` Mech & Peterson (2003) [no title and no venue in the string: not searchable]
- UNDERSPECIFIED WOLF_PACK `620d5880fde1`: names no work: GPS collar data from Yellowstone packs, 2005-2020.
- NOT_FOUND_INDEXED OC `7cc6491b4502` Hochner et al. (2006) 'A Unified View of Animal Body Movements'
- NOT_FOUND_INDEXED OC `b6365f159a5b` Packard & Sanders (1971) 'Body patterns of Octopus vulgaris'
- UNDERSPECIFIED OC `b6365f159a5b` Langridge (2009) [no title and no venue in the string: not searchable]
- NOT_INDEXED OC `b6365f159a5b` Hanlon & Messenger (2018) 'Cephalopod Behaviour' [a record with a similar title and a different first author was returned; not accepted as the cited work]
- NOT_FOUND_INDEXED OC `b77eade4b5c4` Sumbre et al. (2001) 'Octopus shows controlled arm coordination despite decentralized neural design'
- NOT_FOUND_INDEXED OC `b77eade4b5c4` Hochner (2012) 'An almost infinite behavioral repertoire'
- UNDERSPECIFIED OC `8ae2d41bffc9` Hanlon et al. (2009) [no title and no venue in the string: not searchable]
- NOT_FOUND_INDEXED OC `bc73fb7c6187` Fossati et al. (2011) 'Neural regeneration in the arm of Octopus vulgaris'
- NOT_FOUND_INDEXED OC `bc73fb7c6187` Rohrbach & Schmidtberg (2006) 'Arm regeneration in Octopus vulgaris'
- NOT_FOUND_INDEXED KA `60703e1d04e7` Alexander & Vernon (1975) 'The mechanics of hopping by kangaroos'
- NOT_FOUND_INDEXED KA `abee7a95cd88` Baudinette et al. (1992) 'Cost of locomotion in wild tammar wallabies'
- NOT_FOUND_INDEXED KA `dd03a167489c` Dawson & Taylor (1973) 'Energetic cost of locomotion in kangaroos'
- NOT_INDEXED LLM `2899c24ea768` Vaswani et al. (2017) 'Attention is all you need' [book, chapter or non-biomedical venue marker in the string; searched, no record identified]
- NOT_INDEXED LLM `2899c24ea768` Dai et al. (2019) 'Transformer-XL' [book, chapter or non-biomedical venue marker in the string; searched, no record identified]
- NOT_INDEXED LLM `6b7af81e854f` Brown et al. (2020) 'Language models are few-shot learners' [a record with a similar title and a different first author was returned; not accepted as the cited work]
- NOT_INDEXED LLM `6b7af81e854f` Min et al. (2022) 'Rethinking the role of demonstrations' [book, chapter or non-biomedical venue marker in the string; searched, no record identified]
- NOT_INDEXED LLM `c9e39bea49b4` Mikolov et al. (2013) 'Distributed representations of words' [book, chapter or non-biomedical venue marker in the string; searched, no record identified]
- NOT_INDEXED LLM `c9e39bea49b4` Devlin et al. (2018) 'BERT' [book, chapter or non-biomedical venue marker in the string; searched, no record identified]
- NOT_INDEXED LLM `e18606a00b7d` Ippolito et al. (2022) 'Creative writing with an AI collaborator' [book, chapter or non-biomedical venue marker in the string; searched, no record identified]
- NOT_INDEXED LLM `e18606a00b7d` Chakrabarty et al. (2023) 'Art or artifice? Large language models and the false promise of creativity' [book, chapter or non-biomedical venue marker in the string; searched, no record identified]
- NOT_INDEXED MORMYRID `5bea5baaff13` Heiligenberg (1991) 'Neural Nets in Electric Fish' [book, chapter or non-biomedical venue marker in the string; searched, no record identified]
- NOT_INDEXED MORMYRID `89472de72cbd` Hopkins (1988) 'Social communication in the aquatic environment' [book, chapter or non-biomedical venue marker in the string; searched, no record identified]
- UNDERSPECIFIED MORMYRID `89472de72cbd` Terleph & Moller (2003) [no title and no venue in the string: not searchable]
- UNDERSPECIFIED MORMYRID `ffdbcf284aff` Bodznick & Boord (1986) [no title and no venue in the string: not searchable]
- UNDERSPECIFIED MORMYRID `ffdbcf284aff` Engelmann et al. (2002) [no title and no venue in the string: not searchable]
- NOT_INDEXED MORMYRID `6ef3d475b788` Moller (1995) 'Electric Fishes: History and Behavior' [book, chapter or non-biomedical venue marker in the string; searched, no record identified]
- UNDERSPECIFIED MORMYRID `6ef3d475b788` Bell (2001) [no title and no venue in the string: not searchable]
- NOT_FOUND_INDEXED TU `f302e91023b2` Bowen et al. (1993) 'Population structure of loggerhead turtles in the northwestern Atlantic Ocean and Mediterranean Sea'
- UNDERSPECIFIED TU `f302e91023b2` Luschi et al. (1998) [no title and no venue in the string: not searchable]
- NOT_INDEXED TU `ca989883fbb0` Bolten (2003) 'Variation in sea turtle life history patterns' [book, chapter or non-biomedical venue marker in the string; searched, no record identified]
- UNDERSPECIFIED TU `ca989883fbb0` Gaspar et al. (2006) [no title and no venue in the string: not searchable]
- NOT_FOUND_INDEXED AN `0f5c97bb9388` Goss et al. (1989) 'Self-organized shortcuts in the Argentine ant'
- NOT_INDEXED AN `bb2a3794dfe4` Tschinkel (2003) 'Subterranean ant nests: trace fossils past and future' [book, chapter or non-biomedical venue marker in the string; searched, no record identified]
- NOT_INDEXED AN `eefbde78a762` Gordon (2010) 'Ant Encounters: Interaction Networks and Colony Behavior' [book, chapter or non-biomedical venue marker in the string; searched, no record identified]

## Limits

- One index. A work absent from PubMed may be in another index; nothing else was searched.
- The match rule is mechanical (declared before the run). A work whose cited title is
  paraphrased, or whose first author is cited differently, can be missed.
- UNDERSPECIFIED says the string gives too little to search on. It says nothing about
  the work. The works were searched once by description words before this state
  existed; those searches identified nothing and are kept on each work under queries.
- MATCH_SUSPECT is a mechanical test (title run, year or venue). It was written after
  the one row it applies to was seen.
- The book and non-biomedical test is a word list. It decides only the label of a miss.
