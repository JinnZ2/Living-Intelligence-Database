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

    args = parser.parse_args()

    if args.command == "gaussian":
        cmd_gaussian(args)
    elif args.command == "markov":
        cmd_markov(args)
    elif args.command == "score":
        cmd_score(args)
    elif args.command == "erasure":
        cmd_erasure(args)
    elif args.command == "resonance":
        cmd_resonance(args)
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


if __name__ == "__main__":
    main()
