#!/usr/bin/env python3
"""
Living Intelligence Database — Sensor Data Ingestion

Bridges real-world timeseries data (CSV, JSON) into the MLE and
sovereign simulation toolkit. Loads sensor readings, runs analysis,
and maps physical measurements to the ontology's energy framework.

Usage:
    # Analyze a CSV timeseries
    python scripts/ingest.py csv data.csv --column temperature --analyze

    # Analyze a JSON timeseries
    python scripts/ingest.py json readings.json --key values --analyze

    # Inline data (for quick tests)
    python scripts/ingest.py inline 25.1 25.3 26.0 28.5 30.2 29.1 25.0 --analyze

    # Full sovereign pipeline: ingest + simulate
    python scripts/ingest.py csv motor_temps.csv --column temp --sovereign

    # As a Python library
    from scripts.ingest import load_csv, analyze_series, sovereign_pipeline
"""

import json
import sys
import argparse
import csv
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


# ── Loaders ────────────────────────────────────────────────────────────────

def load_csv(filepath, column=None, time_column=None):
    """
    Load timeseries from CSV.
    If column is specified, extracts that column.
    If time_column is specified, extracts timestamps.
    Otherwise, loads first numeric column.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise ValueError("CSV is empty")

    # Auto-detect column if not specified
    if column is None:
        for key in rows[0]:
            try:
                float(rows[0][key])
                column = key
                break
            except (ValueError, TypeError):
                continue
        if column is None:
            raise ValueError("No numeric column found. Specify --column")

    values = []
    times = []
    for i, row in enumerate(rows):
        try:
            values.append(float(row[column]))
            if time_column and time_column in row:
                times.append(float(row[time_column]))
            else:
                times.append(float(i))
        except (ValueError, KeyError):
            continue

    return np.array(times), np.array(values), column


def load_json_series(filepath, key="values", time_key=None):
    """
    Load timeseries from JSON.
    Supports: {"values": [1,2,3]} or [{"time": 0, "value": 1}, ...]
    """
    filepath = Path(filepath)
    with open(filepath) as f:
        data = json.load(f)

    if isinstance(data, list):
        # Array of objects
        if isinstance(data[0], dict):
            vkey = key if key in data[0] else "value"
            tkey = time_key or "time"
            values = [float(d[vkey]) for d in data if vkey in d]
            times = [float(d.get(tkey, i)) for i, d in enumerate(data)]
        else:
            values = [float(x) for x in data]
            times = list(range(len(values)))
    elif isinstance(data, dict):
        if key in data:
            values = [float(x) for x in data[key]]
            times = list(range(len(values)))
        else:
            raise ValueError(f"Key '{key}' not found. Available: {list(data.keys())}")
    else:
        raise ValueError("Unsupported JSON structure")

    return np.array(times), np.array(values), key


def load_inline(values):
    """Load inline numeric values."""
    vals = np.array([float(v) for v in values])
    times = np.arange(len(vals), dtype=float)
    return times, vals, "inline"


# ── Analysis ───────────────────────────────────────────────────────────────

def analyze_series(times, values, label="series"):
    """
    Run full MLE + sovereign analysis on a timeseries.
    Returns a dict of results.
    """
    from scripts.mle import (
        mle_gaussian, mle_gaussian_continuous,
        estimate_hurst, detect_change_points, solve_mixture,
    )

    n = len(values)
    mu, sigma = mle_gaussian(values)
    _, _, slope, intercept = mle_gaussian_continuous(times, values)
    hurst = estimate_hurst(values)
    change_pts = detect_change_points(values)
    mixture = solve_mixture(values, n_components=2)

    # Entropy estimate (normalized)
    if sigma > 0:
        entropy = 0.5 * np.log(2 * np.pi * np.e * sigma**2)
    else:
        entropy = 0.0

    # Stability (inverse coefficient of variation)
    stability = mu / sigma if sigma > 0 else float("inf")

    return {
        "label": label,
        "n": n,
        "gaussian": {"mu": round(mu, 4), "sigma": round(sigma, 4)},
        "trend": {"slope": round(slope, 4), "intercept": round(intercept, 4)},
        "hurst": hurst,
        "change_points": change_pts,
        "mixture": mixture,
        "entropy": round(entropy, 4),
        "stability": round(stability, 4),
        "min": round(float(np.min(values)), 4),
        "max": round(float(np.max(values)), 4),
        "range": round(float(np.max(values) - np.min(values)), 4),
    }


def sovereign_pipeline(times, values, label="sensor"):
    """
    Map real sensor data into the sovereign framework.
    Treats the timeseries as an environment entropy signal
    and reports sovereign state assessment.
    """
    analysis = analyze_series(times, values, label)

    # Map to sovereign concepts
    mu = analysis["gaussian"]["mu"]
    sigma = analysis["gaussian"]["sigma"]
    hurst = analysis["hurst"]
    n_changes = len(analysis["change_points"])

    # Resilience: inverse of normalized variance
    resilience = 1.0 / (1.0 + sigma / (abs(mu) + 1e-9))

    # Energy profile from stability
    energy = min(analysis["stability"] / 10.0, 1.0) if analysis["stability"] != float("inf") else 1.0

    # Entropy phase from hurst exponent
    if hurst > 0.6:
        phase = "PERSISTENT — momentum carries, system has memory"
    elif hurst > 0.4:
        phase = "BROWNIAN — no memory, random walk"
    else:
        phase = "ANTI-PERSISTENT — mean-reverting, pulled to center"

    # Regime assessment
    if n_changes == 0:
        regime = "STATIONARY — no regime shifts detected"
    elif n_changes <= 2:
        regime = f"TRANSITIONAL — {n_changes} regime shift(s)"
    else:
        regime = f"TURBULENT — {n_changes} regime shifts (high entropy)"

    # Sovereign state
    if resilience > 0.8 and energy > 0.5 and hurst > 0.5:
        state = "SOVEREIGN — high resilience, persistent momentum"
    elif resilience > 0.5:
        state = "STABLE — moderate coupling, some entropy"
    else:
        state = "STRESSED — low resilience, high entropy exposure"

    # Thermal limit check
    thermal_risk = "LOW"
    if analysis["range"] > 3 * sigma and sigma > 0:
        thermal_risk = "HIGH — range exceeds 3 sigma, thermal limit approaching"
    elif analysis["range"] > 2 * sigma and sigma > 0:
        thermal_risk = "MODERATE — range near 2 sigma boundary"

    return {
        "analysis": analysis,
        "sovereign": {
            "resilience": round(resilience, 4),
            "energy_profile": round(energy, 4),
            "phase": phase,
            "regime": regime,
            "state": state,
            "thermal_risk": thermal_risk,
            "hurst": hurst,
        },
    }


# ── CLI ────────────────────────────────────────────────────────────────────

def print_analysis(result):
    """Print analysis results."""
    a = result if "sovereign" not in result else result["analysis"]
    print(f"\n  {'='*60}")
    print(f"  TIMESERIES ANALYSIS: {a['label']} (n={a['n']})")
    print(f"  {'='*60}")
    print(f"\n  Gaussian MLE:")
    print(f"    mu={a['gaussian']['mu']:.4f}  sigma={a['gaussian']['sigma']:.4f}")
    print(f"    range=[{a['min']:.4f}, {a['max']:.4f}]  span={a['range']:.4f}")
    print(f"\n  Trend: slope={a['trend']['slope']:.4f}  intercept={a['trend']['intercept']:.4f}")
    print(f"  Hurst exponent: H={a['hurst']}")
    if a["hurst"] > 0.5:
        print(f"    -> PERSISTENT: trends carry forward")
    elif a["hurst"] < 0.5:
        print(f"    -> ANTI-PERSISTENT: reverts to mean")
    print(f"  Entropy: {a['entropy']:.4f} nats")
    print(f"  Stability: {a['stability']:.4f}")
    if a["change_points"]:
        print(f"  Change points: {a['change_points']}")
    else:
        print(f"  Change points: none (stationary)")
    print(f"  Mixture: {len(a['mixture']['means'])} components")
    for i, (m, s, w) in enumerate(zip(a["mixture"]["means"], a["mixture"]["stds"], a["mixture"]["weights"])):
        print(f"    Component {i+1}: mean={m:.4f} std={s:.4f} weight={w:.2%}")


def print_sovereign(result):
    """Print sovereign assessment."""
    print_analysis(result)
    s = result["sovereign"]
    print(f"\n  {'─'*60}")
    print(f"  SOVEREIGN ASSESSMENT")
    print(f"  {'─'*60}")
    print(f"  Resilience:    {s['resilience']:.4f}")
    print(f"  Energy:        {s['energy_profile']:.4f}")
    print(f"  Phase:         {s['phase']}")
    print(f"  Regime:        {s['regime']}")
    print(f"  Thermal risk:  {s['thermal_risk']}")
    print(f"\n  State: {s['state']}")
    print()


def cmd_csv(args):
    times, values, label = load_csv(args.file, args.column, args.time_column)
    if args.sovereign:
        result = sovereign_pipeline(times, values, label)
        print_sovereign(result)
    elif args.analyze:
        result = analyze_series(times, values, label)
        print_analysis(result)
    else:
        print(f"Loaded {len(values)} values from {args.file}:{label}")
        print(f"Use --analyze or --sovereign for analysis")


def cmd_json(args):
    times, values, label = load_json_series(args.file, args.key)
    if args.sovereign:
        result = sovereign_pipeline(times, values, label)
        print_sovereign(result)
    elif args.analyze:
        result = analyze_series(times, values, label)
        print_analysis(result)
    else:
        print(f"Loaded {len(values)} values from {args.file}:{label}")


def cmd_inline(args):
    times, values, label = load_inline(args.values)
    if args.sovereign:
        result = sovereign_pipeline(times, values, label)
        print_sovereign(result)
    else:
        result = analyze_series(times, values, label)
        print_analysis(result)


def main():
    parser = argparse.ArgumentParser(description="Sensor Data Ingestion")
    sub = parser.add_subparsers(dest="command")

    p_csv = sub.add_parser("csv", help="Load CSV timeseries")
    p_csv.add_argument("file", help="CSV file path")
    p_csv.add_argument("--column", help="Value column name")
    p_csv.add_argument("--time-column", help="Time column name")
    p_csv.add_argument("--analyze", action="store_true", help="Run MLE analysis")
    p_csv.add_argument("--sovereign", action="store_true", help="Run sovereign pipeline")

    p_json = sub.add_parser("json", help="Load JSON timeseries")
    p_json.add_argument("file", help="JSON file path")
    p_json.add_argument("--key", default="values", help="Data key")
    p_json.add_argument("--analyze", action="store_true", help="Run MLE analysis")
    p_json.add_argument("--sovereign", action="store_true", help="Run sovereign pipeline")

    p_inline = sub.add_parser("inline", help="Inline numeric values")
    p_inline.add_argument("values", nargs="+", help="Numeric values")
    p_inline.add_argument("--analyze", action="store_true", default=True)
    p_inline.add_argument("--sovereign", action="store_true", help="Run sovereign pipeline")

    args = parser.parse_args()

    commands = {"csv": cmd_csv, "json": cmd_json, "inline": cmd_inline}
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
