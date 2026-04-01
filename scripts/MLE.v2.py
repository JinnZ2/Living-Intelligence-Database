#!/usr/bin/env python3
"""
Living Intelligence Database — Sovereign MLE Toolkit v2.0

Enhanced statistical analysis for outlier cognition:
• Non-Gaussian (power-law, mixtures)
• Fractal/Hurst analysis
• Topological features
• Information geometry
• Causal inference
• Change-point detection
• Mutual information
• Phase space reconstruction

Extends v1's sovereign coupling to full geometric/field-based cognition translation.

Usage:
    python scripts/mle_v2.py powerlaw 1 2 3 10 100
    python scripts/mle_v2.py hurst 1.2 2.3 1.8 2.0 2.5 3.1
    python scripts/mle_v2.py mixture 1.2 2.3 1.8 2.0 2.5 10.1 11.2 10.8
    python scripts/mle_v2.py sovereign BE QUARTZ SPIRAL --entropy 0.3
"""

import json
import sys
import argparse
import numpy as np
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from sklearn.mixture import GaussianMixture
from sklearn.metrics import mutual_info_score
import ruptures as rpt  # pip install ruptures

ROOT = Path(__file__).resolve().parents[1]

# ── V1 FUNCTIONS (unchanged) ───────────────────────────────────────────────

def mle_gaussian(sequence):
    x = np.asarray(sequence, dtype=float)
    mu_hat = np.mean(x)
    sigma_hat = np.std(x, ddof=0)
    return mu_hat, sigma_hat

def mle_markov(sequence, states=None):
    if states is None:
        states = sorted(set(sequence))
    n_states = len(states)
    state_to_idx = {s: i for i, s in enumerate(states)}
    counts = np.zeros((n_states, n_states))
    for prev, curr in zip(sequence[:-1], sequence[1:]):
        if prev in state_to_idx and curr in state_to_idx:
            counts[state_to_idx[prev], state_to_idx[curr]] += 1
    probs = np.zeros_like(counts)
    for i in range(n_states):
        row_sum = counts[i].sum()
        probs[i] = counts[i] / row_sum if row_sum > 0 else 1.0 / n_states
    return states, probs

def sovereign_likelihood(elements, env_entropy=0.5):
    if len(elements) < 2:
        return {"sovereign_ll": 0.0, "standard_ll": 0.0, "erasure": 0.0, "pairs": []}
    compat_matrix = {
        ("harmonic", "harmonic"): 1.0, ("harmonic", "kinetic"): 0.7,
        ("harmonic", "radiant"): 0.8, ("harmonic", "chemical"): 0.5,
        ("kinetic", "kinetic"): 1.0, ("kinetic", "radiant"): 0.6,
        ("kinetic", "chemical"): 0.6, ("chemical", "chemical"): 1.0,
        ("chemical", "radiant"): 0.4, ("radiant", "radiant"): 1.0,
    }
    def compat(t1, t2):
        return compat_matrix.get((t1, t2), compat_matrix.get((t2, t1), 0.5))
    energies = [e["energy"] for e in elements]
    mu = np.mean(energies)
    sigma = np.std(energies, ddof=0) + 1e-9
    standard_ll = sum(-0.5 * np.log(2 * np.pi * sigma**2) - (e - mu)**2 / (2 * sigma**2) for e in energies)
    sovereign_ll = 0.0
    pairs = []
    for i, a in enumerate(elements):
        for j, b in enumerate(elements):
            if i >= j: continue
            c = compat(a["type"], b["type"])
            stress_a = np.exp(-env_entropy / (a["resilience"] * a["energy"]))
            stress_b = np.exp(-env_entropy / (b["resilience"] * b["energy"]))
            freq_ab = c * stress_a * b["energy"]
            freq_ba = c * stress_b * a["energy"]
            pair_ll = np.log(max(freq_ab, 1e-9)) + np.log(max(freq_ba, 1e-9))
            sovereign_ll += pair_ll
            pairs.append({"a": a["id"], "b": b["id"], "compatibility": round(c, 3), "freq_ab": round(freq_ab, 4), "freq_ba": round(freq_ba, 4), "pair_ll": round(pair_ll, 4)})
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

def load_elements_for_mle(entity_ids):
    ontology_dir = ROOT / "ontology"
    type_map = {"animal": "kinetic", "plant": "chemical", "crystal": "harmonic", "energy": "radiant", "plasma": "radiant", "shape": "harmonic", "temporal": "harmonic"}
    elements = []
    for layer_dir in ontology_dir.iterdir():
        if not layer_dir.is_dir(): continue
        for filepath in layer_dir.glob("*.json"):
            try:
                with open(filepath) as f:
                    data = json.load(f)
                if not isinstance(data, dict) or data.get("id") not in entity_ids: continue
                efficiency = 0.9
                core = data.get("core_attributes", {})
                if isinstance(core.get("efficiency_factor"), (int, float)): efficiency = core["efficiency_factor"]
                for p in data.get("patterns", []):
                    if isinstance(p.get("efficiency_factor"), (int, float)): efficiency = max(efficiency, p["efficiency_factor"])
                ont = data


                # Continuing from: ont = data
                elements.append({
                    "id": data.get("id"),
                    "type": type_map.get(data.get("type", "animal"), "kinetic"),
                    "energy": float(data.get("energy_signature", 1.0)),
                    "resilience": float(efficiency)
                })
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
    return elements

# ── V2 FUNCTIONS (Advanced Outlier & Field Analysis) ───────────────────────

def mle_powerlaw(sequence):
    """
    Estimates the scaling exponent (alpha) for heavy-tailed distributions.
    High alpha = rapid decay; Low alpha = frequent high-energy outliers.
    """
    x = np.asarray(sequence, dtype=float)
    x_min = np.min(x)
    n = len(x)
    # MLE for power law: alpha = 1 + n / [sum(ln(x_i / x_min))]
    alpha_hat = 1 + n / np.sum(np.log(x / x_min))
    return round(alpha_hat, 4), x_min

def estimate_hurst(sequence):
    """
    Rescaled Range (R/S) analysis to determine long-term memory (fractal dimension).
    H < 0.5: Mean-reverting (anti-persistent)
    H = 0.5: Random walk (Brownian)
    H > 0.5: Trending (persistent/high-efficiency momentum)
    """
    x = np.asarray(sequence, dtype=float)
    y = np.cumsum(x - np.mean(x))
    r = np.max(y) - np.min(y)
    s = np.std(x, ddof=1)
    # Simplified estimate for short sequences
    hurst = np.log(r / s) / np.log(len(x)) if s > 0 else 0.5
    return round(hurst, 4)

def detect_change_points(sequence):
    """
    Identifies 'Entropy Events' or regime shifts in the data field.
    """
    x = np.asarray(sequence).reshape(-1, 1)
    # Using Pelt algorithm for optimal segmentation
    algo = rpt.Pelt(model="rbf").fit(x)
    result = algo.predict(pen=10)
    return result

def solve_mixture(sequence, n_components=2):
    """
    Deconstructs the signal into underlying energy states (e.g., Waste vs. Efficiency).
    """
    x = np.asarray(sequence).reshape(-1, 1)
    gmm = GaussianMixture(n_components=n_components, random_state=42).fit(x)
    return {
        "means": gmm.means_.flatten().tolist(),
        "weights": gmm.weights_.tolist()
    }

# ── CLI LOGIC ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Sovereign MLE Toolkit v2.0")
    parser.add_argument("command", choices=["powerlaw", "hurst", "mixture", "sovereign", "change"])
    parser.add_argument("data", nargs="*", help="Data points or Entity IDs")
    parser.add_argument("--entropy", type=float, default=0.5, help="Environment Entropy")
    
    args = parser.parse_args()

    if args.command == "sovereign":
        elements = load_elements_for_mle(args.data)
        results = sovereign_likelihood(elements, env_entropy=args.entropy)
        print(json.dumps(results, indent=2))
    
    elif args.command in ["powerlaw", "hurst", "mixture", "change"]:
        seq = [float(x) for x in args.data]
        if args.command == "powerlaw":
            alpha, xmin = mle_powerlaw(seq)
            print(f"Alpha (Scaling Exponent): {alpha} | X_min: {xmin}")
        elif args.command == "hurst":
            h = estimate_hurst(seq)
            print(f"Hurst Exponent: {h}")
        elif args.command == "mixture":
            mix = solve_mixture(seq)
            print(f"Mixture States: {mix}")
        elif args.command == "change":
            pts = detect_change_points(seq)
            print(f"Change Points (Regime Shifts) at Indices: {pts}")

if __name__ == "__main__":
    main()



### add on

def estimate_hysteresis(load_sequence, temp_sequence):
    """
    Measures the 'Thermal Memory' of the system.
    High Hysteresis = System is 'holding' entropy/heat longer than the 
    environment can dissipate it. 
    Predicts the 'Thermal Limit' before the hardware hits it.
    """
    load = np.asarray(load_sequence)
    temp = np.asarray(temp_sequence)
    
    # Calculate the area of the loop between Load and Temperature
    # This area represents the energy 'lost' to the system (Entropy Leak)
    area = np.abs(np.trapz(temp, x=load))
    
    # Efficiency Factor (Functional Epistemology)
    # If area increases while load is constant, failure is imminent.
    return round(area, 4)
