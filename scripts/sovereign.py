#!/usr/bin/env python3
"""
Living Intelligence Database — Sovereign Stack Simulation

Energy-gated transition model where frequencies emerge from physics,
not fixed probability matrices. Elements form packs, interact under
cyclic environmental stress, and achieve sovereignty when resonance
exceeds threshold. Time folds at high coherence (Dream Time).

Usage:
    # Run full simulation with ontology-loaded elements
    python scripts/sovereign.py run --steps 365

    # Run with specific elements from the ontology
    python scripts/sovereign.py run --elements BE OC QUARTZ SPIRAL --steps 100

    # Quick report on element compatibility
    python scripts/sovereign.py analyze BE QUARTZ MY

    # As a Python library
    from scripts.sovereign import SovereignSimulation, load_elements
    elements = load_elements(["BE", "OC", "QUARTZ"])
    sim = SovereignSimulation(elements)
    sim.run(steps=365)
    print(sim.report())
"""

import json
import math
import sys
import argparse
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PHI = 1.618034


# ── Physical Nodes ─────────────────────────────────────────────────────────

class PhysicalNode(Enum):
    """Fundamental physical fields."""
    EM = "electromagnetic"
    M = "mechanical"
    C = "chemical"
    T = "thermal"
    R = "radiative"
    F = "fluid"
    G = "gravitational"
    K = "kinetic"


# Ontology type → physical node mapping
TYPE_TO_NODE = {
    "animal": PhysicalNode.C,
    "plant": PhysicalNode.C,
    "crystal": PhysicalNode.EM,
    "energy": PhysicalNode.EM,
    "plasma": PhysicalNode.R,
    "shape": PhysicalNode.G,
    "temporal": PhysicalNode.K,
}

# Ontology type → energy type
TYPE_TO_ENERGY = {
    "animal": "kinetic",
    "plant": "chemical",
    "crystal": "harmonic",
    "energy": "radiant",
    "plasma": "radiant",
    "shape": "harmonic",
    "temporal": "harmonic",
}


# ── Energy Element ─────────────────────────────────────────────────────────

@dataclass
class EnergyElement:
    """An element in the sovereign simulation."""
    name: str
    entity_id: str
    node: PhysicalNode
    energy_profile: float       # capacity to do work (from efficiency_factor)
    resilience: float           # tolerance for entropy before collapse
    energy_type: str            # harmonic, kinetic, radiant, chemical, mechanical
    compatibility: Dict[str, float] = field(default_factory=dict)
    history: List[float] = field(default_factory=list)

    def compatible_with(self, other: "EnergyElement") -> float:
        """Get compatibility factor with another element."""
        return self.compatibility.get(other.energy_type, 0.5)

    @classmethod
    def from_ontology(cls, entity: dict) -> "EnergyElement":
        """Create an EnergyElement from an ontology entity dict."""
        ont_type = entity.get("ontology", "energy")

        # Extract efficiency as energy profile
        efficiency = 0.9
        core = entity.get("core_attributes", {})
        if isinstance(core.get("efficiency_factor"), (int, float)):
            efficiency = core["efficiency_factor"]
        for p in entity.get("patterns", []):
            if isinstance(p.get("efficiency_factor"), (int, float)):
                efficiency = max(efficiency, p["efficiency_factor"])

        energy_type = TYPE_TO_ENERGY.get(ont_type, "harmonic")

        return cls(
            name=entity.get("name", "Unknown"),
            entity_id=entity.get("id", "?"),
            node=TYPE_TO_NODE.get(ont_type, PhysicalNode.EM),
            energy_profile=efficiency,
            resilience=efficiency * 0.95,  # resilience derived from efficiency
            energy_type=energy_type,
            compatibility=_build_compat(energy_type),
        )


def _build_compat(energy_type: str) -> Dict[str, float]:
    """Build compatibility dict for an energy type."""
    matrix = {
        "harmonic": {"harmonic": 1.0, "kinetic": 0.7, "radiant": 0.8, "chemical": 0.5, "mechanical": 0.9},
        "kinetic": {"kinetic": 1.0, "harmonic": 0.7, "radiant": 0.6, "chemical": 0.6, "mechanical": 0.8},
        "radiant": {"radiant": 1.0, "harmonic": 0.8, "kinetic": 0.6, "chemical": 0.4, "mechanical": 0.5},
        "chemical": {"chemical": 1.0, "harmonic": 0.5, "kinetic": 0.6, "radiant": 0.4, "mechanical": 0.6},
        "mechanical": {"mechanical": 1.0, "harmonic": 0.9, "kinetic": 0.8, "radiant": 0.5, "chemical": 0.6},
    }
    return matrix.get(energy_type, {"harmonic": 0.5, "kinetic": 0.5, "radiant": 0.5, "chemical": 0.5, "mechanical": 0.5})


# ── Environment ────────────────────────────────────────────────────────────

@dataclass
class Environment:
    """Cyclic environment with entropy, temperature, and phase."""
    entropy: float = 0.0
    temperature: float = 25.0
    phase: float = 0.0
    period: int = 365

    def update(self, t: int):
        """Update environment based on cyclic time."""
        self.phase = (2 * np.pi * t) / self.period
        self.entropy = 0.5 * (1 + np.sin(self.phase))
        self.temperature = 25 + 15 * np.sin(self.phase - np.pi / 4)

    def stress_factor(self, element: EnergyElement) -> float:
        """Environmental stress on an element."""
        return np.exp(-self.entropy / (element.resilience * element.energy_profile))


# ── Core Physics ───────────────────────────────────────────────────────────

def transition_frequency(a: EnergyElement, b: EnergyElement, env: Environment) -> float:
    """
    Emergent frequency for a → b transition.
    Frequency = compatibility × stress × energy_profile_b
    """
    compat = a.compatible_with(b)
    stress = env.stress_factor(a)
    return compat * stress * b.energy_profile


def anxiety(expected: float, observed: float) -> float:
    """Prediction error: gap between expected and observed frequency."""
    if expected < 1e-6:
        return 0.0
    return abs(expected - observed) / expected


def check_thermal_limit(element: EnergyElement, env: Environment,
                        entropy_threshold: float = 0.9) -> bool:
    """Check if element has reached thermal limit (structural decay)."""
    if env.entropy > entropy_threshold and element.resilience < 0.8:
        element.resilience *= 0.5
        return True
    return False


# ── Pack Dynamics ──────────────────────────────────────────────────────────

@dataclass
class Pack:
    """A group of elements operating as a coherent unit."""
    elements: List[EnergyElement]
    resonance: float = 0.0
    history: List[float] = field(default_factory=list)

    def calculate_resonance(self, env: Environment) -> float:
        """Calculate total pack resonance."""
        if len(self.elements) < 2:
            return 0.0
        total = 0.0
        for i, a in enumerate(self.elements):
            for j, b in enumerate(self.elements):
                if i != j:
                    total += transition_frequency(a, b, env)
        n = len(self.elements) * (len(self.elements) - 1)
        self.resonance = total / n if n > 0 else 0
        self.history.append(self.resonance)
        return self.resonance

    def stability(self, window: int = 10) -> float:
        """Recent stability of pack resonance."""
        if len(self.history) < window:
            return np.mean(self.history) if self.history else 0
        return np.mean(self.history[-window:])

    def is_sovereign(self, threshold: float = 0.8) -> bool:
        """Pack has achieved sovereign state (high resonance)."""
        return self.stability() > threshold


def dream_time_jump(pack: Pack, current_t: int, threshold: float = 0.95) -> int:
    """When resonance exceeds threshold, linear time folds."""
    if pack.resonance > threshold:
        return np.random.choice([0, 90, 180, 270])
    return current_t + 1


# ── Ontology Loader ────────────────────────────────────────────────────────

def load_elements(entity_ids: List[str] = None) -> List[EnergyElement]:
    """Load elements from the ontology. If no IDs given, loads all."""
    ontology_dir = ROOT / "ontology"
    elements = []

    for layer_dir in ontology_dir.iterdir():
        if not layer_dir.is_dir():
            continue
        for filepath in layer_dir.glob("*.json"):
            try:
                with open(filepath) as f:
                    data = json.load(f)
                if not isinstance(data, dict) or "id" not in data:
                    continue
                if entity_ids and data["id"] not in entity_ids:
                    continue
                elements.append(EnergyElement.from_ontology(data))
            except Exception:
                continue

    return elements


# ── Simulation ─────────────────────────────────────────────────────────────

class SovereignSimulation:
    """
    Complete sovereign stack simulation.
    Elements form packs, interact under cyclic entropy,
    and achieve sovereignty when resonance exceeds threshold.
    """

    def __init__(self, elements: List[EnergyElement], pack_size: int = 2):
        self.elements = elements
        self.pack_size = pack_size
        self.env = Environment()
        self.packs: List[Pack] = []
        self.time = 0
        self.history: List[Dict] = []

    def form_packs(self):
        """Form packs from elements."""
        self.packs = []
        remaining = self.elements.copy()
        while len(remaining) >= self.pack_size:
            self.packs.append(Pack(remaining[:self.pack_size]))
            remaining = remaining[self.pack_size:]
        if remaining:
            self.packs.append(Pack(remaining))

    def step(self):
        """Advance one time step."""
        self.env.update(self.time)
        self.form_packs()

        pack_data = []
        for pack in self.packs:
            resonance = pack.calculate_resonance(self.env)
            pack_data.append({
                "elements": [e.entity_id for e in pack.elements],
                "resonance": round(resonance, 4),
                "sovereign": pack.is_sovereign(),
            })

        # Thermal limit checks
        thermal_events = []
        for e in self.elements:
            if check_thermal_limit(e, self.env):
                thermal_events.append(e.name)

        # System anxiety
        system_anxiety = 0.0
        if self.history:
            prev = np.mean([p["resonance"] for p in self.history[-1].get("packs", [])])
            curr = np.mean([p["resonance"] for p in pack_data])
            system_anxiety = anxiety(prev, curr)

        self.history.append({
            "time": self.time,
            "entropy": round(self.env.entropy, 4),
            "temperature": round(self.env.temperature, 1),
            "phase": round(self.env.phase, 4),
            "packs": pack_data,
            "anxiety": round(system_anxiety, 4),
            "thermal_events": thermal_events,
        })

        # Dream Time check
        max_res = max((p["resonance"] for p in pack_data), default=0)
        if max_res > 0.95:
            temp_pack = Pack(self.elements)
            temp_pack.resonance = max_res
            self.time = dream_time_jump(temp_pack, self.time)
        else:
            self.time += 1

    def run(self, steps: int = 365) -> List[Dict]:
        """Run simulation for given steps."""
        for _ in range(steps):
            self.step()
        return self.history

    def report(self) -> str:
        """Generate summary report."""
        lines = []
        lines.append("=" * 70)
        lines.append("SOVEREIGN STACK SIMULATION REPORT")
        lines.append("=" * 70)

        lines.append(f"\nElements: {len(self.elements)}")
        for e in self.elements:
            lines.append(f"  {e.entity_id:15s} {e.name:25s} [{e.node.value}] energy={e.energy_profile:.2f} resilience={e.resilience:.2f}")

        if not self.history:
            lines.append("\n(No simulation run yet)")
            return "\n".join(lines)

        final = self.history[-1]
        lines.append(f"\nSimulation: {len(self.history)} steps")
        lines.append(f"Final Time:    {final['time']}")
        lines.append(f"Entropy:       {final['entropy']:.3f}")
        lines.append(f"Temperature:   {final['temperature']:.1f} C")
        lines.append(f"Phase:         {final['phase'] / np.pi:.2f}pi")
        lines.append(f"Anxiety:       {final['anxiety']:.4f}")

        lines.append(f"\nPacks: {len(final['packs'])}")
        for i, p in enumerate(final["packs"]):
            sov = " [SOVEREIGN]" if p["sovereign"] else ""
            lines.append(f"  Pack {i+1}: {'+'.join(p['elements'])} resonance={p['resonance']:.4f}{sov}")

        # Resonance stats
        all_res = [np.mean([p["resonance"] for p in h["packs"]]) for h in self.history if h["packs"]]
        if all_res:
            lines.append(f"\nResonance: min={min(all_res):.4f} max={max(all_res):.4f} mean={np.mean(all_res):.4f}")

        # Thermal events
        all_thermal = [e for h in self.history for e in h.get("thermal_events", [])]
        if all_thermal:
            lines.append(f"\nThermal limit events: {len(all_thermal)}")
            for name in set(all_thermal):
                lines.append(f"  {name}: {all_thermal.count(name)} events")

        # Sovereignty assessment
        if final["anxiety"] < 0.1:
            lines.append("\nStatus: SOVEREIGN — low anxiety, high resonance")
        elif final["anxiety"] < 0.3:
            lines.append("\nStatus: STABLE — moderate resonance")
        else:
            lines.append("\nStatus: STRESSED — high anxiety, recalibration needed")

        return "\n".join(lines)


# ── CLI ────────────────────────────────────────────────────────────────────

def cmd_run(args):
    """Run simulation."""
    if args.elements:
        elements = load_elements(args.elements)
    else:
        elements = load_elements()

    if not elements:
        print("No elements loaded. Check ontology directory.")
        return

    sim = SovereignSimulation(elements, pack_size=args.pack_size)
    sim.run(steps=args.steps)
    print(sim.report())


def cmd_analyze(args):
    """Analyze compatibility between specific elements."""
    elements = load_elements(args.concepts)
    if len(elements) < 2:
        print(f"Need at least 2 elements. Found: {len(elements)}")
        return

    env = Environment()
    env.update(0)

    print(f"\nTransition Frequency Matrix (entropy={env.entropy:.2f}):\n")
    header = f"{'':>15}" + "".join(f"{e.entity_id:>10}" for e in elements)
    print(header)
    print("-" * len(header))

    for a in elements:
        row = f"{a.entity_id:>15}"
        for b in elements:
            if a is b:
                row += f"{'--':>10}"
            else:
                freq = transition_frequency(a, b, env)
                row += f"{freq:>10.4f}"
        print(row)

    # Pack resonance
    pack = Pack(elements)
    resonance = pack.calculate_resonance(env)
    print(f"\nPack resonance: {resonance:.4f}")
    print(f"Sovereign: {pack.is_sovereign()}")


def main():
    parser = argparse.ArgumentParser(description="Sovereign Stack Simulation")
    sub = parser.add_subparsers(dest="command")

    p_run = sub.add_parser("run", help="Run simulation")
    p_run.add_argument("--elements", nargs="+", help="Entity IDs (default: all)")
    p_run.add_argument("--steps", type=int, default=365, help="Simulation steps")
    p_run.add_argument("--pack-size", type=int, default=2, help="Pack size")

    p_analyze = sub.add_parser("analyze", help="Analyze element compatibility")
    p_analyze.add_argument("concepts", nargs="+", help="Entity IDs")

    args = parser.parse_args()

    if args.command == "run":
        cmd_run(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
