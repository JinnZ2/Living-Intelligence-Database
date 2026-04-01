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

    args = parser.parse_args()

    if args.command == "gaussian":
        cmd_gaussian(args)
    elif args.command == "markov":
        cmd_markov(args)
    elif args.command == "score":
        cmd_score(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
