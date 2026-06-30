#!/usr/bin/env python3
"""
dependency_tree.py — Recursive dependency tracer for goals and entities.

Given a goal description, an entity ID, or a claim, this tool walks the
Living Intelligence Database and the Rosetta Stone constants to build a
complete tree of everything the goal depends on.

Usage:
  python3 dependency_tree.py --goal "maintain a watershed for 7 generations"
  python3 dependency_tree.py --goal "COUNCIL"
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any, List, Optional, Set

from verify import load_ontology
from scope_checker import is_scoped, extract_confidence

# ------------------------------------------------------------------
# 1. Load the Rosetta Stone constants as atomic dependencies
# ------------------------------------------------------------------
ROSETTA_STONE = {
    "speed_of_light": "Physical constant",
    "planck_constant": "Physical constant",
    "gravitational_constant": "Physical constant",
    "boltzmann_constant": "Physical constant",
    "avogadro_number": "Physical constant",
    "elementary_charge": "Physical constant",
    "electron_mass": "Physical constant",
    "proton_mass": "Physical constant",
    "golden_ratio": "Mathematical constant",
    "pi": "Mathematical constant",
    "euler_number": "Mathematical constant",
    "planck_length": "Physical constant",
    "planck_time": "Physical constant",
}

# ------------------------------------------------------------------
# 2. Build an adjacency map from the ontology
# ------------------------------------------------------------------
def build_dependency_graph(ontology: dict) -> dict:
    """
    Build a graph where each entity is a node, and edges point from
    a claim's 'dependencies' to the entities they reference.
    """
    graph = defaultdict(list)
    entities = ontology.get("entities", [])
    id_map = {e["id"]: e for e in entities}

    for e in entities:
        for attr_name, attr_val in e.get("attributes", {}).items():
            if is_scoped(attr_val):
                deps = attr_val.get("scope", {}).get("dependencies", [])
                for dep in deps:
                    if dep in id_map or dep in ROSETTA_STONE:
                        graph[e["id"]].append((dep, "dependency"))
        for link in e.get("links", []):
            target = link.get("to")
            if target in id_map or target in ROSETTA_STONE:
                graph[e["id"]].append((target, link.get("rel", "linked")))

    return graph

# ------------------------------------------------------------------
# 3. Recursive tree builder
# ------------------------------------------------------------------
def trace_dependencies(node_id: str,
                       graph: Dict[str, List[tuple]],
                       id_map: Dict[str, dict],
                       depth: int = 0,
                       max_depth: int = 6,
                       visited: Optional[Set[str]] = None) -> dict:
    """Recursively trace dependencies starting from node_id."""
    if visited is None:
        visited = set()

    if node_id in ROSETTA_STONE:
        return {
            "id": node_id,
            "type": "constant",
            "description": ROSETTA_STONE[node_id],
            "depth": depth,
            "dependencies": []
        }

    if node_id not in id_map:
        return {
            "id": node_id,
            "type": "unknown",
            "warning": "Not found in ontology or constants.",
            "depth": depth,
            "dependencies": []
        }

    if node_id in visited or depth >= max_depth:
        return {
            "id": node_id,
            "type": "truncated",
            "reason": "Cycle or max depth reached." if node_id in visited else "Max depth",
            "depth": depth,
            "dependencies": []
        }

    visited.add(node_id)
    entity = id_map[node_id]
    tree = {
        "id": node_id,
        "name": entity.get("name", node_id),
        "ontology": entity.get("ontology", "unknown"),
        "depth": depth,
        "dependencies": []
    }

    scoped_info = {}
    for attr_name, attr_val in entity.get("attributes", {}).items():
        if is_scoped(attr_val):
            conf = extract_confidence(attr_val)
            scoped_info[attr_name] = {
                "confidence": conf,
                "scope_definition": attr_val["scope"].get("definition", "")[:100]
            }
    if scoped_info:
        tree["scoped_attributes"] = scoped_info

    deps = graph.get(node_id, [])
    for dep_id, rel_type in deps:
        child_tree = trace_dependencies(dep_id, graph, id_map, depth + 1, max_depth, visited)
        child_tree["relation"] = rel_type
        tree["dependencies"].append(child_tree)

    visited.remove(node_id)
    return tree

# ------------------------------------------------------------------
# 4. Main entry point
# ------------------------------------------------------------------
def dependency_tree(goal_or_entity: str,
                    ontology: Optional[dict] = None,
                    ontology_path: Optional[str] = None,
                    max_depth: int = 6) -> dict:
    """Build a dependency tree for a goal (text) or entity ID."""
    if ontology is None:
        ontology = load_ontology(ontology_path)

    id_map = {e["id"]: e for e in ontology.get("entities", [])}

    start_id = None
    if goal_or_entity in id_map:
        start_id = goal_or_entity
    else:
        for e in ontology.get("entities", []):
            if goal_or_entity.lower() in e.get("name", "").lower() or \
               goal_or_entity.lower() in e.get("attributes", {}).get("pattern", "").lower():
                start_id = e["id"]
                break

    graph = build_dependency_graph(ontology)

    if start_id:
        tree = trace_dependencies(start_id, graph, id_map, max_depth=max_depth)
        return {
            "input": goal_or_entity,
            "start_entity": start_id,
            "tree": tree,
            "note": "Each node shows what it depends on. Leaf nodes are constants or unknown. This is the root system of the goal."
        }
    else:
        return {
            "input": goal_or_entity,
            "error": "No matching entity found. Try an entity ID (e.g., 'COUNCIL') or a keyword present in the database.",
            "available_entities": list(id_map.keys())[:20]
        }

# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Trace dependency tree for a goal or entity.")
    parser.add_argument("--goal", type=str, required=True, help="Goal description or entity ID")
    parser.add_argument("--max_depth", type=int, default=6, help="Maximum recursion depth")
    parser.add_argument("--ontology", type=str, default=None)
    args = parser.parse_args()
    result = dependency_tree(args.goal, max_depth=args.max_depth, ontology_path=args.ontology)
    print(json.dumps(result, indent=2))
