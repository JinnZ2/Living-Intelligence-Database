# Exercise 02 — Trace a Cross-Domain Path

**Goal**: Find and interpret connections between very different intelligences.

**Time**: 15-20 minutes.

---

## The scenario

You are helping a researcher who believes that **crystal lattices and large language models share a structural principle**. They ask you to prove or disprove this using the database.

## The task

### Step 1: Get the stats

```bash
python scripts/query.py stats
```

**Observe**: How many entities are in the `crystal` ontology type? How many in `ai`?

### Step 2: Find a crystal lattice entity

```bash
python scripts/query.py type crystal
```

**Question**: What is the ID of the entity most clearly described as a "lattice"? (There is a clear winner.)

### Step 3: Trace a path

```bash
python scripts/query.py path CRYSTAL_LATTICE LLM
```

**Questions**:
- How many hops is the path?
- What entities appear on the path?
- What relation types connect each hop?

### Step 4: Investigate each intermediate entity

For each entity on the path, run:

```bash
python scripts/query.py entity <ID>
```

**Task**: Write down the **key pattern** each intermediate entity expresses. The intermediates are the "bridge" — they must share something with both the crystal and the LLM.

### Step 5: Check for alternative paths

```bash
python scripts/query.py path SILICON_LAT LLM
python scripts/query.py path QUARTZ AUTOENC
```

**Question**: Is there a different crystal -> AI path that is shorter or more meaningful?

### Step 6: Interpret

Form a hypothesis about **what structural principle the crystal and the LLM actually share**. Your answer should:

- Name the principle in 1 sentence
- Cite at least one specific entity on the path that embodies it
- Explain whether the research hypothesis is supported or refuted

## Sample answer structure

> The crystal and LLM share `[PRINCIPLE]`. This is visible in the path `CRYSTAL_LATTICE -> [INTERMEDIATE] -> LLM`, where `[INTERMEDIATE]` embodies `[PATTERN]`. The researcher's hypothesis is `[supported / refuted / partially supported]` because `[REASONING]`.

## Verification

A good answer identifies:

- The path goes through `shape` or `energy` intermediates (probably `TORUS`, `FRACTAL`, or `MULTI_HELIX`)
- The shared principle is something like "pattern repetition through structural symmetry" or "information storage via stable geometric configuration"
- The crystal holds pattern via atomic lattice; the LLM holds pattern via weight matrix — both are **frozen structure encoding relationships**

## Advanced question

Now try:

```bash
python scripts/query.py expand CRYSTAL_LATTICE QUARTZ LLM
```

Does any rule trigger? If not, could this combination produce a meaningful emergent concept? Propose one in the format:

```json
{ "if": ["CRYSTAL_LATTICE", "QUARTZ", "LLM"], "then": "YOUR_EMERGENT_CONCEPT" }
```

Save your proposal — you will use it in exercise 03.

## Next exercise

When you have completed this, try `03_propose_entity.md`.
