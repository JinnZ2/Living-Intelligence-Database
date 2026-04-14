# Exercise 01 — Cold Start Exploration

**Goal**: Practice navigating the database from zero context.

**Time**: 10-15 minutes.

---

## The scenario

You are an AI agent dropped into this repository with no prior knowledge. A user asks you:

> "What can you tell me about how mycelium relates to artificial intelligence?"

You must answer this using only the tools in this repo.

## The task

Work through these steps. Do not skip ahead. Verify each answer before moving on.

### Step 1: Read the manifest

```bash
cat manifest.json | head -30
```

**Question**: What are the 8 ontology types, and which one contains AI entities?

### Step 2: Find mycelium

```bash
python scripts/query.py search mycelium
```

**Question**: What is mycelium's ID in this database? (Hint: it is very short.)

### Step 3: Get the full mycelium entity

```bash
python scripts/query.py entity MY
```

**Questions**:
- What are mycelium's core patterns?
- How many connections does it have?
- Which of its linked entities are in the `ai` ontology type?

### Step 4: Find the shortest path from mycelium to each AI entity

```bash
python scripts/query.py path MY NEURAL_NET
python scripts/query.py path MY GNN
python scripts/query.py path MY LLM
```

**Question**: Which AI entity is *closest* to mycelium in the graph? What is the intermediate entity on that path (if any)?

### Step 5: Check for direct emergent rules

```bash
python scripts/query.py rules MY
```

**Question**: Is there any expander rule that combines mycelium with an AI entity?

### Step 6: Synthesize

Based on what you found, answer the user's question in 3-4 sentences. Your answer should reference:

- At least one specific mycelium pattern
- At least one AI entity that shares that pattern
- The type of relation connecting them (synergy, resonance, etc.)

## Verification

Your answer is correct if:

1. You correctly identified `MY` as mycelium's ID
2. You found that `GNN` (Graph Neural Network) is the closest AI entity, and the path is through `MY -> NEURAL_NET -> GNN` or similar (1-2 hops)
3. You found the rule `[NEURAL_NET + MY + FRACTAL] -> BIOLOGICAL_BACKPROPAGATION`
4. Your final answer mentions distributed graph optimization, message passing, or similar concepts from both mycelium and GNN

## Reflection

- How many commands did you run to answer the question?
- Could you have answered it with just `manifest.json` + one `query.py` call?
- What would have been harder if `query.py` did not exist?

## Next exercise

When you are comfortable with navigation, try `02_trace_path.md`.
