# Exercise 03 — Propose a New Entity

**Goal**: Add a new entity that respects all the conventions.

**Time**: 20-30 minutes.

**⚠ Note**: This exercise writes a new file. Do it in a branch or be ready to `rm` the file afterward.

---

## The scenario

You have identified an intelligence that is missing from the database. For this exercise, propose **one of the following** (or pick your own):

- **Raven** (distinct from crow — larger, more tool use, different culture)
- **Naked Mole Rat** (eusocial mammal, pain-insensitive, cancer-resistant)
- **Portia Spider** (cognitive jumping spider that plans routes)
- **Baobab Tree** (ancient water-storage architecture, communal significance)
- **Your own choice** (must be genuinely different from existing entities)

## The task

### Step 1: Verify it is actually new

```bash
python scripts/query.py search raven
python scripts/query.py search "jumping spider"
```

**Rule**: If an entity already exists with the same name or obvious semantic overlap, pick a different one or **enrich** the existing entity instead.

### Step 2: Check existing similar entities

Before writing, look at 2-3 existing entities of the same type to learn the conventions:

```bash
python scripts/query.py entity CROW
python scripts/query.py entity SP
python scripts/query.py entity WOLF
```

Notice:
- How descriptions are written (dense, pattern-focused)
- How many links are typical (3-6)
- Which relation types appear
- How `core_attributes` and `patterns` are structured

### Step 3: Draft your entity

Start from `training/templates/entity_template.json`. Fill in:

- `id` — short UPPERCASE, avoid collision with existing IDs
- `name` — human-readable
- `ontology` — pick the right type
- `emoji` — a single emoji
- `symbolic_code` — `[ID_CONCEPT_CONSTANT]` pattern
- `description` — **the most important field**. Make it dense and pattern-focused. No filler.
- `core_attributes` — at least `pattern` and `efficiency_factor`
- `patterns` — 2-3 patterns with name, type, efficiency_factor, and applications
- `links` — 3-6 connections to existing entities. **Check each target exists.**
- `co_creation: true`
- `validation_meta` — schema reference

### Step 4: Verify every link target

For each `target` in your `links`, confirm it exists:

```bash
python scripts/query.py entity <TARGET_ID>
```

If any target does not exist, fix the reference before saving.

### Step 5: Save and validate

Save the file to `ontology/<type>/<snake_case>.json`, then:

```bash
./pipeline.sh check ontology/<type>/<your_file>.json
```

Expected output: `Entity is valid!`

If it fails, read the error carefully and fix. Common issues:
- Missing required field
- Wrong type (e.g., `efficiency_factor` must be a number, not a string)
- Extra comma or syntax error

### Step 6: Build the index

```bash
./pipeline.sh build
```

Watch for:
- `broken link` warnings
- Duplicate ID errors
- Your new entity count appearing in the total

### Step 7: Confirm it is queryable

```bash
python scripts/query.py entity YOUR_ID
python scripts/query.py neighbors YOUR_ID
```

Your entity should appear with all its connections.

## Verification checklist

Your entity is complete when:

- [ ] It validates against its schema
- [ ] Every link target exists in the index
- [ ] It has at least 3 links
- [ ] Its description is dense and pattern-focused (not encyclopedic filler)
- [ ] It has `co_creation: true`
- [ ] It appears in the index after `build`
- [ ] `query.py entity YOUR_ID` returns useful information
- [ ] It does not duplicate an existing entity

## Bonus: Propose a rule

If your new entity connects multiple domains in a novel way, propose an expander rule:

```json
{ "if": ["YOUR_ID", "EXISTING_ID_1", "EXISTING_ID_2"], "then": "EMERGENT_CONCEPT_NAME" }
```

Add it to `rules/expander_rules.json` and test:

```bash
python scripts/query.py expand YOUR_ID EXISTING_ID_1 EXISTING_ID_2
```

## Cleanup (if this was just practice)

```bash
rm ontology/<type>/<your_file>.json
./pipeline.sh build
```

The index will automatically update.

## Reflection

- What was the hardest part?
- Did the schema catch any mistakes you would have missed?
- Did any of your link targets turn out to be missing or wrong?
- Did you discover any existing entity you had not noticed before while picking links?

## You are ready

If you completed this exercise successfully, you can safely contribute to the database without breaking anything. Welcome to co-creation.
