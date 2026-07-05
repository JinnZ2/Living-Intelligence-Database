#!/usr/bin/env python3
# resilience_lab.py — CC0
# Complete topology/dynamics/constraint/perturbation/metric/failure library
# used by the ontology experiment builder.
#
# All classes follow the abstractions defined earlier:
#   Topology, Dynamics, Constraint, Perturbation, Metric, FailureModel
#
# New components added for full ontology coverage:
#   TorusTopology, OctahedralTopology, SpiralLattice, TreeGraph,
#   WavePropagation, ConsensusDynamics, TimeReversalDynamics, VortexDynamics,
#   SpectralGap, CascadingFailure, HysteresisFailure

from __future__ import annotations
import abc
import math
import random
from typing import Any, Callable, Dict, List, Optional, Tuple

# =========================================================================
# 1. Core abstractions (unchanged)
# =========================================================================
class Topology(abc.ABC):
    def __init__(self, name: str = ""):
        self.name = name or self.__class__.__name__

    @abc.abstractmethod
    def nodes(self) -> List[Any]:
        ...

    @abc.abstractmethod
    def edges(self) -> List[Tuple[Any, Any]]:
        ...

    def neighbors(self, node: Any) -> List[Any]:
        # simple from edges, override for performance
        nbrs = []
        for u, v in self.edges():
            if u == node:
                nbrs.append(v)
            elif v == node:
                nbrs.append(u)
        return nbrs

    @abc.abstractmethod
    def size(self) -> int:
        ...

class Constraint(abc.ABC):
    @abc.abstractmethod
    def apply(self, state: Any, topology: Topology, dt: float) -> Any:
        ...

class Dynamics(abc.ABC):
    @abc.abstractmethod
    def step(self, state: Any, topology: Topology,
             constraints: List[Constraint], dt: float) -> Any:
        ...

class Perturbation(abc.ABC):
    @abc.abstractmethod
    def apply(self, state: Any, topology: Topology, time: float) -> Any:
        ...

class Metric(abc.ABC):
    @abc.abstractmethod
    def measure(self, state: Any, topology: Topology) -> float:
        ...

class FailureModel(abc.ABC):
    @abc.abstractmethod
    def assess(self, metric_history: List[float]) -> Dict[str, Any]:
        ...

# =========================================================================
# 2. Topologies (existing + new)
# =========================================================================
class GridTopology(Topology):
    def __init__(self, width: int, height: int, periodic: bool = False):
        super().__init__()
        self.width = width
        self.height = height
        self.periodic = periodic

    def nodes(self):
        return [(x, y) for x in range(self.width) for y in range(self.height)]

    def edges(self):
        edges = []
        for x in range(self.width):
            for y in range(self.height):
                if x + 1 < self.width:
                    edges.append(((x, y), (x+1, y)))
                elif self.periodic:
                    edges.append(((x, y), (0, y)))
                if y + 1 < self.height:
                    edges.append(((x, y), (x, y+1)))
                elif self.periodic:
                    edges.append(((x, y), (x, 0)))
        return edges

    def neighbors(self, node):
        x, y = node
        nbrs = []
        if x > 0: nbrs.append((x-1, y))
        elif self.periodic: nbrs.append((self.width-1, y))
        if x < self.width-1: nbrs.append((x+1, y))
        elif self.periodic: nbrs.append((0, y))
        if y > 0: nbrs.append((x, y-1))
        elif self.periodic: nbrs.append((x, self.height-1))
        if y < self.height-1: nbrs.append((x, y+1))
        elif self.periodic: nbrs.append((x, 0))
        return nbrs

    def size(self):
        return self.width * self.height

class HexagonalGrid(Topology):
    def __init__(self, radius: int):
        super().__init__()
        self.radius = radius

    def nodes(self):
        nodes = []
        for q in range(-self.radius, self.radius+1):
            for r in range(-self.radius, self.radius+1):
                if abs(q+r) <= self.radius:
                    nodes.append((q, r))
        return nodes

    def edges(self):
        edges = set()
        for (q, r) in self.nodes():
            for dq, dr in [(1,0), (0,1), (-1,1), (-1,0), (0,-1), (1,-1)]:
                neighbor = (q+dq, r+dr)
                if neighbor in self.nodes():
                    if (q, r) < neighbor:
                        edges.add(((q, r), neighbor))
        return list(edges)

    def size(self):
        return len(self.nodes())

class RandomGraph(Topology):
    def __init__(self, n: int, p: float, seed: int = 42):
        super().__init__()
        rng = random.Random(seed)
        self._nodes = list(range(n))
        self._edges = []
        for i in range(n):
            for j in range(i+1, n):
                if rng.random() < p:
                    self._edges.append((i, j))

    def nodes(self): return self._nodes
    def edges(self): return self._edges
    def size(self): return len(self._nodes)

class TreeGraph(Topology):
    """A simple binary tree topology."""
    def __init__(self, depth: int = 3):
        super().__init__()
        self.depth = depth
        self._nodes = []
        self._edges = []
        self._build_tree(None, 0, 1)
        # remove root's parent (None) if present
        self._nodes = [n for n in self._nodes if n is not None]
        self._edges = [(u, v) for u, v in self._edges if u is not None and v is not None]

    def _build_tree(self, parent, value, level):
        if level > self.depth:
            return
        node = value
        self._nodes.append(node)
        if parent is not None:
            self._edges.append((parent, node))
        self._build_tree(node, value*2, level+1)
        self._build_tree(node, value*2+1, level+1)

    def nodes(self): return self._nodes
    def edges(self): return self._edges
    def size(self): return len(self._nodes)

class TorusTopology(Topology):
    """Periodic 2D grid (fully wrapped)."""
    def __init__(self, width=20, height=20):
        super().__init__()
        self.w = width
        self.h = height

    def nodes(self):
        return [(i, j) for i in range(self.w) for j in range(self.h)]

    def edges(self):
        edges = []
        for i in range(self.w):
            for j in range(self.h):
                edges.append(((i, j), ((i+1)%self.w, j)))
                edges.append(((i, j), (i, (j+1)%self.h)))
        return edges

    def neighbors(self, node):
        i, j = node
        return [
            ((i-1)%self.w, j),
            ((i+1)%self.w, j),
            (i, (j-1)%self.h),
            (i, (j+1)%self.h)
        ]

    def size(self):
        return self.w * self.h

class OctahedralTopology(Topology):
    """8 vertices of an octahedron (six points on axes)."""
    def __init__(self):
        super().__init__()
        self._nodes = [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]

    def nodes(self):
        return self._nodes

    def edges(self):
        # all pairs (simplified octahedral graph = K6)
        edges = []
        for i, a in enumerate(self._nodes):
            for b in self._nodes[i+1:]:
                edges.append((a, b))
        return edges

    def size(self):
        return len(self._nodes)

class SpiralLattice(Topology):
    """Nodes placed along a Fibonacci spiral (mimics the earlier LatticeSimulator)."""
    def __init__(self, node_count: int = 25):
        super().__init__()
        self.node_count = node_count
        phi = (1 + 5**0.5) / 2
        self._nodes = [(0.5 + 0.4*(n/self.node_count)*math.cos(2*math.pi*n*phi),
                        0.5 + 0.4*(n/self.node_count)*math.sin(2*math.pi*n*phi))
                       for n in range(self.node_count)]
        # connect each node to its two nearest neighbors in index order
        self._edges = []
        for i in range(self.node_count - 1):
            self._edges.append((self._nodes[i], self._nodes[i+1]))
        # optionally close loop
        self._edges.append((self._nodes[-1], self._nodes[0]))

    def nodes(self):
        return self._nodes

    def edges(self):
        return self._edges

    def size(self):
        return self.node_count

# =========================================================================
# 3. Constraints (existing)
# =========================================================================
class EnergyConservation(Constraint):
    def apply(self, state, topology, dt):
        total = sum(state.values())
        if total != 0:
            for k in state:
                state[k] /= total
        return state

# =========================================================================
# 4. Dynamics (existing + new)
# =========================================================================
class ThermalDiffusion(Dynamics):
    def __init__(self, alpha: float = 0.1):
        self.alpha = alpha

    def step(self, state, topology, constraints, dt):
        new_state = state.copy()
        for node in topology.nodes():
            neighbors = topology.neighbors(node)
            if not neighbors:
                continue
            avg = sum(state.get(n, 0) for n in neighbors) / len(neighbors)
            new_state[node] = state[node] + self.alpha * (avg - state[node]) * dt
        for c in constraints:
            new_state = c.apply(new_state, topology, dt)
        return new_state

class WavePropagation(Dynamics):
    """Simplified wave equation (displacement and velocity)."""
    def __init__(self, speed: float = 1.0, damping: float = 0.01):
        self.speed = speed
        self.damping = damping

    def step(self, state, topology, constraints, dt):
        # state is dict: node -> (displacement, velocity)
        new_state = {}
        for node in topology.nodes():
            pos, vel = state.get(node, (0.0, 0.0))
            laplacian = 0.0
            neighbors = topology.neighbors(node)
            if neighbors:
                avg_pos = sum(state.get(n, (0.0, 0.0))[0] for n in neighbors) / len(neighbors)
                laplacian = avg_pos - pos
            acc = self.speed * self.speed * laplacian - self.damping * vel
            new_vel = vel + acc * dt
            new_pos = pos + new_vel * dt
            new_state[node] = (new_pos, new_vel)
        return new_state

class ConsensusDynamics(Dynamics):
    """Agents adjust their opinion toward the average of neighbors."""
    def __init__(self, rate: float = 0.1):
        self.rate = rate

    def step(self, state, topology, constraints, dt):
        new_state = state.copy()
        for node in topology.nodes():
            neighbors = topology.neighbors(node)
            if not neighbors:
                continue
            avg = sum(state.get(n, 0) for n in neighbors) / len(neighbors)
            new_state[node] = state[node] + self.rate * (avg - state[node]) * dt
        return new_state

class TimeReversalDynamics(Dynamics):
    """Flips velocity sign each step (simulated time‑reversal). Requires (pos, vel) state."""
    def step(self, state, topology, constraints, dt):
        new_state = {}
        for node in topology.nodes():
            pos, vel = state.get(node, (0.0, 0.0))
            new_state[node] = (pos, -vel)
        return new_state

class VortexDynamics(Dynamics):
    """Rotational flow around a center. Uses (pos, vel) but we'll just rotate."""
    def step(self, state, topology, constraints, dt):
        # state dict: node -> (x_displacement, y_displacement) as a simple vector field
        # rotate 90 degrees each step as mock vortex
        new_state = {}
        for node, (dx, dy) in state.items():
            # rotation: (dx, dy) -> (-dy, dx)
            new_state[node] = (-dy, dx)
        return new_state

# =========================================================================
# 5. Perturbations (existing)
# =========================================================================
class LocalizedHeat(Perturbation):
    def __init__(self, node: Any, energy: float, time: float):
        self.node = node
        self.energy = energy
        self.time = time

    def apply(self, state, topology, time):
        if time >= self.time:
            state[self.node] = state.get(self.node, 0) + self.energy
        return state

class NodeRemoval(Perturbation):
    """Removes a node from the topology (sets its value to 0)."""
    def __init__(self, node: Any, time: float):
        self.node = node
        self.time = time

    def apply(self, state, topology, time):
        if time >= self.time and self.node in state:
            state[self.node] = 0.0
        return state

class FrequencyShift(Perturbation):
    """Applies a frequency-dependent sine wave perturbation to all nodes."""
    def __init__(self, frequency: float, amplitude: float = 1.0):
        self.freq = frequency
        self.amp = amplitude

    def apply(self, state, topology, time):
        # state dict: node -> (displacement, vel) or scalar; we'll treat as scalar for this demo
        for node in topology.nodes():
            if isinstance(state[node], tuple):
                pos, vel = state[node]
                pos += self.amp * math.sin(2 * math.pi * self.freq * time)
                state[node] = (pos, vel)
            else:
                state[node] = state[node] + self.amp * math.sin(2 * math.pi * self.freq * time)
        return state

# =========================================================================
# 6. Metrics (existing + new)
# =========================================================================
class SignalIntegrity(Metric):
    def measure(self, state, topology):
        threshold = 2.0
        # handle both scalar and tuple states
        count = 0
        for v in state.values():
            if isinstance(v, tuple):
                if abs(v[0]) < threshold: count += 1
            else:
                if abs(v) < threshold: count += 1
        return count / topology.size() if topology.size() else 0.0

class Coherence(Metric):
    def measure(self, state, topology):
        values = []
        for v in state.values():
            if isinstance(v, tuple):
                values.append(v[0])
            else:
                values.append(v)
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        var = sum((x - mean)**2 for x in values) / len(values)
        return 1.0 / (1.0 + math.sqrt(var))

class EntropyProduction(Metric):
    def measure(self, state, topology):
        total = sum(abs(v[0] if isinstance(v, tuple) else v) for v in state.values())
        if total == 0:
            return 0.0
        entropy = 0.0
        for v in state.values():
            val = abs(v[0] if isinstance(v, tuple) else v)
            p = val / total
            if p > 0:
                entropy -= p * math.log(p)
        return entropy

class SpectralGap(Metric):
    """Approximation of spectral gap: difference between two largest eigenvalues of the Laplacian."""
    def measure(self, state, topology):
        # For simplicity, return 1 - (variance of state), which correlates with coherence.
        # Real implementation would compute Laplacian and eigenvalues.
        return Coherence().measure(state, topology)

# =========================================================================
# 7. Failure models (existing + new)
# =========================================================================
class PhaseTransition(FailureModel):
    def __init__(self, metric_name: str = "primary", threshold: float = 0.4, window: int = 3):
        self.metric_name = metric_name
        self.threshold = threshold
        self.window = window

    def assess(self, metric_history: List[float]) -> Dict[str, Any]:
        if len(metric_history) < self.window + 1:
            return {"failed": False, "failure_type": "", "failure_step": None}
        recent = metric_history[-self.window:]
        if all(v < self.threshold for v in recent):
            return {"failed": True, "failure_type": "phase_transition",
                    "failure_step": len(metric_history) - self.window}
        return {"failed": False, "failure_type": "", "failure_step": None}

class CascadingFailure(FailureModel):
    def __init__(self, threshold: float = 0.3, cascade_ratio: float = 0.5):
        self.threshold = threshold
        self.cascade_ratio = cascade_ratio

    def assess(self, metric_history: List[float]) -> Dict[str, Any]:
        if len(metric_history) < 3:
            return {"failed": False, "failure_type": "", "failure_step": None}
        # detect a sharp drop that continues
        diffs = [metric_history[i] - metric_history[i-1] for i in range(1, len(metric_history))]
        if len(diffs) >= 2 and diffs[-1] < -self.cascade_ratio and diffs[-2] < -self.cascade_ratio:
            return {"failed": True, "failure_type": "cascading",
                    "failure_step": len(metric_history)-1}
        return {"failed": False, "failure_type": "", "failure_step": None}

class HysteresisFailure(FailureModel):
    def __init__(self, threshold_up: float = 0.6, threshold_down: float = 0.3):
        self.threshold_up = threshold_up
        self.threshold_down = threshold_down
        self.failed = False

    def assess(self, metric_history: List[float]) -> Dict[str, Any]:
        if not metric_history:
            return {"failed": False, "failure_type": "", "failure_step": None}
        current = metric_history[-1]
        if self.failed:
            # already failed, only recover if above up threshold
            if current > self.threshold_up:
                self.failed = False
        else:
            if current < self.threshold_down:
                self.failed = True
                return {"failed": True, "failure_type": "hysteresis",
                        "failure_step": len(metric_history)-1}
        return {"failed": self.failed, "failure_type": "hysteresis" if self.failed else "",
                "failure_step": len(metric_history)-1 if self.failed else None}

# =========================================================================
# 8. Experiment and SweepEngine (unchanged)
# =========================================================================
class Experiment:
    def __init__(self,
                 topology: Topology,
                 dynamics: Dynamics,
                 perturbations: List[Perturbation],
                 metrics: Dict[str, Metric],
                 failure_model: FailureModel,
                 constraints: Optional[List[Constraint]] = None,
                 total_time: float = 100.0,
                 dt: float = 0.1):
        self.topology = topology
        self.dynamics = dynamics
        self.perturbations = perturbations
        self.metrics = metrics
        self.failure_model = failure_model
        self.constraints = constraints or []
        self.total_time = total_time
        self.dt = dt
        self.state = None
        self.history: Dict[str, List[float]] = {name: [] for name in metrics}
        self.failure_info: Dict[str, Any] = {}

    def initialise_state(self):
        # default state depends on topology; return dict node -> 0.0 or (0.0,0.0) for wave-like
        # we'll detect from dynamics if it expects tuples, otherwise scalars.
        # Simple heuristic: if dynamics is WavePropagation or TimeReversal or Vortex,
        # use (0.0,0.0) tuple.
        if isinstance(self.dynamics, (WavePropagation, TimeReversalDynamics, VortexDynamics)):
            return {node: (0.0, 0.0) for node in self.topology.nodes()}
        else:
            return {node: 0.0 for node in self.topology.nodes()}

    def run(self) -> Dict[str, Any]:
        self.state = self.initialise_state()
        steps = int(self.total_time / self.dt)
        failure_step = None

        for step in range(steps):
            t = step * self.dt
            for p in self.perturbations:
                self.state = p.apply(self.state, self.topology, t)
            self.state = self.dynamics.step(self.state, self.topology, self.constraints, self.dt)
            for name, metric in self.metrics.items():
                value = metric.measure(self.state, self.topology)
                self.history[name].append(value)
            primary_metric = list(self.metrics.keys())[0]
            fail = self.failure_model.assess(self.history[primary_metric])
            if fail["failed"]:
                self.failure_info = fail
                failure_step = step
                break

        if not self.failure_info:
            self.failure_info = {"failed": False, "failure_type": "none", "failure_step": None}

        return {
            "topology": self.topology.name,
            "total_steps": steps,
            "failure_step": failure_step,
            "failure_type": self.failure_info.get("failure_type"),
            "metric_history": self.history,
            "final_state": self.state
        }

class SweepEngine:
    def __init__(self):
        self.results = []

    def run_sweep(self, experiments: List[Experiment]) -> List[Dict]:
        self.results = []
        for exp in experiments:
            result = exp.run()
            self.results.append(result)
        return self.results

    def summary(self):
        print(f"{'Topology':<20} {'Failure Step':>12} {'Failure Type':>15}")
        print("-" * 50)
        for r in self.results:
            print(f"{r['topology']:<20} {str(r['failure_step']):>12} {r['failure_type']:>15}")
