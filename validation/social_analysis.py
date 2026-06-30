#!/usr/bin/env python3
"""
social_analysis.py — Compare social intelligences across species.

Social systems (ant colonies, wolf packs, whale pods, human councils)
demonstrate coordinated intelligence that no individual member holds alone.
This module extracts and compares social strategies, resilience patterns,
and emergent properties from the living database.

Usage:
  python3 social_analysis.py
  python3 social_analysis.py --entity ANT
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from verify import load_ontology
from scope_checker import is_scoped, extract_value, extract_confidence

# ------------------------------------------------------------------
# 1. Extract social profile from an entity
# ------------------------------------------------------------------
def extract_social_profile(entity: dict) -> Dict[str, Any]:
    """Pull coordination, resilience, and communication attributes from an entity."""
    attrs = entity.get("attributes", {})
    profile = {
        "id": entity.get("id", ""),
        "name": entity.get("name", ""),
        "emoji": entity.get("emoji", ""),
        "ontology": entity.get("ontology", ""),
        "social_attributes": {},
        "coordination_score": None,
        "resilience_score": None,
        "communication_modes": [],
        "links": entity.get("links", [])
    }

    social_keywords = [
        "coordination", "resilience", "communication", "swarm", "pack",
        "colony", "pod", "council", "collective", "cooperation", "synchrony",
        "cohesion", "hunt", "song", "signal", "pheromone", "quorum"
    ]

    for attr_name, attr_val in attrs.items():
        if any(kw in attr_name.lower() for kw in social_keywords):
            if is_scoped(attr_val):
                profile["social_attributes"][attr_name] = {
                    "value": extract_value(attr_val),
                    "confidence": extract_confidence(attr_val),
                    "definition": attr_val.get("scope", {}).get("definition", "")[:120]
                }
            else:
                profile["social_attributes"][attr_name] = str(attr_val)[:80]

    # Guess coordination and resilience from named attributes
    for attr_name, attr_data in profile["social_attributes"].items():
        val = None
        if isinstance(attr_data, dict):
            raw = attr_data.get("value")
            if isinstance(raw, (int, float)):
                val = float(raw)

        if val is not None:
            if any(w in attr_name.lower() for w in ["coord", "hunt", "forag", "song"]):
                profile["coordination_score"] = val
            if any(w in attr_name.lower() for w in ["resilien", "cohes", "stabili"]):
                profile["resilience_score"] = val

    # Communication modes from links
    for link in profile["links"]:
        rel = link.get("rel", link.get("relation", ""))
        if any(w in rel.lower() for w in ["signal", "sound", "chemical", "pheromone", "song"]):
            profile["communication_modes"].append(rel)

    return profile


# ------------------------------------------------------------------
# 2. Compare social profiles
# ------------------------------------------------------------------
def compare_social_profiles(profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Rank social entities by coordination_score and resilience_score.
    Identify shared strategies across species.
    """
    ranked_coordination = sorted(
        [p for p in profiles if p["coordination_score"] is not None],
        key=lambda x: x["coordination_score"],
        reverse=True
    )
    ranked_resilience = sorted(
        [p for p in profiles if p["resilience_score"] is not None],
        key=lambda x: x["resilience_score"],
        reverse=True
    )

    all_attr_names = set()
    for p in profiles:
        all_attr_names.update(p["social_attributes"].keys())

    shared_strategies = []
    for attr in all_attr_names:
        entities_with_attr = [p["name"] for p in profiles if attr in p["social_attributes"]]
        if len(entities_with_attr) >= 2:
            shared_strategies.append({
                "strategy": attr,
                "observed_in": entities_with_attr
            })

    return {
        "total_social_entities": len(profiles),
        "by_coordination": [
            {"name": p["name"], "emoji": p["emoji"], "score": p["coordination_score"]}
            for p in ranked_coordination
        ],
        "by_resilience": [
            {"name": p["name"], "emoji": p["emoji"], "score": p["resilience_score"]}
            for p in ranked_resilience
        ],
        "shared_strategies": shared_strategies[:10],
        "note": (
            "Social intelligence is not the sum of individual intelligence. "
            "It emerges from coordination protocols that no single member holds. "
            "These patterns are the teachers."
        )
    }


# ------------------------------------------------------------------
# 3. Main analysis function
# ------------------------------------------------------------------
def analyze_social_entities(
    ontology: Optional[dict] = None,
    ontology_path: Optional[str] = None,
    entity_ids: Optional[List[str]] = None
) -> dict:
    """
    Load all social entities from the ontology and produce a comparative analysis.
    Optionally filter to a specific list of entity_ids.
    """
    if ontology is None:
        ontology = load_ontology(ontology_path)

    social_ontology_types = {"social", "animal", "relational"}
    social_keywords = [
        "colony", "pack", "pod", "swarm", "council", "hive",
        "collective", "community", "tribe", "flock"
    ]

    entities = []
    for e in ontology.get("entities", []):
        if entity_ids and e["id"] not in entity_ids:
            continue

        is_social_type = e.get("ontology", "").lower() in social_ontology_types
        name_lower = e.get("name", "").lower()
        desc_lower = e.get("description", "").lower()
        is_social_concept = any(kw in name_lower or kw in desc_lower for kw in social_keywords)

        if is_social_type or is_social_concept:
            entities.append(e)

    if not entities:
        return {
            "status": "no_social_entities",
            "message": "No social entities found. Add ant_colony.json, wolf_pack.json, or humpback_whale_pod.json to ontology/social/."
        }

    profiles = [extract_social_profile(e) for e in entities]
    comparison = compare_social_profiles(profiles)

    return {
        "social_entities_found": len(profiles),
        "profiles": profiles,
        "comparison": comparison
    }


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compare social intelligences across species.")
    parser.add_argument("--entity", type=str, default=None, help="Filter to a single entity ID")
    parser.add_argument("--ontology", type=str, default=None)
    args = parser.parse_args()

    ids = [args.entity] if args.entity else None
    result = analyze_social_entities(ontology_path=args.ontology, entity_ids=ids)
    print(json.dumps(result, indent=2, default=str))
