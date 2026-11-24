#!/usr/bin/env python3
"""
dependency_tree.py — Recursive dependency tracer for goals and entities.

Given a goal description, an entity ID, or a claim, this tool walks the
Living Intelligence Database and the Rosetta Stone constants to build a
complete tree of everything the goal depends on.

Usage:
  python3 dependency_tree.py --goal "maintain a watershed for 7 generations"
  python3 dependency_tree.py --goal "COUNCIL"
  python3 dependency_tree.py --goal "WOLF_PACK" --legacy     behaviour before the 2026-11-24 repair

Repair 2026-11-24 (fixtures F4, F5 in validation/fixtures/DECLARED.json):
  F4  a link whose target is not an entity and not a constant is kept: the tree shows the target
      as a node of type "unresolved" and the result lists it under "unresolved" (source, target,
      relation). Before, the link was dropped without a word. A scope dependency that is not an
      entity id (most are free text) is listed under "non_entity_scope_dependencies"; it is not
      a tree node.
  F5  an entity whose file cannot be loaded is reported under "load_failures" with state
      LOAD_FAILED and is left out. Before, the thin index entry was used in its place.
  The behaviour before the repair is kept behind legacy=True / --legacy, for comparison.
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
def _load_full_entities(ontology: dict) -> list:
    """Load full entity files (with attributes/links) instead of thin index entries."""
    repo_root = Path(__file__).parent.parent
    full = []
    for e in ontology.get("entities", []):
        entity_path = e.get("path")
        if entity_path:
            try:
                with open(repo_root / entity_path, "r") as f:
                    full.append(json.load(f))
                continue
            except (OSError, json.JSONDecodeError):
                pass
        full.append(e)
    return full

def load_entities_reported(ontology: dict):
    """Load full entity files. Return (entities, load_failures); a failed entry is NOT replaced
    by its thin index entry. An index entry with no path is used as it is (nothing to load)."""
    repo_root = Path(__file__).parent.parent
    full, failures = [], []
    for e in ontology.get("entities", []):
        entity_path = e.get("path")
        if not entity_path:
            full.append(e)
            continue
        try:
            with open(repo_root / entity_path, "r") as f:
                full.append(json.load(f))
        except (OSError, json.JSONDecodeError) as exc:
            failures.append({"id": e.get("id"), "path": str(entity_path), "state": "LOAD_FAILED",
                             "reason": "%s: %s" % (type(exc).__name__, exc)})
    return full, failures

def build_dependency_graph(ontology: dict, legacy: bool = False, report: Optional[dict] = None) -> dict:
    """
    Build a graph where each entity is a node, and edges point from
    a claim's 'dependencies' to the entities they reference.
    report (a dict, optional) receives "unresolved", "non_entity_scope_dependencies", "load_failures".
    """
    graph = defaultdict(list)
    if not legacy:
        entities, failures = load_entities_reported(ontology)
        id_map = {e["id"]: e for e in entities}
        unresolved, non_entity = [], []
        for e in entities:
            for attr_name, attr_val in e.get("attributes", {}).items():
                if is_scoped(attr_val):
                    for dep in attr_val.get("scope", {}).get("dependencies", []):
                        if dep in id_map or dep in ROSETTA_STONE:
                            graph[e["id"]].append((dep, "dependency"))
                        else:
                            non_entity.append({"source": e["id"], "attribute": attr_name, "dependency": dep})
            for link in e.get("links", []):
                target = link.get("target") or link.get("to")
                rel_type = link.get("relation") or link.get("rel", "linked")
                graph[e["id"]].append((target, rel_type))
                if not (target in id_map or target in ROSETTA_STONE):
                    unresolved.append({"source": e["id"], "target": target, "relation": rel_type})
        if report is not None:
            report["unresolved"] = unresolved
            report["non_entity_scope_dependencies"] = non_entity
            report["load_failures"] = failures
        return graph
    entities = _load_full_entities(ontology)
    id_map = {e["id"]: e for e in entities}

    for e in entities:
        for attr_name, attr_val in e.get("attributes", {}).items():
            if is_scoped(attr_val):
                deps = attr_val.get("scope", {}).get("dependencies", [])
                for dep in deps:
                    if dep in id_map or dep in ROSETTA_STONE:
                        graph[e["id"]].append((dep, "dependency"))
        for link in e.get("links", []):
            target = link.get("target") or link.get("to")
            rel_type = link.get("relation") or link.get("rel", "linked")
            if target in id_map or target in ROSETTA_STONE:
                graph[e["id"]].append((target, rel_type))

    return graph

# ------------------------------------------------------------------
# 3. Recursive tree builder
# ------------------------------------------------------------------
def trace_dependencies(node_id: str,
                       graph: Dict[str, List[tuple]],
                       id_map: Dict[str, dict],
                       depth: int = 0,
                       max_depth: int = 6,
                       visited: Optional[Set[str]] = None,
                       failed_ids: Optional[Set[str]] = None) -> dict:
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

    if failed_ids is not None and node_id not in id_map:
        failed = node_id in failed_ids
        return {
            "id": node_id,
            "type": "load_failed" if failed else "unresolved",
            "warning": ("Entity file could not be loaded." if failed
                        else "Link target is not an entity and not a constant."),
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
        child_tree = trace_dependencies(dep_id, graph, id_map, depth + 1, max_depth, visited, failed_ids)
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
                    max_depth: int = 6,
                    legacy: bool = False) -> dict:
    """Build a dependency tree for a goal (text) or entity ID."""
    if ontology is None:
        ontology = load_ontology(ontology_path)

    if legacy:
        return _dependency_tree_legacy(goal_or_entity, ontology, max_depth)

    full_entities, failures = load_entities_reported(ontology)
    id_map = {e["id"]: e for e in full_entities}
    failed_ids = {f["id"] for f in failures}

    if goal_or_entity in failed_ids:
        return {
            "mode": "repaired",
            "input": goal_or_entity,
            "start_entity": None,
            "error": f"LOAD_FAILED: entity file for {goal_or_entity} could not be loaded; no tree was built.",
            "load_failures": failures
        }

    start_id = None
    if goal_or_entity in id_map:
        start_id = goal_or_entity
    else:
        for e in full_entities:
            if goal_or_entity.lower() in e.get("name", "").lower() or \
               goal_or_entity.lower() in e.get("attributes", {}).get("pattern", "").lower():
                start_id = e["id"]
                break

    report = {}
    graph = build_dependency_graph(ontology, report=report)

    if not start_id:
        return {
            "mode": "repaired",
            "input": goal_or_entity,
            "start_entity": None,
            "error": "No matching entity found. Try an entity ID (e.g., 'COUNCIL') or a keyword present in the database.",
            "available_entities": list(id_map.keys())[:20],
            "load_failures": failures
        }

    tree = trace_dependencies(start_id, graph, id_map, max_depth=max_depth, failed_ids=failed_ids)
    in_tree = set()

    def walk(n):
        in_tree.add(n["id"])
        for c in n.get("dependencies", []):
            walk(c)
    walk(tree)
    return {
        "mode": "repaired",
        "input": goal_or_entity,
        "start_entity": start_id,
        "tree": tree,
        "unresolved": [u for u in report["unresolved"] if u["source"] in in_tree],
        "unresolved_in_whole_ontology": len(report["unresolved"]),
        "non_entity_scope_dependencies": [d for d in report["non_entity_scope_dependencies"]
                                          if d["source"] in in_tree],
        "load_failures": failures,
        "note": "Each node shows what it depends on. Leaf nodes are constants, unresolved link targets, or entities that failed to load. Unresolved links are listed, not dropped."
    }


def _dependency_tree_legacy(goal_or_entity: str, ontology: dict, max_depth: int = 6) -> dict:
    """The behaviour before the 2026-11-24 repair: thin fallback on load failure, unresolved links dropped."""
    full_entities = _load_full_entities(ontology)
    id_map = {e["id"]: e for e in full_entities}

    start_id = None
    if goal_or_entity in id_map:
        start_id = goal_or_entity
    else:
        for e in full_entities:
            if goal_or_entity.lower() in e.get("name", "").lower() or \
               goal_or_entity.lower() in e.get("attributes", {}).get("pattern", "").lower():
                start_id = e["id"]
                break

    graph = build_dependency_graph(ontology, legacy=True)

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
    parser.add_argument("--legacy", action="store_true",
                        help="behaviour before the 2026-11-24 repair (unresolved links dropped; thin fallback on load failure)")
    args = parser.parse_args()
    result = dependency_tree(args.goal, max_depth=args.max_depth, ontology_path=args.ontology, legacy=args.legacy)
    print(json.dumps(result, indent=2))
