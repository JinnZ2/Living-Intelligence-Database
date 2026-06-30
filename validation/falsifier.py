#!/usr/bin/env python3
"""
falsifier.py — Active falsification engine.

Given a claim (or an entity's scoped attribute), this module tries to break it.
It searches the dependency tree for counterexamples, checks boundary conditions,
and returns a falsification report.

Usage:
  python3 falsifier.py --entity "BE" --attribute "efficiency_factor"
  python3 falsifier.py --entity "COUNCIL"
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

from verify import load_ontology
from scope_checker import is_scoped, extract_value, extract_confidence
from dependency_tree import build_dependency_graph, ROSETTA_STONE

# ------------------------------------------------------------------
# 1. Generate counterexamples from scope boundaries
# ------------------------------------------------------------------
def generate_counterexamples(entity: dict, attribute_name: str) -> List[Dict[str, Any]]:
    """
    Read the scope block of an attribute and propose conditions
    under which the claim would fail.
    """
    attr_val = entity.get("attributes", {}).get(attribute_name, {})
    if not is_scoped(attr_val):
        return [{"type": "unscoped", "note": "Cannot falsify an unscoped claim. Add a scope block first."}]

    scope = attr_val["scope"]
    falsifiability = scope.get("falsifiability", "")
    conditions = scope.get("condition", {})
    constraints = conditions.get("constraints", [])
    limits = scope.get("measurement_limits", "")
    dependencies = scope.get("dependencies", [])

    counterexamples = []

    for c in constraints:
        counterexamples.append({
            "type": "constraint_violation",
            "constraint": c,
            "hypothesis": f"If the constraint '{c}' is violated, the claimed value may no longer hold.",
            "test": f"Find or simulate a scenario where {c} is false."
        })

    env = conditions.get("environment", "")
    if env:
        counterexamples.append({
            "type": "environment_change",
            "environment": env,
            "hypothesis": f"If the environment '{env}' changes, the claim may fail.",
            "test": f"Search for observations outside the environment '{env}'."
        })

    for dep in dependencies:
        counterexamples.append({
            "type": "dependency_break",
            "dependency": dep,
            "hypothesis": f"If dependency '{dep}' is not present or fails, the claim may break.",
            "test": f"Check whether dependency '{dep}' exists and is verified in the database."
        })

    if falsifiability:
        counterexamples.append({
            "type": "explicit_falsifiability",
            "statement": falsifiability,
            "hypothesis": f"The claim's own falsifiability statement: {falsifiability}",
            "test": "Check the database and Rosetta Stone for evidence of this falsifying condition."
        })

    if limits:
        counterexamples.append({
            "type": "measurement_limit",
            "limit": limits,
            "hypothesis": f"The claim may be invalid beyond its measurement limits: {limits}",
            "test": f"Search for data outside the measurement limits: {limits}"
        })

    return counterexamples

# ------------------------------------------------------------------
# 2. Check counterexamples against the database
# ------------------------------------------------------------------
def check_counterexample(counterexample: dict, ontology: dict) -> Dict[str, Any]:
    """Search the ontology for any entity that might serve as a counterexample."""
    search_terms = []
    if "constraint" in counterexample:
        search_terms.append(counterexample["constraint"])
    if "environment" in counterexample:
        search_terms.append(counterexample["environment"])
    if "dependency" in counterexample:
        search_terms.append(counterexample["dependency"])

    matches = []
    for entity in ontology.get("entities", []):
        entity_text = json.dumps(entity).lower()
        for term in search_terms:
            if term.lower() in entity_text:
                for attr_name, attr_val in entity.get("attributes", {}).items():
                    if is_scoped(attr_val):
                        val = extract_value(attr_val)
                        matches.append({
                            "entity": entity["id"],
                            "attribute": attr_name,
                            "value": val,
                            "note": f"Found entity {entity['id']} that may relate to '{term}'."
                        })
    return {
        "counterexample": counterexample,
        "matches_in_db": matches[:3],
        "falsification_risk": "high" if matches else "low"
    }

# ------------------------------------------------------------------
# 3. Main falsification function
# ------------------------------------------------------------------
def falsify(entity_id: str,
            attribute_name: str = None,
            ontology: Optional[dict] = None,
            ontology_path: Optional[str] = None) -> dict:
    """Try to falsify a claim stored in an entity's scoped attribute."""
    if ontology is None:
        ontology = load_ontology(ontology_path)

    entity = None
    for e in ontology.get("entities", []):
        if e["id"] == entity_id:
            entity = e
            break

    if entity is None:
        return {"error": f"Entity {entity_id} not found."}

    if attribute_name is None:
        for attr_name, attr_val in entity.get("attributes", {}).items():
            if is_scoped(attr_val):
                attribute_name = attr_name
                break

    if attribute_name is None:
        return {"error": f"No scoped attributes found in entity {entity_id}."}

    counterexamples = generate_counterexamples(entity, attribute_name)
    checks = []
    survived = 0
    failed = 0

    for ce in counterexamples:
        check = check_counterexample(ce, ontology)
        checks.append(check)
        if check["falsification_risk"] == "high":
            failed += 1
        else:
            survived += 1

    total = survived + failed
    score = survived / total if total > 0 else 1.0

    return {
        "entity": entity_id,
        "attribute": attribute_name,
        "counterexamples_generated": len(counterexamples),
        "tests_survived": survived,
        "tests_failed": failed,
        "falsification_resistance": round(score, 2),
        "details": checks,
        "note": "A high falsification resistance means the claim survived many stress tests. A low score means the claim may have narrow scope or hidden brittleness."
    }

# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Actively try to falsify a claim.")
    parser.add_argument("--entity", type=str, required=True, help="Entity ID (e.g., 'BE')")
    parser.add_argument("--attribute", type=str, default=None, help="Attribute name (default: first scoped)")
    parser.add_argument("--ontology", type=str, default=None)
    args = parser.parse_args()
    result = falsify(args.entity, args.attribute, ontology_path=args.ontology)
    print(json.dumps(result, indent=2))
