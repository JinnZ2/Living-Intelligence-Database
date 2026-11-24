#!/usr/bin/env python3
"""Build reference trace v0.3 from v0.2 (2026-11-24). v0.2 is read, never written.

Python standard library only. Deterministic. Changes are additions and dated
notes. Earlier claim text is kept, and an earlier status is recorded in
`status_history` when it changes.

What v0.3 adds, each one checked against the source this session:
  - C_FLOW_T  TRACED -> CONTESTED. Bauer & Bienefeld 2013 measured wax at
              33.6-37.6 °C while hexagons were built, against about 45 °C in
              Karihaloo 2013. Both are kept.
  - F_FLOW    a fourth account (direct construction), plus Pirk 2004 and
              Smith 2021. Correction: the source labelled 'Nature 2026' in
              v0.2 is in npj Entomology.
  - G3D_DAUTER  new D0 node: the Fejes Tóth gain improved to 0.50% by a 2.8°
              face tilt (Dauter & Jaskolski 2025).
  - P_BUILT_MEASURED  new D5 node: what bees actually build (Yang et al. 2022).
These leads came from an outside reader's report (Kimi, 2026-11-25). Every
one was re-fetched before being added.
"""
import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "reference_trace_BE_hex_v0.2.json")
OUT = os.path.join(HERE, "reference_trace_BE_hex_v0.3.json")
DATE = "2026-11-24"

BAUER = "https://pubmed.ncbi.nlm.nih.gov/23149932/"
PIRK = "https://pubmed.ncbi.nlm.nih.gov/15257392/"
SMITH = "https://pubmed.ncbi.nlm.nih.gov/34312229/"
DAUTER = "https://pmc.ncbi.nlm.nih.gov/articles/PMC11873813/"
YANG = "https://hal.science/hal-04025696/document"
GALLO = "https://www.nature.com/articles/s44434-026-00004-2"

v2 = json.load(open(SRC))
t = copy.deepcopy(v2)
t["version"] = "0.3"
t["date"] = DATE
t["supersedes_note"] = ("v0.1 and v0.2 files kept unchanged beside this one. v0.3 adds nodes and dated "
                        "notes; leads from an outside reader (Kimi, 2026-11-25), each re-fetched.")
N = {n["id"]: n for n in t["nodes"]}


def note(n, text):
    prev = n.get("note")
    add = f"v0.3 ({DATE}): {text}"
    n["note"] = f"{prev} | {add}" if prev else add


# C_FLOW_T: contested temperature
c = N["C_FLOW_T"]
c["status_history"] = [{"version": "0.2", "status": c["status"]}]
c["status"] = "CONTESTED"
c["source"] = c["source"] + [BAUER]
note(c, "CONTESTED. Bauer & Bienefeld 2013 (infrared and thermographic video) measured wax at 33.6–37.6 °C "
        "during hexagonal-cell construction, below the ~40 °C they take as needed for liquid equilibrium; "
        "Karihaloo 2013 gives about 45 °C. Both kept; not reconciled. The original claim text is unchanged.")

# REGIME_HEX inherits the dispute through its lower bound
note(N["REGIME_HEX"], "the 45 °C lower bound comes from C_FLOW_T, now CONTESTED; the regime is CONDITIONAL on "
                      "which account holds. Bauer & Bienefeld's 33.6–37.6 °C would fall below this bound.")

# F_FLOW: fourth account, more sources, label correction
f = N["F_FLOW"]
f["source"] = f["source"] + [BAUER, PIRK, SMITH]
note(f, "(d) direct construction: bees shape wax with antennae, mandibles and legs, wax 33.6–37.6 °C, "
        "no liquid equilibrium (Bauer & Bienefeld, Naturwissenschaften 100:45–49, 2013). Earlier "
        "liquid-equilibrium account: Pirk et al. 2004. Irregular building under constraint: Smith, Napp & "
        "Petersen, PNAS 118:e2103605118, 2021. Label correction: the v0.2 source cited as 'Nature 2026' is "
        "Gallo, Bridges, Woodgate & Chittka, npj Entomology, published 2026-10-06 " + GALLO + ".")

# New D0 node
t["nodes"].append({
    "id": "G3D_DAUTER", "layer": "D0_law", "role": "governing_law",
    "claim": ("The Fejes Tóth cell's surface-area economy can be improved beyond the FT gain to 0.50% by "
              "increasing the tilt of the hexagonal faces by 2.8°."),
    "status": "TRACED", "source": [DAUTER],
    "value": {"y": 0.005, "unit": "fraction of cell surface area saved", "deviation": "not stated (geometric result)"},
    "note": f"v0.3 ({DATE}): Dauter & Jaskolski, Acta Cryst. A 2025. Mathematical; an optimum, not a "
            "measurement of bees. Lead from Kimi (2026-11-25), who called it a review; it presents new analysis.",
})

# New D5 node: what is actually built
t["nodes"].append({
    "id": "P_BUILT_MEASURED", "layer": "D5_pattern", "role": "pattern",
    "claim": ("Natural combs of Apis cerana cerana and Apis mellifera ligustica contain no more than 18% "
              "Fejes Tóth cells on average; bees can build them but mostly build three-rhombus cells. "
              "Measured dihedral angle at the cell bottom: 108.70° ± 0.16° (n = 238 cells), against a "
              "theoretical 120°."),
    "status": "TRACED", "source": [YANG],
    "value": {"y": 108.70, "unit": "degrees",
              "deviation": "± 0.16 as reported; statistic type and species of this sample not checked; "
                           "other samples 109.60 ± 0.44, 108.70 ± 0.20, 111.10 ± 0.26"},
    "depends_on": ["G3D_FEJES", "G3D_DAUTER", "F_FLOW"],
    "note": f"v0.3 ({DATE}): Yang et al., Apidologie 53:6, 2022. The measured gap between the D0 optimum and "
            "the built artifact. It is a sourced quantity, not noise.",
})
N["P_HEX_CELL"]["depends_on"] = N["P_HEX_CELL"]["depends_on"] + ["P_BUILT_MEASURED"]
note(N["P_HEX_CELL"], "now also depends on P_BUILT_MEASURED (what is built), beside the D0 optima.")

with open(OUT, "w") as fh:
    json.dump(t, fh, indent=1, ensure_ascii=False)
print("wrote", OUT, "nodes", len(t["nodes"]))
