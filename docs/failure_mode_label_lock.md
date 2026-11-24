# Failure mode: label lock

Status: definition and four cases. Every case rests on abstracts or on
bibliographic records only; no full text was read. Co-authored (JinnZ2 +
Claude), 2026-11-24.

Tags used in this file: ABSTRACT READ (abstract fetched from PubMed via NCBI
efetch on 2026-11-24), RECORD ONLY (bibliographic record fetched; it has no
abstract), NOT OPENED (not fetched; nothing is stated from it), NOT RECORDED
(no source read here gives the value).

Delay, as used in this file: the time from data available to label accepted.
A gap between two publications is not a delay in this sense.

## Definition

A label placed before measurement stops investigation. The data waits on the
fight over the definition.

The pattern has three parts:

1. a capability is observed (a count, a signal, a changed response);
2. a label is attached to it ("tool use", "pain", "learning", "intelligence");
3. the argument moves to whether the label applies, and the observation is
   accepted or rejected with the label.

The `functional_intelligence` block is built to keep part 1 apart from part
2: each capability is `yes` / `no` / `unmeasured` with its own status and
source, and the disputed label goes in the open `contested_label` slot. A
dispute over a label does not change a yes/no field.

## Cases

For each case: the label disputed, the data available at the time, the delay,
and whether it is resolved.

### 1. Chimpanzee tool use

| | |
|---|---|
| label disputed | "tool use" as a human-only trait |
| data available at the time | Goodall J (1964) "Tool-using and aimed throwing in a community of free-living chimpanzees", Nature 201:1264-6, doi:10.1038/2011264a0, PMID 14151401. RECORD ONLY: the title states tool-using in free-living chimpanzees; no abstract exists in the record |
| the "redefine tool" statement attributed to Leakey | NOT OPENED. No source for the wording was fetched, so it is not quoted here |
| the 1960 observation | NOT OPENED |
| delay | NOT RECORDED |
| resolved? | NOT RECORDED |

### 2. "Bird brain": corvid and parrot cognition

| | |
|---|---|
| label disputed | "intelligence" as tied to a primate-like brain |
| data available at the time | Emery NJ, Clayton NS (2004) "The mentality of crows: convergent evolution of intelligence in corvids and apes", Science 306(5703):1903-7, doi:10.1126/science.1098410, PMID 15591194. ABSTRACT READ: a review of studies of tool manufacture, mental time travel and social cognition in corvids; it argues that complex cognitive abilities evolved multiple times in distantly related species with vastly different brain structures |
| parrot studies | NOT OPENED |
| delay | NOT RECORDED |
| resolved? | NOT RECORDED |

### 3. Fish pain

| | |
|---|---|
| label disputed | "pain", as distinct from "nociception" |
| data available at the time | Sneddon LU, Braithwaite VA, Gentle MJ (2003) "Do fishes have nociceptors? Evidence for the evolution of a vertebrate sensory system", Proc Biol Sci 270(1520):1115-21, doi:10.1098/rspb.2003.2349, PMID 12816648. ABSTRACT READ: recordings from trigeminal nerves identified polymodal nociceptors on the head of the trout; noxious substances applied to the lips raised opercular beat rate and the time taken to resume feeding. The abstract itself separates pain perception from nociception and ends with "suggesting discomfort" |
| the neocortex-requirement position | NOT OPENED. No source for it was fetched |
| related, from another case's source | Taiz et al. 2019 (case 4) lists vertebrates "including fish" among the animals that met the consciousness criteria it adopts. ABSTRACT READ |
| delay | NOT RECORDED |
| resolved? | NOT RECORDED |

### 4. Plant learning

| | |
|---|---|
| labels disputed | "learning", "consciousness", "intelligence" |
| claim | Gagliano M, Renton M, Depczynski M, Mancuso S (2014), Oecologia 175(1):63-72, doi:10.1007/s00442-013-2873-7, PMID 24390479. ABSTRACT READ: leaf folding in Mimosa pudica under repeated disturbance "exhibits clear habituation"; the response was still shown after a month undisturbed |
| claim | Gagliano M, Vyazovskiy VV, Borbély AA, Grimonprez M, Depczynski M (2016) "Learning by Association in Plants", Sci Rep 6:38427, doi:10.1038/srep38427, PMID 27910933. ABSTRACT READ: in a Y-maze, the position of a neutral cue predicting light affected the growth direction of pea seedlings |
| failed replication | Markel K (2020) "Lack of evidence for associative learning in pea plants", eLife 9:e57614, doi:10.7554/eLife.57614, PMID 32573434. ABSTRACT READ: a replication of the 2016 protocol with a larger sample and fully blinded analysis did not show the result |
| exchange | Comment by Gagliano et al. (eLife 9:e61141, PMID 32909941) and response by Markel (eLife 9:e61689, PMID 32909944). RECORD ONLY: titles read, text not read |
| critique | Taiz L, Alkon D, Draguhn A, Murphy A, Blatt M, Hawes C, Thiel G, Robinson DG (2019) "Plants Neither Possess nor Require Consciousness", Trends Plant Sci 24(8):677-687, doi:10.1016/j.tplants.2019.05.008, PMID 31279732. ABSTRACT READ: it calls the likelihood that plants have consciousness "effectively nil" |
| delay | NOT RECORDED. 2016→2020 is a publication gap, not label-lock delay (= data available → label accepted) |
| resolved? | NOT RECORDED. The pea result did not replicate in the one attempt read; no source read here addresses a replication of the Mimosa result |

Layer with no dispute located in the sources read (disputes were not
searched for):

- Toyota M, Spencer D, Sawai-Toyota S, Jiaqi W, Zhang T, Koo AJ, Howe GA,
  Gilroy S (2018) "Glutamate triggers long-distance, calcium-based plant
  defense signaling", Science 361(6407):1112-1115,
  doi:10.1126/science.aat7744, PMID 30213912. ABSTRACT READ: glutamate is a
  wound signal; GLUTAMATE RECEPTOR-LIKE channels convert it into a rise in
  intracellular calcium that propagates to distant organs, where defense
  responses are induced.
- Böhm J, Scherzer S, Krol E, et al. (2016) "The Venus Flytrap Dionaea
  muscipula Counts Prey-Induced Action Potentials to Induce Sodium Uptake",
  Curr Biol 26(3):286-95, doi:10.1016/j.cub.2015.11.057, PMID 26804557.
  ABSTRACT READ: two action potentials close the trap; more than three are
  needed for hydrolase gene expression, which is proportional to the number
  of stimulations. Record: `ontology/plant/venus_flytrap.json`.

In case 4 the same organisms carry both layers. The signalling and counting
results were measured and published while the label fight ran beside them.

Context reviews:

- Lin Y (2026) "Plant embodied intelligence: A paradigmatic perspective",
  iScience 29(7):116511, doi:10.1016/j.isci.2026.116511, PMID 42383002.
  ABSTRACT READ.
- Segundo-Ortin (2026), Philosophy Compass. NOT OPENED: not found in PubMed;
  the title is not confirmed.

## Lab isolation is an observer cut

Most of the results above come from a plant, fish or bird studied alone in a
controlled setting. That setting is a cut: it removes the loops that run
through the organism's surroundings (prey, soil, neighbours, season). A
capability that exists only inside such a loop reads as absent, and a cost
paid inside it reads as 0. See
[`loop_topology_findings.md`](loop_topology_findings.md).

The `observation_context` block records, per claim, whether it was observed
in the `lab`, in the `field`, `long_term_coupled`, or `mixed`. A `no` taken
in the lab is a `no` under that cut.

## Records

| record | state |
|---|---|
| `ontology/plant/venus_flytrap.json` | pilot: `gate_sensing`, `functional_intelligence`, `observation_context`, from the Böhm 2016 abstract |
| `ontology/plant/mimosa.json` | new, `contested_label` only; the five capability fields are null |
