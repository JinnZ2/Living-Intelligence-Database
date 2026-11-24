#!/usr/bin/env python3
"""Common-denominator check for the LID bee reference trace (v0.3, 2026-11-24).

Status of this tool: PROPOSED. It is an audit instrument, not a repository
decision. Python standard library only; no network; deterministic.

Rule tested (PROPOSED): a quantity is only comparable with another when both
carry, explicitly,
  1. an SI dimension vector (kg, m, s, K, mol),
  2. a value interval (low, central, high) as stated by the source,
  3. a time basis: INSTANT, AVERAGE_OVER:<cycle id>, PER_EVENT:<event>, or NONE,
  4. a scope string and a source URL or a DERIVED marker.
Multiplication and division combine dimensions. Addition, subtraction and ratio
comparison require identical dimensions. Any operation whose operands carry
different time bases is not computed silently: the result is flagged
DENOMINATOR_MISMATCH and kept only as a labelled bound, or refused.

No values are normalised silently, no equations are generated, and no
uncertainty is invented: intervals are propagated by interval arithmetic
over the endpoints the sources state.

Usage: python3 common_denominator.py [out.json]
"""
import json
import math
import sys

DIMS = ("kg", "m", "s", "K", "mol")


def dim(**kw):
    return tuple(kw.get(d, 0) for d in DIMS)


def dim_str(v):
    parts = [f"{d}^{p}" if p != 1 else d for d, p in zip(DIMS, v) if p]
    return "·".join(parts) if parts else "dimensionless"


class Q:
    def __init__(self, qid, what, lo, mid, hi, dimension, basis, scope, source,
                 status="TRACED", note=None, counts=None):
        self.qid, self.what = qid, what
        self.lo, self.mid, self.hi = lo, mid, hi
        self.dim, self.basis = dimension, basis
        self.scope, self.source, self.status, self.note = scope, source, status, note
        self.counts = counts  # for a rate: the event it counts (e.g. "scale")
        self.flags = []

    def as_dict(self):
        d = {"id": self.qid, "what": self.what,
             "interval": [self.lo, self.mid, self.hi],
             "dimension": dim_str(self.dim), "time_basis": self.basis,
             "scope": self.scope, "source": self.source, "status": self.status}
        if self.note:
            d["note"] = self.note
        if self.flags:
            d["flags"] = self.flags
        return d


def _basis_join(a, b, op):
    """Return (basis, flags). NONE combines with anything (a constant)."""
    if a.basis == "NONE":
        return b.basis, []
    if b.basis == "NONE" or a.basis == b.basis:
        return a.basis, []
    # per-event quantity x rate of that same event -> rate over the rate's cycle
    if op == "product":
        for x, y in ((a, b), (b, a)):
            if x.basis.startswith("PER_EVENT:") and y.counts == x.basis.split(":", 1)[1]:
                return y.basis, []
    return f"MIXED({a.basis}|{b.basis})", [
        f"DENOMINATOR_MISMATCH: {op} of {a.qid} [{a.basis}] with {b.qid} [{b.basis}]"]


def mul(qid, what, a, b, scope, note=None):
    vals = [x * y for x in (a.lo, a.hi) for y in (b.lo, b.hi)]
    basis, fl = _basis_join(a, b, "product")
    q = Q(qid, what, min(vals), a.mid * b.mid, max(vals),
          tuple(x + y for x, y in zip(a.dim, b.dim)), basis, scope,
          f"DERIVED from {a.qid} × {b.qid}", "DERIVED", note)
    q.flags = a.flags + b.flags + fl
    return q


def div(qid, what, a, b, scope, note=None):
    vals = [x / y for x in (a.lo, a.hi) for y in (b.lo, b.hi)]
    basis, fl = _basis_join(a, b, "quotient")
    q = Q(qid, what, min(vals), a.mid / b.mid, max(vals),
          tuple(x - y for x, y in zip(a.dim, b.dim)), basis, scope,
          f"DERIVED from {a.qid} / {b.qid}", "DERIVED", note)
    q.flags = a.flags + b.flags + fl
    return q


def compare(a, b):
    """Ratio a/b, only if dimension and basis match; otherwise refuse."""
    if a.dim != b.dim:
        return {"pair": [a.qid, b.qid], "result": "REFUSED",
                "reason": f"dimension {dim_str(a.dim)} vs {dim_str(b.dim)}"}
    if a.basis != b.basis:
        return {"pair": [a.qid, b.qid], "result": "REFUSED",
                "reason": f"time basis {a.basis} vs {b.basis}"}
    return {"pair": [a.qid, b.qid], "result": "COMPARABLE",
            "ratio_central": a.mid / b.mid, "dimension": dim_str(a.dim),
            "time_basis": a.basis}


FAO_WAX = "https://www.fao.org/4/i0842e/i0842e12.pdf"
FAO_T = "https://www.fao.org/4/t0104e/T0104E04.htm"
WIKI_WAX = "https://en.wikipedia.org/wiki/Beeswax"
USDA = "https://fdc.nal.usda.gov/portal-data/external/169640"
SURF = "https://en.wikipedia.org/wiki/Solar_irradiance"
ZHU = "https://pubmed.ncbi.nlm.nih.gov/18374559/"
IJFST = "https://academic.oup.com/ijfst/article/54/12/3185/7805247"
ADAMS = "https://pubmed.ncbi.nlm.nih.gov/19368902/"


def build():
    out = {"tool": "common_denominator.py", "version": "0.3", "date": "2026-11-24",
           "status": "PROPOSED", "rule": __doc__.split("Rule tested (PROPOSED):")[1]
           .split("No values")[0].strip(), "quantities": [], "derived": [],
           "comparisons": [], "cycle_ladder": [], "findings": []}

    # --- Sourced inputs -------------------------------------------------
    scale_rate = Q("R_SCALE", "wax scales secreted per wax-producing worker",
                   8 / 43200, 8 / 43200, 8 / 43200, dim(s=-1),
                   "AVERAGE_OVER:CY_SCALE", "wax-producing worker", FAO_WAX,
                   note="'8 scales every 12 h' -> 1.85e-4 scales/s; scale counted as a dimensionless event",
                   counts="scale")
    scale_mass = Q("M_SCALE", "mass per wax scale", 1e-6, 1e-6, 1e-6, dim(kg=1),
                   "PER_EVENT:scale", "beeswax", FAO_WAX,
                   note="'about 1 million scales per kg' -> 1e-6 kg; the word 'about' carries no stated ±, so no interval is invented")
    honey_per_wax = Q("K_HONEY_WAX", "honey consumed per mass of wax",
                      6.66, 8.0, 15.0, dim(), "NONE", "comb building",
                      [FAO_WAX, WIKI_WAX, FAO_T],
                      note="interval is the union of sources: 6.66–8.80 (Whitcomb via Wikipedia), ~8 (FAO), 8–15 (FAO T0104E)")
    honey_energy = Q("E_HONEY", "energy per mass of honey", 12.7e6, 12.7e6, 12.7e6,
                     dim(kg=0, m=2, s=-2), "NONE", "human-nutrition energy of honey",
                     USDA, status="PROXY",
                     note="USDA FDC 169640: 1270 kJ/100 g, derivation 'Calculated' from human energy-conversion factors. This is human metabolizable energy, used here as a PROXY for the bee's usable energy (see weld W07).")
    surf = Q("I_SURF", "clear-sky noon surface irradiance", 700, 1000, 1300,
             dim(kg=1, s=-3), "INSTANT", "sea level-ish, clear sky, noon", SURF)
    eta = Q("ETA_C3", "max solar-to-biomass conversion, C3", 0.046, 0.046, 0.046,
            dim(), "NONE", "theoretical upper bound, 30 °C, 380 ppm", ZHU,
            note="upper bound, not typical")
    sugar_m = Q("S_MANUKA", "total sugar in mānuka honey", 0.5911 - 0.0036, 0.5911,
                0.5911 + 0.0036, dim(), "NONE", "n=3, one study", IJFST,
                note="59.11 ± 0.36 g/100 g; ± as reported (dispersion statistic per source)")
    sugar_w = Q("S_MULTI", "total sugar in multifloral honey A", 0.5602 - 0.0202,
                0.5602, 0.5602 + 0.0202, dim(), "NONE", "n=3, one study", IJFST,
                note="56.02 ± 2.02 g/100 g")
    dha_m = Q("C_DHA_MANUKA", "DHA in fresh mānuka comb honey", 1192e-6, None, 5099e-6,
              dim(), "NONE", "fresh comb honey", ADAMS,
              note="1192–5099 mg/kg; no central value stated, none invented")
    for q in (scale_rate, scale_mass, honey_per_wax, honey_energy, surf, eta,
              sugar_m, sugar_w, dha_m):
        out["quantities"].append(q.as_dict())

    # --- Derived chain on the time-rate denominator ---------------------
    wax_rate = mul("D_WAX_RATE", "wax mass rate per wax-producing worker",
                   scale_rate, scale_mass, "wax-producing worker")
    e_scale = mul("D_E_SCALE_PART", "honey mass per scale", scale_mass,
                  honey_per_wax, "per scale")
    e_per_scale = mul("D_E_PER_SCALE", "honey energy per wax scale (proxy)",
                      e_scale, honey_energy, "per scale")
    e_cycle = Q("D_E_PER_CYCLE", "honey energy per 12 h scale cycle (proxy)",
                e_per_scale.lo * 8, e_per_scale.mid * 8, e_per_scale.hi * 8,
                e_per_scale.dim, "PER_EVENT:CY_SCALE", "one 12 h cycle, one worker",
                "DERIVED from D_E_PER_SCALE × 8 scales", "DERIVED")
    honey_rate = mul("D_HONEY_RATE", "honey mass rate", wax_rate, honey_per_wax,
                     "wax-producing worker")
    power = mul("D_POWER_WAX", "honey-energy throughput into wax (proxy)",
                honey_rate, honey_energy, "wax-producing worker, CY_SCALE average")
    bio_flux = mul("D_BIO_FLUX_MAX", "max biomass energy flux, clear noon", surf, eta,
                   "clear-sky noon, C3 upper bound")
    # The weld test: noon INSTANT flux against a 12-h AVERAGE power.
    area = div("D_AREA_BOUND", "leaf area at max efficiency to match wax power",
               power, bio_flux, "BOUND ONLY",
               note="Computed to show the flag. A 12-h average divided by a noon peak understates the area; a day-average irradiance is NOT sourced here, so no corrected value is given.")
    for q in (wax_rate, e_scale, e_per_scale, e_cycle, honey_rate, power, bio_flux, area):
        out["derived"].append(q.as_dict())

    # --- Comparisons: what can sit over the same denominator -----------
    out["comparisons"] = [
        compare(sugar_m, sugar_w),
        compare(power, bio_flux),
        compare(power, Q("_tmp", "", 1, 1, 1, power.dim, "INSTANT", "", "")),
        {"pair": ["C_DHA_MANUKA", "multifloral DHA"], "result": "REFUSED",
         "reason": "no counterpart quantity: multifloral regime has no reported DHA→MGO pathway (presence/absence, not a ratio)",
         "source": ADAMS},
    ]
    # rename the synthetic operand so output does not imply a real quantity
    out["comparisons"][2]["pair"][1] = "any INSTANT power (synthetic probe)"

    # --- Cycle ladder: time is the one denominator every layer shares ---
    trace_path = "reference_trace_BE_hex_v0.2.json"
    try:
        with open(trace_path) as f:
            cyc = json.load(f)["cycles"]
        for c in cyc:
            p = c.get("period_s")
            out["cycle_ladder"].append({
                "id": c["id"], "kind": c.get("kind"), "parent": c.get("parent"),
                "period_s": p, "log10_s": round(math.log10(p), 3) if p else None,
                "status": c.get("status")})
    except FileNotFoundError:
        out["cycle_ladder"] = "NOT_TESTED: v0.2 trace not found next to script"

    out["findings"] = [
        "Every sourced quantity in the energy chain could be placed on one SI dimension vector; the chain from scale rate to watts closes without any unsourced constant except the PROXY honey-energy value.",
        "The time basis, not the unit, is where combinations failed: the leaf-area bound mixes a noon INSTANT with a CY_SCALE AVERAGE and is flagged rather than reported as a result.",
        "Sugar in the two regimes is comparable on a mass basis; DHA/MGO is not comparable because one regime has no counterpart quantity. Energy is a common denominator for the sugar layer only.",
        "Time (seconds, on a named cycle) is the only denominator every node in the trace shares; it is necessary but not sufficient, because averaging over a cycle hides that cycle's phases.",
    ]
    return out


if __name__ == "__main__":
    res = build()
    path = sys.argv[1] if len(sys.argv) > 1 else "common_denominator_results.json"
    with open(path, "w") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
    for q in res["derived"]:
        print(f'{q["id"]:16s} {q["interval"][1]:.4g} [{q["interval"][0]:.4g}, {q["interval"][2]:.4g}] {q["dimension"]:18s} {q["time_basis"]} {q.get("flags", "")}')
    for c in res["comparisons"]:
        print(c["pair"], c["result"], c.get("reason", c.get("ratio_central")))
