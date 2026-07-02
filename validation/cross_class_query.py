#!/usr/bin/env python3
# CC0 — JinnZ2 ecosystem — living-intelligence
# stdlib only, no cloud dependency
#
# cross_class_query.py
# ====================
# EDGE B — pull from BOTH source classes for a shared constraint.
#
# intelligence_source.py covers: things that transmit (fidelity decays)
# embodied_solution.py covers: things that persist (physics re-derives continuously)
#
# The two classes are usually read separately. But a real constraint problem
# (e.g., "close the nitrogen loop without Haber-Bosch") can be held by BOTH:
#   soil aggregate (embodied)  — fractal pore hierarchy hosts microbial N-cycling
#   humanure N-cycling (source) — behavioral practice that closes the loop
#
# A query that returns BOTH for one constraint is the actual payoff of having
# typed the two classes separately. The learner sees: same problem, two modes
# of holding. Neither cancels the other.

from embodied_solution import SEEDS as EMBODIED_SEEDS, EmbodiedSolution
from intelligence_source import SEEDS as SOURCE_SEEDS, IntelligenceSource


def _embodied_text(src: EmbodiedSolution) -> str:
    return " ".join([
        src.name, src.objective, src.solution_form,
        src.must_recover, src.notes,
        *src.constraint_set,
        src.envelope.driver,
        src.styling_error,
    ]).lower()


def _source_text(src: IntelligenceSource) -> str:
    return " ".join([
        src.name, src.notes,
        *src.conserved,
        *src.sensing,
        *src.blindspots,
        src.loss_vector.residue_hold,
        src.loss_vector.substitution_error,
    ]).lower()


def query_by_constraint(keyword: str,
                        embodied_seeds=None,
                        source_seeds=None) -> dict:
    """
    Return all embodied solutions AND intelligence sources that touch
    a shared constraint keyword.

    Both collections are searched against all text fields — not just
    the constraint_set tuple — so partial or related matches surface.

    Usage:
        query_by_constraint("nitrogen")    # hits humanure source only
        query_by_constraint("microbial")   # hits soil aggregate + humanure (cross!)
        query_by_constraint("N-cycling")   # hits soil aggregate + humanure (cross!)

    Note: matching is keyword/substring, not semantic. "nitrogen" misses
    "microbial life" even though the soil aggregate holds N. This is honest
    about the limit — it names the gap where a semantic/LLM layer would
    close the cross-class pull more completely.
    """
    if embodied_seeds is None:
        embodied_seeds = EMBODIED_SEEDS
    if source_seeds is None:
        source_seeds = SOURCE_SEEDS

    kw = keyword.lower()
    embodied_matches = [s for s in embodied_seeds if kw in _embodied_text(s)]
    source_matches   = [s for s in source_seeds   if kw in _source_text(s)]

    cross_insight = None
    if embodied_matches and source_matches:
        cross_insight = (
            f"Constraint '{keyword}' is held by {len(embodied_matches)} embodied "
            f"solution(s) (physics, continuously re-derived) AND "
            f"{len(source_matches)} intelligence source(s) (transmitted, fidelity-bound). "
            "Neither cancels the other. Together they show: "
            "the same constraint problem has both a standing physical answer "
            "and a practiced human answer. The learner needs both."
        )
    elif embodied_matches:
        cross_insight = (
            f"Only embodied solutions found for '{keyword}'. "
            "The human practice that addresses the same constraint may be "
            "unnamed or not yet in the source seed records."
        )
    elif source_matches:
        cross_insight = (
            f"Only intelligence sources found for '{keyword}'. "
            "A physics-embodied solution to the same constraint may exist "
            "but is not yet in the embodied seed records."
        )
    else:
        cross_insight = f"No matches for '{keyword}' in either class."

    return {
        "constraint_keyword": keyword,
        "embodied_solutions": [
            {"name": s.name, "constraint_set": s.constraint_set,
             "must_recover": s.must_recover}
            for s in embodied_matches
        ],
        "intelligence_sources": [
            {"name": s.name, "conserved": s.conserved,
             "residue_hold": s.loss_vector.residue_hold}
            for s in source_matches
        ],
        "cross_class_insight": cross_insight,
    }


if __name__ == "__main__":
    import json

    for kw in ("nitrogen", "microbial", "N-cycling", "network"):
        result = query_by_constraint(kw)
        print(f"\n── {kw} ──")
        print(f"  embodied : {[r['name'] for r in result['embodied_solutions']]}")
        print(f"  sources  : {[r['name'] for r in result['intelligence_sources']]}")
        if result["embodied_solutions"] and result["intelligence_sources"]:
            print(f"  CROSS    : {result['cross_class_insight'][:120]}...")
