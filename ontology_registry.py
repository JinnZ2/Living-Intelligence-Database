# ontology_registry.py

from resilience_lab import (
    Topology, GridTopology, HexagonalGrid, RandomGraph, TreeGraph,
    Dynamics, ThermalDiffusion, WavePropagation, ConsensusDynamics,
    Perturbation, LocalizedHeat, NodeRemoval, FrequencyShift,
    Metric, SignalIntegrity, Coherence, EntropyProduction, SpectralGap,
    FailureModel, PhaseTransition, CascadingFailure, HysteresisFailure,
    Experiment
)
from gb_explorer import (
    QuantumBridge, TernaryBridge, MultiLevelBridge,
    LatticeSimulator, ChipArchitecture, BandEnvironment
)
import math

# ---------------------------------------------------------------------
# Archetype → default component mapping
# ---------------------------------------------------------------------
ARCHETYPE_DEFAULTS = {
    "engine":   {"dynamics": ThermalDiffusion, "failure": CascadingFailure},
    "sensor":   {"metric": SignalIntegrity, "failure": PhaseTransition},
    "bridge":   {"topology": GridTopology, "dynamics": WavePropagation},
    "chassis":  {"topology": HexagonalGrid, "metric": Coherence},
    "cycle":    {"dynamics": ThermalDiffusion, "failure": HysteresisFailure},
}

# ---------------------------------------------------------------------
# Entity → component factory registry
# ---------------------------------------------------------------------
ENTITY_REGISTRY = {}

def register(entity_id, component_type, factory):
    ENTITY_REGISTRY[(entity_id, component_type)] = factory

# ----- AI entities -----
register("LLM", "topology", lambda: GridTopology(10, 10))
register("LLM", "dynamics", lambda: ThermalDiffusion())
register("LLM", "metric", lambda: Coherence())

register("SWARM_AI", "topology", lambda: HexagonalGrid(radius=4))
register("SWARM_AI", "dynamics", lambda: ConsensusDynamics())
register("SWARM_AI", "metric", lambda: EntropyProduction())

register("GAN", "topology", lambda: RandomGraph(20, 0.3))
register("GAN", "failure", lambda: PhaseTransition(threshold=0.3))

# ----- Animals (selected) -----
register("BE", "topology", lambda: HexagonalGrid(radius=4))
register("BE", "metric", lambda: SignalIntegrity())

register("OC", "topology", lambda: RandomGraph(50, 0.1))
register("OC", "dynamics", lambda: WavePropagation())

register("AN", "topology", lambda: GridTopology(20, 20))
register("AN", "dynamics", lambda: ConsensusDynamics())

# ----- Plants (selected) -----
register("MY", "topology", lambda: TreeGraph())
register("MY", "dynamics", lambda: ThermalDiffusion())
register("MY", "metric", lambda: Coherence())

register("MOTHER_TREE", "topology", lambda: TreeGraph())
register("MOTHER_TREE", "failure", lambda: HysteresisFailure())

# ----- Crystals -----
register("SILICON_LAT", "topology", lambda: ChipArchitecture("square").simulator)
register("SILICON_LAT", "metric", lambda: SignalIntegrity())

register("QUARTZ", "topology", lambda: ChipArchitecture("hexagonal").simulator)
register("QUARTZ", "perturbation", lambda: FrequencyShift(24.0))

# ----- Energy / Bridges -----
register("CONSCIOUSNESS_BR", "topology", lambda: GridTopology(5,5))
register("CONSCIOUSNESS_BR", "dynamics", lambda: WavePropagation())
register("CONSCIOUSNESS_BR", "metric", lambda: SpectralGap())

register("EMOTION_BR", "topology", lambda: RandomGraph(10, 0.5))
register("EMOTION_BR", "failure", lambda: PhaseTransition(threshold=0.2))

# ----- Temporal -----
register("ECHO", "failure", lambda: HysteresisFailure())
register("FOLD", "dynamics", lambda: TimeReversalDynamics())  # placeholder
register("CYCLE", "dynamics", lambda: ThermalDiffusion())

# ----- Shapes -----
register("TORUS", "topology", lambda: TorusTopology())  # custom
register("SPIRAL", "topology", lambda: LatticeSimulator("fibonacci_spiral"))
register("HEX", "topology", lambda: HexagonalGrid(radius=4))
register("FRACTAL", "topology", lambda: TreeGraph())
register("OCTA_STATE", "topology", lambda: OctahedralTopology())  # custom
