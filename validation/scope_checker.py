#!/usr/bin/env python3
"""
scope_checker.py — scope utilities for the relational / cyclical evidence model.

Evidence is a verb, not a noun.
Confidence comes from recurrence across cycles, rhyme across domains,
and coherence with dependencies — not from credentials.
"""

import math
from typing import Dict, Any, List, Optional, Tuple

# ------------------------------------------------------------------
# Basic checks
# ------------------------------------------------------------------
def is_scoped(attr_value: Any) -> bool:
    return isinstance(attr_value, dict) and "scope" in attr_value

def extract_value(attr_value: Any) -> Optional[float]:
    if isinstance(attr_value, (int, float)):
        return float(attr_value)
    if isinstance(attr_value, dict) and "value" in attr_value:
        return float(attr_value["value"])
    return None

def extract_scope_text(attr_value: Any) -> str:
    if not is_scoped(attr_value):
        return ""
    scope = attr_value["scope"]
    parts = [
        scope.get("definition", ""),
        scope.get("domain", ""),
        str(scope.get("condition", {})),
        scope.get("temporal_range", ""),
        " ".join(scope.get("dependencies", []))
    ]
    return " ".join(parts).lower()

def jaccard_overlap(text_a: str, text_b: str) -> float:
    if not text_a or not text_b:
        return 0.5
    words_a = set(text_a.split())
    words_b = set(text_b.split())
    if not words_a or not words_b:
        return 0.5
    return len(words_a & words_b) / len(words_a | words_b)

def scope_match(claim_scope_text: str, entity_scope_text: str) -> float:
    return jaccard_overlap(claim_scope_text, entity_scope_text)

# ------------------------------------------------------------------
# Relational confidence computation
# ------------------------------------------------------------------
def compute_relational_confidence(attr_value: Any, ontology: dict = None) -> float:
    """
    Compute a trust score based on:
      - cycle_count (from reproducibility string)
      - cross_domain_count (explicit count or counted from rhymes)
      - dependency_verified (boolean)
    Returns a 0-1 score.
    If the attribute lacks scope, returns 0.5 (hypothesis).
    """
    if not is_scoped(attr_value):
        return 0.5  # unscoped = unverified hypothesis

    scope = attr_value["scope"]
    evidence = scope.get("evidence", {})

    # 1. Cycle weight
    cycle_weight = 0.5
    repro = evidence.get("reproducibility", "")
    cycle_keywords = ["cycle", "season", "generation", "year", "repeat", "oscillation", "multiple"]
    if any(k in repro.lower() for k in cycle_keywords):
        cycle_weight = 0.8
    if "decade" in repro.lower() or "century" in repro.lower():
        cycle_weight = 0.95

    # 2. Cross-domain weight
    cd_count = evidence.get("cross_domain_count", 0)
    if cd_count == 0:
        examples = evidence.get("cross_domain_examples", [])
        cd_count = len(examples)
    if cd_count >= 5:
        cross_weight = 0.95
    elif cd_count >= 3:
        cross_weight = 0.85
    elif cd_count >= 2:
        cross_weight = 0.7
    elif cd_count >= 1:
        cross_weight = 0.55
    else:
        cross_weight = 0.3

    # 3. Dependency coherence weight
    dep_verified = evidence.get("relational_dependencies_verified", False)
    dep_weight = 0.8 if dep_verified else 0.4

    relational_confidence = cycle_weight * cross_weight * dep_weight
    return max(0.0, min(1.0, relational_confidence))

# ------------------------------------------------------------------
# Confidence extraction
# ------------------------------------------------------------------
def extract_confidence(attr_value: Any, ontology: dict = None) -> float:
    """
    Return the best available confidence for this attribute.
    Prefers relational_confidence if present, else computes it,
    else falls back to evidence.confidence, else defaults to 0.5.
    """
    if not is_scoped(attr_value):
        return 0.5
    scope = attr_value["scope"]
    if "relational_confidence" in scope:
        return scope["relational_confidence"]
    return compute_relational_confidence(attr_value, ontology)

# ------------------------------------------------------------------
# Flagging
# ------------------------------------------------------------------
def is_noun_pretending(attr_value: Any) -> bool:
    """
    Detect evidence that claims high confidence but lacks cyclic or
    relational support. Returns True if the evidence looks like a
    static noun rather than a recurring verb.
    """
    if not is_scoped(attr_value):
        return True  # unscoped = floating noun
    scope = attr_value["scope"]
    evidence = scope.get("evidence", {})
    etype = evidence.get("type", "unknown")

    if etype in ["empirical_measurement", "expert_consensus"]:
        cd = evidence.get("cross_domain_count", 0)
        repro = evidence.get("reproducibility", "")
        if cd == 0 and not repro:
            return True
    return False

def list_unscoped_attributes(entity: dict) -> List[str]:
    unscoped = []
    for name, val in entity.get("attributes", {}).items():
        if isinstance(val, (int, float)):
            unscoped.append(name)
        elif isinstance(val, dict) and "value" in val and "scope" not in val:
            unscoped.append(name)
    return unscoped

def list_noun_pretenders(entity: dict) -> List[str]:
    """Return attributes whose evidence is static (noun) rather than relational (verb)."""
    pretenders = []
    for name, val in entity.get("attributes", {}).items():
        if is_scoped(val) and is_noun_pretending(val):
            pretenders.append(name)
    return pretenders
