# Reading Path — AI and Biological Mirrors

Each AI entity in this database has a biological ancestor. Here are the pairings.

## The core insight

Modern AI architectures were not invented from nothing. Every major approach has a biological counterpart that solved the same problem millions of years earlier. Understanding the biological mirror often reveals limitations and extensions the AI engineers missed.

## The pairings

### `NEURAL_NET` <-> `MY` (Mycelium)

The original neural network is a fungus. Mycelial networks route signals through weighted connections, strengthen productive pathways (load-responsive growth), and prune unused ones. Backpropagation has a mycelial analog: carbon flows preferentially to hyphae that returned nutrients.

```bash
python scripts/query.py path NEURAL_NET MY
```

**What the biological teaches**: mycelium achieves distributed optimization without a central processor. The "backprop must be global" assumption in deep learning may be wrong.

### `LLM` <-> `OC` (Octopus)

Language models use attention — a mechanism for dynamic relational binding across a sequence. Octopuses use distributed arm cognition — each arm has 40 million neurons and can solve local problems while the central brain handles strategy. Both decompose intelligence into parallel specialists.

```bash
python scripts/query.py entity OC
python scripts/query.py path LLM OC
```

**What the biological teaches**: the octopus does not have a "context window." Its arms maintain persistent local state. LLMs are rediscovering this with recurrent memory architectures.

### `EVOL_ALG` <-> `CORAL` (Coral Reef)

Evolutionary algorithms run population-based search through mutation and selection. Coral reefs are the longest-running evolutionary algorithm on Earth — populations of polyps adapting their symbiont strains, construction patterns, and niche specializations over deep time.

```bash
python scripts/query.py entity CORAL
```

**What the biological teaches**: real evolution uses co-evolution (multiple fitness landscapes shifting simultaneously). Single-objective evolutionary algorithms are a simplification.

### `SWARM_AI` <-> `BE`, `AN`, `TERMITE`

Swarm optimization algorithms (particle swarm, ant colony) are direct imitations of social insects. The biological originals do it without floating-point numbers, global clocks, or explicit position vectors.

```bash
python scripts/query.py expand SWARM_AI BE TERMITE
```

**What the biological teaches**: real swarms use stigmergy — communication through environment modification, not direct message passing. This is more robust to agent failure than most AI implementations.

### `RL_AGENT` <-> `DOLPHIN`

Reinforcement learners maximize cumulative reward through trial and error. Dolphins learn echolocation calibration the same way — each click is an action, each echo is information, and over development they tune their sonar through feedback loops.

```bash
python scripts/query.py path RL_AGENT DOLPHIN
```

**What the biological teaches**: dolphins also use *social* learning — they watch conspecifics and imitate. Pure RL ignores this. Modern work on imitation learning is reinventing what dolphins already do.

### `GAN` <-> `ORCHID` / `CU` (Cuttlefish)

Generative Adversarial Networks pit a generator against a discriminator. Orchids pit a signal (chemical mimicry) against pollinator detection systems across evolutionary time. Cuttlefish pit their chromatophore patterns against predator vision.

```bash
python scripts/query.py path GAN ORCHID
```

**What the biological teaches**: biological adversarial games are not symmetric. The orchid does not retrain the bee — it adapts to the bee's static sensory system. Many GAN training instabilities disappear when you accept asymmetry.

### `GNN` <-> `MY` (Mycelium again)

Graph neural networks pass messages between nodes along graph edges. Mycelia *are* graph networks with message passing. Period.

```bash
python scripts/query.py path GNN MY
```

**What the biological teaches**: mycelia handle dynamic graphs (hyphae grow and die). Most GNNs assume static topology. Dynamic GNNs are catching up.

### `AUTOENC` <-> `QUARTZ` / `ECHO`

Autoencoders compress information through a bottleneck and reconstruct it. Quartz crystals do frequency compression — taking a broad vibration and resonating only at their characteristic frequency, "reconstructing" a clean signal. Echoes do temporal compression.

```bash
python scripts/query.py expand AUTOENC QUARTZ ECHO
```

**What the biological/mineral teaches**: lossy compression that preserves the right thing is more useful than lossless compression. Quartz throws away everything except the signal that matches its structure.

## The summary path

```bash
python scripts/query.py path NEURAL_NET BE
python scripts/query.py path LLM GRANDMOTHER
python scripts/query.py path GAN CU
```

Each path should be 2-3 hops. The short distance is the proof: these intelligences are close relatives, not distant analogies.

## Question to sit with

For which AI entity is the biological mirror **not yet** in the database? In other words: which modern AI architecture has a biological ancestor that has not been added as a proper entity yet?

When you find it, you have just identified the next entity to contribute.
