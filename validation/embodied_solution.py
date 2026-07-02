#!/usr/bin/env python3
# CC0 — JinnZ2 ecosystem — living-intelligence
# stdlib only, no cloud dependency
#
# embodied_solution.py
# ====================
# Sources that do not transmit. They PERSIST as standing solutions
# to a physics constraint problem, re-derived continuously by the
# same physics. No symbol layer. No fidelity decay while constraints
# hold. The human-centric schema (intelligence_source.py) can't hold
# these — it assumes a transmission. This is the parallel class.
#
# LOAD-BEARING FIELD: constraint_set.
# The embodiment is the ANSWER. Copying the answer without recovering
# the QUESTION = "biomimicry as styling" = fails outside envelope.
# copy_audit() refuses the copy until the constraint set is recovered.
#
# Inverse of PhysicsGuard:
#   PhysicsGuard : claim        -> constraint equations   (forward)
#   this reader  : embodiment   -> constraint set          (recover)
# Hooks: constraint_recovery_framework, indigenous_encoding_recovery.

from dataclasses import dataclass


@dataclass
class Envelope:
    """Where the solution holds. Copy outside this and it breaks —
    which is exactly what the styling-copier never checks."""
    bounds: tuple            # named operating limits
    driver: str              # the energy/gradient that runs it


@dataclass
class EmbodiedSolution:
    name: str
    constraint_set: tuple    # the physics PROBLEM being solved
    objective: str           # what is minimized / conserved
    solution_form: str       # geometry / material / behavior embodied
    envelope: Envelope
    # the overwrite specific to this class:
    styling_error: str       # what a form-copier wrongly extracts
    must_recover: str        # constraint that MUST be recovered first
    # fidelity: transmission is replaced by continuous re-derivation
    rederived_by: str        # the physics that keeps re-solving it
    notes: str = ""


def copy_audit(src: EmbodiedSolution,
               recovered_constraints: tuple = ()) -> dict:
    """Gate between inspiration and engineering.
    GREEN only if the learner recovered the constraint set."""
    have = set(recovered_constraints)
    need = set(src.constraint_set)
    missing = tuple(need - have)
    if not recovered_constraints:
        verdict = ("RED: styling. form copied, problem not recovered. "
                   "will fail outside envelope.")
    elif missing:
        verdict = f"YELLOW: partial. missing constraints -> {missing}"
    else:
        verdict = ("GREEN: engineering. form is now portable within "
                   "its envelope.")
    return {
        "source": src.name,
        "verdict": verdict,
        "envelope_driver": src.envelope.driver,
        "envelope_bounds": src.envelope.bounds,
        "do_not_extract": src.styling_error,
        "must_recover": src.must_recover,
    }


# ── SEED RECORDS (physics-embodied, non-transmitting) ─────────

SEEDS = [
    EmbodiedSolution(
        name="avian long-bone (trabecular truss)",
        constraint_set=("max stiffness+strength per unit mass",
                        "fixed bone modulus",
                        "species flight load field"),
        objective="minimize mass at required bending/torsion resistance",
        solution_form=(
            "hollow tube + internal struts aligned to the "
            "principal stress trajectories (Michell topology)"),
        envelope=Envelope(
            bounds=("this species' load directions", "impact bounds"),
            driver="mechanical load re-grown each generation"),
        styling_error="'hollow shell with random struts' — struts as decor",
        must_recover=(
            "the struts TRACK a specific stress-trajectory "
            "field. wrong load field -> wrong truss -> failure."),
        rederived_by="bone remodeling (Wolff) re-solves it every life",
    ),
    EmbodiedSolution(
        name="Macrotermes mound (passive gas exchange)",
        constraint_set=("O2/CO2 exchange for fungus+colony",
                        "zero metabolic pumping cost",
                        "diurnal external temperature swing"),
        objective="gas turnover on no active energy",
        solution_form=(
            "porous shell acting as a tidal lung driven by "
            "day/night thermal oscillation (NOT a steady chimney)"),
        envelope=Envelope(
            bounds=("diurnal swing amplitude", "shell porosity range"),
            driver="OSCILLATORY external temperature, not steady buoyancy"),
        styling_error="'termite mound = chimney' (the classic wrong copy)",
        must_recover=(
            "the PUMP is the diurnal oscillation. steady-state "
            "chimney models fail; the driver is time-varying."),
        rederived_by="sun cycle + colony maintenance, continuously",
    ),
    EmbodiedSolution(
        name="soil aggregate (hierarchical porosity)",
        constraint_set=("hold water (capillary)",
                        "transmit gas (air pores)",
                        "resist structural collapse",
                        "host microbial life"),
        objective="four functions on one pore network simultaneously",
        solution_form=(
            "fractal pore hierarchy — macropores drain/aerate, "
            "micropores retain; aggregation from roots+biota+glomalin"),
        envelope=Envelope(
            bounds=("moisture range", "texture", "biological activity"),
            driver="root exudate + fungal binding + wet/dry cycling"),
        styling_error="soil as inert bulk-density number / growth medium",
        must_recover=(
            "the pore-size HIERARCHY is the function. tillage / "
            "bulk metrics erase it and take all four functions."),
        rederived_by="living roots+fungi rebuild aggregates continuously",
        notes="ties to interface-moisture whitespace + humanure N-cycling",
    ),
    EmbodiedSolution(
        name="spider dragline silk (ambient-spun toughness)",
        constraint_set=("high strength AND high extensibility (toughness)",
                        "aqueous protein feedstock",
                        "no heat, no pressure, no solvent"),
        objective="max toughness from ambient-temperature processing",
        solution_form=(
            "beta-sheet nanocrystals in amorphous matrix, set by "
            "shear + pH drop + ion gradient along the spinning duct"),
        envelope=Envelope(
            bounds=("draw rate", "hydration", "duct gradient"),
            driver="mechanical shear + chemical gradient during extrusion"),
        styling_error="'copy the protein sequence' — molecule alone",
        must_recover=(
            "the PROCESSING gradient co-makes the material. "
            "same sequence, no gradient -> weak silk."),
        rederived_by="spun fresh on demand; not stored",
    ),
    EmbodiedSolution(
        name="rhombohedral (ABC) stacking — phase selector",
        constraint_set=("flat band / high DOS at low carrier density",
                        "from geometry alone, fixed composition"),
        objective="correlation-ready electronic structure by symmetry",
        solution_form=(
            "broken z-mirror chiral staircase stacking of "
            "4-5 carbon layers"),
        envelope=Envelope(
            bounds=("4-5 layers", "ultracold", "hole-doped regime"),
            driver="stacking symmetry (geometric configuration bit)"),
        styling_error="'it's just carbon' — composition thinking",
        must_recover=(
            "GEOMETRY is the engineering, not the element. "
            "(links rhombohedral_phase_menu.py)"),
        rederived_by="crystal structure — standing, not transmitted",
    ),
]


if __name__ == "__main__":
    bone = SEEDS[0]
    print("no recovery:")
    print(" ", copy_audit(bone))
    print("full recovery:")
    print(" ", copy_audit(bone, bone.constraint_set))
