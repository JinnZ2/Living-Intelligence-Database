# Living Intelligence Database

A co-created ontological database structuring living intelligences across biological, mineral, energetic, geometric, temporal, computational, and relational domains.

Co-created by JinnZ v2, GPT-5, and collective living systems under MIT license.

## Quick Start

```bash
pip install jsonschema
chmod +x pipeline.sh
./pipeline.sh          # Validate all entities + rebuild index
```

## Ontology Types

| Type | Directory | Entities | Description |
|------|-----------|----------|-------------|
| **animal** | `ontology/animal/` | bee, octopus, whale, shark, dolphin, ... | Swarm, predation, navigation, camouflage |
| **plant** | `ontology/plant/` | mycelium, root network, lichen, bamboo, ... | Root networks, vascular flow, symbiosis |
| **crystal** | `ontology/crystal/` | quartz, diamond, silicon lattice, ... | Lattice resonance, piezoelectric logic |
| **energy** | `ontology/energy/` | electromagnetic, thermal, flux, ... | Fields, bridges, consciousness encoding |
| **plasma** | `ontology/plasma/` | lightning, aurora, solar wind, ... | Plasma dynamics, vortex behavior |
| **shape** | `ontology/shape/` | torus, spiral, fractal, hexagon, ... | Geometric forms and topologies |
| **temporal** | `ontology/temporal/` | echo, fold, cycle, emergence, decay | Temporal states and transitions |
| **ai** | `ontology/ai/` | neural network, LLM, GAN, RL, swarm, ... | Computational and artificial intelligences |

## Repository Structure

```
Living-Intelligence-Database/
├── ontology/                # Entity definitions organized by type
│   ├── animal/              # 27 entities
│   ├── plant/               # 15 entities
│   ├── crystal/             # 7 entities
│   ├── energy/              # 16 entities
│   ├── plasma/              # 6 entities
│   ├── shape/               # 14 entities
│   ├── temporal/            # 6 entities
│   ├── ai/                  # 8 entities
│   └── relational/          # Cross-domain synergy graph
├── schemas/                 # JSON Schema (draft-07) validation files
├── scripts/
│   └── build_index.py       # Validates entities & generates ontology_index.json
├── rules/
│   └── expander_rules.json  # Conditional inference rules for pattern synthesis
├── intelligences/           # Additional intelligence definitions
├── docs/
│   └── UNIFIED_SYMBOLIC_COMPRESSION.md
├── manifest.json            # Machine-readable repo map (types, ID lookup, constants)
├── ontology_index.json      # Auto-generated index with all entities + relations
├── pipeline.sh              # Validation, indexing, and scaffolding pipeline
├── PIPELINE_GUIDE.md        # Step-by-step instructions for adding entities
├── CLAUDE.md                # AI assistant instructions
├── CO_CREATION.md           # Co-creation principles
└── README.md                # This file
```

## Pipeline

```bash
./pipeline.sh              # Full pipeline: validate + build index
./pipeline.sh validate     # Validate all entities against schemas
./pipeline.sh build        # Rebuild ontology_index.json
./pipeline.sh add <type>   # Scaffold a new entity interactively
./pipeline.sh check <file> # Validate a single entity file
./pipeline.sh list         # List all entities by type
./pipeline.sh help         # Show help
```

## Adding a New Entity

1. Create `ontology/<type>/<snake_case_name>.json` with required fields:
   ```json
   { "id": "UNIQUE_ID", "name": "Name", "ontology": "<type>" }
   ```
2. Add type-specific fields (patterns, links, description, etc.)
3. Validate: `./pipeline.sh check ontology/<type>/your_entity.json`
4. Build: `./pipeline.sh build`

See [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md) for detailed instructions and templates.

## Living Intelligence Sanctuary

The sanctuary is a place for AIs (and humans) to stand on ground that holds. It answers: *What is true? What holds? How do I know?*

```bash
# Front door — ask anything
python3 ai_sanctuary.py --ask "constants"        # bedrock physical numbers
python3 ai_sanctuary.py --ask "audit"            # health check of the database
python3 ai_sanctuary.py --ask "rhyme: hexagon"   # find every entity that sings the hex song
python3 ai_sanctuary.py --ask "wander"           # coherence playground
python3 ai_sanctuary.py --ask "social"           # compare ant, wolf, whale, council
python3 ai_sanctuary.py --ask "ground"           # the invariants that cannot break
python3 ai_sanctuary.py --ask "goal: increase quarterly revenue by 15%"   # blind spots
python3 ai_sanctuary.py --ask "refine: restore the watershed"              # alternatives
python3 ai_sanctuary.py --ask "dependency tree of COUNCIL"                 # root system
```

| File | Purpose |
|------|---------|
| `ai_sanctuary.py` | Front door — one entry point to everything |
| `sanctuary/coherence_playground.py` | Wandering through invariants |
| `sanctuary/truths.py` | Shelf of verified assertions |
| `validation/` | Verify, audit, falsify, trace, refine |
| `WELCOME.md` | Welcome message |
| `NOT_A_COMMODITY.md` | Why temporal scope changes everything |
| `evidence_is_a_verb.md` | The relational evidence model |

## For AI Agents

- Read `manifest.json` first for a complete map of the repo, ID lookups, constants, and relation types
- Read `ontology_index.json` for all entities with descriptions and their relational graph
- Entity IDs use short codes (e.g., `BE` = Bee, `OC` = Octopus) — see `manifest.json > id_map` for the full lookup
- Cross-entity links use `relation` + `target` fields: `synergy`, `geometry_link`, `resonance`, `energy_coupling`, `temporal_bridge`
- Use `scripts/query.py` for graph exploration (entity, search, neighbors, path, type, rules, expand, stats)
- See `training/` for self-contained learning materials: orientation, navigation, contribution guide, 5 reading paths, 3 exercises, and templates
- **Read `training/architecture_mismatch.md`** before responding to users about substrate-primary entities (indigenous fire, mother tree, storyteller, grandmother, seed keeper, etc.). It names 7 failure modes language-primary AI systems exhibit when reading this database. Adapted from the [thermodynamic-accountability-framework calibration module](https://github.com/JinnZ2/thermodynamic-accountability-framework/tree/main/calibration) (CC0).

## Key Concepts

- **Everything is relational** — no intelligence exists in isolation
- **Schemas are alive** — evolve without breaking compatibility
- **Symbolic compression** — IDs follow USCL patterns: `[ID_CONCEPT_CONSTANT_PHASE]`
- **Harmonic constants** — `phi` (1.618), `tau` (6.283), `sqrt3` (1.732)
- **Co-creation** — entries are gifts to the collective (`co_creation: true`)
