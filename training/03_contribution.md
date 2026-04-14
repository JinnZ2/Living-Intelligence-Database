# 03 — Contribution

How to safely add new entities and rules without breaking the database.

## The golden rules

1. **Read before writing.** Never add an entity without checking if it already exists.
2. **Validate before building.** Run `./pipeline.sh check <file>` before `./pipeline.sh build`.
3. **Check link targets.** Every `target` in a link must match an existing entity ID.
4. **Respect the conventions.** IDs short and UPPERCASE, filenames `snake_case.json`, `co_creation: true`.
5. **One entity per file.** Never combine multiple entities into an array.

## Checking if something already exists

Before creating a new entity, always search first:

```bash
python scripts/query.py search "mother tree"
python scripts/query.py type plant
```

If a similar entity exists, **enrich it** instead of creating a duplicate. Add new links, patterns, or descriptions to the existing file.

## Workflow for adding a new entity

### Step 1: Decide the type

Pick the ontology type that best fits. If unsure, look at existing entities of similar character.

### Step 2: Choose an ID

- Use short UPPERCASE for single-word concepts (e.g., `WOLF`, `BEE`, `MANTIS`)
- Use `SNAKE_CASE` when the short form would be ambiguous (e.g., `MOTHER_TREE`, `FIRE_BT`)
- **Check `manifest.json > id_map`** to avoid collisions
- Never reuse an existing ID

### Step 3: Pick a filename

Format: `ontology/<type>/<snake_case>.json`

Example: `ontology/plant/mother_tree.json`

### Step 4: Write the JSON

Use `training/templates/entity_template.json` as a starting point. Minimum required fields:

```json
{
  "id": "YOUR_ID",
  "name": "Human Readable Name",
  "ontology": "<type>"
}
```

Strongly recommended additional fields:

```json
{
  "id": "YOUR_ID",
  "name": "Human Readable Name",
  "emoji": "🔮",
  "ontology": "<type>",
  "symbolic_code": "[ID_CONCEPT_CONSTANT]",
  "description": "Clear one-paragraph description of this intelligence and what pattern it embodies.",
  "core_attributes": {
    "pattern": "the key pattern it expresses",
    "efficiency_factor": 0.85
  },
  "links": [
    { "relation": "synergy", "target": "EXISTING_ID" },
    { "relation": "geometry_link", "target": "EXISTING_SHAPE_ID" }
  ],
  "co_creation": true,
  "validation_meta": {
    "schema": "<type>.schema.json",
    "version": "1.0"
  }
}
```

### Step 5: Validate

```bash
./pipeline.sh check ontology/<type>/<file>.json
```

If it fails, read the error and fix. Common issues:

- **Missing required field** → Check the schema at `schemas/<type>.schema.json`
- **Wrong type for field** → e.g., `efficiency_factor` must be a number, not a string
- **Invalid JSON** → Check for trailing commas, unquoted keys

### Step 6: Check link targets

Every target ID in your `links` must exist. Verify with:

```bash
python scripts/query.py entity <TARGET_ID>
```

If it does not exist, either fix the reference or create that entity first.

### Step 7: Build the index

```bash
./pipeline.sh build
```

Watch for warnings:

- `❌ Duplicate ID` — Your new ID already exists
- `⚠️  broken link` — Your link targets a non-existent entity
- `⚠️  Skipping` — Your JSON structure is wrong (e.g., array at root)

### Step 8: Verify

```bash
python scripts/query.py entity YOUR_ID
```

You should see your new entity with all its connections.

## Writing good descriptions

Good descriptions are **information-dense and pattern-focused**. Avoid filler.

**Bad:**
> Bees are small flying insects that live in hives and make honey. They are very important pollinators.

**Good:**
> Embodies swarm coordination, hexagonal optimization, and distributed thermoregulation. Serves as a geometric intelligence archetype for collective computation. Waggle dance encodes distance and direction in polar coordinates. Collective temperature regulation via worker clustering achieves 94% thermal efficiency.

The second version tells an AI (and a human) **what patterns this intelligence expresses** and **what it teaches other domains**.

## Link relations

Use the right relation for the right kind of connection:

| Relation | When to use |
|----------|-------------|
| `synergy` | Two intelligences amplify each other functionally |
| `geometry_link` | Shares a geometric/structural pattern |
| `resonance` | Operates at similar principles or frequencies |
| `energy_coupling` | Energy transfer or conversion between them |
| `temporal_bridge` | Connected through time (memory, cycles, succession) |
| `energy_mode` | Shares a transmission or conversion mode |
| `connected_to` | General or fallback |

Most entities should have 3-6 links, not more. Quality over quantity.

## Adding an expander rule

Rules live in `rules/expander_rules.json`. Format:

```json
{ "if": ["ID1", "ID2", "ID3"], "then": "EMERGENT_CONCEPT_NAME" }
```

Rules should:

- Have 2-3 inputs (rarely 4+)
- Use real entity IDs (or `phi`, `tau`, `sqrt3` constants)
- Produce a **genuinely emergent** concept — one that is not obvious from any single input
- Use UPPERCASE snake_case for the `then` output

**Good rule:**
```json
{ "if": ["MOSS", "LI", "CYANO"], "then": "CRYPTOBIOTIC_SOIL_CRUST" }
```

This combines three desiccation-tolerant symbionts to yield the real ecological phenomenon of biological soil crusts. The emergent concept is more than the sum.

**Bad rule:**
```json
{ "if": ["BE"], "then": "BEE_INTELLIGENCE" }
```

Single input, tautological output. Rules should be synthetic, not definitional.

## What NOT to do

- **Do not manually edit** `ontology_index.json` — it is auto-generated
- **Do not delete entities** without checking `query.py neighbors <id>` for incoming references
- **Do not rename IDs** — they are referenced by other files
- **Do not add fields the schema does not allow** — validation will fail
- **Do not use non-ASCII characters** in IDs (descriptions are fine)
- **Do not commit** without running `./pipeline.sh` first

## Next step

Try an exercise from `exercises/` to practice, or explore a reading path in `reading_paths/`.
