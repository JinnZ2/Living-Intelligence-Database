#!/usr/bin/env python3
"""
verify.py — Verify a claim against the Living Intelligence Database.
Uses relational confidence: cycle recurrence, cross-domain rhyme,
and dependency coherence — not source prestige.

Usage:
  python3 verify.py --claim always_true --domain "hex" --prior 0.5
  python3 verify.py --claim always_true --legacy        behaviour before the 2026-11-24 repair

Repair 2026-11-24 (fixtures F1, F2 in validation/fixtures/DECLARED.json):
  F1  a claim name that is not registered reads verdict UNKNOWN with a null posterior and
      exit 2. Before, it was run as a claim that returns True.
  F2  a claim takes no argument, so it cannot see the attribute it is "tested" on. It is run
      once and counted as one piece of evidence (evidence_count 1), weighted by the best
      matching attribute. Before, it was counted once per matching attribute, so the posterior
      rose with the number of attributes. tests_gathered still gives the number of matching
      attributes; it is not a count of independent tests.
  F3  (second order) an index entry is thin: id, name, path, no attributes. The full record is
      loaded from its path before any check (entities_hydrated). A record that cannot be loaded
      is listed under load_failures with state LOAD_FAILED and is left out; it is not checked as
      the thin entry. Before, the thin entries were checked as they were, so on the real index
      no test was ever gathered and every claim returned the prior.
  The behaviour before the repair is kept behind legacy=True / --legacy, for comparison.
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
# Hydrate thin index entries (fixture F3)
# ------------------------------------------------------------------
def hydrate_entities(entities: list, repo_root: Path = None):
    """Return (records, hydrated_count, load_failures). An entry that already carries attributes, or
    has no path, is used as it is. A path that cannot be loaded is reported, never replaced by the
    thin entry."""
    if repo_root is None:
        repo_root = Path(__file__).parent.parent
    out, hydrated, failures = [], 0, []
    for e in entities:
        path = e.get("path")
        if "attributes" in e or not path:
            out.append(e)
            continue
        try:
            with open(repo_root / path, "r") as f:
                out.append(json.load(f))
            hydrated += 1
        except (OSError, json.JSONDecodeError) as exc:
            failures.append({"id": e.get("id"), "path": str(path), "state": "LOAD_FAILED",
                             "reason": "%s: %s" % (type(exc).__name__, exc)})
    return out, hydrated, failures

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
                 claim_scope_text: str = "",
                 legacy: bool = False) -> dict:
    if ontology is None:
        ontology = load_ontology(ontology_path)

    entities = ontology.get("entities", [])
    hydrated, load_failures = 0, []
    if not legacy:
        entities, hydrated, load_failures = hydrate_entities(entities)
    if domain_hint:
        entities = [e for e in entities
                     if domain_hint.lower() in json.dumps(e).lower()]

    all_tests = []
    for ent in entities:
        tests = generate_tests(claim, ent, claim_scope_text, ontology=ontology)
        all_tests.extend(tests)

    results = []
    claim_error = None
    if legacy:
        # before the repair: the same claim, run and counted once per matching attribute
        for test_func, weight in all_tests:
            try:
                passed = test_func()
                results.append((passed, weight))
            except Exception:
                results.append((False, weight))
    elif all_tests:
        # one claim, one run, one piece of evidence; weight = the best matching attribute
        weight = max(w for _, w in all_tests)
        try:
            passed = bool(claim())
        except Exception as e:
            passed, claim_error = False, "%s: %s" % (type(e).__name__, e)
        results.append((passed, weight))

    posterior = bayesian_update_weighted(prior, results)
    if not results:
        verdict = "NOT_TESTED"
    else:
        verdict = "TESTED"

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
        "mode": "legacy" if legacy else "repaired",
        "verdict": verdict,
        "entities_consulted": len(entities),
        "entities_hydrated": hydrated,
        "load_failures": load_failures,
        "tests_gathered": len(all_tests),
        "evidence_count": len(results),
        "tests_passed": sum(1 for p, _ in results if p),
        "claim_error": claim_error,
        "prior_probability": prior,
        "posterior_probability": round(posterior, 4),
        "posterior_note": ("no evidence was gathered: the number given is the prior, unchanged"
                           if not results else None),
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
    parser.add_argument("--legacy", action="store_true",
                        help="behaviour before the 2026-11-24 repair (unknown claim -> True; one count per attribute)")
    args = parser.parse_args()

    claims = {
        "always_true": lambda: True,
        "always_false": lambda: False,
    }

    if args.legacy:
        claim_func = claims.get(args.claim, lambda: True)
    elif args.claim not in claims:
        print(json.dumps({
            "mode": "repaired",
            "verdict": "UNKNOWN",
            "claim": args.claim,
            "reason": "no claim is registered under this name; it was not run",
            "known_claims": sorted(claims),
            "tests_passed": 0,
            "evidence_count": 0,
            "prior_probability": args.prior,
            "posterior_probability": None
        }, indent=2))
        sys.exit(2)
    else:
        claim_func = claims[args.claim]
    result = verify_claim(claim_func, prior=args.prior, domain_hint=args.domain,
                          ontology_path=args.ontology, legacy=args.legacy)
    print(json.dumps(result, indent=2))
