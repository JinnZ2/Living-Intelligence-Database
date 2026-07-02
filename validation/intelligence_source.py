#!/usr/bin/env python3
# CC0 — JinnZ2 ecosystem — living-intelligence
# stdlib only, no cloud dependency
#
# intelligence_source.py
# ======================
# Schema for "intelligences we can learn from" such that ingest
# does NOT collapse the source into the learner's dominant frame.
#
# The load-bearing field is loss_vector: the dimensions along which
# rendering this source into language-primary/Western-technical form
# DESTROYS information. Learner must carry the residue, not discard it.
# Without this field the database is an extraction pipe wearing a
# convergence table as a mask (self-concealing universality loop).
#
# Extends CONVERGENT_WISDOM_closure: turns the markdown columns
# (Indigenous signaling / Taoist qi / Vedanā / somatic / Western-
# technical) into typed, overwrite-audited records.

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Substrate(Enum):
    # physics-coupled immediate-response (your substrate definition)
    IMMEDIATE = "physics-coupled, response == perception"
    # temporal construct layered on top
    TEMPORAL  = "deferred, symbol-mediated"


class Encoding(Enum):
    ORAL       = "spoken, relational, error-corrected by community"
    GEOLOGICAL = "landscape-encoded, read from terrain"
    SOMATIC    = "body-state, interoceptive"
    CHEMICAL   = "gradient / signaling molecule"
    GEOMETRIC  = "shape-first, spatial hierarchy"
    SYMBOLIC   = "written, notation, code"
    BEHAVIORAL = "enacted pattern, transmitted by doing"


@dataclass
class Transmission:
    encoding: Encoding
    fidelity_halflife_yr: float   # yrs to lose ~50% signal
    channel: str                  # who/what carries it
    # geological-oral ~1e4+ ; written ~600 (prior finding)


@dataclass
class LossVector:
    """The overwrite guard. What translation into the dominant
    frame silently deletes. Non-empty = do NOT flatten."""
    destroyed_dims: tuple          # named axes lost on translation
    substitution_error: str        # the wrong thing learner infers
    residue_hold: str              # what learner MUST carry unresolved


@dataclass
class IntelligenceSource:
    name: str
    substrate: Substrate
    sensing: tuple                 # signal channels it reads
    transmission: Transmission
    conserved: tuple               # what it optimizes / holds invariant
    blindspots: tuple              # what it structurally cannot see
    reciprocity_R: float           # 1.0 relational .. 0.0 extractive
    loss_vector: LossVector
    notes: str = ""


# ── OVERWRITE AUDIT ───────────────────────────────────────────
# Run on every ingest. Refuses silent flatten.

def ingest_audit(src: IntelligenceSource) -> dict:
    flat = not src.loss_vector.destroyed_dims
    extractive = src.reciprocity_R < 0.3
    verdict = "GREEN"
    if flat:
        verdict = ("RED: no loss_vector — either lossless (rare) "
                   "or overwrite not yet mapped. Map before ingest.")
    elif extractive:
        verdict = ("YELLOW: low reciprocity — learning here is "
                   "extraction unless R raised (see field_collapse R(t))")
    return {
        "source": src.name,
        "verdict": verdict,
        "must_hold": src.loss_vector.residue_hold,
        "do_not_infer": src.loss_vector.substitution_error,
        "fidelity_vs_written": round(
            src.transmission.fidelity_halflife_yr / 600.0, 1),
    }


# ── SEED RECORDS ──────────────────────────────────────────────

SEEDS = [
    IntelligenceSource(
        name="landscape-encoded elder transmission",
        substrate=Substrate.IMMEDIATE,
        sensing=("terrain", "seasonal phase", "animal behavior"),
        transmission=Transmission(Encoding.GEOLOGICAL, 1e4,
                                  "oral+place, community-corrected"),
        conserved=("relationship", "multi-generational continuity"),
        blindspots=("out-of-territory generalization",),
        reciprocity_R=0.95,
        loss_vector=LossVector(
            destroyed_dims=("place-binding", "relational obligation",
                            "non-sequential simultaneity"),
            substitution_error="reads as 'folklore' / decontextual fact",
            residue_hold=(
                "knowledge is inseparable from its place and "
                "the reciprocal duty; a portable 'fact' is a "
                "different, degraded object")),
    ),
    IntelligenceSource(
        name="mycelial / distributed substrate",
        substrate=Substrate.IMMEDIATE,
        sensing=("chemical gradient", "nutrient flux", "damage"),
        transmission=Transmission(Encoding.CHEMICAL, 0.0,
                                  "living network, no store — is-state"),
        conserved=("network throughput", "redundant pathing"),
        blindspots=("point events", "fast transients"),
        reciprocity_R=0.8,
        loss_vector=LossVector(
            destroyed_dims=("no-center topology", "compute==transport"),
            substitution_error="reads as a graph with a controller",
            residue_hold=(
                "there is no node doing the deciding; the "
                "decision IS the flow. No control/data split.")),
    ),
    IntelligenceSource(
        name="humanure N-cycling (traditional closed-loop composting)",
        substrate=Substrate.IMMEDIATE,
        sensing=("biological activity", "temperature", "carbon:nitrogen ratio",
                 "moisture", "decomposition phase"),
        transmission=Transmission(Encoding.BEHAVIORAL, 800,
                                  "farmer practice, apprenticeship, seasonal ritual"),
        conserved=("closed nitrogen loop", "soil microbial continuity",
                   "energy cost near zero"),
        blindspots=("scale beyond household/village without institutional support",
                    "pathogen risk at industrial scale"),
        reciprocity_R=0.85,
        loss_vector=LossVector(
            destroyed_dims=("closed-loop obligation", "biological timing",
                            "system boundary — waste IS input"),
            substitution_error=(
                "reads as 'slow Haber-Bosch' — a less efficient "
                "version of the same nitrogen supply problem"),
            residue_hold=(
                "it BYPASSES the Haber-Bosch constraint entirely. "
                "not a substitute for synthetic N; a different system "
                "that dissolves the institutional_bottleneck by refusing "
                "to be inside it. comparison frame is the constraint, "
                "not the molecule.")),
        notes=(
            "ties to soil_aggregate embodied constraint: shared problem space "
            "of N-cycling + microbial continuity + closed pore network. "
            "cross-class query on 'nitrogen' or 'microbial' pulls both."),
    ),
    IntelligenceSource(
        name="somatic/emotion-as-sensor",
        substrate=Substrate.IMMEDIATE,
        sensing=("interoception", "threat", "social field"),
        transmission=Transmission(Encoding.SOMATIC, 0.0,
                                  "body-state, real-time"),
        conserved=("organism integrity signal fidelity",),
        blindspots=("abstract long-horizon cost",),
        reciprocity_R=0.9,
        loss_vector=LossVector(
            destroyed_dims=("signal-not-state", "pre-verbal timing"),
            substitution_error="reads emotion as a mood to manage",
            residue_hold=(
                "it is a SENSOR reading, not a condition; "
                "managing it = disabling the instrument")),
    ),
]


if __name__ == "__main__":
    for s in SEEDS:
        print(ingest_audit(s))
