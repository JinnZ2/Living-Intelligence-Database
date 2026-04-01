#!/usr/bin/env python3
"""
Compute and assign edge weights to the synergies graph.

Weights are derived from:
- Entity efficiency factors (higher = stronger link)
- Link relation type (synergy > resonance > geometry_link > connected_to)
- Shared pattern types between entities
- Bidirectionality (mutual links score higher)

Run: python scripts/weight_edges.py
"""

import json
from pathlib import Path
from itertools import combinations

ROOT = Path(__file__).resolve().parents[1]
SYNERGIES = ROOT / "ontology" / "relational" / "synergies.json"
ONTOLOGY_DIR = ROOT / "ontology"

# Relation type base weights
RELATION_WEIGHTS = {
    "synergy": 1.0,
    "resonance": 0.8,
    "energy_coupling": 0.7,
    "energy_exchange": 0.7,
    "geometry_link": 0.6,
    "temporal_bridge": 0.5,
    "connected_to": 0.4,
}


def load_entities():
    """Load all entities into a dict keyed by ID."""
    entities = {}
    for layer in ONTOLOGY_DIR.iterdir():
        if not layer.is_dir():
            continue
        for fp in layer.glob("*.json"):
            try:
                with open(fp) as f:
                    data = json.load(f)
                if isinstance(data, dict) and "id" in data:
                    entities[data["id"]] = data
            except Exception:
                continue
    return entities


def entity_efficiency(entity):
    """Extract the best efficiency factor from an entity."""
    eff = 0.9
    core = entity.get("core_attributes", {})
    if isinstance(core.get("efficiency_factor"), (int, float)):
        eff = core["efficiency_factor"]
    for p in entity.get("patterns", []):
        if isinstance(p.get("efficiency_factor"), (int, float)):
            eff = max(eff, p["efficiency_factor"])
    return eff


def shared_pattern_types(a, b):
    """Count shared pattern type keywords between two entities."""
    def get_types(entity):
        types = set()
        for p in entity.get("patterns", []):
            t = p.get("type", "")
            if t:
                types.add(t)
        core = entity.get("core_attributes", {})
        pattern_str = core.get("pattern", "")
        if pattern_str:
            types.update(w.strip() for w in pattern_str.split(","))
        return types

    a_types = get_types(a)
    b_types = get_types(b)
    return len(a_types & b_types)


def is_bidirectional(entity_a_id, entity_b_id, entities):
    """Check if both entities link to each other."""
    a = entities.get(entity_a_id, {})
    b = entities.get(entity_b_id, {})
    a_targets = {l.get("target") for l in a.get("links", [])}
    b_targets = {l.get("target") for l in b.get("links", [])}
    return entity_b_id in a_targets and entity_a_id in b_targets


def compute_weight(edge, entities):
    """Compute weight for a single edge."""
    source_id = edge["source"]
    target_id = edge["target"]
    relation = edge["relation"]

    source = entities.get(source_id, {})
    target = entities.get(target_id, {})

    # Base weight from relation type
    base = RELATION_WEIGHTS.get(relation, 0.3)

    # Efficiency bonus: average of both entities
    eff_source = entity_efficiency(source)
    eff_target = entity_efficiency(target)
    eff_avg = (eff_source + eff_target) / 2.0

    # Shared pattern bonus
    shared = shared_pattern_types(source, target)
    pattern_bonus = min(shared * 0.05, 0.2)  # cap at 0.2

    # Bidirectional bonus
    bidir_bonus = 0.15 if is_bidirectional(source_id, target_id, entities) else 0.0

    # Final weight: base × efficiency + bonuses
    weight = round(base * eff_avg + pattern_bonus + bidir_bonus, 3)
    return min(weight, 1.0)  # cap at 1.0


def main():
    entities = load_entities()

    with open(SYNERGIES) as f:
        graph = json.load(f)

    print(f"Computing weights for {len(graph['edges'])} edges...\n")

    weight_stats = {"min": 1.0, "max": 0.0, "total": 0.0}

    for edge in graph["edges"]:
        w = compute_weight(edge, entities)
        edge["weight"] = w
        weight_stats["min"] = min(weight_stats["min"], w)
        weight_stats["max"] = max(weight_stats["max"], w)
        weight_stats["total"] += w

    avg = weight_stats["total"] / len(graph["edges"])

    # Write back in compact format
    lines = ["{", '  "nodes": [']
    for i, n in enumerate(graph["nodes"]):
        comma = "," if i < len(graph["nodes"]) - 1 else ""
        lines.append(f'    {{ "id": "{n["id"]}", "label": "{n["label"]}" }}{comma}')
    lines.append("  ],")
    lines.append('  "edges": [')
    for i, e in enumerate(graph["edges"]):
        comma = "," if i < len(graph["edges"]) - 1 else ""
        lines.append(
            f'    {{ "source": "{e["source"]}", "target": "{e["target"]}", '
            f'"relation": "{e["relation"]}", "weight": {e["weight"]} }}{comma}'
        )
    lines.append("  ]")
    lines.append("}")

    with open(SYNERGIES, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"  Weights: min={weight_stats['min']:.3f}  max={weight_stats['max']:.3f}  avg={avg:.3f}")
    print(f"  Written to {SYNERGIES.relative_to(ROOT)}")

    # Show top 10 strongest edges
    ranked = sorted(graph["edges"], key=lambda e: e["weight"], reverse=True)
    print(f"\n  Top 10 strongest edges:")
    for e in ranked[:10]:
        print(f"    {e['source']:>15} <-> {e['target']:<15} [{e['relation']}] w={e['weight']}")

    # Show bottom 5 weakest
    print(f"\n  Bottom 5 weakest edges:")
    for e in ranked[-5:]:
        print(f"    {e['source']:>15} <-> {e['target']:<15} [{e['relation']}] w={e['weight']}")


if __name__ == "__main__":
    main()
