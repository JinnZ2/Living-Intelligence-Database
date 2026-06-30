#!/usr/bin/env python3
"""
goal_refiner.py — Given a goal, propose alternative strategies that widen the
temporal scope by rhyming with cross-domain patterns from the Living Intelligence
Database.

Usage:
  python3 goal_refiner.py --goal "increase quarterly revenue by 15%"
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from temporal_scope import assess_goal
from verify import load_ontology
from paradigm_selector import select_paradigm as suggest_paradigm
from scope_checker import is_scoped, extract_value, extract_confidence

# ------------------------------------------------------------------
# 1. Extract core purpose and domain keywords from goal text
# ------------------------------------------------------------------
def extract_purpose(goal: str) -> Dict[str, Any]:
    """Simple keyword extraction for domain detection."""
    keywords = {
        "revenue": "economic",
        "profit": "economic",
        "efficiency": "optimization",
        "growth": "expansion",
        "reduce": "conservation",
        "soil": "ecological",
        "water": "ecological",
        "community": "social",
        "trauma": "psychological",
        "resilience": "resilience",
        "heal": "psychological",
        "beauty": "aesthetic",
        "harmony": "aesthetic",
        "coordination": "social",
        "governance": "social",
    }
    domain = "general"
    for word, dom in keywords.items():
        if word in goal.lower():
            domain = dom
            break
    return {"goal_text": goal, "core_purpose": goal, "domain": domain}

# ------------------------------------------------------------------
# 2. Find rhyming entities from the database
# ------------------------------------------------------------------
def find_rhymes(domain: str, ontology: dict) -> List[dict]:
    """Find entities whose patterns relate to the goal's domain."""
    rhymes = []
    for ent in ontology.get("entities", []):
        pattern = ent.get("attributes", {}).get("pattern", "")
        if domain.lower() in pattern.lower() or domain.lower() in ent.get("ontology", "").lower():
            rhymes.append(ent)
    return rhymes

# ------------------------------------------------------------------
# 3. Generate alternative strategies from a rhyming entity
# ------------------------------------------------------------------
def generate_alternatives(goal: str, goal_domain: str, entity: dict) -> List[Dict[str, Any]]:
    """For a given entity, produce one or more alternative strategies."""
    alternatives = []
    pattern = entity.get("attributes", {}).get("pattern", "")
    name = entity.get("name", entity.get("id", ""))
    symbol = entity.get("emoji", "")

    inspirations = []
    for attr_name, attr_val in entity.get("attributes", {}).items():
        if is_scoped(attr_val):
            val = extract_value(attr_val)
            conf = extract_confidence(attr_val)
            inspirations.append({
                "attribute": attr_name,
                "value": val,
                "confidence": conf,
                "definition": attr_val.get("scope", {}).get("definition", "")
            })

    strategy_template = (
        f"Apply the pattern of {name} ({pattern}) to the goal of '{goal}'. "
        f"Instead of optimizing only for immediate output, design the system "
        f"so that it self-organizes like {name}. "
        f"This may involve: decentralized decision-making, feedback loops, "
        f"and long-term resource cycling."
    )

    if inspirations:
        strategy_template += f" Known efficiency: {inspirations[0]['value']} ({inspirations[0]['attribute']})."

    alternatives.append({
        "source_entity": name,
        "emoji": symbol,
        "pattern_used": pattern,
        "strategy": strategy_template,
        "inspiration_evidence": inspirations,
        "temporal_note": f"Pattern observed in {entity.get('attributes', {}).get('temporal_range', 'multiple cycles')}."
    })
    return alternatives

# ------------------------------------------------------------------
# 4. Score an alternative
# ------------------------------------------------------------------
def score_alternative(alternative: dict, goal_horizon: dict, goal_domain: str) -> float:
    """Score based on temporal coherence and cross-domain rhyme strength."""
    score = 0.5
    if goal_horizon["name"] in ["generational", "deep_time"]:
        if "cyclic_observation" in alternative.get("pattern_used", ""):
            score += 0.2
    for ev in alternative.get("inspiration_evidence", []):
        if "cross_domain_count" in str(ev):
            score += 0.1
    return min(1.0, score)

# ------------------------------------------------------------------
# 5. Main refine function
# ------------------------------------------------------------------
def refine_goal(goal: str, ontology: Optional[dict] = None, ontology_path: Optional[str] = None) -> dict:
    """
    Take a goal, assess its temporal scope, find rhymes,
    generate alternatives, score them, and return a report.
    """
    if ontology is None:
        ontology = load_ontology(ontology_path)

    temporal_assessment = assess_goal(goal)
    goal_info = extract_purpose(goal)
    domain = goal_info["domain"]
    horizon = temporal_assessment["detected_horizon"]

    rhymes = find_rhymes(domain, ontology)
    if not rhymes:
        rhymes = ontology.get("entities", [])[:10]

    all_alternatives = []
    for ent in rhymes:
        alts = generate_alternatives(goal, domain, ent)
        for alt in alts:
            alt["score"] = round(score_alternative(alt, horizon, domain), 2)
            all_alternatives.append(alt)

    all_alternatives.sort(key=lambda x: x["score"], reverse=True)
    top_alternatives = all_alternatives[:5]

    recommendation = "Consider these alternatives, each inspired by a teacher from the Living Intelligence Database. They widen the temporal scope and reduce blind spots."
    if temporal_assessment.get("mismatch_warning"):
        recommendation += " " + temporal_assessment["mismatch_warning"]

    return {
        "original_goal": goal,
        "temporal_assessment": temporal_assessment,
        "domain": domain,
        "rhyme_sources_count": len(rhymes),
        "alternatives": top_alternatives,
        "recommendation": recommendation
    }

# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Refine a goal using cross-domain rhymes.")
    parser.add_argument("--goal", type=str, required=True, help="The goal to refine")
    parser.add_argument("--ontology", type=str, default=None, help="Path to ontology_index.json")
    args = parser.parse_args()
    result = refine_goal(args.goal, ontology_path=args.ontology)
    print(json.dumps(result, indent=2))
