#!/usr/bin/env python3
"""
grounding_inspector.py — L0-L5 Grounding Inspector with Lε Epistemic Calibration Layer

Models the epistemic membrane between substrate-measurable facts (L0-L4) and
interpreted relational claims (L5). Scores each entity's evidence quality across
four Lε sub-layers: observation → pattern → cross-domain transfer → encoding fidelity.

Based on the L0-L5 Grounding Inspector framework (JinnZ2/Resilient-AI-Human-Collaboration-)
expanded for the Living Intelligence Database.

Usage:
  python3 validation/grounding_inspector.py --inspect WHALE
  python3 validation/grounding_inspector.py --inspect ant
  python3 validation/grounding_inspector.py --audit
  python3 validation/grounding_inspector.py --audit --threshold 0.70
  python3 validation/grounding_inspector.py --explain
"""

import json
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_FILE = ROOT / "ontology_index.json"


# ── L-layer classification ────────────────────────────────────────────────────

# Primary L-layer by ontology type
_ONTOLOGY_LAYER = {
    "shape":      "L0",   # geometric invariants, physical forms
    "crystal":    "L1",   # thermodynamic mineral structure
    "energy":     "L1",   # field dynamics, thermodynamic conversion
    "plasma":     "L2",   # planetary-scale energy
    "plant":      "L3",   # ecological systems
    "animal":     "L3",   # ecological + biomechanical
    "social":     "L4",   # embodied social intelligence (L4↔L5 boundary)
    "temporal":   "Le",   # epistemic membrane / pattern-recognition structures
    "ai":         "L5",   # language-primary constructs
    "relational": "L5",   # cross-domain interpretive links
}

_LAYER_ORDER = ["L0", "L1", "L2", "L3", "L4", "Le", "L5"]

_LAYER_DESC = {
    "L0": "Classical physics — geometric invariants, conservation laws",
    "L1": "Thermodynamics — energy conservation, entropy, Carnot limits",
    "L2": "Planetary constraints — water cycles, minerals, carbon sinks",
    "L3": "Ecological systems — allometric scaling, carrying capacity",
    "L4": "Biological biomechanics — body limits, reaction time, metabolic power",
    "Le": "Epistemic membrane — where observation becomes claim",
    "L5": "Social / cultural constructs — consensus, governance, language",
}


# ── Lε scoring tables ─────────────────────────────────────────────────────────

# Lε.pat — base score by evidence type
_EVIDENCE_TYPE_SCORE = {
    "lab_measurement":    0.95,
    "mathematical_proof": 0.95,
    "cyclic_observation": 0.90,
    "field_observation":  0.80,
    "cross_domain_rhyme": 0.65,
    "theoretical":        0.55,
    "simulation":         0.70,
    "expert_consensus":   0.60,
    "anecdotal":          0.40,
    "unknown":            0.30,
}


# ── Data loading ──────────────────────────────────────────────────────────────

def _load_index() -> dict:
    with open(INDEX_FILE) as f:
        return json.load(f)


def _load_entity_file(path_str: str) -> dict:
    path = ROOT / path_str
    with open(path) as f:
        return json.load(f)


def _find_entry(query: str, index: dict) -> dict | None:
    q = query.upper()
    # Exact ID match
    for e in index["entities"]:
        if e["id"] == q:
            return e
    # Case-insensitive name match
    q_low = query.lower()
    for e in index["entities"]:
        if e["name"].lower() == q_low:
            return e
    # Substring match on name
    for e in index["entities"]:
        if q_low in e["name"].lower():
            return e
    return None


# ── L-layer derivation ────────────────────────────────────────────────────────

def derive_layer(entry: dict) -> str:
    ontology = entry.get("ontology", "")
    substrate = entry.get("substrate_layer", "")
    base = _ONTOLOGY_LAYER.get(ontology, "L5")

    # substrate_primary pulls language-type entities down toward L3
    if substrate == "substrate_primary" and base == "L5":
        return "L3"
    return base


# ── Lε sub-layer scoring ──────────────────────────────────────────────────────

def _score_obs(scope: dict) -> tuple[float, list[str]]:
    """Lε.obs — observation quality: measurement_limits + condition documentation."""
    warnings = []
    score = 1.0

    if not scope.get("measurement_limits"):
        score -= 0.15
        warnings.append("Lε.obs: no measurement_limits — observation window is undefined")

    condition = scope.get("condition", {})
    if not condition:
        score -= 0.10
        warnings.append("Lε.obs: no condition block — environmental constraints undocumented")

    return max(0.0, score), warnings


def _score_pat(evidence: dict) -> tuple[float, list[str]]:
    """Lε.pat — pattern recognition quality: evidence type + reproducibility."""
    warnings = []

    ev_type = evidence.get("evidence_type", "unknown")
    base = _EVIDENCE_TYPE_SCORE.get(ev_type, 0.30)

    repro = evidence.get("reproducibility", "")
    if repro == "high" or repro == "certain":
        base = min(1.0, base + 0.05)
    elif repro == "medium":
        pass  # no change
    elif repro == "low":
        base = max(0.0, base - 0.15)
        warnings.append(f"Lε.pat: low reproducibility on {ev_type!r} evidence")
    elif not repro:
        base = max(0.0, base - 0.05)
        warnings.append("Lε.pat: reproducibility not documented")

    return round(base, 3), warnings


def _score_xfr(evidence: dict) -> tuple[float, list[str]]:
    """Lε.xfr — cross-domain transfer validity: cross_domain_count + relational_confidence."""
    warnings = []
    score = 0.70  # baseline

    cd_count = evidence.get("cross_domain_count", 0)
    if cd_count == 0:
        score -= 0.20
        warnings.append("Lε.xfr: no cross-domain examples — rhyme is speculative")
    elif cd_count == 1:
        score -= 0.10
        warnings.append("Lε.xfr: only 1 cross-domain example — pattern may be coincidental")
    elif cd_count >= 3:
        score = min(1.0, score + 0.10)

    # relational_confidence should not exceed what evidence supports
    rel_conf = evidence.get("relational_confidence")
    if rel_conf is not None and score > 0:
        gap = rel_conf - score
        if gap > 0.15:
            warnings.append(
                f"Lε.xfr: confidence inflation — relational_confidence={rel_conf:.2f} "
                f"exceeds transfer score={score:.2f} (gap={gap:.2f})"
            )

    return round(score, 3), warnings


def _score_enc(scope: dict) -> tuple[float, list[str]]:
    """Lε.enc — encoding fidelity: falsifiability + definition precision + dependencies."""
    warnings = []
    score = 1.0

    if not scope.get("falsifiability"):
        score -= 0.20
        warnings.append("Lε.enc: no falsifiability — claim cannot be tested")

    if not scope.get("definition"):
        score -= 0.15
        warnings.append("Lε.enc: no definition — what is actually being measured?")

    deps = scope.get("dependencies", [])
    if not deps:
        score -= 0.05
        # Soft warning — some attributes genuinely have no dependencies
        warnings.append("Lε.enc: no dependencies listed (may be a leaf claim)")

    return max(0.0, score), warnings


def le_score_bare_float(name: str, value: float) -> dict:
    """Score a bare numeric with no scope block — always fragile (noun-pretender)."""
    return {
        "le_score": 0.20,
        "sublayers": {},
        "warnings": [
            f"Bare efficiency_factor={value} — unscoped numeric (noun-pretender). "
            "Add a scope block with definition, evidence, and falsifiability."
        ],
    }


def le_score_attribute(attribute: dict) -> dict:
    """
    Compute full Lε score for a single attribute dict (must have 'scope' key).
    Returns dict with per-sublayer scores, warnings, and aggregate.
    """
    scope = attribute.get("scope", {})
    if not scope:
        return {
            "le_score": 0.25,
            "sublayers": {},
            "warnings": ["No scope block — claim is entirely ungrounded"],
        }

    evidence = scope.get("evidence", {})
    if not evidence:
        return {
            "le_score": 0.30,
            "sublayers": {},
            "warnings": ["No evidence block — Lε cannot be computed"],
        }

    obs_score, obs_warn = _score_obs(scope)
    pat_score, pat_warn = _score_pat(evidence)
    xfr_score, xfr_warn = _score_xfr(evidence)
    enc_score, enc_warn = _score_enc(scope)

    # Weighted aggregate: pat and enc are more critical than xfr and obs
    aggregate = round(
        0.20 * obs_score +
        0.35 * pat_score +
        0.25 * xfr_score +
        0.20 * enc_score,
        3
    )

    return {
        "le_score": aggregate,
        "sublayers": {
            "Le.obs": round(obs_score, 3),
            "Le.pat": round(pat_score, 3),
            "Le.xfr": round(xfr_score, 3),
            "Le.enc": round(enc_score, 3),
        },
        "warnings": obs_warn + pat_warn + xfr_warn + enc_warn,
    }


def _score_all_attributes(entity: dict) -> dict:
    """
    Score all scoreable attributes from an entity dict.
    Checks scoped 'attributes', then falls back to bare efficiency_factors in 'patterns'.
    """
    attr_scores = {}

    # Scoped attributes (new format)
    attrs_raw = entity.get("attributes") or {}
    for name, val in attrs_raw.items():
        if isinstance(val, dict) and ("scope" in val or "evidence" in val):
            attr_scores[name] = le_score_attribute(val)

    # Bare efficiency_factors in patterns array (old format — flag as noun-pretenders)
    for pat in entity.get("patterns", []):
        ef = pat.get("efficiency_factor")
        if ef is not None:
            pat_name = pat.get("name", "unnamed_pattern")
            # Only flag if there's no matching scoped attribute with the same name
            if pat_name not in attr_scores:
                attr_scores[f"patterns/{pat_name}"] = le_score_bare_float(pat_name, ef)

    # Also check bare floats in core_attributes (very old format)
    core = entity.get("core_attributes") or {}
    ef_core = core.get("efficiency_factor")
    if ef_core is not None and isinstance(ef_core, float) and "core_efficiency_factor" not in attr_scores:
        attr_scores["core_attributes/efficiency_factor"] = le_score_bare_float(
            "efficiency_factor", ef_core
        )

    return attr_scores


# ── Entity-level inspection ───────────────────────────────────────────────────

def inspect_entity(query: str) -> dict:
    """Full grounding report for one entity (by ID, name, or substring)."""
    index = _load_index()
    entry = _find_entry(query, index)
    if not entry:
        return {"error": f"Entity {query!r} not found in index"}

    entity = _load_entity_file(entry["path"])
    layer = derive_layer(entry)
    substrate = entry.get("substrate_layer", "unknown")

    attr_scores = _score_all_attributes(entity)

    # Entity-level Lε (mean of attribute scores)
    if attr_scores:
        mean_le = round(
            sum(v["le_score"] for v in attr_scores.values()) / len(attr_scores),
            3
        )
    else:
        mean_le = None

    # Substrate coherence check
    coherence_issues = []
    if substrate == "language_primary" and layer in ("L0", "L1", "L2", "L3"):
        coherence_issues.append(
            f"Incoherence: substrate_layer=language_primary but ontology suggests {layer} grounding"
        )
    if substrate == "substrate_primary" and layer == "L5":
        coherence_issues.append(
            "Incoherence: substrate_layer=substrate_primary but ontology is L5 (social/ai)"
        )

    # Collect all warnings
    all_warnings = coherence_issues[:]
    for attr_name, result in attr_scores.items():
        for w in result.get("warnings", []):
            all_warnings.append(f"{attr_name}: {w}")

    return {
        "id": entry["id"],
        "name": entry.get("name"),
        "ontology": entry.get("ontology"),
        "grounding_layer": layer,
        "layer_description": _LAYER_DESC.get(layer, ""),
        "substrate_layer": substrate,
        "le_score_mean": mean_le,
        "grounding_status": _grade(mean_le),
        "attributes": attr_scores,
        "substrate_coherence_issues": coherence_issues,
        "all_warnings": all_warnings,
    }


def _grade(score: float | None) -> str:
    if score is None:
        return "unscored (no evidence blocks)"
    if score >= 0.85:
        return "strong"
    if score >= 0.70:
        return "adequate"
    if score >= 0.55:
        return "weak — review evidence blocks"
    return "fragile — claim may be a noun-pretender"


# ── Audit all entities ────────────────────────────────────────────────────────

def audit_all(threshold: float = 0.65) -> None:
    """Scan all entities and report Lε score distribution."""
    index = _load_index()
    scored = []
    unscored = []

    for entry in index["entities"]:
        entity = _load_entity_file(entry["path"])
        layer = derive_layer(entry)
        attr_scores = _score_all_attributes(entity)

        if attr_scores:
            mean = round(sum(v["le_score"] for v in attr_scores.values()) / len(attr_scores), 3)
            scored.append((entry["id"], entry.get("name", "?"), layer, mean))
        else:
            unscored.append((entry["id"], entry.get("name", "?"), layer))

    scored.sort(key=lambda x: x[3])

    print("\n=== Lε Grounding Audit ===")
    print(f"Threshold for warning: {threshold}\n")
    print(f"{'ID':<18} {'Layer':<5} {'Lε Score':<10} {'Status':<10}  Name")
    print("─" * 72)

    for eid, name, layer, score in scored:
        flag = "⚠️ " if score < threshold else "✅ "
        status = _grade(score).split(" ")[0]
        print(f"{eid:<18} {layer:<5} {score:<10.3f} {flag}{status:<8}  {name}")

    if unscored:
        print(f"\n── No evidence blocks ({len(unscored)} entities) ──")
        for eid, name, layer in unscored:
            print(f"  {eid:<18} {layer:<5} {name}")

    if scored:
        all_scores = [r[3] for r in scored]
        mean_all = sum(all_scores) / len(all_scores)
        weak = [r for r in scored if r[3] < threshold]
        print(
            f"\nTotal: {len(scored)+len(unscored)} entities | "
            f"Scored: {len(scored)} | "
            f"Mean Lε: {mean_all:.3f} | "
            f"Below threshold: {len(weak)}"
        )


# ── Explanation mode ──────────────────────────────────────────────────────────

def explain() -> None:
    print("""
Lε Epistemic Membrane — Four Sub-Layers
════════════════════════════════════════

The Lε layer sits between substrate reality (L0-L4) and relational claims (L5).
Every numeric attribute in this database crosses Lε. This inspector scores that crossing.

  Lε.obs  (weight 20%)  Observation quality
           Checks: measurement_limits, condition documentation
           Failure: lab value applied to field conditions without noting the gap

  Lε.pat  (weight 35%)  Pattern recognition quality
           Checks: evidence_type, reproducibility, source quality
           Failure: treating a single observation as a representative pattern

  Lε.xfr  (weight 25%)  Cross-domain transfer validity
           Checks: cross_domain_count, relational_confidence gap
           Failure: rhyming wolf pack with corporate teams without noting
                    the 4M-year evolutionary substrate that grounds the wolf

  Lε.enc  (weight 20%)  Encoding fidelity
           Checks: falsifiability, definition precision, dependencies
           Failure: claiming confidence 0.94 on a non-falsifiable assertion

Grading:
  ≥ 0.85  strong        Evidence is well-grounded; claims can be trusted
  ≥ 0.70  adequate      Minor gaps; usable with noted caveats
  ≥ 0.55  weak          Evidence blocks need review
  < 0.55  fragile       Likely a noun-pretender — static value, no scope

L-layer assignments:
  L0  shape       — geometric invariants
  L1  crystal, energy, plasma   — thermodynamic structure
  L2  plasma (planetary scale)
  L3  plant, animal — ecological systems
  L4  social      — embodied social intelligence (L4↔L5 boundary)
  Lε  temporal    — epistemic membrane / pattern-recognition itself
  L5  ai, relational — language-primary constructs

See docs/GROUNDING_LAYERS.md for full layer definitions.
""")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="L0-L5 Grounding Inspector with Lε Epistemic Calibration"
    )
    parser.add_argument("--inspect", metavar="ID", help="Inspect one entity by ID or name")
    parser.add_argument("--audit", action="store_true", help="Audit all entities by Lε score")
    parser.add_argument(
        "--threshold", type=float, default=0.65,
        help="Lε score below which entities are flagged (default: 0.65)"
    )
    parser.add_argument("--explain", action="store_true", help="Explain the Lε model")
    args = parser.parse_args()

    if args.explain:
        explain()
    elif args.inspect:
        result = inspect_entity(args.inspect)
        print(json.dumps(result, indent=2))
    elif args.audit:
        audit_all(threshold=args.threshold)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
