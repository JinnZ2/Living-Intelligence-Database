# Pipeline Guide — Living Intelligence Database

A step-by-step guide for adding new intelligences and using the pipeline.

---

## Quick Start

```bash
# 1. Install dependencies (one time)
pip install jsonschema

# 2. Make the pipeline executable (one time)
chmod +x pipeline.sh

# 3. Run the full pipeline (validate + rebuild index)
./pipeline.sh
```

---

## Pipeline Commands

| Command | What it does |
|---------|-------------|
| `./pipeline.sh` | Run full pipeline: validate all entities, then rebuild the index |
| `./pipeline.sh validate` | Validate every entity in `ontology/` against its schema |
| `./pipeline.sh build` | Rebuild `ontology_index.json` from valid entities |
| `./pipeline.sh add <type>` | Interactively scaffold a new entity file |
| `./pipeline.sh check <file>` | Validate a single entity file against its schema |
| `./pipeline.sh list` | List all entities in the index, grouped by type |
| `./pipeline.sh help` | Show help and usage examples |

---

## Adding a New Intelligence — Step by Step

### Option A: Interactive (recommended for beginners)

```bash
# 1. Run the scaffold command with the ontology type
./pipeline.sh add ai

# 2. Follow the prompts:
#    - Entity ID (UPPERCASE): NEURAL_NET
#    - Entity name: Neural Network
#    - Filename (snake_case): neural_network
#    - Description: Foundational AI architecture...

# 3. Edit the generated file to add patterns, links, etc.
nano ontology/ai/neural_network.json

# 4. Validate your new entity
./pipeline.sh check ontology/ai/neural_network.json

# 5. Rebuild the index
./pipeline.sh build
```

### Option B: Manual

1. **Create the JSON file** in the right directory:
   ```
   ontology/<type>/<snake_case_name>.json
   ```

2. **Include the three required fields**:
   ```json
   {
     "id": "UNIQUE_ID",
     "name": "Human-Readable Name",
     "ontology": "<type>"
   }
   ```

3. **Add type-specific fields** (see below).

4. **Validate and build**:
   ```bash
   ./pipeline.sh check ontology/<type>/<file>.json
   ./pipeline.sh build
   ```

---

## Available Ontology Types

| Type | Directory | Description |
|------|-----------|-------------|
| `animal` | `ontology/animal/` | Animal intelligences (bee, octopus, whale, etc.) |
| `plant` | `ontology/plant/` | Plant intelligences (mycelium, root networks) |
| `crystal` | `ontology/crystal/` | Crystal/mineral intelligences (quartz, diamond) |
| `energy` | `ontology/energy/` | Energy forms (flux, fields, bridges) |
| `plasma` | `ontology/plasma/` | Plasma intelligences (lightning, aurora) |
| `shape` | `ontology/shape/` | Geometric forms (torus, spiral, fractal) |
| `temporal` | `ontology/temporal/` | Temporal states (echo, fold, emergence) |
| `ai` | `ontology/ai/` | Artificial intelligences (neural nets, LLMs, RL) |

---

## Entity Template

Here is a complete template with all common fields:

```json
{
  "id": "YOUR_ID",
  "name": "Your Intelligence Name",
  "emoji": "🔮",
  "ontology": "ai",
  "symbolic_code": "[ID_CONCEPT_CONSTANT]",
  "description": "A clear description of this intelligence.",
  "core_attributes": {
    "architecture": "how it is structured",
    "pattern": "key patterns it embodies",
    "learning_mode": "how it learns or adapts",
    "efficiency_factor": 0.85
  },
  "patterns": [
    {
      "name": "pattern_name",
      "type": "pattern_category",
      "efficiency_factor": 0.90,
      "geometry": "geometric_form",
      "applications": ["use_case_1", "use_case_2"]
    }
  ],
  "links": [
    { "relation": "synergy", "target": "OTHER_ENTITY_ID" },
    { "relation": "geometry_link", "target": "SHAPE_ID" },
    { "relation": "resonance", "target": "ENTITY_ID" }
  ],
  "co_creation": true,
  "validation_meta": {
    "schema": "ai.schema.json",
    "version": "1.0"
  }
}
```

---

## Link / Relation Types

Use these relation types in the `links` array to connect entities:

| Relation | Meaning |
|----------|---------|
| `synergy` | Complementary intelligences that amplify each other |
| `geometry_link` | Shares a geometric pattern or structure |
| `resonance` | Resonates at similar frequencies or principles |
| `energy_coupling` | Energy transfer or coupling relationship |
| `temporal_bridge` | Connected across temporal states |
| `connected_to` | General relationship |
| `energy_mode` | Shares an energy transmission mode |

---

## Validation Rules

- **ID**: Must be unique across the entire database
- **Name**: Human-readable, descriptive
- **Ontology**: Must match the directory name and schema `const` value
- **Links**: Target IDs should reference existing entities (verify with `./pipeline.sh list`)
- **Filename**: Use `snake_case.json` (e.g., `neural_network.json`)

---

## Example Workflow

```bash
# See what's already in the database
./pipeline.sh list

# Add a new AI intelligence
./pipeline.sh add ai

# Edit the scaffolded file
# (add patterns, links, descriptions...)

# Check it validates
./pipeline.sh check ontology/ai/my_new_entity.json

# Run the full pipeline
./pipeline.sh

# Commit your addition
git add ontology/ai/my_new_entity.json
git commit -m "Create my_new_entity.json"
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `jsonschema not installed` | Run `pip install jsonschema` |
| `No schema for '<type>'` | Create a schema file at `schemas/<type>.schema.json` |
| `Missing required 'id' or 'name'` | Ensure your entity JSON has `id`, `name`, and `ontology` fields |
| `Validation error` | Check your entity against the schema in `schemas/<type>.schema.json` |
| Entity not in index | Run `./pipeline.sh build` to regenerate the index |
