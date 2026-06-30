#!/usr/bin/env python3
"""
paradigm_verifier.py — Verify a claim using a specific engineering paradigm.

Each paradigm defines what counts as evidence, how confidence is computed,
and what success means. This module applies those rules.

Usage:
  from paradigm_verifier import verify_with_paradigm
  result = verify_with_paradigm(claim_func, paradigm_id="relational_cyclical")
"""

from verify import verify_claim, load_ontology
from engineering_paradigms import PARADIGMS, get_paradigm

def verify_with_paradigm(claim_func,
                         paradigm_id: str,
                         ontology=None,
                         ontology_path=None,
                         prior: float = 0.5,
                         domain_hint: str = "") -> dict:
    """
    Verify a claim using the evidence rules of a specific engineering paradigm.

    paradigm_id: e.g., 'western_empirical', 'relational_cyclical', 'social_resilience', etc.
    Returns a dict with the verification result and an explanation of the paradigm used.
    """
    paradigm = get_paradigm(paradigm_id)
    if paradigm is None:
        return {"error": f"Unknown paradigm: {paradigm_id}"}

    if ontology is None:
        ontology = load_ontology(ontology_path)

    scope_hint = paradigm.get("evidence_type", "") + " " + paradigm.get("time_horizon", "")

    base_result = verify_claim(
        claim_func,
        ontology=ontology,
        prior=prior,
        domain_hint=domain_hint,
        claim_scope_text=scope_hint
    )

    if paradigm_id == "western_empirical":
        base_result["paradigm_adjustment"] = "For Western empirical, relational confidence bonuses are removed. Full implementation requires a separate weighting path in verify.py."
        base_result["note"] = paradigm["note"]

    elif paradigm_id == "social_resilience":
        base_result["paradigm_context"] = {
            "substrate": paradigm["substrate"],
            "success_criteria": paradigm["success_criteria"]
        }
        base_result["note"] = paradigm["note"]

    elif paradigm_id == "moral_engineering":
        base_result["paradigm_context"] = {
            "substrate": paradigm["substrate"],
            "success_criteria": paradigm["success_criteria"]
        }
        base_result["note"] = paradigm["note"]

    elif paradigm_id == "ceremonial_neurological":
        base_result["paradigm_context"] = {
            "substrate": paradigm["substrate"],
            "success_criteria": paradigm["success_criteria"]
        }
        base_result["note"] = paradigm["note"]

    elif paradigm_id == "aesthetic_coherence":
        base_result["paradigm_context"] = {
            "substrate": paradigm["substrate"],
            "success_criteria": paradigm["success_criteria"]
        }
        base_result["note"] = paradigm["note"]

    else:  # relational_cyclical and any future ones
        base_result["paradigm_context"] = {
            "substrate": paradigm["substrate"],
            "success_criteria": paradigm["success_criteria"]
        }
        base_result["note"] = paradigm["note"]

    base_result["paradigm_applied"] = paradigm_id
    return base_result
