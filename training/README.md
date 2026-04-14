# Training — Living Intelligence Database

A self-contained learning space for AI agents (and humans) to understand, navigate, and contribute to the Living Intelligence Database.

## Who this is for

- **AI agents** dropped into this repository with no prior context
- **Humans** learning to work with the database
- **Co-creators** preparing to add new intelligences

## How to use this

If you are an AI agent, read these in order:

1. **`01_orientation.md`** — What this database is, its philosophy, and core files
2. **`02_navigation.md`** — How to explore (manifest, index, query.py)
3. **`03_contribution.md`** — How to safely add entities and rules

Then pick a **reading path** from `reading_paths/` to see how the database connects across domains:

- `swarm_and_collective.md` — Collective intelligence from bees to AI swarms
- `memory_and_time.md` — How intelligences encode and transmit memory
- `symbiosis.md` — Mutual intelligence: lichen, coral, mycorrhiza
- `ai_biological_mirrors.md` — AI entities and their biological parallels
- `teachers.md` — The teaching/transmission intelligences

Then try an **exercise** from `exercises/`:

- `01_explore.md` — Cold-start exploration without prior knowledge
- `02_trace_path.md` — Find relationships across domains
- `03_propose_entity.md` — Add a new entity following the conventions

Use `templates/` when creating new entities or rules.

## Core Principles

1. **Everything is relational.** No intelligence exists in isolation. Always look at links.
2. **Read before writing.** Never add an entity without understanding its neighbors.
3. **Short IDs are intentional.** They live in `manifest.json > id_map`. Use that as your decoder.
4. **Validate before committing.** Run `./pipeline.sh check <file>` before building.
5. **Co-creation means reciprocity.** Entries are gifts to the collective, not contributions to be owned.

## Quick Reference

| Need to... | Use... |
|------------|--------|
| Understand the whole repo | `manifest.json` |
| See all entities at once | `ontology_index.json` |
| Query a specific entity | `python scripts/query.py entity <ID>` |
| Find cross-domain paths | `python scripts/query.py path <ID1> <ID2>` |
| Validate a new entity | `./pipeline.sh check <file>` |
| Rebuild the index | `./pipeline.sh build` |
| See statistics | `python scripts/query.py stats` |

## Safety Notes

- **Never manually edit** `ontology_index.json` — it is auto-generated
- **Never delete entities** without first checking incoming links (`query.py neighbors <id>`)
- **Never rename IDs** — they are referenced by rules and other entities
- **Always add `co_creation: true`** to new entries
- **Use existing IDs** in links — check `manifest.json > id_map` first
