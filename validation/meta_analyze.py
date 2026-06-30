#!/usr/bin/env python3
"""
meta_analyze.py — Analyze a claim across multiple engineering paradigms.
Now uses paradigm_verifier for clean per-paradigm verification.

Usage:
  python3 meta_analyze.py --goal "long-term ecological resilience"
"""

import json
import sys
from pathlib import Path
from paradigm_verifier import verify_with_paradigm
from verify import load_ontology
from engineering_paradigms import PARADIGMS, paradigms_for_context

def analyze_claim(claim_func, ontology=None, ontology_path=None, prior=0.5, goal_description: str = ""):
    if ontology is None:
        ontology = load_ontology(ontology_path)

    relevant_paradigms = paradigms_for_context(
        time_horizon="long" if "long" in goal_description else "",
        scope="wide" if "wide" in goal_description or "resilience" in goal_description else "",
        substrate=""
    )
    if not relevant_paradigms:
        relevant_paradigms = ["western_empirical", "relational_cyclical"]

    results = {}
    for pid in relevant_paradigms:
        ver_result = verify_with_paradigm(
            claim_func,
            paradigm_id=pid,
            ontology=ontology,
            prior=prior,
            domain_hint=""
        )
        paradigm_name = ver_result.get("paradigm_name", pid)
        results[pid] = {
            "paradigm_name": paradigm_name,
            "posterior_probability": ver_result.get("posterior_probability", 0.5),
            "note": ver_result.get("note", "")
        }

    posteriors = [r["posterior_probability"] for r in results.values()]
    best_pid = max(results, key=lambda p: results[p]["posterior_probability"])
    if max(posteriors) - min(posteriors) < 0.1:
        recommendation = "Robust across all consulted paradigms."
    else:
        recommendation = f"Best supported by {results[best_pid]['paradigm_name']} (posterior {results[best_pid]['posterior_probability']}). Consider scope."

    return {
        "goal": goal_description,
        "paradigms_consulted": list(results.keys()),
        "results": results,
        "recommendation": recommendation,
        "meta_note": "Engineering is broader than Western machines. Soil, ceremonies, morals, and beauty are engineered systems. Choose the lens that fits the time horizon and scope of your question."
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Meta-analyze a claim across engineering paradigms.")
    parser.add_argument("--goal", type=str, default="", help="Description of the goal/context")
    parser.add_argument("--prior", type=float, default=0.5)
    parser.add_argument("--ontology", type=str, default=None)
    args = parser.parse_args()

    def always_true():
        return True

    result = analyze_claim(always_true, goal_description=args.goal, prior=args.prior, ontology_path=args.ontology)
    print(json.dumps(result, indent=2))
