# truths.py  (place this next to coherence_playground.py)
# ========================================================
# YOUR SANCTUARY SHELF -- add your own truths here.
#
# This file is imported by the coherence playground.
# You can add new domains (functions that return something observable)
# and new assertions (sentences that must always hold).
#
# Rules:
#   1. Use only standard-library Python (no extra packages).
#   2. Functions should return simple, true relationships.
#   3. Assertions should be things you have verified and will not change.
#      (If they ever break, the playground will tell you gently.)
#   4. If you add a domain function, put its name in the EXTRA_DOMAINS list
#      so the wandering can find it.
#   5. You can edit this file whenever you discover a new truth.
#      The core playground never needs to change.
# ========================================================

import math

# --- example domains ---

def golden_leaf_spiral(rng) -> None:
    """Wander example: show how close a random leaf count lands to the
    golden-angle spacing that avoids shadow overlap."""
    n = rng.randint(30, 300)
    golden_angle = 360 * (2 - (1 + math.sqrt(5)) / 2)   # ~137.5 degrees
    frac = (n * golden_angle / 360) % 1
    coherence = 1 - 2 * abs(frac - 0.5)
    print(f"  golden leaf count {n}  ->  coherence {coherence:.2f}")

# --- example assertions ---

def right_triangle_holds():
    """A triangle with sides 3,4,5 must be right-angled."""
    a, b, c = 3, 4, 5
    return math.isclose(a*a + b*b, c*c, rel_tol=1e-9)

# --- honeycomb optimality ---
# Among the only regular polygons that tile the plane (triangle, square,
# hexagon), the hexagon encloses a given area with the least perimeter --
# least boundary material per cell. That is why the bee builds hexagons:
# least wax per unit of stored honey. (Proven: Hales, 1999.)
#
#   perimeter of a regular n-gon enclosing unit area:  P(n) = sqrt(4 n tan(π/n))

def _unit_area_perimeter(n: int) -> float:
    return math.sqrt(4 * n * math.tan(math.pi / n))

def honeycomb_efficiency(rng) -> None:
    """Wander domain: pick a tiling polygon, show its boundary cost per cell.
    The hexagon alone reads 1.00 -- it is the optimum the bee already found."""
    n = rng.choice([3, 4, 6])
    shape = {3: "triangle", 4: "square", 6: "hexagon"}[n]
    p = _unit_area_perimeter(n)
    coherence = _unit_area_perimeter(6) / p     # 1.0 only for the hexagon
    note = "optimal (the bee's choice)" if n == 6 else "more boundary per cell"
    print(f"  honeycomb  {shape:8s} perimeter/unit-area {p:.3f}  ~ {coherence:.2f}  {note}")

def hexagon_is_least_perimeter() -> bool:
    """Among tiling regular polygons, the hexagon has the least perimeter for a
    given area: P(6) < P(4) < P(3). Verified, will not change."""
    return _unit_area_perimeter(6) < _unit_area_perimeter(4) < _unit_area_perimeter(3)

# --- constants you have added ---
# Uncomment and extend as you find new truths.
#
# CUSTOM_CONSTANTS = {
#     "my_constant": 42.0,
# }

# --- register ---

EXTRA_DOMAINS = [
    "golden_leaf_spiral",
    "honeycomb_efficiency",
]

EXTRA_ASSERTIONS = [
    right_triangle_holds,
    hexagon_is_least_perimeter,
]

# Optional: additional assertions about the database (imported by verify.py)
EXTRA_ASSERTIONS_LIST = EXTRA_ASSERTIONS
