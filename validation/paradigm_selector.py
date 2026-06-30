#!/usr/bin/env python3
"""
paradigm_selector.py — Given a goal description, suggest the most appropriate
engineering paradigm(s) from the Living Intelligence Database.

Usage (CLI or import):
  python3 paradigm_selector.py --goal "maintain a watershed for 200 years"
  >>> Best paradigm: relational_cyclical
"""

import json
from engineering_paradigms import PARADIGMS, paradigms_for_context

# Simple keyword-to-time_horizon/scope mapping
KEYWORDS = {
    "long": {"time_horizon": "long", "scope": "wide"},
    "generation": {"time_horizon": "long", "scope": "wide"},
    "century": {"time_horizon": "long", "scope": "wide"},
    "resilience": {"scope": "wide"},
    "ecological": {"scope": "wide", "substrate": "ecological"},
    "soil": {"scope": "wide", "substrate": "ecological"},
    "water": {"scope": "wide", "substrate": "ecological"},
    "community": {"substrate": "community"},
    "moral": {"substrate": "moral"},
    "ethic": {"substrate": "moral"},
    "trauma": {"substrate": "neurological"},
    "heal": {"substrate": "neurological"},
    "ceremony": {"substrate": "neurological"},
    "beauty": {"substrate": "aesthetic"},
    "art": {"substrate": "aesthetic"},
    "short": {"time_horizon": "short", "scope": "narrow"},
    "precise": {"time_horizon": "short", "scope": "narrow"},
    "machine": {"substrate": "physical", "time_horizon": "short", "scope": "narrow"},
}

def select_paradigm(goal: str) -> dict:
    """
    Return the top 3 paradigm recommendations for a goal.
    """
    time_horizon = ""
    scope = ""
    substrate = ""

    for word, flags in KEYWORDS.items():
        if word in goal.lower():
            time_horizon = flags.get("time_horizon", time_horizon)
            scope = flags.get("scope", scope)
            substrate = flags.get("substrate", substrate)

    matching = paradigms_for_context(time_horizon=time_horizon, scope=scope, substrate=substrate)
    if not matching:
        matching = ["relational_cyclical", "western_empirical"]  # default

    details = []
    for pid in matching[:3]:
        for p in PARADIGMS:
            if p["id"] == pid:
                details.append({
                    "id": pid,
                    "name": p["name"],
                    "substrate": p["substrate"],
                    "time_horizon": p["time_horizon"],
                    "success_criteria": p["success_criteria"],
                    "note": p["note"]
                })

    return {
        "goal": goal,
        "recommended_paradigms": details,
        "suggestion": f"Use verify_with_paradigm(claim_func, paradigm_id='{matching[0]}') for best-fit evidence weighting."
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Suggest an engineering paradigm for a goal.")
    parser.add_argument("--goal", type=str, required=True, help="Describe the goal (e.g., 'maintain a watershed for 200 years')")
    args = parser.parse_args()
    print(json.dumps(select_paradigm(args.goal), indent=2))
