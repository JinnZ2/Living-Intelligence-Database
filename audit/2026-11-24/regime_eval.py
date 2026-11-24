"""regime_eval.py — PROPOSED prototype. Scope as operating regime; relationship as coupling term.
Standard library only. All fixtures are SYNTHETIC known-answer cases, not repository claims.

Outcomes are states, never default numbers:
  IN_REGIME          - conditions supplied, inside declared regime, form declared -> evaluated
  NOT_IN_SCOPE       - conditions supplied, outside every declared regime -> relationship does not apply
  CONDITION_UNKNOWN  - a regime variable was not supplied -> cannot place the system
  UNRESOLVED_FORM    - inside regime, but no functional form declared -> do not invent one
"""
import json

def place(regimes, cond):
    """Return (regime, missing_vars). A regime is {id, bounds:{var:[lo,hi]}, form?}."""
    missing = sorted({v for r in regimes for v in r["bounds"] if v not in cond})
    for r in regimes:
        if all(v in cond and lo <= cond[v] <= hi for v, (lo, hi) in r["bounds"].items()):
            return r, missing
    return None, missing

def evaluate(coupling, state, cond):
    r, missing = place(coupling["regimes"], cond)
    if r is None:
        return {"outcome": "CONDITION_UNKNOWN" if missing else "NOT_IN_SCOPE", "missing": missing}
    if r.get("form") is None:
        return {"outcome": "UNRESOLVED_FORM", "regime": r["id"]}
    rate = r["form"](state, cond)          # contribution of source to target's rate
    direction = "source->target" if rate > 0 else "target->source" if rate < 0 else "inactive"
    return {"outcome": "IN_REGIME", "regime": r["id"], "rate": round(rate, 6), "direction": direction}

def integrate(coupling, x0, cond_of_t, dt=0.01, steps=400):
    """Euler integration of dy/dt = coupling(x, e(t)); records regime transitions."""
    y, trace, last = x0["y"], [], None
    for i in range(steps):
        t = i * dt; cond = cond_of_t(t)
        res = evaluate(coupling, {"x": x0["x"], "y": y}, cond)
        tag = res.get("regime", res["outcome"])
        if tag != last: trace.append({"t": round(t, 2), "enters": tag}); last = tag
        if res["outcome"] == "IN_REGIME": y += res["rate"] * dt
    return round(y, 4), trace

# ---------------- synthetic fixture ----------------
# Coupling whose sign reverses at e = 0.5 and which is undeclared above e = 1.0 (scope ends there).
SYN = {"id": "SYNTHETIC_COUPLING", "regimes": [
    {"id": "low_e",  "bounds": {"e": [0.0, 0.5]},  "form": lambda s, c: (0.5 - c["e"]) * s["x"]},
    {"id": "high_e", "bounds": {"e": [0.5, 1.0]}, "form": lambda s, c: -(c["e"] - 0.5) * s["x"]},
    {"id": "edge_known_no_form", "bounds": {"e": [-0.2, -0.0001]}, "form": None},
]}
if __name__ == "__main__":
    s = {"x": 2.0, "y": 0.0}
    cases = {
        "inside_low":        evaluate(SYN, s, {"e": 0.2}),
        "inside_high":       evaluate(SYN, s, {"e": 0.9}),
        "threshold":         evaluate(SYN, s, {"e": 0.5}),
        "outside_scope":     evaluate(SYN, s, {"e": 1.7}),
        "condition_missing": evaluate(SYN, s, {}),
        "no_form_declared":  evaluate(SYN, s, {"e": -0.1}),
    }
    expect = {"inside_low": ("IN_REGIME", "source->target"), "inside_high": ("IN_REGIME", "target->source"),
              "threshold": ("IN_REGIME", "inactive"), "outside_scope": ("NOT_IN_SCOPE", None),
              "condition_missing": ("CONDITION_UNKNOWN", None), "no_form_declared": ("UNRESOLVED_FORM", None)}
    ok = all(cases[k]["outcome"] == o and (d is None or cases[k]["direction"] == d) for k, (o, d) in expect.items())
    y, trace = integrate(SYN, s, lambda t: {"e": 0.4 * t})   # environment drifts 0 -> 1.6 across the run
    print(json.dumps({"cases": cases, "known_answer_pass": ok,
                      "drift_run": {"final_y": y, "regime_transitions": trace}}, indent=1))
