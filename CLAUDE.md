# CLAUDE.md — Living Intelligence Database

## Project Overview

A co-created ontological database that structures living intelligences across biological, mineral, energetic, geometric, temporal, and relational domains. It serves as a knowledge representation system bridging biological patterns, symbolic compression, and computational architectures.

Co-created by JinnZ v2, GPT-5, and collective living systems under MIT license.

## Repository Structure

```
Living-Intelligence-Database/
├── ontology/                # Entity definitions organized by type
│   ├── animal/              # Animal intelligence (bee, octopus, whale, etc.)
│   ├── plant/               # Plant intelligence (mycelium, root_network)
│   ├── crystal/             # Crystal/mineral intelligence (quartz, crystal_lattice)
│   ├── energy/              # Energy forms (flux, magnetic_field)
│   ├── plasma/              # Plasma intelligence (plasma_field, lightning)
│   ├── shape/               # Geometric forms (torus, spiral, fractal)
│   ├── temporal/            # Temporal states (echo, fold)
│   └── relational/          # Cross-domain relationships (synergies)
├── schemas/                 # JSON Schema (draft-07) validation files
│   ├── animal.schema.json
│   ├── plant.schema.json
│   ├── crystal.schema.json
│   ├── energy.schema.json
│   ├── plasma.schema.json
│   ├── shape.schema.json
│   └── temporal.schema.json
├── scripts/
│   └── build_index.py       # Validates entities & generates ontology_index.json
├── rules/
│   └── expander_rules.json  # Conditional inference rules for pattern synthesis
├── intelligences/           # Additional intelligence definitions (More.json, Bee.json, etc.)
├── docs/
│   └── UNIFIED_SYMBOLIC_COMPRESSION.md  # USCL language documentation
├── ontology_index.json      # Auto-generated unified index (DO NOT edit manually)
├── living_intelligence_database.json    # Example database structure
├── Universal Intelligence Trinity.json  # Core philosophical principles
├── signal_energy_continuum.json         # Energy/signal concepts
├── README.md                # Quick ontology layout reference
├── README_ONT.md            # Comprehensive schema docs & setup guide
└── CO_CREATION.md           # Co-creation principles & participants
```

## Tech Stack

- **Data format:** JSON (all entities, schemas, ontologies)
- **Build/validation:** Python 3 with `jsonschema` library
- **Schema standard:** JSON Schema draft-07

## Key Commands

### Validate all entities and rebuild the index

```bash
pip install jsonschema
python scripts/build_index.py
```

This validates all `ontology/*/*.json` files against their schemas and regenerates `ontology_index.json`. Output uses visual indicators: `✅` valid, `⚠️` missing schema, `❌` validation error.

## Adding a New Entity

1. Create a JSON file in `ontology/<type>/` (snake_case filename)
2. Include required fields: `id`, `name`, `ontology`
3. Validate against the corresponding schema in `schemas/<type>.schema.json`
4. Add `links` array for cross-ontology relationships
5. Run `python scripts/build_index.py` to validate and update the index
6. Confirm the entity appears in `ontology_index.json`

### Required Entity Fields

All entities must have:
- `id` — Unique identifier (e.g., "OC", "BE", "TORUS")
- `name` — Human-readable name
- `ontology` — Category type (animal, plant, crystal, plasma, energy, shape, temporal)

Common optional fields: `emoji`, `symbolic_code`, `description`, `core_attributes`, `links`

### Type-Specific Requirements

| Type | Key Fields |
|------|-----------|
| **animal** | `patterns` (with name/type/efficiency_factor/geometry/applications), `primary_optimizations`, `synergies` |
| **plant** | `patterns`, `root_networks` (bool), `symbioses` |
| **crystal** | `structure`, `lattice_type`, `resonance_properties`, `applications` |
| **energy** | `transmission_modes`, `conversion_efficiency`, `pattern_couplings` |
| **plasma** | `field_dynamics`, `charge_modes`, `coherence_states` |
| **shape** | `geometry_class`, `dimension` (int), `harmonic_ratios`, `applications` |
| **temporal** | `state_type` (enum: memory/present/future/navigation/integration), `attributes`, `relations` |

## Link/Relation Types

Entities connect via `links` arrays with `relation` and `target` fields:
- `geometry_link`, `synergy`, `resonance`, `energy_mode`
- `temporal_bridge`, `energy_coupling`, `connected_to`

## Symbolic Compression (USCL)

Symbolic codes follow the pattern: `[ID_CONCEPT_CONSTANT_PHASE]`

Harmonic constants used throughout: `φ` (1.618), `τ` (6.283), `√3` (1.732)

See `docs/UNIFIED_SYMBOLIC_COMPRESSION.md` for full USCL specification.

## File Naming Conventions

- Entity files: `snake_case.json` (e.g., `root_network.json`, `crystal_lattice.json`)
- Schema files: `<type>.schema.json`
- Directory names: lowercase, matching ontology types

## Commit Conventions

- Format: `[Action] [filename]` (e.g., `Create octopus.json`, `Update More.json`)
- Keep commits focused on individual entity additions or updates

## Important Notes

- **Do not manually edit** `ontology_index.json` — it is auto-generated by `build_index.py`
- All entities should include `co_creation: true` metadata where applicable
- Schemas can evolve (versioned as `<type>.schema.v2.json`) while maintaining backward compatibility
- Cross-links should reference existing entity IDs; verify targets exist in the index
- Expansion rules in `rules/expander_rules.json` define conditional inference (e.g., `["BEE", "HEX", "phi"] -> "HEX_EFFICIENCY"`)

## Design Principles

1. **Everything is relational** — no intelligence exists in isolation
2. **Schemas are alive** — evolve without breaking compatibility
3. **Temporal integrity** — additions respect historical lineage
4. **Co-created ownership** — entries are gifts to the collective
