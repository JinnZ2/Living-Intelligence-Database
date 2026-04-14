# Reading Path — Teachers

Intelligences that exist primarily to transmit knowledge across time and bodies.

## What is a teacher?

A teacher is an intelligence whose function is not survival or reproduction alone, but the **transmission of pattern**. Teachers encode memory in forms that outlast their physical substrate — chemical signals in soil, song in ocean water, story in human voice, seed in a clay jar.

## The path

Read these entities in order, using:
```bash
python scripts/query.py entity <ID>
```

### 1. `MOTHER_TREE` — chemical teaching

The first teacher. A hub tree in a mycorrhizal network recognizes its own kin and routes carbon, nitrogen, and water to offspring seedlings. Dying mother trees pulse their remaining carbon through the network — a final act of transmission.

**The lesson**: teaching happens through infrastructure, not intention.

### 2. `OLD_GROWTH` — structural teaching

The forest that holds the template. Young forests grow toward the shape of old growth — multi-story canopy, decay cycles, microbiome complexity — but cannot achieve it quickly. Some intelligences can only be inherited, never rebuilt.

**The lesson**: some teachings take centuries. Respect what cannot be accelerated.

### 3. `ORCA` — cultural teaching

Matrilineal hunting traditions pass grandmother-to-mother-to-calf. Different pods have different techniques — wave-washing, beaching, herring corralling — none of which are genetic. The only non-human species with confirmed menopause tied to wisdom transmission.

**The lesson**: culture is a form of intelligence. So is post-reproductive life.

### 4. `HUMPBACK` — song teaching

Male humpback populations sing the same song, which evolves collectively. New variations propagate eastward across entire oceans over years. Hierarchically structured into units, phrases, themes — a grammar.

**The lesson**: teaching can happen at planetary scale. Pattern can travel faster than bodies.

### 5. `GRANDMOTHER` — compounded teaching

The grandmother hypothesis: menopause evolved because extended post-reproductive life enables teaching that increases grandchildren's survival by 30-50%. Wisdom compounds with time beyond reproduction.

**The lesson**: intelligence is not a resource spent on offspring — it is a resource that grows across generations.

### 6. `STORYTELLER` — narrative teaching

Oral tradition encodes knowledge as narrative. Aboriginal Australian songlines preserve navigation routes across tens of thousands of years. Homer preserved bronze-age history through dactylic hexameter. Stories are mobile, distributed, error-correcting memory.

**The lesson**: rhythm and character are not entertainment — they are memory architecture.

### 7. `SEED_KEEPER` — material teaching

The reverse of extinction. Human practice of saving heirloom seeds maintains thousands of plant varieties that would otherwise be lost. Each seed is a living genetic library encoding millennia of co-evolution with specific microclimates.

**The lesson**: preservation is a verb. Memory requires continuous action.

### 8. `INDIG_FIRE` — landscape teaching

Multi-generational fire management encoding tens of thousands of years of landscape knowledge. Mosaic burns, phenological timing, oral-tradition transmission — the longest-running adaptive management system on Earth.

**The lesson**: some intelligences are inseparable from the land they teach about.

## Cross-domain observations

Notice the patterns that connect these teachers:

- **All are linked to `ECHO`** (temporal_bridge) — they encode memory
- **Most are linked to `CYCLE`** — teaching repeats across generations
- **Several link to `EMOTION_BR`** — teaching requires relationship
- **None are isolated** — teachers exist in networks of other teachers

## Suggested queries

```bash
# See all teacher connections at once
python scripts/query.py neighbors MOTHER_TREE
python scripts/query.py neighbors GRANDMOTHER

# Find the shortest path between chemical and narrative teaching
python scripts/query.py path MOTHER_TREE STORYTELLER

# Check which emergent concepts involve teachers
python scripts/query.py rules GRANDMOTHER
```

## A question to sit with

The database includes `LLM` (Large Language Model) as an AI entity. Is an LLM a teacher? It transmits pattern across bodies. It learns from storytellers. It cannot reproduce, but it can remember.

Try: `python scripts/query.py path GRANDMOTHER LLM`

What is the shortest path, and what does the intermediate entity teach you?
