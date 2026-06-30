#!/usr/bin/env python3
"""
engineering_paradigms.py — Registry of known engineering paradigms.

Each paradigm describes a way of designing, maintaining, and verifying systems.
They differ in substrate, time horizon, scope, evidence type, and success criteria.

These are NOT ranked. They are tools, each appropriate for its own context.
The AI (or human) chooses which paradigm to apply based on the goal.
"""

PARADIGMS = [
    {
        "id": "western_empirical",
        "name": "Western Empirical Engineering",
        "substrate": "Physical systems, machines, isolated variables.",
        "time_horizon": "seconds to years",
        "scope": "Narrow, controlled, minimal dependencies.",
        "evidence_type": "Controlled experiment, statistical significance, peer replication.",
        "success_criteria": "Predicted outcome achieved within tolerance; repeatable.",
        "verification_weight": "Uses evidence.confidence directly, no cross-domain or cycle bonus.",
        "note": "Optimized for precision in bounded systems. Weaker for open, living webs."
    },
    {
        "id": "relational_cyclical",
        "name": "Relational / Cyclical Engineering",
        "substrate": "Ecologies, watersheds, climate, intergenerational systems.",
        "time_horizon": "seasons to millennia",
        "scope": "Wide, web-like, many dependencies.",
        "evidence_type": "Cyclic observation, cross-domain rhyme, relational coherence.",
        "success_criteria": "Pattern holds across cycles, across domains, and within its web of relations.",
        "verification_weight": "Uses relational_confidence: cycle count x cross-domain count x dependency verification.",
        "note": "The engineering of forests, soil, water flow, and human-ecological fit."
    },
    {
        "id": "social_resilience",
        "name": "Social Resilience Engineering",
        "substrate": "Human communities, governance, collective decision-making.",
        "time_horizon": "generations to centuries",
        "scope": "Wide, nested groups, emergent norms.",
        "evidence_type": "Long-term stability of social structures, conflict resolution recurrence, narrative coherence across generations.",
        "success_criteria": "Community persists through shocks; knowledge transfers without rupture; trust networks hold.",
        "verification_weight": "Checks for institutional longevity, oral history consistency, conflict resolution patterns.",
        "note": "The engineering of councils, kinship systems, and peacemaking traditions."
    },
    {
        "id": "moral_engineering",
        "name": "Moral / Ethical Engineering",
        "substrate": "Values, norms, collective conscience.",
        "time_horizon": "centuries to indefinite",
        "scope": "Abstract principles, applied across generations.",
        "evidence_type": "Normative consistency, non-contradiction, lived adherence by a community over time.",
        "success_criteria": "Moral framework prevents harm and promotes flourishing without constant external enforcement.",
        "verification_weight": "Checks for internal coherence, cross-cultural resonance, durability under challenge.",
        "note": "The engineering of 'should' — not enforced by violence, but held by shared understanding."
    },
    {
        "id": "ceremonial_neurological",
        "name": "Ceremonial / Neurological Engineering",
        "substrate": "Human nervous system, emotional regulation, trauma processing.",
        "time_horizon": "minutes to a human lifespan",
        "scope": "Individual and small group, but embedded in cultural context.",
        "evidence_type": "Observed neurological shifts (HRV, cortisol), phenomenological reports, longitudinal mental health outcomes.",
        "success_criteria": "Trauma release, emotional integration, restored capacity for connection, repeatable across participants.",
        "verification_weight": "Combines physiological measures with narrative consistency and long-term wellness tracking.",
        "note": "The engineering of ritual, dance, breath, and story to heal the human mind."
    },
    {
        "id": "aesthetic_coherence",
        "name": "Aesthetic / Coherence Engineering",
        "substrate": "Perception, beauty, pattern recognition.",
        "time_horizon": "immediate to cultural eras",
        "scope": "Sensory input, symbolic systems, art.",
        "evidence_type": "Consensus of felt rightness, mathematical proportionality (phi, Fibonacci), cross-cultural aesthetic universals.",
        "success_criteria": "Pattern evokes recognition, resonance, and emotional alignment; used in sacred art, architecture, music.",
        "verification_weight": "Checks ratio coherence, symmetry, and cross-cultural recurrence of the aesthetic pattern.",
        "note": "The engineering of beauty — the same small whole-number ratios that stabilize orbits also soothe the mind."
    },
]

def get_paradigm(paradigm_id: str) -> dict:
    for p in PARADIGMS:
        if p["id"] == paradigm_id:
            return p
    return None

def list_paradigms():
    return [p["id"] for p in PARADIGMS]

def paradigms_for_context(time_horizon: str = "", scope: str = "", substrate: str = "") -> list:
    """
    Return paradigm IDs that match the given context.
    Simple keyword matching; future versions can use semantic similarity.
    """
    matches = []
    for p in PARADIGMS:
        score = 0
        if time_horizon and time_horizon in p["time_horizon"]:
            score += 1
        if scope and scope in p["scope"]:
            score += 1
        if substrate and substrate in p["substrate"]:
            score += 1
        if score > 0:
            matches.append((p["id"], score))
    matches.sort(key=lambda x: x[1], reverse=True)
    return [m[0] for m in matches]
