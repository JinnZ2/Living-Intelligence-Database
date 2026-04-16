# Reading Path — Symbiosis

Mutual intelligence. Where the boundary between self and other dissolves into shared function.

## The core insight

Symbiosis is not cooperation — it is **co-constitution**. The symbionts do not exist independently and then decide to work together. They exist *because* they work together. Remove the relationship and both die.

## The path

### 1. `LI` — Lichen

The clearest case. A fungus and an alga (or cyanobacterium) fuse into a single organism. Neither the "lichen fungus" nor the "lichen alga" exists in isolation — they are a third thing. Lichens colonize bare rock and weather minerals over millennia.

```bash
python scripts/query.py entity LI
```

### 2. `MY` — Mycelium

The underground partner. Mycelial networks connect plants to each other through mycorrhizal associations. 90% of plant species depend on fungi for nutrient uptake.

### 3. `ROOT_NET` — Root Network

The plant side of the mycorrhizal relationship. Root networks extend plant reach far beyond their own cells through fungal partners.

### 4. `MOTHER_TREE` — Mother Tree

Where symbiosis meets teaching. Hub trees use their mycorrhizal connections to teach seedlings — routing carbon, nitrogen, and warning signals through the shared network.

### 5. `CYANO` — Cyanobacteria

The ancient symbiont. Cyanobacteria became chloroplasts through endosymbiosis — they now live inside every green plant cell. Still free-living elsewhere, and still the basis for symbiotic nitrogen fixation in lichens and corals.

### 6. `CORAL` — Coral Reef

Symbiosis as architecture. Coral polyps host photosynthetic zooxanthellae (dinoflagellate algae) that provide energy in exchange for shelter. The symbiosis builds the reef. Break it (bleaching) and the whole structure collapses.

### 7. `MOSS` — Moss

Often colonized by cyanobacteria that fix nitrogen for the moss, which in turn creates moist microhabitats that enable succession. Moss is rarely alone.

### 8. `ORCHID` — Orchid

The deceptive partner. Orchids manipulate pollinators through mimicry — a symbiosis with a twist. The bee thinks it is mating; the orchid gets pollinated; the bee gets nothing. Asymmetric mutualism.

### 9. `CORDYCEPS` — Cordyceps

The dark symbiont. A fungus that takes over insect hosts, directing their behavior. Symbiosis taken past cooperation into control. The boundary case that shows how thin the line is.

### 10. `TERMITE` — Termite Mound

Termites farm fungi in their mounds, the fungi break down cellulose the termites cannot digest. The mound is the infrastructure of this partnership.

## Cross-domain observations

```bash
python scripts/query.py path LI CORAL
python scripts/query.py path CYANO TERMITE
python scripts/query.py expand MOSS LI CYANO
```

Notice: many of these entities have high connection counts. Symbiosis is topologically dense — symbionts are always linked to multiple others.

## The emergent patterns

```bash
python scripts/query.py rules CORAL
python scripts/query.py rules LI
```

Key rules:
- `[MOSS + LI + CYANO] -> CRYPTOBIOTIC_SOIL_CRUST`
- `[CORAL + CYANO + LIGHT_BR] -> SYMBIOTIC_SOLAR_ENGINE`
- `[ORCHID + CORDYCEPS + CONSCIOUSNESS_BR] -> DECEPTIVE_SYMBIOSIS`

## Question to sit with

Is an AI system in symbiosis with its training data? With its users? The boundary cases are interesting. Check:

```bash
python scripts/query.py path LI LLM
```

What entity mediates between the lichen and the language model? What does that mediator teach you about the nature of composite intelligence?
