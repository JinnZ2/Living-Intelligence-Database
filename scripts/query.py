#!/usr/bin/env python3
"""
query.py — Living Intelligence Database Query Interface

A command-line tool for exploring the ontology graph. Designed for both
human use and AI agent tool-calling.

Usage:
  python scripts/query.py entity <id>         Show full entity details + neighbors
  python scripts/query.py search <term>       Search entities by name/description
  python scripts/query.py neighbors <id>      List all directly connected entities
  python scripts/query.py path <id1> <id2>    Find shortest path between two entities
  python scripts/query.py type <type>         List all entities of a given type
  python scripts/query.py rules <id>          Show expander rules involving an entity
  python scripts/query.py stats               Show database statistics
  python scripts/query.py expand <id> <id>... Check if a combination triggers any rule
"""

import json, sys
from pathlib import Path
from collections import defaultdict, deque

ROOT = Path(__file__).resolve().parents[1]
INDEX_FILE = ROOT / "ontology_index.json"
RULES_FILE = ROOT / "rules" / "expander_rules.json"
MANIFEST_FILE = ROOT / "manifest.json"


def load_index():
    with open(INDEX_FILE) as f:
        return json.load(f)


def load_rules():
    with open(RULES_FILE) as f:
        return json.load(f)


def load_entity_file(path):
    with open(ROOT / path) as f:
        return json.load(f)


def load_manifest():
    with open(MANIFEST_FILE) as f:
        return json.load(f)


def build_graph(index):
    """Build adjacency list from relations."""
    graph = defaultdict(set)
    for rel in index.get("relations", []):
        graph[rel["source"]].add(rel["target"])
        graph[rel["target"]].add(rel["source"])
    return graph


def id_to_name(index):
    return {e["id"]: e["name"] for e in index["entities"]}


# ─── Commands ────────────────────────────────────────────────────


def cmd_entity(args):
    """Show full entity details + neighbors."""
    if not args:
        print("Usage: query.py entity <id>")
        return
    target_id = args[0].upper()
    index = load_index()
    names = id_to_name(index)

    # Find entity in index
    entity_meta = None
    for e in index["entities"]:
        if e["id"] == target_id:
            entity_meta = e
            break

    if not entity_meta:
        print(f"Entity '{target_id}' not found.")
        suggest_similar(target_id, names)
        return

    # Load full entity file
    full = load_entity_file(entity_meta["path"])

    print(f"\n{'=' * 60}")
    print(f"  {full.get('emoji', '')} {full['name']} [{full['id']}]")
    print(f"  Type: {full['ontology']}")
    if "symbolic_code" in full:
        print(f"  Code: {full['symbolic_code']}")
    print(f"{'=' * 60}")

    if "description" in full:
        print(f"\n  {full['description']}")

    if "core_attributes" in full:
        print(f"\n  Core Attributes:")
        for k, v in full["core_attributes"].items():
            print(f"    {k}: {v}")

    if "patterns" in full:
        print(f"\n  Patterns:")
        for p in full["patterns"]:
            eff = p.get("efficiency_factor", "?")
            print(f"    - {p['name']} ({p['type']}, efficiency: {eff})")
            if "applications" in p:
                print(f"      applications: {', '.join(p['applications'])}")

    # Show connections
    outgoing = [r for r in index["relations"] if r["source"] == target_id]
    incoming = [r for r in index["relations"] if r["target"] == target_id]

    if outgoing or incoming:
        print(f"\n  Connections ({len(outgoing)} outgoing, {len(incoming)} incoming):")
        for r in outgoing:
            name = names.get(r["target"], r["target"])
            print(f"    -> {name} [{r['target']}] ({r['relation']})")
        for r in incoming:
            name = names.get(r["source"], r["source"])
            print(f"    <- {name} [{r['source']}] ({r['relation']})")

    # Show applicable rules
    rules = load_rules()
    applicable = [r for r in rules if target_id in r["if"]]
    if applicable:
        print(f"\n  Expander Rules ({len(applicable)}):")
        for r in applicable:
            inputs = " + ".join(r["if"])
            print(f"    [{inputs}] -> {r['then']}")

    print()


def cmd_search(args):
    """Search entities by name or description."""
    if not args:
        print("Usage: query.py search <term>")
        return
    term = " ".join(args).lower()
    index = load_index()

    results = []
    for e in index["entities"]:
        score = 0
        if term in e["name"].lower():
            score += 10
        if term in e.get("description", "").lower():
            score += 5
        if term in e["id"].lower():
            score += 3
        if term in e["ontology"].lower():
            score += 1
        if score > 0:
            results.append((score, e))

    results.sort(key=lambda x: -x[0])

    if not results:
        print(f"No results for '{term}'.")
        return

    print(f"\n  Search: '{term}' ({len(results)} results)\n")
    for score, e in results[:20]:
        desc = e.get("description", "")[:80]
        print(f"  [{e['id']:15s}] {e['name']:30s} ({e['ontology']})")
        if desc:
            print(f"  {'':17s} {desc}...")
    print()


def cmd_neighbors(args):
    """List all directly connected entities."""
    if not args:
        print("Usage: query.py neighbors <id>")
        return
    target_id = args[0].upper()
    index = load_index()
    names = id_to_name(index)

    outgoing = [r for r in index["relations"] if r["source"] == target_id]
    incoming = [r for r in index["relations"] if r["target"] == target_id]

    if not outgoing and not incoming:
        print(f"No connections found for '{target_id}'.")
        suggest_similar(target_id, names)
        return

    print(f"\n  Neighbors of {names.get(target_id, target_id)} [{target_id}]\n")

    by_relation = defaultdict(list)
    for r in outgoing:
        by_relation[r["relation"]].append(("->", r["target"]))
    for r in incoming:
        by_relation[r["relation"]].append(("<-", r["source"]))

    for rel, connections in sorted(by_relation.items()):
        print(f"  {rel}:")
        for direction, eid in connections:
            name = names.get(eid, eid)
            print(f"    {direction} {name} [{eid}]")
    print()


def cmd_path(args):
    """Find shortest path between two entities."""
    if len(args) < 2:
        print("Usage: query.py path <id1> <id2>")
        return
    start, end = args[0].upper(), args[1].upper()
    index = load_index()
    names = id_to_name(index)
    graph = build_graph(index)

    if start not in names:
        print(f"Entity '{start}' not found.")
        return
    if end not in names:
        print(f"Entity '{end}' not found.")
        return

    # BFS
    visited = {start}
    queue = deque([(start, [start])])
    while queue:
        node, path = queue.popleft()
        if node == end:
            print(f"\n  Path from {names[start]} to {names[end]} ({len(path) - 1} hops):\n")
            for i, eid in enumerate(path):
                prefix = "  " if i == 0 else "  -> "
                print(f"  {prefix}{names.get(eid, eid)} [{eid}]")
            print()
            return
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    print(f"  No path found between {names[start]} and {names[end]}.")
    print()


def cmd_type(args):
    """List all entities of a given type."""
    if not args:
        print("Usage: query.py type <type>")
        index = load_index()
        types = defaultdict(int)
        for e in index["entities"]:
            types[e["ontology"]] += 1
        print("\n  Available types:")
        for t, c in sorted(types.items()):
            print(f"    {t:12s} ({c} entities)")
        print()
        return

    target_type = args[0].lower()
    index = load_index()

    entities = [e for e in index["entities"] if e["ontology"] == target_type]
    if not entities:
        print(f"No entities found for type '{target_type}'.")
        return

    print(f"\n  {target_type.upper()} ({len(entities)} entities)\n")
    for e in sorted(entities, key=lambda x: x["name"]):
        desc = e.get("description", "")[:70]
        print(f"  [{e['id']:15s}] {e['name']}")
        if desc:
            print(f"  {'':17s} {desc}...")
    print()


def cmd_rules(args):
    """Show expander rules involving an entity."""
    if not args:
        print("Usage: query.py rules <id>")
        return
    target_id = args[0].upper()
    rules = load_rules()
    index = load_index()
    names = id_to_name(index)

    # Rules where entity is an input
    as_input = [r for r in rules if target_id in r["if"]]
    # Rules where entity is the output
    as_output = [r for r in rules if r["then"] == target_id]

    if not as_input and not as_output:
        print(f"No rules found for '{target_id}'.")
        return

    print(f"\n  Rules involving {names.get(target_id, target_id)} [{target_id}]\n")

    if as_input:
        print(f"  As input ({len(as_input)} rules):")
        for r in as_input:
            input_names = [names.get(i, i) for i in r["if"]]
            print(f"    {' + '.join(input_names)} -> {r['then']}")

    if as_output:
        print(f"\n  As output ({len(as_output)} rules):")
        for r in as_output:
            input_names = [names.get(i, i) for i in r["if"]]
            print(f"    {' + '.join(input_names)} -> {r['then']}")
    print()


def cmd_expand(args):
    """Check if a combination of entities triggers any rule."""
    if len(args) < 2:
        print("Usage: query.py expand <id1> <id2> [<id3> ...]")
        return
    input_ids = set(a.upper() for a in args)
    rules = load_rules()
    index = load_index()
    names = id_to_name(index)

    # Also accept 'phi' as lowercase
    input_ids_lower = set(a.lower() for a in args) | input_ids

    triggered = []
    for r in rules:
        rule_inputs = set(r["if"])
        if rule_inputs.issubset(input_ids) or rule_inputs.issubset(input_ids_lower):
            triggered.append(r)

    input_names = [names.get(i, i) for i in sorted(input_ids)]
    print(f"\n  Expanding: {' + '.join(input_names)}\n")

    if triggered:
        print(f"  Triggered {len(triggered)} rule(s):")
        for r in triggered:
            print(f"    -> {r['then']}")
    else:
        print("  No rules triggered for this combination.")
        # Suggest partial matches
        partial = []
        for r in rules:
            overlap = set(r["if"]) & input_ids
            if overlap and not set(r["if"]).issubset(input_ids):
                missing = set(r["if"]) - input_ids
                partial.append((r, missing))
        if partial:
            print(f"\n  Near matches (add one more to trigger):")
            for r, missing in partial[:5]:
                missing_names = [names.get(m, m) for m in missing]
                print(f"    + {', '.join(missing_names)} -> {r['then']}")
    print()


def cmd_stats(args):
    """Show database statistics."""
    index = load_index()
    rules = load_rules()

    entities = index["entities"]
    relations = index["relations"]

    types = defaultdict(int)
    for e in entities:
        types[e["ontology"]] += 1

    rel_types = defaultdict(int)
    for r in relations:
        rel_types[r["relation"]] += 1

    # Graph metrics
    graph = build_graph(index)
    degrees = {eid: len(neighbors) for eid, neighbors in graph.items()}
    most_connected = sorted(degrees.items(), key=lambda x: -x[1])[:10]
    names = id_to_name(index)
    isolated = [e["id"] for e in entities if e["id"] not in graph]

    print(f"\n  {'=' * 50}")
    print(f"  Living Intelligence Database Statistics")
    print(f"  {'=' * 50}")

    print(f"\n  Entities: {len(entities)}")
    for t, c in sorted(types.items()):
        print(f"    {t:12s} {c:3d}")

    print(f"\n  Relations: {len(relations)}")
    for rt, c in sorted(rel_types.items(), key=lambda x: -x[1]):
        print(f"    {rt:20s} {c:3d}")

    print(f"\n  Expander Rules: {len(rules)}")

    print(f"\n  Most Connected Entities:")
    for eid, degree in most_connected:
        print(f"    {names.get(eid, eid):30s} [{eid:15s}] {degree} connections")

    if isolated:
        print(f"\n  Isolated Entities (no connections): {len(isolated)}")
        for eid in isolated:
            print(f"    {names.get(eid, eid)} [{eid}]")

    print()


def suggest_similar(target, names):
    """Suggest similar entity IDs."""
    target_lower = target.lower()
    candidates = []
    for eid, name in names.items():
        if target_lower in eid.lower() or target_lower in name.lower():
            candidates.append(f"{name} [{eid}]")
    if candidates:
        print(f"  Did you mean: {', '.join(candidates[:5])}")


# ─── Main ────────────────────────────────────────────────────────

COMMANDS = {
    "entity": cmd_entity,
    "search": cmd_search,
    "neighbors": cmd_neighbors,
    "path": cmd_path,
    "type": cmd_type,
    "rules": cmd_rules,
    "expand": cmd_expand,
    "stats": cmd_stats,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("help", "--help", "-h"):
        print(__doc__)
        return

    cmd = sys.argv[1].lower()
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(COMMANDS.keys())}")
        return

    COMMANDS[cmd](sys.argv[2:])


if __name__ == "__main__":
    main()
