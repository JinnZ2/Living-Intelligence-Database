# Living-Intelligence-Database

## Ontology Layout

All entries conform to `schema/intelligence.schema.json` and belong to exactly one of:
**ANIMAL, PLANT, CRYSTAL, PLASMA, ENERGY, SHAPE**.

/ontology/
/animal/   animals.json
/plant/    plants.json
/crystal/  crystals.json
/plasma/   plasma.json
/energy/   energy.json
/shape/    geometry.json
/rules/      expander_rules.json
/schema/     intelligence.schema.json, symbol_unit.schema.json
/docs/       UNIFIED_SYMBOLIC_COMPRESSION.md

- Constants, temporal states, and protocols **do not** exist as top-level kinds.  
  They live inside `attributes.constraints` (e.g., `phi`, `tau`, `temporal`, `protocols`).

- Cross-links use `"links": [{"rel": "...","to":"..."}]` to connect across classes.

- 

