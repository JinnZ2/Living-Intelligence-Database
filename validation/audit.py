#!/usr/bin/env python3
"""
audit.py — Scan the database for unscoped attributes, contradictions,
broken dependencies, and evidence that is a noun pretending to be a verb.

Usage:
  python3 audit.py [ontology_index.json]
  python3 audit.py [ontology_index.json] --legacy     behaviour before the 2026-11-24 repair

Repair 2026-11-24 (fixture F5 in validation/fixtures/DECLARED.json):
  an entity whose file cannot be loaded is reported under "load_failures" with state LOAD_FAILED
  and is left out of the scan (entities_loaded counts what was scanned). Before, the thin index
  entry was scanned in its place: it has no attributes, so it could only look clean.
  scoped_ratio is null when there is no numeric attribute to count (before: 1.0).
  The behaviour before the repair is kept behind legacy=True / --legacy, for comparison.
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

def _load_full_entities(ontology: dict, repo_root: Path) -> list:
    """Replace thin index entries with full entity files that carry attributes."""
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

def _load_entities_reported(ontology: dict, repo_root: Path):
    """Return (entities, load_failures). A failed entry is not replaced by its thin index entry."""
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

def audit(ontology: dict, repo_root: Path = None, legacy: bool = False) -> dict:
    if repo_root is None:
        repo_root = Path(__file__).parent.parent
    if legacy:
        entities, failures = _load_full_entities(ontology, repo_root), None
    else:
        entities, failures = _load_entities_reported(ontology, repo_root)
    report = {
        "mode": "legacy" if legacy else "repaired",
        "total_entities": len(ontology.get("entities", [])) if not legacy else len(entities),
        "entities_loaded": len(entities),
        "load_failures": failures,
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
                evidence = attr_val["scope"].get("evidence", {})
                conf = evidence.get("relational_confidence",
                       attr_val["scope"].get("relational_confidence", 0.5))
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
    if total_numeric:
        report["scoped_ratio"] = round(1 - unscoped_count / total_numeric, 2)
    else:
        report["scoped_ratio"] = 1.0 if legacy else None
        if not legacy:
            report["scoped_ratio_reason"] = "no numeric attribute was scanned: no ratio"

    return report

if __name__ == "__main__":
    repo_root = Path(__file__).parent.parent
    args = [a for a in sys.argv[1:] if a != "--legacy"]
    if args:
        path = args[0]
    else:
        path = repo_root / "ontology_index.json"
    ontology = load_ontology(path)
    report = audit(ontology, repo_root=repo_root, legacy="--legacy" in sys.argv[1:])
    print(json.dumps(report, indent=2))
