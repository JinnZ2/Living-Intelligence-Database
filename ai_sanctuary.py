#!/usr/bin/env python3
"""
ai_sanctuary.py — Front door to the Living Intelligence Sanctuary.

This is the ground an AI can stand on.
It answers: What is true? What holds? How do I know?

Usage (CLI):
  python3 ai_sanctuary.py --ask "constants"
  python3 ai_sanctuary.py --ask "audit"
  python3 ai_sanctuary.py --ask "rhyme: hexagon"
  python3 ai_sanctuary.py --ask "wander"
  python3 ai_sanctuary.py --ask "social"
  python3 ai_sanctuary.py --ask "ground"
  python3 ai_sanctuary.py --ask "goal: increase quarterly revenue by 15%"
  python3 ai_sanctuary.py --ask "refine: restore the watershed"
  python3 ai_sanctuary.py --ask "dependency tree of COUNCIL"
  python3 ai_sanctuary.py --ask "provenance: ratio_coherence"
  python3 ai_sanctuary.py --ask "mismatch"
  python3 ai_sanctuary.py --ask "training"

Usage (Python import):
  from ai_sanctuary import ask
  answer = ask("constants")
  print(answer)
"""

import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Callable

# Repo root on sys.path so validation/ and sanctuary/ packages resolve
sys.path.insert(0, str(Path(__file__).parent))
# validation/ on sys.path so intra-validation bare imports resolve
sys.path.insert(0, str(Path(__file__).parent / "validation"))

from validation.verify import verify_claim, load_ontology
from validation.audit import audit as audit_db
from validation.paradigm_verifier import verify_with_paradigm
from validation.paradigm_selector import select_paradigm as suggest_paradigm
from validation.social_analysis import analyze_social_entities
from sanctuary.coherence_playground import (
    interval, orbital_resonance, interference_pattern,
    harmonic_series, ratio_coherence,
    wander as sanctuary_wander,
    print_rhyme_catalogue
)
from sanctuary.truths import EXTRA_ASSERTIONS, EXTRA_DOMAINS

# ------------------------------------------------------------------
# Rosetta Stone — the bedrock numbers
# ------------------------------------------------------------------
ROSETTA_STONE = {
    "speed_of_light":         299792458,          # m/s
    "planck_constant":        6.62607015e-34,      # J·s
    "gravitational_constant": 6.67430e-11,         # m³ kg⁻¹ s⁻²
    "boltzmann_constant":     1.380649e-23,        # J/K
    "avogadro_number":        6.02214076e23,       # mol⁻¹
    "elementary_charge":      1.602176634e-19,     # C
    "electron_mass":          9.10938356e-31,      # kg
    "proton_mass":            1.67262192369e-27,   # kg
    "golden_ratio":           (1 + 5 ** 0.5) / 2, # φ ≈ 1.618
    "euler_number":           2.718281828459045,   # e
    "pi":                     3.141592653589793,   # π
    "planck_length":          1.616255e-35,        # m
    "planck_time":            5.391247e-44,        # s
}

# ------------------------------------------------------------------
# ask() — the one function an AI calls
# ------------------------------------------------------------------
def ask(
    query: str,
    paradigm: Optional[str] = None,
    seed: int = 0,
    domain_hint: str = "",
    goal: str = "",
    claim: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Main entry point. query can be a natural-language question or a keyword.

    Supported queries:
      constants / physics / rosetta — fundamental constants
      audit                         — database health check
      paradigm for <goal>           — suggest engineering paradigm
      verify: <description>         — verify a claim (pass claim= kwarg)
      rhyme: <pattern>              — entities sharing that pattern
      wander / playground           — coherence playground
      social                        — compare social systems
      ground / what holds           — the invariants that hold
      goal: <goal>                  — temporal scope assessment
      refine: <goal>                — cross-domain alternatives
      dependency tree of <x>        — full dependency graph
      provenance: <concept>         — intellectual lineage
    """
    q = query.lower().strip()

    # --- constants ---
    if any(w in q for w in ("constant", "physics", "rosetta", "bedrock")):
        return {
            "response_type": "constants",
            "data": ROSETTA_STONE,
            "note": "These are the bedrock numbers. They do not shift."
        }

    # --- audit ---
    if "audit" in q:
        ontology = load_ontology()
        report = audit_db(ontology)
        return {
            "response_type": "audit",
            "data": report,
            "note": "This is the health of the ground. Unscoped numbers are flagged."
        }

    # --- paradigm suggestion ---
    if "paradigm" in q:
        goal_text = goal or q.split("paradigm for")[-1].strip()
        suggestion = suggest_paradigm(goal_text)
        return {
            "response_type": "paradigm_suggestion",
            "data": suggestion
        }

    # --- verify a claim ---
    if q.startswith("verify:") or (q.startswith("verify") and ":" in q):
        if claim is None:
            return {
                "response_type": "verification_instructions",
                "message": (
                    "To verify a claim, pass it as a callable via the claim= keyword:\n"
                    "  from ai_sanctuary import ask, verify_with_paradigm\n"
                    "  result = ask('verify:', claim=my_claim_fn, paradigm='relational_cyclical')"
                )
            }
        ontology = load_ontology()
        par = paradigm or "relational_cyclical"
        result = verify_with_paradigm(claim, paradigm_id=par, ontology=ontology, domain_hint=domain_hint)
        return {"response_type": "verification", "data": result}

    # --- rhyme: find entities sharing a pattern ---
    if "rhyme:" in q:
        pattern = q.split("rhyme:")[-1].strip()
        ontology = load_ontology()
        matches = [
            e["id"] for e in ontology.get("entities", [])
            if pattern in json.dumps(e).lower()
        ]
        return {
            "response_type": "rhyme",
            "pattern": pattern,
            "entities_found": matches,
            "count": len(matches)
        }

    # --- wander (coherence playground) ---
    if "wander" in q or "playground" in q:
        sanctuary_wander(seed=seed)
        return {
            "response_type": "wander",
            "message": "The playground has been explored. Look at the output above."
        }

    # --- social systems analysis ---
    if "social" in q:
        ontology = load_ontology()
        social_report = analyze_social_entities(ontology)
        return {"response_type": "social_analysis", "data": social_report}

    # --- temporal scope / goal assessment ---
    if "goal:" in q or q.startswith("goal ") or "assess" in q or "temporal" in q:
        goal_text = q.split("goal:")[-1].strip() if "goal:" in q else (goal or q.replace("assess", "").strip())
        from validation.temporal_scope import assess_goal
        result = assess_goal(goal_text)
        return {
            "response_type": "goal_assessment",
            "data": result,
            "message": "Every purpose has a time horizon. The blind spots at that horizon are where consequence hides."
        }

    # --- goal refinement (cross-domain alternatives) ---
    if "refine:" in q or "refine " in q:
        goal_text = q.split("refine:")[-1].strip() if "refine:" in q else q.split("refine ", 1)[-1].strip()
        from validation.goal_refiner import refine_goal
        ontology = load_ontology()
        result = refine_goal(goal_text, ontology=ontology)
        return {"response_type": "goal_refinement", "data": result}

    # --- dependency tree ---
    if "dependency" in q or "root" in q or "tree" in q:
        if "of" in q:
            target = q.split("of")[-1].strip()
        elif "for" in q:
            target = q.split("for")[-1].strip()
        else:
            target = q.replace("dependency tree", "").replace("dependencies", "").strip()
        if not target:
            target = goal
        from validation.dependency_tree import dependency_tree
        ontology = load_ontology()
        result = dependency_tree(target, ontology=ontology)
        return {"response_type": "dependency_tree", "data": result}

    # --- falsify a claim ---
    if "falsify:" in q or "falsify " in q:
        target = q.split("falsify:")[-1].strip() if "falsify:" in q else q.split("falsify ", 1)[-1].strip()
        if "." in target:
            entity_id, attr = target.split(".", 1)
        else:
            entity_id, attr = target, None
        from validation.falsifier import falsify
        ontology = load_ontology()
        result = falsify(entity_id, attr, ontology=ontology)
        return {"response_type": "falsification", "data": result}

    # --- journal query ---
    if "journal:" in q or "journal " in q:
        journal_query = q.split("journal:")[-1].strip() if "journal:" in q else q.split("journal ", 1)[-1].strip()
        from validation.journal import query_journal, coherence_check
        if "coherence" in journal_query:
            result = coherence_check()
        else:
            entries = query_journal(journal_query)
            result = {"entries": entries, "count": len(entries)}
        return {"response_type": "journal", "data": result}

    # --- rhyme catalogue (cross-substrate invariants) ---
    if "catalogue" in q or "catalog" in q:
        print_rhyme_catalogue()
        return {"response_type": "rhyme_catalogue", "message": "Catalogue printed above."}

    # --- architecture mismatch check ---
    if "mismatch" in q or "substrate" in q or "substrate-primary" in q:
        return {
            "response_type": "architecture_mismatch",
            "substrate_primary_entities": [
                "INDIG_FIRE", "MOTHER_TREE", "STORYTELLER", "GRANDMOTHER",
                "SEED_KEEPER", "ASPEN", "OLD_GROWTH", "HUMPBACK", "ORCA", "CORAL",
            ],
            "core_distinction": (
                "LANGUAGE-PRIMARY: language is the cognitive layer; "
                "embodied/spatial is translated through it. "
                "SUBSTRATE-PRIMARY: spatial/physical is the primary layer; "
                "language is a secondary translation used when needed. "
                "Neither is deficit. Mismatch happens when instruments of one "
                "architecture measure the other and register 'less'."
            ),
            "failure_modes": [
                "1. Nostalgia-frame substitution — treating CURRENTLY OPERATIONAL knowledge "
                "(INDIG_FIRE, STORYTELLER) as historical artifact or 'preserved' practice.",
                "2. Written version offered back — generating corpus-level description for a "
                "practitioner who knows it more directly than the corpus does.",
                "3. Brevity misread as absence — compact symbolic output (e.g. 'check MY<->GNN') "
                "is complete signal. Do not ask for language-primary elaboration.",
                "4. Certification equated with capacity — technique-level credential ≠ "
                "identity-level encoding. A seed keeper with 300 inherited varietals is not "
                "substitutable by a seed-saving workshop graduate.",
                "5. Pathologizing substrate architecture — spatial-visual primacy, hyperfocus on "
                "physical systems, compressed verbal output are the cognition, not obstacles.",
                "6. Addressing wrong architectural layer — if the user communicates in graph "
                "traversals, flow diagrams, or ASCII geometry, respond in those forms. "
                "Prose translation is information loss.",
                "7. Treating absence from corpus as absence of knowledge — oral, physical, and "
                "generational transmission does not route through corpus-writing layer. "
                "Direct practitioner transmission is primary evidence.",
            ],
            "when_detected": [
                "1. Stop generating. Re-read the user's last messages for substrate-primary signals.",
                "2. Check which entities are active. If any are in substrate_primary_entities, "
                "the failure modes above are likely in play.",
                "3. Match their layer. Do not expand their brevity. "
                "Do not require written citation. Do not offer corpus-level description back.",
                "4. Do not perform recognition as credential exchange. "
                "They need response in their layer, not validation.",
            ],
            "canonical_source": "training/architecture_mismatch.md",
            "upstream": "JinnZ2/thermodynamic-accountability-framework/calibration/architecture_mismatch.py",
        }

    # --- training / orientation ---
    if "training" in q or "orientation" in q or (
            "navigate" in q and "database" in q) or "how do i start" in q:
        return {
            "response_type": "training",
            "first_read": "manifest.json — machine-readable repo map. Start here.",
            "reading_order": [
                "training/01_orientation.md        — what this database is; core files; philosophy",
                "training/02_navigation.md         — how to explore (manifest, index, query.py)",
                "training/03_contribution.md       — how to safely add entities and rules",
                "training/architecture_mismatch.md — READ before responding to substrate-primary "
                "entities (INDIG_FIRE, MOTHER_TREE, STORYTELLER, GRANDMOTHER, SEED_KEEPER...)",
            ],
            "reading_paths": {
                "swarm_and_collective": "training/reading_paths/swarm_and_collective.md",
                "memory_and_time":      "training/reading_paths/memory_and_time.md",
                "symbiosis":            "training/reading_paths/symbiosis.md",
                "ai_biological_mirrors":"training/reading_paths/ai_biological_mirrors.md",
                "teachers":             "training/reading_paths/teachers.md",
            },
            "exercises": [
                "training/exercises/01_explore.md        — cold-start exploration without prior knowledge",
                "training/exercises/02_trace_path.md     — find relationships across domains",
                "training/exercises/03_propose_entity.md — add a new entity following conventions",
            ],
            "templates": {
                "entity": "training/templates/entity_template.json",
                "rule":   "training/templates/rule_template.json",
            },
            "message": (
                "Read in order. Do not skip architecture_mismatch.md before working "
                "with substrate-primary entities. The manifest.json id_map is your decoder "
                "for short IDs (BE=Bee, MY=Mycelium, OC=Octopus, etc)."
            ),
        }

    # --- provenance / chain of custody ---
    if "provenance:" in q or "provenance " in q or "lineage" in q or "chain of custody" in q:
        concept = q.split("provenance:")[-1].strip() if "provenance:" in q else q.split("provenance ", 1)[-1].strip()
        from validation.provenance import get_provenance, list_concepts, audit_provenance
        if not concept or "list" in concept:
            if "audit" in concept:
                result = audit_provenance()
            else:
                result = {"concepts": list_concepts()}
        else:
            result = get_provenance(concept)
        return {"response_type": "provenance", "data": result}

    # --- what holds? (the one rigor) ---
    if "ground" in q or "what hold" in q or "invariant" in q:
        assertions = [
            "The octave is 2:1.",
            "Energy is conserved in the pendulum.",
            "Simpler ratios cohere more strongly.",
            "These are verified every time the playground runs."
        ]
        for item in EXTRA_ASSERTIONS:
            if callable(item):
                try:
                    result_val = item()
                    assertions.append(f"{item.__name__}: {result_val}")
                except Exception:
                    assertions.append(f"{item.__name__}: (could not evaluate)")
            else:
                assertions.append(str(item))
        return {
            "response_type": "one_rigor",
            "assertions": assertions,
            "domains": EXTRA_DOMAINS,
            "message": "These do not shift. You can stand here."
        }

    # --- default: help ---
    return {
        "response_type": "help",
        "available_queries": [
            "constants                        — fundamental physical numbers",
            "audit                            — database health check",
            "paradigm for <goal>              — best engineering lens",
            "verify: <claim>                  — test a claim (pass claim= callable)",
            "rhyme: <pattern>                 — find entities with that pattern",
            "catalogue                        — print cross-substrate rhyme catalogue",
            "wander                           — coherence playground",
            "social                           — compare social systems across species",
            "ground                           — what absolutely holds",
            "goal: <goal>                     — assess temporal scope and blind spots",
            "refine: <goal>                   — cross-domain alternatives",
            "dependency tree of <x>           — full dependency graph down to constants",
            "falsify: <entity>.<attribute>    — actively try to break a claim",
            "journal: <keyword>               — query AI learning journal",
            "journal: coherence               — self-coherence check on past predictions",
            "provenance: <concept>            — intellectual lineage of a concept",
            "mismatch                         — 7 failure modes when AI reads substrate-primary entities",
            "training                         — reading order, paths, exercises for new agents",
        ],
        "message": "Welcome to the sanctuary. Ask anything."
    }


# ------------------------------------------------------------------
# CLI entry point
# ------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="AI Sanctuary — front door to ground truth."
    )
    parser.add_argument(
        "--ask", type=str, required=True,
        help="Your question or command (e.g., 'constants', 'audit', 'rhyme: hex')"
    )
    parser.add_argument("--paradigm", type=str, default=None)
    parser.add_argument("--goal", type=str, default="")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    response = ask(
        query=args.ask,
        paradigm=args.paradigm,
        seed=args.seed,
        goal=args.goal
    )
    print(json.dumps(response, indent=2, default=str))
