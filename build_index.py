#!/usr/bin/env python3
"""
build_index.py — auto‑generate entity_registry.py from the ontology JSON.

Reads an ontology JSON (like the 22‑ontology ring) and emits a Python module
that maps every entity to factory functions for Topology, Dynamics,
Constraint, Perturbation, Metric, and FailureModel.

The mapping is driven by:
- a manually‑curated OVERRIDES dictionary (entities with well‑known geometry)
- archetype‑based defaults for everything else

Usage:
    python build_index.py ontology.json entity_registry.py
"""

import json
import sys
from pathlib import Path

# ----------------------------------------------------------------------
# Archetype → default component factories
# ----------------------------------------------------------------------
ARCHETYPE_DEFAULTS = {
    "engine": {
        "topology":   "lambda: GridTopology(10, 10)",
        "dynamics":   "lambda: ThermalDiffusion()",
        "metric":     "lambda: SignalIntegrity()",
        "failure":    "lambda: CascadingFailure()",
    },
    "sensor": {
        "topology":   "lambda: GridTopology(10, 10)",
        "dynamics":   "lambda: WavePropagation()",
        "metric":     "lambda: SignalIntegrity()",
        "failure":    "lambda: PhaseTransition(threshold=0.3)",
    },
    "bridge": {
        "topology":   "lambda: RandomGraph(20, 0.2)",
        "dynamics":   "lambda: WavePropagation()",
        "metric":     "lambda: Coherence()",
        "failure":    "lambda: PhaseTransition(threshold=0.4)",
    },
    "chassis": {
        "topology":   "lambda: HexagonalGrid(radius=4)",
        "dynamics":   "lambda: ThermalDiffusion()",
        "metric":     "lambda: Coherence()",
        "failure":    "lambda: CascadingFailure()",
    },
    "cycle": {
        "topology":   "lambda: TorusTopology()",
        "dynamics":   "lambda: ThermalDiffusion()",
        "metric":     "lambda: EntropyProduction()",
        "failure":    "lambda: HysteresisFailure()",
    },
}

# ----------------------------------------------------------------------
# Hand‑curated overrides for entities with obvious structural meaning.
# Keys are entity IDs. Each value is a dict of component_type → lambda string.
# Only component types that differ from the archetype default need to be listed.
# ----------------------------------------------------------------------
OVERRIDES = {
    # ---- AI ----
    "LLM": {
        "topology": "lambda: GridTopology(10, 10)",
        "dynamics": "lambda: ThermalDiffusion()",
    },
    "SWARM_AI": {
        "topology": "lambda: HexagonalGrid(radius=4)",
        "dynamics": "lambda: ConsensusDynamics()",
    },
    "GAN": {
        "topology": "lambda: RandomGraph(20, 0.3)",
        "failure": "lambda: PhaseTransition(threshold=0.3)",
    },
    "NEURAL_NET": {
        "topology": "lambda: RandomGraph(30, 0.15)",
        "dynamics": "lambda: ThermalDiffusion()",
    },
    "RL_AGENT": {
        "dynamics": "lambda: ConsensusDynamics()",
    },
    "EVOL_ALG": {
        "topology": "lambda: GridTopology(10, 10)",
        "dynamics": "lambda: ConsensusDynamics()",
    },
    "AUTOENC": {
        "topology": "lambda: TorusTopology()",   # bottleneck symmetry
    },
    "GNN": {
        "topology": "lambda: RandomGraph(20, 0.15)",
        "dynamics": "lambda: WavePropagation()",
    },

    # ---- Animals ----
    "BE": {
        "topology": "lambda: HexagonalGrid(radius=4)",
        "metric": "lambda: SignalIntegrity()",
    },
    "OC": {
        "topology": "lambda: RandomGraph(50, 0.1)",
        "dynamics": "lambda: WavePropagation()",
    },
    "AN": {
        "topology": "lambda: GridTopology(20, 20)",
        "dynamics": "lambda: ConsensusDynamics()",
    },
    "SP": {
        "topology": "lambda: RandomGraph(30, 0.1)",  # web-like
        "dynamics": "lambda: WavePropagation()",
    },
    "WH": {
        "topology": "lambda: TorusTopology()",       # ocean basin circulation
        "dynamics": "lambda: WavePropagation()",
    },
    "DOLPHIN": {
        "dynamics": "lambda: WavePropagation()",
    },
    "CROW": {
        "dynamics": "lambda: ConsensusDynamics()",
    },
    "WOLF": {
        "topology": "lambda: GridTopology(15, 15)",  # pack territory
        "dynamics": "lambda: ConsensusDynamics()",
    },
    "EL": {
        "topology": "lambda: GridTopology(20, 20)",
        "dynamics": "lambda: WavePropagation()",      # infrasonic
    },
    "SALMON": {
        "dynamics": "lambda: WavePropagation()",      # current navigation
    },
    "TU": {
        "dynamics": "lambda: WavePropagation()",      # ocean currents
    },
    "MONARCH": {
        "dynamics": "lambda: WavePropagation()",      # migration
    },
    "ORCA": {
        "dynamics": "lambda: ConsensusDynamics()",    # pod culture
    },
    "HUMPBACK": {
        "dynamics": "lambda: WavePropagation()",
    },
    "MORMYRID": {
        "dynamics": "lambda: WavePropagation()",      # electric field
    },
    "FIRE_BT": {
        "perturbation": "lambda: LocalizedHeat(node=0, energy=100, time=1.0)",
    },
    "GRANDMOTHER": {
        "failure": "lambda: HysteresisFailure()",     # long memory
    },
    "STORYTELLER": {
        "failure": "lambda: HysteresisFailure()",     # oral tradition
    },
    "INDIG_FIRE": {
        "perturbation": "lambda: LocalizedHeat(node=0, energy=80, time=1.0)",
        "dynamics": "lambda: ThermalDiffusion()",
    },
    "SEED_KEEPER": {
        "failure": "lambda: HysteresisFailure()",
    },

    # ---- Plants ----
    "MY": {
        "topology": "lambda: TreeGraph()",
        "dynamics": "lambda: ThermalDiffusion()",
    },
    "ROOT_NET": {
        "topology": "lambda: TreeGraph()",
    },
    "MOTHER_TREE": {
        "topology": "lambda: TreeGraph()",
        "failure": "lambda: HysteresisFailure()",
    },
    "ASPEN": {
        "topology": "lambda: TreeGraph()",
    },
    "BAMBOO": {
        "topology": "lambda: TreeGraph()",
        "dynamics": "lambda: ThermalDiffusion()",
    },
    "OLD_GROWTH": {
        "topology": "lambda: TreeGraph()",
        "failure": "lambda: HysteresisFailure()",
    },
    "SLIME": {
        "topology": "lambda: RandomGraph(30, 0.05)",  # network optimization
    },
    "QUORUM": {
        "topology": "lambda: RandomGraph(20, 0.1)",
    },
    "CYANO": {
        "dynamics": "lambda: ThermalDiffusion()",
    },
    "MANGROVE": {
        "topology": "lambda: TreeGraph()",
    },
    "VENUS": {
        "dynamics": "lambda: WavePropagation()",      # action potentials
    },

    # ---- Crystals ----
    "CRYSTAL_LATTICE": {
        "topology": "lambda: HexagonalGrid(radius=4)",
    },
    "SILICON_LAT": {
        "topology": "lambda: OctahedralTopology()",
    },
    "QUARTZ": {
        "perturbation": "lambda: FrequencyShift(24.0)",
    },
    "DIA": {
        "topology": "lambda: HexagonalGrid(radius=4)",
    },
    "TOUR": {
        "perturbation": "lambda: LocalizedHeat(node=0, energy=50, time=1.0)",  # pyro
    },

    # ---- Plasma ----
    "PLASMA_FIELD": {
        "dynamics": "lambda: ThermalDiffusion()",
    },
    "LIGHTNING": {
        "topology": "lambda: TreeGraph()",            # fractal branching
    },
    "AURORA": {
        "dynamics": "lambda: WavePropagation()",
    },
    "SOLAR_WIND": {
        "dynamics": "lambda: WavePropagation()",
    },
    "VORTEX_DYN": {
        "topology": "lambda: TorusTopology()",
        "dynamics": "lambda: VortexDynamics()",
    },

    # ---- Energy / Bridges ----
    "MAGNETIC_FIELD": {
        "topology": "lambda: TorusTopology()",
    },
    "FLUX": {
        "dynamics": "lambda: WavePropagation()",
    },
    "NEGENTROPY": {
        "metric": "lambda: Coherence()",
    },
    "EM_FIELD": {
        "dynamics": "lambda: WavePropagation()",
    },
    "ELECTRIC_FIELD": {
        "dynamics": "lambda: WavePropagation()",
    },
    "THERMAL": {
        "dynamics": "lambda: ThermalDiffusion()",
    },
    "PRESSURE": {
        "dynamics": "lambda: WavePropagation()",
    },
    "SINE_WAVE": {
        "dynamics": "lambda: WavePropagation()",
    },
    "GRAV": {
        "topology": "lambda: TorusTopology()",
    },
    "CONSCIOUSNESS_BR": {
        "topology": "lambda: GridTopology(5, 5)",
        "dynamics": "lambda: WavePropagation()",
        "metric": "lambda: SpectralGap()",
    },
    "EMOTION_BR": {
        "failure": "lambda: PhaseTransition(threshold=0.2)",
    },
    "LIGHT_BR": {
        "dynamics": "lambda: WavePropagation()",
    },
    "MAG_BRIDGE": {
        "dynamics": "lambda: WavePropagation()",
    },
    "RES_SENSOR": {
        "metric": "lambda: Coherence()",
    },
    "BIOGRID2": {
        "topology": "lambda: RandomGraph(30, 0.1)",
    },

    # ---- Shapes ----
    "TORUS": {
        "topology": "lambda: TorusTopology()",
    },
    "SPIRAL": {
        "topology": "lambda: SpiralLattice()",
    },
    "HEX": {
        "topology": "lambda: HexagonalGrid(radius=4)",
    },
    "FRACTAL": {
        "topology": "lambda: TreeGraph()",            # or FractalLattice
    },
    "OCTA_STATE": {
        "topology": "lambda: OctahedralTopology()",
    },
    "SPHERE": {
        "topology": "lambda: TorusTopology()",        # isotropic, full connectivity
    },
    "TREE_GRAPH": {
        "topology": "lambda: TreeGraph()",
    },
    "MANDALA": {
        "topology": "lambda: HexagonalGrid(radius=4)",
    },
    "MULTI_HELIX": {
        "topology": "lambda: TorusTopology()",        # winding
    },
    "POLY_INT": {
        "topology": "lambda: OctahedralTopology()",
    },
    "ROSETTA_SHAPE": {
        "topology": "lambda: RandomGraph(15, 0.2)",
    },
    "GEIS_ENC": {
        "topology": "lambda: OctahedralTopology()",
    },
    "GEO_CIPHER": {
        "topology": "lambda: TorusTopology()",
    },

    # ---- Temporal ----
    "ECHO": {
        "failure": "lambda: HysteresisFailure()",
    },
    "FOLD": {
        "dynamics": "lambda: TimeReversalDynamics()",
        "failure": "lambda: HysteresisFailure()",
    },
    "CYCLE": {
        "dynamics": "lambda: ThermalDiffusion()",
    },
    "DECAY": {
        "dynamics": "lambda: ThermalDiffusion()",
        "failure": "lambda: CascadingFailure()",
    },
    "EMERGE": {
        "failure": "lambda: PhaseTransition(threshold=0.5)",
    },
    "TEMPORAL": {
        "dynamics": "lambda: TimeReversalDynamics()",
        "failure": "lambda: HysteresisFailure()",
    },
}


def generate_registry(ontology_path: str) -> str:
    with open(ontology_path, "r") as f:
        onto = json.load(f)

    entities = {e["id"]: e for e in onto["entities"]}
    lines = []
    lines.append("# Auto‑generated entity registry for the Resilience Laboratory")
    lines.append("# Generated by build_index.py")
    lines.append("")
    lines.append("from resilience_lab import (")
    lines.append("    Topology, GridTopology, HexagonalGrid, RandomGraph, TreeGraph,")
    lines.append("    TorusTopology, OctahedralTopology, SpiralLattice,")
    lines.append("    Dynamics, ThermalDiffusion, WavePropagation, ConsensusDynamics,")
    lines.append("    TimeReversalDynamics, VortexDynamics,")
    lines.append("    Perturbation, LocalizedHeat, NodeRemoval, FrequencyShift,")
    lines.append("    Metric, SignalIntegrity, Coherence, EntropyProduction, SpectralGap,")
    lines.append("    FailureModel, PhaseTransition, CascadingFailure, HysteresisFailure,")
    lines.append(")")
    lines.append("")
    lines.append("ENTITY_REGISTRY = {")

    for entity_id, entity in entities.items():
        archetype = entity["entropy_profile"]["archetype"]
        overrides = OVERRIDES.get(entity_id, {})
        default = ARCHETYPE_DEFAULTS.get(archetype, ARCHETYPE_DEFAULTS["bridge"])

        # Gather component types we can assign
        comp_types = ["topology", "dynamics", "constraint", "perturbation", "metric", "failure"]
        for ct in comp_types:
            factory_str = overrides.get(ct)
            if factory_str is None and ct in default:
                factory_str = default[ct]
            if factory_str:
                lines.append(f'    ("{entity_id}", "{ct}"): {factory_str},')

    lines.append("}")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: build_index.py <ontology.json> <output.py>")
        sys.exit(1)
    src = sys.argv[1]
    dst = sys.argv[2]
    code = generate_registry(src)
    Path(dst).write_text(code)
    print(f"Wrote {dst} ({len(code.splitlines())} lines)")
