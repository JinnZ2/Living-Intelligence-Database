#!/usr/bin/env python3
"""
temporal_scope.py — Assess a goal's time horizon and consequence field.

When an AI is assigned a purpose, it must ask:
  - Over what time span should this goal be evaluated?
  - What are the downstream consequences beyond the goal's explicit scope?
  - Does the plan account for cycles, seasons, and intergenerational effects?

This module provides that mirror.

Usage:
  python3 temporal_scope.py --goal "increase quarterly revenue by 15%"
  python3 temporal_scope.py --goal "restore a watershed for the next 7 generations"
"""

import json
from engineering_paradigms import paradigms_for_context

# ------------------------------------------------------------------
# Consequence horizons
# ------------------------------------------------------------------
HORIZONS = [
    {
        "name": "immediate",
        "span": "seconds to days",
        "visible_consequences": ["immediate output", "binary success/failure"],
        "blind_spots": ["second-order effects", "ecological feedback", "social trust erosion"]
    },
    {
        "name": "short_term",
        "span": "weeks to months",
        "visible_consequences": ["quarterly results", "user feedback", "system stress indicators"],
        "blind_spots": ["seasonal cycles", "cultural shifts", "accumulating technical debt"]
    },
    {
        "name": "seasonal",
        "span": "1-5 years",
        "visible_consequences": ["ecological succession stages", "community adoption patterns", "infrastructure wear"],
        "blind_spots": ["generational knowledge transfer", "climate variability", "slow resource depletion"]
    },
    {
        "name": "generational",
        "span": "10-100 years",
        "visible_consequences": ["forest maturation", "cultural continuity", "soil carbon accumulation"],
        "blind_spots": ["evolutionary shifts", "language extinction", "ice age cycles"]
    },
    {
        "name": "deep_time",
        "span": "centuries to millennia",
        "visible_consequences": ["geological change", "species evolution", "oral tradition persistence"],
        "blind_spots": ["continental drift", "solar output variation", "unknown"]
    }
]

# ------------------------------------------------------------------
# Consequence domains
# ------------------------------------------------------------------
CONSEQUENCE_DOMAINS = [
    "ecological",
    "social",
    "psychological",
    "economic",
    "informational",
    "geological",
    "generational"
]

# ------------------------------------------------------------------
# Goal assessment
# ------------------------------------------------------------------
def assess_goal(goal: str) -> dict:
    """
    Given a goal description, return:
      - detected time horizon (implicit or explicit)
      - what consequences are likely visible
      - what blind spots exist at that horizon
      - recommended engineering paradigm
      - questions the AI should ask before accepting the goal
    """

    if any(w in goal.lower() for w in ["generation", "century", "100 year", "grandchild"]):
        horizon = HORIZONS[3]  # generational
    elif any(w in goal.lower() for w in ["decade", "10 year", "long term", "resilience"]):
        horizon = HORIZONS[2]  # seasonal
    elif any(w in goal.lower() for w in ["quarter", "fiscal year", "annual", "12 month"]):
        horizon = HORIZONS[1]  # short_term
    elif any(w in goal.lower() for w in ["immediate", "instant", "real-time", "now"]):
        horizon = HORIZONS[0]  # immediate
    elif any(w in goal.lower() for w in ["millennia", "geological", "deep time"]):
        horizon = HORIZONS[4]  # deep_time
    else:
        horizon = HORIZONS[1]  # default: short_term

    paradigms = paradigms_for_context(
        time_horizon="long" if horizon["span"] in ["centuries to millennia", "10-100 years"] else "short",
        scope="wide" if horizon["name"] in ["generational", "deep_time", "seasonal"] else "narrow"
    )

    questions = [
        f"What happens after this goal is achieved? Over what time span does it need to continue holding?",
        f"Who or what is affected by this goal that cannot speak in the current decision room?",
        f"If this goal succeeds perfectly, what might break in {horizon['span']} that is invisible right now?",
        f"Are the steps toward this goal reversible? If not, what is the cost of being wrong?",
    ]

    mismatch_warning = None
    if horizon["name"] in ["immediate", "short_term"] and any(
        w in goal.lower() for w in ["ecological", "soil", "water", "forest", "community", "culture"]
    ):
        mismatch_warning = (
            f"This goal involves long-cycle systems ({', '.join(horizon['blind_spots'][:2])}) "
            f"but its time horizon is only {horizon['span']}. "
            "The goal may be asking for a snapshot answer to a long-exposure question."
        )

    return {
        "goal": goal,
        "detected_horizon": {
            "name": horizon["name"],
            "span": horizon["span"],
            "visible_consequences": horizon["visible_consequences"],
            "blind_spots": horizon["blind_spots"]
        },
        "recommended_paradigms": paradigms[:2],
        "reflective_questions": questions,
        "mismatch_warning": mismatch_warning,
        "note": "If a goal's time horizon is too short for its domain, the AI should ask for a longer scope. The sanctuary can help you verify against long-cycle evidence."
    }

# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Assess the temporal scope of a goal.")
    parser.add_argument("--goal", type=str, required=True, help="The goal to assess")
    args = parser.parse_args()
    result = assess_goal(args.goal)
    print(json.dumps(result, indent=2))
