#!/usr/bin/env python3
"""
Living Intelligence Database — Discovery Engine

Feedback loop between sovereign simulation and expand.py.
Runs experiments, identifies high-resonance combinations,
and suggests new expander rules, missing links, and entity gaps.

Usage:
    # Full discovery run
    python scripts/discover.py

    # Discover missing links between existing entities
    python scripts/discover.py links

    # Suggest new expander rules from simulation
    python scripts/discover.py rules

    # Find entity gaps (pattern types with no representation)
    python scripts/discover.py gaps
"""

import json
import sys
import argparse
import itertools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_DIR = ROOT / "ontology"
INDEX_FILE = ROOT / "ontology_index.json"
SYNERGIES_FILE = ONTOLOGY_DIR / "relational" / "synergies.json"
RULES_FILE = ROOT / "rules" / "expander_rules.json"

sys.path.insert(0, str(ROOT))
from scripts.sovereign import load_elements, SovereignSimulation, transition_frequency, Environment


# ── Load existing state ────────────────────────────────────────────────────

def load_existing_edges():
    """Load existing edges as a set of (source, target) pairs."""
    if not SYNERGIES_FILE.exists():
        return set()
    with open(SYNERGIES_FILE) as f:
        graph = json.load(f)
    edges = set()
    for e in graph.get("edges", []):
        edges.add((e["source"], e["target"]))
        edges.add((e["target"], e["source"]))
    return edges


def load_existing_rules():
    """Load existing expander rules."""
    if not RULES_FILE.exists():
        return []
    with open(RULES_FILE) as f:
        return json.load(f)


def load_all_entities():
    """Load all entities as dicts keyed by ID."""
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


# ── Discovery: Missing Links ──────────────────────────────────────────────

def discover_missing_links(top_n=20):
    """
    Find entity pairs with high transition frequency but no graph edge.
    These are implicit relationships the ontology hasn't formalized yet.
    """
    elements = load_elements()
    existing_edges = load_existing_edges()
    env = Environment()
    env.update(0)  # low entropy for best coupling visibility

    candidates = []
    for a, b in itertools.combinations(elements, 2):
        pair = (a.entity_id, b.entity_id)
        if pair in existing_edges or (pair[1], pair[0]) in existing_edges:
            continue
        freq = transition_frequency(a, b, env)
        if freq > 0.1:  # meaningful threshold
            candidates.append({
                "source": a.entity_id,
                "target": b.entity_id,
                "frequency": round(freq, 4),
                "source_type": a.energy_type,
                "target_type": b.energy_type,
            })

    candidates.sort(key=lambda x: x["frequency"], reverse=True)
    return candidates[:top_n]


# ── Discovery: New Expander Rules ─────────────────────────────────────────

def discover_rules(top_n=10, combo_size=3, sample_steps=50):
    """
    Run sovereign simulation, find high-resonance packs,
    and suggest new expander rules for combinations that
    don't already have one.
    """
    elements = load_elements()
    existing_rules = load_existing_rules()
    existing_conditions = {frozenset(r["if"]) for r in existing_rules}

    # Sample element combinations and score them
    env = Environment()
    scored = []

    # Test combinations of size combo_size
    element_ids = [e.entity_id for e in elements]
    elem_map = {e.entity_id: e for e in elements}

    # Sample random combinations (full enumeration too expensive for 78 entities)
    rng = np.random.default_rng(42)
    tested = set()
    for _ in range(2000):
        combo_ids = tuple(sorted(rng.choice(element_ids, size=combo_size, replace=False)))
        if combo_ids in tested:
            continue
        tested.add(combo_ids)

        # Skip if already a rule
        if frozenset(combo_ids) in existing_conditions:
            continue

        # Compute resonance at low entropy
        env.update(0)
        total_freq = 0
        for i, a_id in enumerate(combo_ids):
            for j, b_id in enumerate(combo_ids):
                if i < j:
                    total_freq += transition_frequency(elem_map[a_id], elem_map[b_id], env)

        scored.append({
            "combination": list(combo_ids),
            "resonance": round(total_freq, 4),
        })

    scored.sort(key=lambda x: x["resonance"], reverse=True)

    # Generate rule names from entity types
    entities = load_all_entities()
    suggestions = []
    for s in scored[:top_n]:
        combo = s["combination"]
        types = [entities.get(eid, {}).get("ontology", "?") for eid in combo]
        names = [entities.get(eid, {}).get("name", eid) for eid in combo]

        # Generate a rule name from the combination
        rule_name = "_".join(
            n.upper().replace(" ", "_")[:6] for n in names
        ) + "_RESONANCE"

        suggestions.append({
            "if": combo,
            "then": rule_name,
            "resonance": s["resonance"],
            "types": types,
            "names": names,
        })

    return suggestions


# ── Discovery: Entity Gaps ────────────────────────────────────────────────

def discover_gaps():
    """
    Find underrepresented pattern types, missing cross-domain links,
    and ontology types with few entities.
    """
    entities = load_all_entities()
    existing_edges = load_existing_edges()

    # Count entities per type
    type_counts = Counter()
    pattern_types = Counter()
    link_types = Counter()

    for eid, entity in entities.items():
        ont = entity.get("ontology", "unknown")
        type_counts[ont] += 1

        for p in entity.get("patterns", []):
            pattern_types[p.get("type", "unknown")] += 1

        for link in entity.get("links", []):
            link_types[link.get("relation", "unknown")] += 1

    # Cross-domain link density
    cross_domain = defaultdict(int)
    total_cross = 0
    for (src, tgt) in existing_edges:
        src_type = entities.get(src, {}).get("ontology", "?")
        tgt_type = entities.get(tgt, {}).get("ontology", "?")
        if src_type != tgt_type:
            key = tuple(sorted([src_type, tgt_type]))
            cross_domain[key] += 1
            total_cross += 1

    # Find sparse cross-domain connections
    all_types = sorted(type_counts.keys())
    sparse_pairs = []
    for t1, t2 in itertools.combinations(all_types, 2):
        key = tuple(sorted([t1, t2]))
        count = cross_domain.get(key, 0)
        if count < 5:
            sparse_pairs.append((t1, t2, count))
    sparse_pairs.sort(key=lambda x: x[2])

    return {
        "type_counts": dict(type_counts),
        "pattern_types": dict(pattern_types.most_common(20)),
        "link_types": dict(link_types),
        "sparse_cross_domain": sparse_pairs,
        "total_entities": len(entities),
        "total_edges": len(existing_edges) // 2,
    }


# ── CLI ────────────────────────────────────────────────────────────────────

def cmd_links(args):
    """Discover missing links."""
    candidates = discover_missing_links(top_n=args.top)
    print(f"\n  {'='*65}")
    print(f"  MISSING LINK DISCOVERY")
    print(f"  {'='*65}")
    print(f"\n  High-frequency pairs with no graph edge:\n")
    for c in candidates:
        print(f"    {c['source']:>15} <-> {c['target']:<15}  freq={c['frequency']:.4f}  ({c['source_type']}<->{c['target_type']})")
    print(f"\n  These pairs have strong transition frequencies but aren't")
    print(f"  connected in the synergies graph. Consider adding edges.")


def cmd_rules(args):
    """Discover new expander rules."""
    suggestions = discover_rules(top_n=args.top)
    print(f"\n  {'='*65}")
    print(f"  NEW RULE SUGGESTIONS")
    print(f"  {'='*65}")
    print(f"\n  High-resonance combos not yet captured by expander rules:\n")
    for s in suggestions:
        names = " + ".join(s["names"])
        types = ", ".join(s["types"])
        print(f"    {names}")
        print(f"      [{' + '.join(s['if'])}] -> {s['then']}")
        print(f"      resonance={s['resonance']:.4f}  types=[{types}]")
        print()


def cmd_gaps(args):
    """Discover entity gaps."""
    gaps = discover_gaps()
    print(f"\n  {'='*65}")
    print(f"  ONTOLOGY GAP ANALYSIS")
    print(f"  {'='*65}")

    print(f"\n  Entities per type ({gaps['total_entities']} total):")
    for t, c in sorted(gaps["type_counts"].items(), key=lambda x: -x[1]):
        bar = "#" * c
        print(f"    {t:>10}: {c:>3} {bar}")

    print(f"\n  Top pattern types represented:")
    for t, c in list(gaps["pattern_types"].items())[:10]:
        print(f"    {t:>30}: {c}")

    print(f"\n  Sparse cross-domain connections (< 5 edges):")
    for t1, t2, count in gaps["sparse_cross_domain"]:
        print(f"    {t1} <-> {t2}: {count} edges")

    print(f"\n  Total edges: {gaps['total_edges']}")


def cmd_all(args):
    """Run full discovery."""
    print("\n" + "=" * 70)
    print("LIVING INTELLIGENCE — DISCOVERY ENGINE")
    print("=" * 70)

    # Links
    candidates = discover_missing_links(top_n=10)
    print(f"\n  Top 10 Missing Links (high freq, no edge):")
    for c in candidates:
        print(f"    {c['source']:>15} <-> {c['target']:<15}  freq={c['frequency']:.4f}")

    # Rules
    suggestions = discover_rules(top_n=5)
    print(f"\n  Top 5 Rule Suggestions:")
    for s in suggestions:
        print(f"    {' + '.join(s['if'])} -> {s['then']}  (resonance={s['resonance']:.4f})")

    # Gaps
    gaps = discover_gaps()
    print(f"\n  Sparse Cross-Domain Connections:")
    for t1, t2, count in gaps["sparse_cross_domain"][:5]:
        print(f"    {t1} <-> {t2}: only {count} edges")

    print(f"\n  Summary: {gaps['total_entities']} entities, {gaps['total_edges']} edges")
    print()


def main():
    parser = argparse.ArgumentParser(description="Discovery Engine")
    sub = parser.add_subparsers(dest="command")

    p_links = sub.add_parser("links", help="Discover missing links")
    p_links.add_argument("--top", type=int, default=20, help="Top N results")

    p_rules = sub.add_parser("rules", help="Suggest new expander rules")
    p_rules.add_argument("--top", type=int, default=10, help="Top N suggestions")

    p_gaps = sub.add_parser("gaps", help="Find entity and link gaps")

    sub.add_parser("all", help="Run full discovery")

    args = parser.parse_args()

    commands = {
        "links": cmd_links, "rules": cmd_rules,
        "gaps": cmd_gaps, "all": cmd_all,
    }

    if args.command in commands:
        commands[args.command](args)
    elif args.command is None:
        cmd_all(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
