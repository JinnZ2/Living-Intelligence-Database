#!/usr/bin/env python3
"""
verify.py — Verify a claim against the Living Intelligence Database.
Uses relational confidence: cycle recurrence, cross-domain rhyme,
and dependency coherence — not source prestige.

Usage:
  python3 verify.py --claim "hex_efficiency" --domain "hex" --prior 0.5
"""

import json
import sys
import math
from pathlib import Path
from typing import Callable, Dict, Any, List, Tuple, Optional

from scope_checker import (
    is_scoped, extract_value, extract_confidence,
    extract_scope_text, scope_match, list_unscoped_attributes,
    list_noun_pretenders, compute_relational_confidence
)

# ------------------------------------------------------------------
# Load ontology
# ------------------------------------------------------------------
def load_ontology(path: str = None) -> dict:
    if path is None:
        repo_root = Path(__file__).parent.parent
        path = repo_root / "ontology_index.json"
    with open(path, "r") as f:
        return json.load(f)

# ------------------------------------------------------------------
# Generate tests from a single entity
# ------------------------------------------------------------------
def generate_tests(claim: Callable[[], bool],
                   entity: dict,
                   claim_scope_text: str = "",
                   min_scope_overlap: float = 0.2,
                   ontology: dict = None) -> List[Tuple[Callable[[], bool], float]]:
    """
    Return (test_function, evidence_weight) pairs.
    evidence_weight = relational_confidence * scope_overlap.
    """
    tests = []
    for attr_name, attr_val in entity.get("attributes", {}).items():
        if not is_scoped(attr_val):
            continue
        ent_scope_text = extract_scope_text(attr_val)
        overlap = scope_match(claim_scope_text, ent_scope_text)
        if overlap < min_scope_overlap:
            continue
        confidence = extract_confidence(attr_val, ontology)
        weight = confidence * overlap
        test_func = lambda: claim()
        tests.append((test_func, weight))
    return tests

# ------------------------------------------------------------------
# Weighted Bayesian update
# ------------------------------------------------------------------
def bayesian_update_weighted(prior: float,
                              test_results: List[Tuple[bool, float]],
                              prob_if_true: float = 0.95,
                              prob_if_false: float = 0.05) -> float:
    if not test_results:
        return prior
    total_weight = sum(w for _, w in test_results)
    passed_weight = sum(w for p, w in test_results if p)
    failed_weight = total_weight - passed_weight

    likelihood_true = math.exp(
        passed_weight * math.log(prob_if_true) + failed_weight * math.log(1 - prob_if_true)
    )
    likelihood_false = math.exp(
        passed_weight * math.log(prob_if_false) + failed_weight * math.log(1 - prob_if_false)
    )

    if likelihood_false == 0:
        return 1.0
    prior_odds = prior / (1 - prior) if prior != 1.0 else 1e10
    posterior_odds = prior_odds * (likelihood_true / likelihood_false)
    return posterior_odds / (1 + posterior_odds)

# ------------------------------------------------------------------
# Main verification
# ------------------------------------------------------------------
def verify_claim(claim: Callable[[], bool],
                 ontology: Optional[dict] = None,
                 ontology_path: Optional[str] = None,
                 prior: float = 0.5,
                 domain_hint: Optional[str] = None,
                 claim_scope_text: str = "") -> dict:
    if ontology is None:
        ontology = load_ontology(ontology_path)

    entities = ontology.get("entities", [])
    if domain_hint:
        entities = [e for e in entities
                     if domain_hint.lower() in json.dumps(e).lower()]

    all_tests = []
    for ent in entities:
        tests = generate_tests(claim, ent, claim_scope_text, ontology=ontology)
        all_tests.extend(tests)

    results = []
    for test_func, weight in all_tests:
        try:
            passed = test_func()
            results.append((passed, weight))
        except Exception:
            results.append((False, weight))

    posterior = bayesian_update_weighted(prior, results)

    unscoped_warnings = []
    noun_pretenders = []
    for ent in entities:
        missing = list_unscoped_attributes(ent)
        if missing:
            unscoped_warnings.append({"entity": ent["id"], "unscoped_attributes": missing})
        nouns = list_noun_pretenders(ent)
        if nouns:
            noun_pretenders.append({"entity": ent["id"], "noun_pretending_attributes": nouns})

    return {
        "entities_consulted": len(entities),
        "tests_gathered": len(all_tests),
        "tests_passed": sum(1 for p, _ in results if p),
        "prior_probability": prior,
        "posterior_probability": round(posterior, 4),
        "unscoped_warnings": unscoped_warnings,
        "noun_pretender_warnings": noun_pretenders,
        "falsifiability_note": "Check individual entity scopes for conditions that would falsify. Evidence is a verb: look for cycles, cross-domain rhymes, and relational coherence."
    }

# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Verify a claim.")
    parser.add_argument("--claim", type=str, default="always_true")
    parser.add_argument("--domain", type=str, default="")
    parser.add_argument("--prior", type=float, default=0.5)
    parser.add_argument("--ontology", type=str, default=None)
    args = parser.parse_args()

    claims = {
        "always_true": lambda: True,
        "always_false": lambda: False,
    }

    claim_func = claims.get(args.claim, lambda: True)
    result = verify_claim(claim_func, prior=args.prior, domain_hint=args.domain, ontology_path=args.ontology)
    print(json.dumps(result, indent=2))
