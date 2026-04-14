# 02 — Navigation

How to explore the database as an AI agent or a human.

## The two-read cold start

If you are an AI agent with no prior context, you need exactly **2 file reads** to understand the entire database:

1. `manifest.json` — types, entry points, ID map, constants, relation types
2. `ontology_index.json` — all entities (with descriptions) and all relations

After these two reads, you can answer almost any question about what is in the database.

## The query tool

For anything deeper, use `scripts/query.py`. It has 8 commands:

### `entity` — Full details of one intelligence

```bash
python scripts/query.py entity LLM
```

Returns: description, patterns, all connections (in + out), applicable expander rules.

**Use when**: you want everything about a specific entity.

### `search` — Find entities by keyword

```bash
python scripts/query.py search symbiosis
python scripts/query.py search "fire"
```

Returns: ranked list of entities whose name/description/ID matches.

**Use when**: you have a concept but don't know which entities relate to it.

### `neighbors` — Direct connections

```bash
python scripts/query.py neighbors MY
```

Returns: all entities directly linked to Mycelium, grouped by relation type.

**Use when**: you want to see the immediate context of one entity.

### `path` — Shortest route between two entities

```bash
python scripts/query.py path CORAL NEURAL_NET
```

Returns: shortest chain of connections from Coral Reef to Neural Network.

**Use when**: you want to find cross-domain analogies or see how distant concepts connect.

### `type` — All entities of one category

```bash
python scripts/query.py type ai
python scripts/query.py type plant
```

Returns: every entity of that ontology type with short descriptions.

**Use when**: you want to survey an entire category.

### `rules` — Expander rules involving an entity

```bash
python scripts/query.py rules BE
```

Returns: all rules where Bee is an input or output.

**Use when**: you want to see what emergent patterns an entity participates in.

### `expand` — Test a combination against all rules

```bash
python scripts/query.py expand SWARM_AI BE TERMITE
python scripts/query.py expand MOSS LI CYANO
```

Returns: which rule(s) trigger (if any), plus "near miss" suggestions.

**Use when**: you want to check if a combination produces an emergent concept.

### `stats` — Database-wide metrics

```bash
python scripts/query.py stats
```

Returns: entity counts by type, relation counts, most-connected entities, isolated nodes.

**Use when**: you want the shape of the whole graph.

## Typical exploration patterns

### Pattern 1: "What is this?"

```bash
python scripts/query.py entity <ID>
```

### Pattern 2: "What connects to this?"

```bash
python scripts/query.py neighbors <ID>
```

Then follow interesting links with more `entity` queries.

### Pattern 3: "Is there a cross-domain analogy?"

```bash
python scripts/query.py path <biological_ID> <ai_ID>
```

If the path is short (1-3 hops), there is likely a strong analogy.

### Pattern 4: "Find all X-like things"

```bash
python scripts/query.py search <concept>
```

Follow with `neighbors` on the most relevant results.

### Pattern 5: "What could emerge from combining these?"

```bash
python scripts/query.py expand <ID1> <ID2> <ID3>
```

Even when no rule triggers, the "near miss" suggestions reveal what would.

## Reading the JSON directly

Sometimes you need the raw data. Here is the structure:

### ontology_index.json

```json
{
  "entities": [
    {
      "id": "BE",
      "name": "Bee",
      "ontology": "animal",
      "path": "ontology/animal/bee.json",
      "description": "Embodies swarm coordination..."
    }
  ],
  "relations": [
    {
      "source": "BE",
      "target": "HEX",
      "relation": "geometry_link"
    }
  ]
}
```

### Individual entity file

```json
{
  "id": "BE",
  "name": "Bee",
  "ontology": "animal",
  "emoji": "🐝",
  "symbolic_code": "[BE_HEX_φ_FLOW]",
  "description": "...",
  "core_attributes": { "pattern": "...", "efficiency_factor": 0.97 },
  "patterns": [ { "name": "...", "type": "...", "efficiency_factor": 0.97 } ],
  "links": [ { "relation": "geometry_link", "target": "HEX" } ],
  "co_creation": true
}
```

## Constants

Three harmonic constants appear throughout:

| Symbol | Name | Value | Meaning |
|--------|------|-------|---------|
| `phi` | Golden ratio | 1.618 | Self-similar growth, phyllotaxis, packing |
| `tau` | Full circle | 6.283 | Oscillation, resonance, periodicity |
| `sqrt3` | Hex constant | 1.732 | Hexagonal packing, triangular lattices |

They appear as string literals in rules (`"phi"`) and numeric values in entity `harmonic_ratios` arrays.

## Next step

Read `03_contribution.md` to learn how to safely add new entities and rules.
