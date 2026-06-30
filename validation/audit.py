#!/usr/bin/env python3
"""
audit.py — Scan the database for unscoped attributes, contradictions,
broken dependencies, and evidence that is a noun pretending to be a verb.

Usage:
  python3 audit.py [ontology_index.json]
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from scope_checker import (
    is_scoped, extract_value, extract_confidence,
    list_unscoped_attributes, list_noun_pretenders
)

def load_ontology(path):
    with open(path, "r") as f:
        return json.load(f)

def audit(ontology: dict) -> dict:
    entities = ontology.get("entities", [])
    report = {
        "total_entities": len(entities),
        "unscoped_numerics": [],
        "noun_pretenders": [],
        "confidence_distribution": defaultdict(int),
        "possible_contradictions": [],
        "dependency_checks": [],
        "scoped_ratio": 0.0
    }

    id_map = {e["id"]: e for e in entities}

    for e in entities:
        # Unscoped numerics
        for attr_name, attr_val in e.get("attributes", {}).items():
            if isinstance(attr_val, (int, float)):
                report["unscoped_numerics"].append({
                    "entity": e["id"],
                    "attribute": attr_name,
                    "value": attr_val,
                    "note": "No scope. Treat as hypothesis, not ground truth."
                })
            elif isinstance(attr_val, dict) and "value" in attr_val and "scope" not in attr_val:
                report["unscoped_numerics"].append({
                    "entity": e["id"],
                    "attribute": attr_name,
                    "value": attr_val["value"],
                    "note": "Has value but no scope block."
                })
            elif is_scoped(attr_val):
                conf = attr_val["scope"]["evidence"]["confidence"]
                report["confidence_distribution"][round(conf, 2)] += 1

        # Noun pretenders
        nouns = list_noun_pretenders(e)
        if nouns:
            report["noun_pretenders"].append({
                "entity": e["id"],
                "attributes": nouns,
                "note": "These attributes claim confidence but lack cyclic or cross-domain evidence. They may be static nouns rather than recurring verbs."
            })

    # Contradictions
    attr_groups = defaultdict(list)
    for e in entities:
        for attr_name, attr_val in e.get("attributes", {}).items():
            val = extract_value(attr_val)
            if val is not None:
                attr_groups[attr_name].append((e["id"], val))
    for attr, vals in attr_groups.items():
        if len(vals) > 1:
            values = [v for _, v in vals]
            if len(set(values)) > 1:
                report["possible_contradictions"].append({
                    "attribute": attr,
                    "values": {eid: v for eid, v in vals},
                    "note": "Same attribute, different values. Check if scopes differ."
                })

    # Dependency breaks
    for e in entities:
        for attr_name, attr_val in e.get("attributes", {}).items():
            if is_scoped(attr_val):
                deps = attr_val["scope"].get("dependencies", [])
                for dep in deps:
                    if dep not in id_map:
                        report["dependency_checks"].append({
                            "entity": e["id"],
                            "attribute": attr_name,
                            "missing_dependency": dep
                        })

    # Scoped ratio
    total_numeric = sum(1 for e in entities
                        for a in e.get("attributes",{}).values()
                        if isinstance(a,(int,float)) or (isinstance(a,dict) and "value" in a))
    unscoped_count = len(report["unscoped_numerics"])
    report["scoped_ratio"] = round(1 - unscoped_count / total_numeric, 2) if total_numeric else 1.0

    return report

if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = Path(__file__).parent.parent / "ontology_index.json"
    ontology = load_ontology(path)
    report = audit(ontology)
    print(json.dumps(report, indent=2))
