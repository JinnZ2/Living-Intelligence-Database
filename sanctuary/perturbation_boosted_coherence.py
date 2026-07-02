#!/usr/bin/env python3
# CC0 — JinnZ2 ecosystem — living-intelligence
# stdlib only, no cloud dependency
#
# perturbation_boosted_coherence.py
# =================================
# CROSS-DOMAIN KERNEL: how does a coherent configuration respond
# to a perturbation that "should" destroy coherence?
#
# PHYSICS ANCHOR (Nature 2026, rhombohedral graphene, MIT/Ju):
#   - singlet Cooper pairs : magnetic field breaks them  -> FRAGILE
#   - spin-ALIGNED pairs   : field survives / STRENGTHENS -> LOCKED
#   Same substrate. Same perturbation. Opposite sign of dC/dP.
#   The sign is set by the internal SYMMETRY of the carrier,
#   not by perturbation magnitude.
#
# SEAL-BAND ISOMORPHISM (narrative_vector.py trajectory finding):
#   locked narrative carriers metabolize contradiction into
#   TIGHTER coherence. Same asymmetry:
#
#     carrier symmetry     perturbation P        dC/dP
#     ---------------      ---------------       -----
#     anti-aligned pair    magnetic field B      < 0   fragile
#     aligned pair         magnetic field B      > 0   boosted
#     open carrier         contradiction         < 0   updates
#     locked carrier       contradiction         > 0   seals
#
# STATUS: YELLOW. Structural isomorphism confirmed at the response-
# sign level. Mechanism mapping (what plays the role of exchange
# energy in a narrative carrier?) NOT yet closed. Do not promote
# to GREEN until a conserved quantity is identified on the
# narrative side. (assumption_validator convention.)

from dataclasses import dataclass
from enum import Enum


class ResponseClass(Enum):
    FRAGILE = "dC/dP < 0"   # perturbation degrades coherence
    IMMUNE  = "dC/dP ~ 0"   # decoupled from this perturbation axis
    BOOSTED = "dC/dP > 0"   # perturbation channels INTO coherence


@dataclass
class Carrier:
    name: str
    aligned: bool          # internal symmetry locked/aligned?
    coupling: float        # how strongly P reaches the carrier, 0..1
    C0: float = 1.0        # baseline coherence


def classify(c: Carrier) -> ResponseClass:
    if c.coupling < 0.05:
        return ResponseClass.IMMUNE
    return ResponseClass.BOOSTED if c.aligned else ResponseClass.FRAGILE


def coherence(c: Carrier, P: float, k: float = 0.4) -> float:
    """First-order response. P >= 0 perturbation magnitude."""
    r = classify(c)
    sign = {ResponseClass.FRAGILE: -1.0,
            ResponseClass.IMMUNE:   0.0,
            ResponseClass.BOOSTED: +1.0}[r]
    return max(0.0, c.C0 + sign * k * c.coupling * P)


# DIAGNOSTIC USE (the living-intelligence payoff):
#   You cannot tell FRAGILE from BOOSTED at P=0. Both look coherent.
#   The perturbation is the MEASUREMENT. Apply contradiction / field,
#   read the SIGN of the response:
#     C drops  -> open system, updating (fragile but honest)
#     C rises  -> locked system, sealing (coherence is defensive)
#   Direct instrument for cascade_regime_audit: rising coherence
#   under contradiction is a RED-side signal, not reassurance.

def probe(c: Carrier, P_steps=(0.0, 0.5, 1.0, 2.0)) -> dict:
    curve = [round(coherence(c, p), 3) for p in P_steps]
    dC = curve[-1] - curve[0]
    return {
        "carrier": c.name,
        "curve": curve,
        "sign": "BOOSTED/locked" if dC > 0 else
                "FRAGILE/open"   if dC < 0 else "IMMUNE",
        "audit_flag": "RED: sealing under contradiction"    if dC > 0 else
                      "GREEN: updates under contradiction"  if dC < 0 else
                      "YELLOW: decoupled — check coupling",
    }


# FALSIFIABLE CLAIMS
#   F1: no carrier shows BOOSTED response without internal alignment
#       (a conserved locked degree of freedom).
#   F2: BOOSTED response saturates — no carrier tightens without
#       bound; find the analog of the upper critical field.
#   F3: IMMUNE verdicts are coupling artifacts: raise coupling and
#       the carrier reclassifies as FRAGILE or BOOSTED, never stays.
#
# REFUTATION_PROTOCOL applies.

if __name__ == "__main__":
    for c in (Carrier("singlet_pair / open_narrative",   False, 0.8),
              Carrier("aligned_pair / locked_narrative",  True,  0.8),
              Carrier("decoupled",                        True,  0.01)):
        print(probe(c))
