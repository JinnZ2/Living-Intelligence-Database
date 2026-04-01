#!/usr/bin/env python3
"""
Living Intelligence Database — Maximum Likelihood Estimation Toolkit

Statistical tools for analyzing sequences and transition patterns
in the ontology. Provides Gaussian MLE, Markov chain transition
matrices, mixed-type sequence analysis, log-likelihood scoring,
and continuous-time trend estimation.

Usage:
    # Fit Gaussian to a sequence
    python scripts/mle.py gaussian 1.2 2.3 1.8 2.0 2.5

    # Fit Markov chain transitions
    python scripts/mle.py markov A B A A B B A B

    # Log-likelihood score for element combinations
    python scripts/mle.py score BE QUARTZ SPIRAL

    # As a Python library
    from scripts.mle import mle_gaussian, mle_markov, log_likelihood_score
"""

import json
import sys
import argparse
import numpy as np
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


# ── Gaussian MLE ───────────────────────────────────────────────────────────

def mle_gaussian(sequence):
    """
    MLE for mean and variance of independent Gaussian observations.

    Args:
        sequence: array-like of numeric values

    Returns:
        (mu_hat, sigma_hat): MLE estimates of mean and std
    """
    x = np.asarray(sequence, dtype=float)
    mu_hat = np.mean(x)
    sigma_hat = np.std(x, ddof=0)  # MLE uses N, not N-1
    return mu_hat, sigma_hat


# ── Continuous-Time Gaussian MLE ───────────────────────────────────────────

def mle_gaussian_continuous(times, values):
    """
    MLE for Gaussian process with time-dependent samples.
    Fits both static statistics and a linear trend.

    Args:
        times: array of timestamps
        values: array of observed values

    Returns:
        (mu, sigma, slope, intercept)
    """
    t = np.asarray(times, dtype=float)
    v = np.asarray(values, dtype=float)
    mu_hat = np.mean(v)
    sigma_hat = np.std(v, ddof=0)

    # Linear trend via least squares
    A = np.vstack([t, np.ones(len(t))]).T
    slope, intercept = np.linalg.lstsq(A, v, rcond=None)[0]

    return mu_hat, sigma_hat, slope, intercept


# ── Markov Chain MLE ───────────────────────────────────────────────────────

def mle_markov(sequence, states=None):
    """
    MLE for first-order Markov chain transition probabilities.

    Args:
        sequence: list of state observations
        states: optional list of all possible states

    Returns:
        (states, transition_matrix): state labels and NxN probability matrix
    """
    if states is None:
        states = sorted(set(sequence))
    n_states = len(states)
    state_to_idx = {s: i for i, s in enumerate(states)}

    counts = np.zeros((n_states, n_states))
    for prev, curr in zip(sequence[:-1], sequence[1:]):
        if prev in state_to_idx and curr in state_to_idx:
            counts[state_to_idx[prev], state_to_idx[curr]] += 1

    # Normalize rows
    probs = np.zeros_like(counts)
    for i in range(n_states):
        row_sum = counts[i].sum()
        probs[i] = counts[i] / row_sum if row_sum > 0 else 1.0 / n_states

    return states, probs


# ── Mixed-Type Sequence MLE ────────────────────────────────────────────────

def mle_mixed(sequence):
    """
    MLE for sequences with both categorical and numeric components.

    Args:
        sequence: list of (category, numeric_value) tuples

    Returns:
        (states, transition_matrix, numeric_summary)
    """
    cat_values = [s[0] for s in sequence]
    num_values = [s[1] for s in sequence]

    # Categorical transitions
    states, probs = mle_markov(cat_values)

    # Numeric statistics per category
    category_stats = defaultdict(list)
    for cat, num in sequence:
        category_stats[cat].append(num)

    numeric_summary = {}
    for cat, nums in category_stats.items():
        numeric_summary[cat] = {
            "mean": float(np.mean(nums)),
            "std": float(np.std(nums, ddof=0)),
            "count": len(nums),
        }

    return states, probs, numeric_summary


# ── Log-Likelihood Scoring ─────────────────────────────────────────────────

def log_likelihood_score(energy_profiles, compatibility_matrix=None):
    """
    Log-likelihood score for a combination of elements.
    High resonance = high probability of stability.

    Args:
        energy_profiles: list of (name, energy_profile) tuples
        compatibility_matrix: optional dict of (type_a, type_b) -> coefficient

    Returns:
        log_likelihood: float score (higher = more stable combination)
    """
    if len(energy_profiles) < 2:
        return 0.0

    log_l = 0.0
    for (name_a, energy_a), (name_b, energy_b) in combinations(energy_profiles, 2):
        resonance = (energy_a + energy_b) / 2.0
        log_l += np.log(max(resonance, 1e-9))

    return float(log_l)


# ── Sovereign Likelihood ──────────────────────────────────────────────────
#
# Standard MLE:  θ̂ = argmax Σ log P(xᵢ | θ)     — independent draws
# Sovereign MLE: θ̂ = argmax Σ log freq(xᵢ, xⱼ)  — coupled transitions
#
# The standard approach treats each element as an isolated observation and
# solves for the mean (μ̂). The sovereign approach treats each pair as a
# coupled transition and solves for the resonance peak.

def sovereign_likelihood(elements, env_entropy=0.5):
    """
    Coupling-aware log-likelihood for a pack of elements.
    Instead of ∏P(xᵢ), computes ∏freq(xᵢ → xⱼ | env).

    Args:
        elements: list of dicts with 'id', 'energy', 'type', 'resilience'
        env_entropy: environmental entropy (0=order, 1=chaos)

    Returns:
        dict with sovereign_ll, standard_ll, erasure, and per-pair details
    """
    if len(elements) < 2:
        return {"sovereign_ll": 0.0, "standard_ll": 0.0, "erasure": 0.0, "pairs": []}

    # Compatibility matrix
    compat_matrix = {
        ("harmonic", "harmonic"): 1.0, ("harmonic", "kinetic"): 0.7,
        ("harmonic", "radiant"): 0.8, ("harmonic", "chemical"): 0.5,
        ("kinetic", "kinetic"): 1.0, ("kinetic", "radiant"): 0.6,
        ("kinetic", "chemical"): 0.6, ("chemical", "chemical"): 1.0,
        ("chemical", "radiant"): 0.4, ("radiant", "radiant"): 1.0,
    }

    def compat(t1, t2):
        return compat_matrix.get((t1, t2), compat_matrix.get((t2, t1), 0.5))

    # Standard MLE: independent, averaged
    energies = [e["energy"] for e in elements]
    mu = np.mean(energies)
    sigma = np.std(energies, ddof=0) + 1e-9
    standard_ll = sum(
        -0.5 * np.log(2 * np.pi * sigma**2) - (e - mu)**2 / (2 * sigma**2)
        for e in energies
    )

    # Sovereign MLE: coupled transitions
    sovereign_ll = 0.0
    pairs = []
    for i, a in enumerate(elements):
        for j, b in enumerate(elements):
            if i >= j:
                continue
            # Transition frequency: compat × stress × energy_b
            c = compat(a["type"], b["type"])
            stress_a = np.exp(-env_entropy / (a["resilience"] * a["energy"]))
            stress_b = np.exp(-env_entropy / (b["resilience"] * b["energy"]))
            freq_ab = c * stress_a * b["energy"]
            freq_ba = c * stress_b * a["energy"]
            pair_ll = np.log(max(freq_ab, 1e-9)) + np.log(max(freq_ba, 1e-9))
            sovereign_ll += pair_ll
            pairs.append({
                "a": a["id"], "b": b["id"],
                "compatibility": round(c, 3),
                "freq_ab": round(freq_ab, 4),
                "freq_ba": round(freq_ba, 4),
                "pair_ll": round(pair_ll, 4),
            })

    # Erasure: how much information the standard MLE destroys
    # Measured as the gap between sovereign (coupled) and standard (independent)
    erasure = sovereign_ll - standard_ll

    return {
        "sovereign_ll": round(sovereign_ll, 4),
        "standard_ll": round(standard_ll, 4),
        "erasure": round(erasure, 4),
        "mu_hat": round(mu, 4),
        "sigma_hat": round(sigma, 4),
        "env_entropy": env_entropy,
        "pairs": pairs,
    }


def resonance_peak(elements, env_range=(0.0, 1.0), steps=100):
    """
    Find the environmental entropy where sovereign likelihood peaks.
    This is the resonance frequency — the environment state where
    the pack is maximally coupled.

    Standard MLE finds μ̂ (static center).
    Sovereign MLE finds env* (dynamic resonance peak).

    Args:
        elements: list of element dicts
        env_range: (min_entropy, max_entropy) to search
        steps: resolution of the search

    Returns:
        dict with optimal_entropy, peak_ll, and the full curve
    """
    entropies = np.linspace(env_range[0], env_range[1], steps)
    curve = []

    for entropy in entropies:
        result = sovereign_likelihood(elements, env_entropy=entropy)
        curve.append((round(float(entropy), 4), result["sovereign_ll"]))

    # Find peak
    best_idx = max(range(len(curve)), key=lambda i: curve[i][1])
    optimal_entropy = curve[best_idx][0]
    peak_ll = curve[best_idx][1]

    return {
        "optimal_entropy": optimal_entropy,
        "peak_ll": round(peak_ll, 4),
        "curve": curve,
    }


def load_elements_for_mle(entity_ids):
    """Load ontology entities as element dicts for sovereign MLE."""
    ontology_dir = ROOT / "ontology"
    type_map = {
        "animal": "kinetic", "plant": "chemical", "crystal": "harmonic",
        "energy": "radiant", "plasma": "radiant", "shape": "harmonic",
        "temporal": "harmonic",
    }
    elements = []

    for layer_dir in ontology_dir.iterdir():
        if not layer_dir.is_dir():
            continue
        for filepath in layer_dir.glob("*.json"):
            try:
                with open(filepath) as f:
                    data = json.load(f)
                if not isinstance(data, dict) or data.get("id") not in entity_ids:
                    continue

                efficiency = 0.9
                core = data.get("core_attributes", {})
                if isinstance(core.get("efficiency_factor"), (int, float)):
                    efficiency = core["efficiency_factor"]
                for p in data.get("patterns", []):
                    if isinstance(p.get("efficiency_factor"), (int, float)):
                        efficiency = max(efficiency, p["efficiency_factor"])

                ont = data.get("ontology", "energy")
                elements.append({
                    "id": data["id"],
                    "name": data.get("name", "?"),
                    "energy": efficiency,
                    "type": type_map.get(ont, "harmonic"),
                    "resilience": efficiency * 0.95,
                })
            except Exception:
                continue

    return elements


def score_ontology_combo(entity_ids):
    """
    Score a combination of ontology entities by log-likelihood.

    Args:
        entity_ids: list of entity ID strings

    Returns:
        (score, element_details)
    """
    ontology_dir = ROOT / "ontology"
    profiles = []

    for layer_dir in ontology_dir.iterdir():
        if not layer_dir.is_dir():
            continue
        for filepath in layer_dir.glob("*.json"):
            try:
                with open(filepath) as f:
                    data = json.load(f)
                if not isinstance(data, dict) or data.get("id") not in entity_ids:
                    continue

                # Extract efficiency
                efficiency = 0.9
                core = data.get("core_attributes", {})
                if isinstance(core.get("efficiency_factor"), (int, float)):
                    efficiency = core["efficiency_factor"]
                for p in data.get("patterns", []):
                    if isinstance(p.get("efficiency_factor"), (int, float)):
                        efficiency = max(efficiency, p["efficiency_factor"])

                profiles.append((data["id"], efficiency))
            except Exception:
                continue

    score = log_likelihood_score(profiles)
    return score, profiles


# ── V2: Advanced Field Analysis ───────────────────────────────────────────
#
# Non-Gaussian tools for systems where the bell curve is the wrong model.

def mle_powerlaw(sequence):
    """
    MLE for power-law scaling exponent alpha: P(x) ~ x^(-alpha).
    Low alpha = heavy tail = frequent high-energy outliers that
    a Gaussian would erase as "noise."
    """
    x = np.asarray(sequence, dtype=float)
    x = x[x > 0]
    x_min = np.min(x)
    n = len(x)
    alpha_hat = 1 + n / np.sum(np.log(x / x_min))
    return round(alpha_hat, 4), round(x_min, 4)


def estimate_hurst(sequence):
    """
    Rescaled Range (R/S) analysis for long-term memory.
    H < 0.5: anti-persistent (pulled to mean).
    H = 0.5: random walk (no memory — Markov assumption).
    H > 0.5: persistent (momentum carries — Markov fails).
    """
    x = np.asarray(sequence, dtype=float)
    if len(x) < 4:
        return 0.5
    y = np.cumsum(x - np.mean(x))
    r = np.max(y) - np.min(y)
    s = np.std(x, ddof=1)
    if s == 0:
        return 0.5
    return round(np.log(r / s) / np.log(len(x)), 4)


def detect_change_points(sequence, penalty=3.0):
    """
    Detect regime shifts via CUSUM (no external dependencies).
    These are the entropy events — phase boundaries where
    linear prediction breaks.
    """
    x = np.asarray(sequence, dtype=float)
    n = len(x)
    if n < 4:
        return []
    cusum = np.cumsum(x - np.mean(x))
    threshold = penalty * np.std(x)
    above = np.abs(cusum) > threshold
    return [i for i in range(1, n) if above[i] and not above[i - 1]]


def solve_mixture(sequence, n_components=2):
    """
    Gaussian mixture via EM algorithm (no sklearn dependency).
    Finds the resonance peaks that a single Gaussian averages away.
    """
    x = np.asarray(sequence, dtype=float)
    n = len(x)
    means = np.linspace(np.min(x), np.max(x), n_components)
    stds = np.full(n_components, np.std(x))
    weights = np.full(n_components, 1.0 / n_components)

    for _ in range(100):
        resp = np.zeros((n, n_components))
        for k in range(n_components):
            resp[:, k] = weights[k] * np.exp(-0.5 * ((x - means[k]) / stds[k]) ** 2) / (stds[k] + 1e-9)
        resp_sum = resp.sum(axis=1, keepdims=True)
        resp_sum[resp_sum == 0] = 1e-9
        resp /= resp_sum
        for k in range(n_components):
            nk = resp[:, k].sum()
            if nk < 1e-9:
                continue
            weights[k] = nk / n
            means[k] = (resp[:, k] * x).sum() / nk
            stds[k] = np.sqrt((resp[:, k] * (x - means[k]) ** 2).sum() / nk) + 1e-9

    return {
        "means": [round(m, 4) for m in means],
        "stds": [round(s, 4) for s in stds],
        "weights": [round(w, 4) for w in weights],
    }


def estimate_hysteresis(load_sequence, temp_sequence):
    """
    Thermal memory: area of the load-temperature hysteresis loop.
    High area = system holds entropy longer than environment dissipates.
    """
    load = np.asarray(load_sequence, dtype=float)
    temp = np.asarray(temp_sequence, dtype=float)
    return round(float(np.abs(np.trapezoid(temp, x=load))), 4)


def check_cascading_risk(node_states, threshold=0.5):
    """
    Cascading failure risk across coupled systems.
    Returns stress level and failing nodes.
    """
    total_stress = 0.0
    failing = []
    for node, efficiency in node_states.items():
        if efficiency < threshold:
            total_stress += (threshold - efficiency) * 1.5
            failing.append((node, round(efficiency, 3)))
    status = "HIGH RISK — CASCADE IMMINENT" if total_stress > 1.0 else "ABSORPTIVE"
    return {"total_stress": round(total_stress, 4), "status": status, "failing_nodes": failing}


def fisher_distance(mu1, sigma1, mu2, sigma2):
    """
    Fisher-Rao distance between two Gaussians on the information manifold.
    Euclidean distance ignores probability curvature. This doesn't.
    """
    d_mu = mu2 - mu1
    d_sigma = np.log(sigma2) - np.log(sigma1)
    return round(float(np.sqrt(d_mu ** 2 / sigma1 ** 2 + 2 * d_sigma ** 2)), 4)


# ── CLI ────────────────────────────────────────────────────────────────────

def cmd_gaussian(args):
    """Fit Gaussian MLE."""
    values = [float(v) for v in args.values]
    mu, sigma = mle_gaussian(values)
    print(f"\n  Gaussian MLE (n={len(values)}):")
    print(f"  Mean:  {mu:.4f}")
    print(f"  Std:   {sigma:.4f}")
    print(f"  Var:   {sigma**2:.4f}")


def cmd_markov(args):
    """Fit Markov chain MLE."""
    states, probs = mle_markov(args.states)
    print(f"\n  Markov Chain MLE (n={len(args.states)}, states={states}):\n")
    header = f"{'From/To':>10}" + "".join(f"{s:>10}" for s in states)
    print(header)
    print("-" * len(header))
    for i, s_from in enumerate(states):
        row = f"{s_from:>10}" + "".join(f"{probs[i,j]:>10.3f}" for j in range(len(states)))
        print(row)


def cmd_score(args):
    """Score ontology element combination."""
    score, profiles = score_ontology_combo(args.ids)
    print(f"\n  Log-Likelihood Score: {score:.4f}\n")
    for name, energy in profiles:
        print(f"  {name:>15}: energy={energy:.3f}")
    if not profiles:
        print("  No matching entities found.")


def main():
    parser = argparse.ArgumentParser(description="MLE Toolkit for Living Intelligence")
    sub = parser.add_subparsers(dest="command")

    p_gauss = sub.add_parser("gaussian", help="Gaussian MLE for a sequence")
    p_gauss.add_argument("values", nargs="+", help="Numeric values")

    p_markov = sub.add_parser("markov", help="Markov chain transition MLE")
    p_markov.add_argument("states", nargs="+", help="State sequence")

    p_score = sub.add_parser("score", help="Log-likelihood score for entity combo")
    p_score.add_argument("ids", nargs="+", help="Entity IDs from ontology")

    p_erasure = sub.add_parser("erasure", help="Compare standard vs sovereign MLE")
    p_erasure.add_argument("ids", nargs="+", help="Entity IDs from ontology")
    p_erasure.add_argument("--entropy", type=float, default=0.5, help="Environment entropy (0-1)")

    p_resonance = sub.add_parser("resonance", help="Find resonance peak across entropy range")
    p_resonance.add_argument("ids", nargs="+", help="Entity IDs from ontology")

    # V2 commands
    p_powerlaw = sub.add_parser("powerlaw", help="Power-law exponent (heavy tails)")
    p_powerlaw.add_argument("values", nargs="+", help="Positive numeric values")

    p_hurst = sub.add_parser("hurst", help="Hurst exponent (fractal memory)")
    p_hurst.add_argument("values", nargs="+", help="Numeric sequence (10+ values recommended)")

    p_mixture = sub.add_parser("mixture", help="Gaussian mixture decomposition")
    p_mixture.add_argument("values", nargs="+", help="Numeric values")
    p_mixture.add_argument("--components", type=int, default=2, help="Number of components")

    p_change = sub.add_parser("change", help="Detect regime shifts (change points)")
    p_change.add_argument("values", nargs="+", help="Numeric sequence")
    p_change.add_argument("--penalty", type=float, default=3.0, help="Sensitivity")

    p_fisher = sub.add_parser("fisher", help="Fisher-Rao distance between two Gaussians")
    p_fisher.add_argument("mu1", type=float)
    p_fisher.add_argument("sigma1", type=float)
    p_fisher.add_argument("mu2", type=float)
    p_fisher.add_argument("sigma2", type=float)

    args = parser.parse_args()

    commands = {
        "gaussian": cmd_gaussian, "markov": cmd_markov, "score": cmd_score,
        "erasure": cmd_erasure, "resonance": cmd_resonance,
        "powerlaw": cmd_powerlaw, "hurst": cmd_hurst, "mixture": cmd_mixture,
        "change": cmd_change, "fisher": cmd_fisher,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


def cmd_erasure(args):
    """Show what standard MLE erases vs sovereign MLE."""
    elements = load_elements_for_mle(args.ids)
    if len(elements) < 2:
        print(f"  Need 2+ elements. Found: {len(elements)}")
        return

    result = sovereign_likelihood(elements, env_entropy=args.entropy)

    print(f"\n  {'='*65}")
    print(f"  STANDARD MLE vs SOVEREIGN MLE (entropy={result['env_entropy']})")
    print(f"  {'='*65}")

    print(f"\n  Elements:")
    for e in elements:
        print(f"    {e['id']:>15}  energy={e['energy']:.3f}  type={e['type']}  resilience={e['resilience']:.3f}")

    print(f"\n  Standard MLE (independent, averaged):")
    print(f"    mu_hat (mean):     {result['mu_hat']:.4f}")
    print(f"    sigma_hat (std):   {result['sigma_hat']:.4f}")
    print(f"    log-likelihood:    {result['standard_ll']:.4f}")
    print(f"    -> Treats each element as isolated draw from N(mu, sigma^2)")
    print(f"    -> Solves for center of bell curve")

    print(f"\n  Sovereign MLE (coupled transitions):")
    print(f"    log-likelihood:    {result['sovereign_ll']:.4f}")
    print(f"    -> Treats each pair as energy-gated transition")
    print(f"    -> Solves for resonance of the pack")

    print(f"\n  Pairwise coupling:")
    for p in result["pairs"]:
        print(f"    {p['a']:>10} <-> {p['b']:<10}  compat={p['compatibility']:.2f}  freq={p['freq_ab']:.4f}/{p['freq_ba']:.4f}  ll={p['pair_ll']:.4f}")

    print(f"\n  {'─'*65}")
    print(f"  ERASURE = sovereign_ll - standard_ll = {result['erasure']:.4f}")
    if result["erasure"] > 0:
        print(f"  The standard MLE DESTROYS {result['erasure']:.4f} nats of coupling information.")
        print(f"  This is the structure that averaging erases.")
    else:
        print(f"  Standard MLE captures more variance than coupling contributes.")
        print(f"  Pack coupling is weak at this entropy level.")
    print()


def cmd_resonance(args):
    """Find resonance peak across entropy range."""
    elements = load_elements_for_mle(args.ids)
    if len(elements) < 2:
        print(f"  Need 2+ elements. Found: {len(elements)}")
        return

    result = resonance_peak(elements, steps=50)

    print(f"\n  {'='*65}")
    print(f"  RESONANCE PEAK SEARCH")
    print(f"  {'='*65}")

    print(f"\n  Elements: {', '.join(e['id'] for e in elements)}")
    print(f"\n  Optimal entropy:  {result['optimal_entropy']:.4f}")
    print(f"  Peak likelihood:  {result['peak_ll']:.4f}")

    # Show curve as ASCII sparkline
    curve = result["curve"]
    lls = [c[1] for c in curve]
    ll_min, ll_max = min(lls), max(lls)
    ll_range = ll_max - ll_min if ll_max > ll_min else 1.0

    print(f"\n  Sovereign LL across entropy (0 = order, 1 = chaos):\n")
    bars = "▁▂▃▄▅▆▇█"
    for i in range(0, len(curve), 2):  # every other point
        entropy, ll = curve[i]
        normalized = (ll - ll_min) / ll_range
        bar_idx = min(int(normalized * (len(bars) - 1)), len(bars) - 1)
        bar = bars[bar_idx] * 3
        marker = " <-- PEAK" if abs(entropy - result["optimal_entropy"]) < 0.03 else ""
        print(f"    {entropy:.2f} |{bar}| {ll:.4f}{marker}")

    # Compare peak vs mean
    detail_peak = sovereign_likelihood(elements, result["optimal_entropy"])
    detail_mid = sovereign_likelihood(elements, 0.5)
    print(f"\n  At peak (entropy={result['optimal_entropy']:.2f}):  sovereign_ll={detail_peak['sovereign_ll']:.4f}")
    print(f"  At mid  (entropy=0.50):  sovereign_ll={detail_mid['sovereign_ll']:.4f}")
    print(f"  Resonance advantage: {detail_peak['sovereign_ll'] - detail_mid['sovereign_ll']:.4f} nats")
    print()


def cmd_powerlaw(args):
    """Power-law scaling exponent."""
    values = [float(v) for v in args.values]
    alpha, x_min = mle_powerlaw(values)
    print(f"\n  Power-Law MLE (n={len(values)}):")
    print(f"  Alpha (scaling exponent): {alpha}")
    print(f"  X_min: {x_min}")
    if alpha < 2.0:
        print(f"  -> Heavy tail: frequent high-energy outliers")
    elif alpha < 3.0:
        print(f"  -> Moderate tail: some outlier activity")
    else:
        print(f"  -> Light tail: rapid decay, near-Gaussian")


def cmd_hurst(args):
    """Hurst exponent for fractal memory."""
    values = [float(v) for v in args.values]
    h = estimate_hurst(values)
    print(f"\n  Hurst Exponent (n={len(values)}): H = {h}")
    if h > 0.5:
        print(f"  -> PERSISTENT (H > 0.5): system has memory, trends carry forward")
        print(f"  -> Markov assumption (H=0.5) would erase this momentum")
    elif h < 0.5:
        print(f"  -> ANTI-PERSISTENT (H < 0.5): mean-reverting, pulled back to center")
    else:
        print(f"  -> RANDOM WALK (H = 0.5): no memory, Markov-compatible")


def cmd_mixture(args):
    """Gaussian mixture decomposition."""
    values = [float(v) for v in args.values]
    result = solve_mixture(values, n_components=args.components)
    print(f"\n  Gaussian Mixture (n={len(values)}, k={args.components}):")
    for i, (m, s, w) in enumerate(zip(result["means"], result["stds"], result["weights"])):
        print(f"    Component {i+1}: mean={m:.4f}  std={s:.4f}  weight={w:.2%}")
    # Compare with single Gaussian
    mu, sigma = mle_gaussian(values)
    print(f"\n  Single Gaussian: mean={mu:.4f}  std={sigma:.4f}")
    print(f"  -> The mixture reveals {args.components} resonance peaks that averaging collapses into one.")


def cmd_change(args):
    """Detect regime shifts."""
    values = [float(v) for v in args.values]
    points = detect_change_points(values, penalty=args.penalty)
    print(f"\n  Change Point Detection (n={len(values)}, penalty={args.penalty}):")
    if points:
        print(f"  Regime shifts at indices: {points}")
        for cp in points:
            if cp < len(values):
                before = np.mean(values[:cp])
                after = np.mean(values[cp:]) if cp < len(values) else 0
                print(f"    Index {cp}: mean {before:.3f} -> {after:.3f}")
    else:
        print(f"  No regime shifts detected (system is stationary).")


def cmd_fisher(args):
    """Fisher-Rao distance between two Gaussians."""
    d = fisher_distance(args.mu1, args.sigma1, args.mu2, args.sigma2)
    print(f"\n  Fisher-Rao Distance:")
    print(f"    State A: N({args.mu1}, {args.sigma1}^2)")
    print(f"    State B: N({args.mu2}, {args.sigma2}^2)")
    print(f"    Distance: {d}")
    print(f"    -> Measures separation on the information manifold")
    print(f"    -> Euclidean would give {abs(args.mu2-args.mu1):.4f} (ignores curvature)")


if __name__ == "__main__":
    main()
