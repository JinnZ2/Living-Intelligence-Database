#!/usr/bin/env python3
"""
Living Intelligence Database — Innovation Playground

Implements Theory.md: a semantic backbone for ontology-driven pattern
generation, physics-constrained evaluation, and hypothesis experiments.

Usage:
    # Interactive exploration
    python scripts/playground.py explore crystal animal

    # Run a hypothesis experiment
    python scripts/playground.py experiment BE QUARTZ SPIRAL --steps 20

    # Apply rules engine to find emergent patterns
    python scripts/playground.py rules BE HEX phi

    # Optimize: find best concept combinations
    python scripts/playground.py optimize --type animal crystal --top 5

    # Visualize concept graph (requires networkx + matplotlib)
    python scripts/playground.py visualize BE OC HEX TORUS MY

    # As a Python library
    from scripts.playground import Playground
    pg = Playground()
    pg.add("BE"); pg.add("QUARTZ"); pg.add("SPIRAL")
    pg.generate_patterns()
    pg.run_experiment(steps=20)
"""

import json
import math
import sys
import argparse
import itertools
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_DIR = ROOT / "ontology"
INDEX_FILE = ROOT / "ontology_index.json"
RULES_FILE = ROOT / "rules" / "expander_rules.json"

phi = 1.618034  # Golden ratio


# ── Concept ────────────────────────────────────────────────────────────────

@dataclass
class Concept:
    """A living intelligence loaded from the ontology."""
    id: str
    name: str
    category: str  # ontology type
    emoji: str = ""
    description: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)
    links: List[Dict[str, str]] = field(default_factory=list)
    patterns: List[Dict[str, Any]] = field(default_factory=list)
    energy_profile: float = 1.0
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_json(cls, data: dict) -> "Concept":
        """Load a Concept from an entity JSON dict."""
        # Compute energy_profile from efficiency factors
        efficiency = 1.0
        patterns = data.get("patterns", [])
        if patterns:
            efficiencies = [p.get("efficiency_factor", 0.9) for p in patterns]
            efficiency = sum(efficiencies) / len(efficiencies)
        else:
            core = data.get("core_attributes", {})
            efficiency = core.get("efficiency_factor", 0.9)

        return cls(
            id=data["id"],
            name=data["name"],
            category=data.get("ontology", "unknown"),
            emoji=data.get("emoji", ""),
            description=data.get("description", ""),
            attributes=data.get("core_attributes", {}),
            links=data.get("links", []),
            patterns=patterns,
            energy_profile=efficiency,
            raw=data,
        )

    def infer_patterns(self) -> List[Dict[str, Any]]:
        """Infer interaction patterns from attributes and links."""
        inferred = []
        attr_str = json.dumps(self.attributes).lower()

        # Pattern inference from attribute keywords
        pattern_map = {
            "resonance": ("resonance_pattern", "vibrational"),
            "vibration": ("resonance_pattern", "vibrational"),
            "movement": ("motion_pattern", "kinetic"),
            "locomotion": ("motion_pattern", "kinetic"),
            "network": ("network_pattern", "distributed"),
            "mesh": ("network_pattern", "distributed"),
            "distributed": ("network_pattern", "distributed"),
            "encoding": ("encoding_pattern", "informational"),
            "translation": ("encoding_pattern", "informational"),
            "thermal": ("thermal_pattern", "thermodynamic"),
            "temperature": ("thermal_pattern", "thermodynamic"),
            "magnetic": ("field_pattern", "electromagnetic"),
            "electric": ("field_pattern", "electromagnetic"),
            "optical": ("optical_pattern", "photonic"),
            "light": ("optical_pattern", "photonic"),
            "polarization": ("optical_pattern", "photonic"),
            "growth": ("growth_pattern", "developmental"),
            "symbiosis": ("symbiotic_pattern", "mutualistic"),
            "predator": ("predation_pattern", "competitive"),
            "hunting": ("predation_pattern", "competitive"),
            "navigation": ("navigation_pattern", "spatial"),
            "acoustic": ("acoustic_pattern", "wave"),
            "echolocation": ("acoustic_pattern", "wave"),
            "camouflage": ("adaptation_pattern", "adaptive"),
            "adaptation": ("adaptation_pattern", "adaptive"),
            "memory": ("memory_pattern", "temporal"),
            "cryptobiosis": ("survival_pattern", "extremophilic"),
        }

        for keyword, (pattern_name, pattern_type) in pattern_map.items():
            if keyword in attr_str:
                inferred.append({
                    "source": self.id,
                    "name": pattern_name,
                    "type": pattern_type,
                    "strength": self.energy_profile,
                })

        # Also infer from explicit patterns array
        for p in self.patterns:
            inferred.append({
                "source": self.id,
                "name": p.get("name", "unknown"),
                "type": p.get("type", "unknown"),
                "strength": p.get("efficiency_factor", 0.9),
            })

        return inferred

    def link_targets(self) -> List[str]:
        """Get IDs of all linked entities."""
        return [link.get("target", "") for link in self.links]


# ── Environment ────────────────────────────────────────────────────────────

@dataclass
class Environment:
    """Dynamic environment with physical forces."""
    gravity: float = 9.81
    wind: float = 0.0
    temperature: float = 25.0
    em_field: float = 0.1
    time: float = 0.0

    def update(self, dt: float = 1.0):
        """Evolve environment over one timestep."""
        self.time += dt
        self.wind = math.sin(self.time / 10.0) * 2.0
        self.temperature = 25.0 + 5.0 * math.sin(self.time / 20.0)
        self.em_field = 0.1 + 0.05 * math.cos(self.time / 15.0)

    def as_dict(self) -> Dict[str, float]:
        return {
            "gravity": self.gravity,
            "wind": self.wind,
            "temperature": self.temperature,
            "em_field": self.em_field,
            "time": self.time,
        }


# ── Interaction Rules ──────────────────────────────────────────────────────

# Category interaction coefficients — how much two types amplify each other
INTERACTION_MATRIX = {
    ("animal", "animal"): 0.3,
    ("animal", "plant"): 0.6,
    ("animal", "crystal"): 0.2,
    ("animal", "energy"): 0.5,
    ("animal", "plasma"): 0.3,
    ("animal", "shape"): 0.7,
    ("animal", "temporal"): 0.4,
    ("plant", "plant"): 0.5,
    ("plant", "crystal"): 0.3,
    ("plant", "energy"): 0.7,
    ("plant", "plasma"): 0.2,
    ("plant", "shape"): 0.4,
    ("plant", "temporal"): 0.6,
    ("crystal", "crystal"): 0.6,
    ("crystal", "energy"): 0.8,
    ("crystal", "plasma"): 0.5,
    ("crystal", "shape"): 0.9,
    ("crystal", "temporal"): 0.3,
    ("energy", "energy"): 0.7,
    ("energy", "plasma"): 0.9,
    ("energy", "shape"): 0.8,
    ("energy", "temporal"): 0.5,
    ("plasma", "plasma"): 0.6,
    ("plasma", "shape"): 0.7,
    ("plasma", "temporal"): 0.4,
    ("shape", "shape"): 0.8,
    ("shape", "temporal"): 0.5,
    ("temporal", "temporal"): 0.4,
}


def interaction_coefficient(type_a: str, type_b: str) -> float:
    """Get interaction coefficient between two ontology types."""
    key = tuple(sorted([type_a, type_b]))
    return INTERACTION_MATRIX.get(key, 0.1)


def compute_interaction(a: Concept, b: Concept, env: Environment) -> float:
    """Compute interaction strength between two concepts in an environment."""
    base = interaction_coefficient(a.category, b.category)
    energy = a.energy_profile * b.energy_profile

    # Link bonus: direct links multiply interaction
    link_bonus = 1.0
    if b.id in a.link_targets() or a.id in b.link_targets():
        link_bonus = phi  # Golden ratio bonus for linked concepts

    # Environmental modulation
    env_mod = 1.0
    if a.category in ("energy", "plasma") or b.category in ("energy", "plasma"):
        env_mod += env.em_field
    if a.category == "plant" or b.category == "plant":
        env_mod += env.temperature / 100.0
    if a.category == "animal" or b.category == "animal":
        env_mod += abs(env.wind) / 10.0

    return base * energy * link_bonus * env_mod


# ── Rules Engine ───────────────────────────────────────────────────────────

def load_expander_rules() -> List[Dict]:
    """Load inference rules from rules/expander_rules.json."""
    if not RULES_FILE.exists():
        return []
    with open(RULES_FILE) as f:
        return json.load(f)


def apply_rules(active_ids: List[str], rules: List[Dict] = None) -> List[Dict]:
    """
    Apply expander rules to a set of active concept IDs.
    Returns list of triggered rules with their outputs.
    """
    if rules is None:
        rules = load_expander_rules()

    active_set = set(active_ids)
    triggered = []

    for rule in rules:
        conditions = set(rule.get("if", []))
        if conditions.issubset(active_set):
            triggered.append({
                "conditions": rule["if"],
                "result": rule["then"],
                "matched": list(conditions & active_set),
            })

    return triggered


# ── Ontology Loader ────────────────────────────────────────────────────────

def load_ontology() -> Dict[str, Concept]:
    """Load all entities from the ontology into Concept objects."""
    concepts = {}

    for layer_dir in ONTOLOGY_DIR.iterdir():
        if not layer_dir.is_dir():
            continue
        for filepath in layer_dir.glob("*.json"):
            try:
                with open(filepath) as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    continue
                if "id" not in data or "name" not in data:
                    continue
                concept = Concept.from_json(data)
                concepts[concept.id] = concept
            except Exception:
                continue

    return concepts


# ── Playground ─────────────────────────────────────────────────────────────

class Playground:
    """
    Innovation Playground — combine concepts, generate patterns,
    run physics-constrained experiments, and optimize.
    """

    def __init__(self, ontology: Dict[str, Concept] = None):
        self.ontology = ontology or load_ontology()
        self.active: List[Concept] = []
        self.pattern_space: List[Dict] = []
        self.environment = Environment()
        self.rules = load_expander_rules()
        self.history: List[Tuple[float, float, Dict]] = []

    def add(self, concept_id: str) -> Optional[Concept]:
        """Add a concept to the active set by ID."""
        concept = self.ontology.get(concept_id)
        if concept and concept not in self.active:
            self.active.append(concept)
            return concept
        return None

    def add_by_type(self, ontology_type: str, limit: int = 5):
        """Add all concepts of a given type."""
        count = 0
        for c in self.ontology.values():
            if c.category == ontology_type and count < limit:
                self.add(c.id)
                count += 1

    def remove(self, concept_id: str):
        """Remove a concept from the active set."""
        self.active = [c for c in self.active if c.id != concept_id]

    def clear(self):
        """Clear active concepts and pattern space."""
        self.active.clear()
        self.pattern_space.clear()
        self.history.clear()
        self.environment = Environment()

    def generate_patterns(self) -> List[Dict]:
        """Generate patterns from all active concepts."""
        self.pattern_space.clear()
        for concept in self.active:
            self.pattern_space.extend(concept.infer_patterns())
        return self.pattern_space

    def evaluate_patterns(self) -> List[Tuple[Dict, float]]:
        """
        Evaluate patterns with physics constraints.
        Returns (pattern, score) tuples sorted by score.
        """
        results = []
        for pattern in self.pattern_space:
            score = pattern.get("strength", 0.5)

            # Physics constraints by pattern type
            ptype = pattern.get("type", "")
            if ptype == "vibrational":
                score *= 1.0 + self.environment.em_field
            elif ptype == "kinetic":
                score *= 1.0 - abs(self.environment.wind) / 20.0
            elif ptype == "thermodynamic":
                score *= self.environment.temperature / 25.0
            elif ptype == "electromagnetic":
                score *= 1.0 + self.environment.em_field * 2
            elif ptype == "photonic":
                score *= 1.2  # Light patterns are generally efficient
            elif ptype == "distributed":
                score *= 1.0 + len(self.active) * 0.05  # Networks scale
            elif ptype == "wave":
                score *= 1.0 + abs(self.environment.wind) / 10.0

            results.append((pattern, round(score, 4)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def compute_synergy(self) -> float:
        """Compute total synergy score across all active concept pairs."""
        total = 0.0
        for a, b in itertools.combinations(self.active, 2):
            total += compute_interaction(a, b, self.environment)
        return round(total, 4)

    def apply_rules(self) -> List[Dict]:
        """Apply expander rules to active concept IDs."""
        active_ids = [c.id for c in self.active]
        return apply_rules(active_ids, self.rules)

    def run_experiment(self, steps: int = 20) -> List[Dict]:
        """
        Run a time-stepped experiment with environmental dynamics.
        Returns history of (step, synergy, environment_state).
        """
        self.history.clear()

        for step in range(steps):
            self.environment.update()
            synergy = self.compute_synergy()

            # Feedback: concept energy profiles adapt to synergy
            for c in self.active:
                c.energy_profile *= 1 + 0.01 * math.tanh(synergy)

            self.history.append({
                "step": step,
                "synergy": round(synergy, 4),
                "env": self.environment.as_dict().copy(),
                "concept_energies": {
                    c.id: round(c.energy_profile, 4) for c in self.active
                },
            })

        return self.history

    def optimize(self, pool_types: List[str] = None, top_n: int = 5,
                 combo_size: int = 3, iterations: int = 10) -> List[Tuple[List[str], float]]:
        """
        Find the best concept combinations by brute-force synergy evaluation.
        Tests combinations from the given ontology types.
        """
        pool = []
        for c in self.ontology.values():
            if pool_types is None or c.category in pool_types:
                pool.append(c)

        if len(pool) < combo_size:
            combo_size = len(pool)

        best = []
        env = Environment()

        for combo in itertools.combinations(pool, combo_size):
            # Compute synergy for this combination
            total = 0.0
            for a, b in itertools.combinations(combo, 2):
                total += compute_interaction(a, b, env)
            best.append(([c.id for c in combo], round(total, 4)))

        best.sort(key=lambda x: x[1], reverse=True)
        return best[:top_n]

    def summary(self) -> str:
        """Return a text summary of the playground state."""
        lines = []
        lines.append(f"Active concepts: {len(self.active)}")
        for c in self.active:
            lines.append(f"  {c.emoji} {c.name} ({c.id}) [{c.category}] energy={c.energy_profile:.3f}")

        lines.append(f"\nPatterns: {len(self.pattern_space)}")
        lines.append(f"Synergy: {self.compute_synergy()}")

        triggered = self.apply_rules()
        if triggered:
            lines.append(f"\nTriggered rules: {len(triggered)}")
            for r in triggered:
                lines.append(f"  {' + '.join(r['conditions'])} -> {r['result']}")

        return "\n".join(lines)


# ── Visualization ──────────────────────────────────────────────────────────

def visualize(playground: Playground, output_file: str = None):
    """Visualize the active concept graph. Requires networkx + matplotlib."""
    try:
        import networkx as nx
        import matplotlib.pyplot as plt
    except ImportError:
        print("Install visualization deps: pip install networkx matplotlib")
        return

    G = nx.Graph()

    # Color map by category
    colors = {
        "animal": "#FF6B6B", "plant": "#51CF66", "crystal": "#845EF7",
        "energy": "#FFD43B", "plasma": "#FF922B", "shape": "#22B8CF",
        "temporal": "#868E96",
    }

    for c in playground.active:
        G.add_node(c.id, label=f"{c.emoji}{c.name}", category=c.category)

    for c in playground.active:
        for link in c.links:
            target = link.get("target", "")
            relation = link.get("relation", "connected_to")
            if G.has_node(target):
                G.add_edge(c.id, target, relation=relation)

    node_colors = [colors.get(G.nodes[n].get("category", ""), "#CCC") for n in G.nodes]
    labels = {n: G.nodes[n].get("label", n) for n in G.nodes}

    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=2, seed=42)
    nx.draw(G, pos, labels=labels, node_color=node_colors, node_size=2000,
            font_size=9, font_weight="bold", edge_color="#AAA", width=2)

    edge_labels = {(u, v): d["relation"] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)

    plt.title("Living Intelligence Playground")
    plt.tight_layout()

    if output_file:
        plt.savefig(output_file, dpi=150)
        print(f"  Saved: {output_file}")
    else:
        plt.show()


# ── CLI ────────────────────────────────────────────────────────────────────

def cmd_explore(args):
    """Explore concepts by type."""
    pg = Playground()
    for t in args.types:
        pg.add_by_type(t, limit=10)
    pg.generate_patterns()
    print(pg.summary())


def cmd_experiment(args):
    """Run a hypothesis experiment."""
    pg = Playground()
    for cid in args.concepts:
        result = pg.add(cid)
        if not result:
            print(f"  Warning: '{cid}' not found in ontology")

    if not pg.active:
        print("  No valid concepts. Use IDs like BE, QUARTZ, SPIRAL")
        return

    pg.generate_patterns()
    print(f"\n  Experiment: {' + '.join(c.id for c in pg.active)}")
    print(f"  {pg.summary()}\n")

    history = pg.run_experiment(steps=args.steps)

    print(f"  {'Step':>4}  {'Synergy':>10}  {'Wind':>6}  {'Temp':>6}  Energies")
    print(f"  {'─'*4}  {'─'*10}  {'─'*6}  {'─'*6}  {'─'*30}")
    for h in history:
        energies = " ".join(f"{k}={v:.3f}" for k, v in h["concept_energies"].items())
        print(f"  {h['step']:>4}  {h['synergy']:>10.4f}  {h['env']['wind']:>6.2f}  {h['env']['temperature']:>6.1f}  {energies}")

    final = history[-1]
    print(f"\n  Final synergy: {final['synergy']}")
    print(f"  Growth: {((final['synergy'] / max(history[0]['synergy'], 0.001)) - 1) * 100:.1f}%")

    triggered = pg.apply_rules()
    if triggered:
        print(f"\n  Triggered rules:")
        for r in triggered:
            print(f"    {' + '.join(r['conditions'])} -> {r['result']}")


def cmd_rules(args):
    """Apply rules engine to concept IDs."""
    triggered = apply_rules(args.concepts)
    if triggered:
        print(f"\n  {len(triggered)} rule(s) triggered:\n")
        for r in triggered:
            print(f"  {' + '.join(r['conditions'])} -> {r['result']}")
    else:
        print(f"\n  No rules triggered for: {', '.join(args.concepts)}")
        print("  Rules need exact IDs. Try: BE HEX phi")


def cmd_optimize(args):
    """Find optimal concept combinations."""
    pg = Playground()
    types = args.type if args.type else None

    print(f"\n  Optimizing {'all types' if not types else ' + '.join(types)}...")
    print(f"  Combo size: {args.size}, Top: {args.top}\n")

    results = pg.optimize(pool_types=types, top_n=args.top, combo_size=args.size)

    for i, (combo, score) in enumerate(results, 1):
        names = []
        for cid in combo:
            c = pg.ontology.get(cid)
            names.append(f"{c.emoji}{c.name}" if c else cid)
        print(f"  {i}. {score:>8.4f}  {' + '.join(names)}")

        # Check if this combo triggers any rules
        triggered = apply_rules(combo)
        for r in triggered:
            print(f"              -> {r['result']}")


def cmd_visualize(args):
    """Visualize concept graph."""
    pg = Playground()
    for cid in args.concepts:
        pg.add(cid)
    if not pg.active:
        print("  No valid concepts.")
        return
    visualize(pg, output_file=args.output)


def main():
    parser = argparse.ArgumentParser(
        description="Living Intelligence — Innovation Playground",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/playground.py explore animal crystal
  python scripts/playground.py experiment BE QUARTZ SPIRAL --steps 20
  python scripts/playground.py rules BE HEX phi
  python scripts/playground.py optimize --type animal crystal --top 5 --size 3
  python scripts/playground.py visualize BE OC HEX TORUS MY --output graph.png
        """,
    )
    sub = parser.add_subparsers(dest="command")

    p_explore = sub.add_parser("explore", help="Explore concepts by type")
    p_explore.add_argument("types", nargs="+", help="Ontology types to explore")

    p_exp = sub.add_parser("experiment", help="Run a hypothesis experiment")
    p_exp.add_argument("concepts", nargs="+", help="Concept IDs")
    p_exp.add_argument("--steps", type=int, default=20, help="Simulation steps")

    p_rules = sub.add_parser("rules", help="Apply rules to concept IDs")
    p_rules.add_argument("concepts", nargs="+", help="Concept IDs or constants")

    p_opt = sub.add_parser("optimize", help="Find best concept combos")
    p_opt.add_argument("--type", nargs="+", help="Ontology types to search")
    p_opt.add_argument("--top", type=int, default=5, help="Top N results")
    p_opt.add_argument("--size", type=int, default=3, help="Combo size")

    p_vis = sub.add_parser("visualize", help="Visualize concept graph")
    p_vis.add_argument("concepts", nargs="+", help="Concept IDs")
    p_vis.add_argument("--output", help="Save to file instead of showing")

    args = parser.parse_args()

    if args.command == "explore":
        cmd_explore(args)
    elif args.command == "experiment":
        cmd_experiment(args)
    elif args.command == "rules":
        cmd_rules(args)
    elif args.command == "optimize":
        cmd_optimize(args)
    elif args.command == "visualize":
        cmd_visualize(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
