#!/usr/bin/env python3
"""Build reference trace v0.4 from v0.3 (2026-11-24). v0.3 is read, never written.

Python standard library only. Deterministic. By the owner's order 'trace v0.4'
(registry/DECLARED.json, 'trace v0.4: severity assignment; schema pinning; pilot rebuilt from v0.4').
Every change leaves a status_history entry on the node or cycle it touches, holding the v0.3 state.

What v0.4 changes:
  - G2D_HALES  scope stated: the 2D cross-section perimeter only (Hales, Discrete Comput Geom
               25:1-22, 2001; journal reference read on the arXiv record this session). The v0.3
               note is kept, word for word, in status_history.
  - G3D_BASE_NOT_OPTIMAL  new D0 node: the 3D cell base bees build is not the optimum
               (Fejes Toth 1964; 0.50% improvement, 2025). Status per source read: the 2025
               article was read this session; the 1964 paper was not opened (ams.org unreachable).
  - P_HEX_CELL depends_on += G3D_BASE_NOT_OPTIMAL, REGIME_HEX, C_MELT, D4_HOT_WORKERS.
               The last three were used by the record and were unreachable from the root.
               The 0.3.0 schema has no per-edge record, so the edge status (PROPOSED) and its
               note are written in the root's status_history and note.
  - CY_WILDFLOWER  PROPOSED_UNSOURCED -> PROPOSED with unsourced true; legacy_status kept.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "reference_trace_BE_hex_v0.3.json")
OUT = os.path.join(HERE, "reference_trace_BE_hex_v0.4.json")
DATE = "2026-11-24"
PMC = "https://pmc.ncbi.nlm.nih.gov/articles/PMC11873813/"
ARXIV = "https://arxiv.org/abs/math/9906042"

t = json.load(open(SRC, encoding="utf-8"))
t["version"] = "0.4"
t["date"] = DATE
t["supersedes_note"] = ("v0.1, v0.2 and v0.3 files kept unchanged beside this one. v0.4 states the scope of "
                        "G2D_HALES, adds one D0 node, adds four edges from the root and maps one cycle status. "
                        "Schema: schemas/reference_trace.schema.json, adopted 0.3.0 (pin in schema_pins.json).")
N = {n["id"]: n for n in t["nodes"]}
C = {c["id"]: c for c in t["cycles"]}


def history(x, text):
    x["status_history"] = x.get("status_history", []) + [{"version": "0.3", "status": x["status"], "date": DATE,
                                                           "note": text}]


def note(n, text):
    prev = n.get("note")
    add = f"v0.4 ({DATE}): {text}"
    n["note"] = f"{prev} | {add}" if prev else add


# G2D_HALES: scope stated. The v0.3 note moves, unchanged, into status_history.
g = N["G2D_HALES"]
history(g, "changed in v0.4: scope stated as the 2D cross-section perimeter. Status unchanged. "
           "The v0.3 note, word for word: " + g["note"])
g["note"] = (f"v0.4 ({DATE}): scope: the 2D cross-section perimeter only. The theorem is about a partition of "
             "the plane into regions of equal area; it says nothing about cell depth, the cell base, volume or "
             "wax mass. Reference: Hales, Discrete Comput Geom 25:1-22 (2001), journal reference as given on the "
             "arXiv record. What the v0.3 note said about the repository record is kept in status_history and on "
             "the root node P_HEX_CELL.")

# New D0 node
t["nodes"].append({
    "id": "G3D_BASE_NOT_OPTIMAL", "layer": "D0_law", "role": "governing_law",
    "claim": ("The three-rhombus (444) cell base that honeybees build is not the most economical in wax. "
              "Fejes Tóth (1964) found a base of two hexagons and two rhombi (6464) whose gain over the 444 base "
              "is less than 0.35% of the hexagonal cross-section area; increasing the tilt of its hexagonal faces "
              "by 2.8° raises the gain to 0.50% over the 444 base."),
    "status": "TRACED",
    "source": [PMC, "Fejes Tóth, L. (1964). Bull. Am. Math. Soc. 70, 468–481 (as listed in the references of the "
                    "article above; not opened)"],
    "value": {"y": 0.5, "unit": "% surface-area economy over the tri-rhombic 444 base",
              "deviation": "not stated (geometric result)"},
    "depends_on": ["G3D_FEJES", "G3D_DAUTER"],
    "status_history": [{"version": "0.3", "status": "NOT_PRESENT", "date": DATE,
                        "note": "node added in v0.4. It joins G3D_FEJES and G3D_DAUTER, which stay as they are."}],
    "note": f"v0.4 ({DATE}): status per source read. Read this session: the 2025 article (PMC11873813): 'less "
            "than 0.35%' for the Fejes Tóth gain, '0.50% better than the tri-rhombic 444 variant', 2.8° tilt. "
            "Not opened: the 1964 paper (ams.org did not answer from this machine); the owner's order gives it as "
            "Bull AMS 70(4), the article lists volume 70, pages 468–481; the issue number is not confirmed here. "
            "Mathematical; an optimum, not a measurement of bees.",
})

# Root: four more edges
r = N["P_HEX_CELL"]
used = ["REGIME_HEX", "C_MELT", "D4_HOT_WORKERS"]
history(r, "changed in v0.4: depends_on += G3D_BASE_NOT_OPTIMAL, REGIME_HEX, C_MELT, D4_HOT_WORKERS. Status "
           "unchanged. Edges to REGIME_HEX, C_MELT and D4_HOT_WORKERS: PROPOSED; used by record, previously "
           "unreachable.")
r["depends_on"] = r["depends_on"] + ["G3D_BASE_NOT_OPTIMAL"] + used
note(r, "depends_on += G3D_BASE_NOT_OPTIMAL (new D0 node) and REGIME_HEX, C_MELT, D4_HOT_WORKERS. The last three "
        "edges are PROPOSED: used by record, previously unreachable. The record itself is unchanged in "
        "ontology/animal/bee.json: its citation string for the honeycomb proof reads '36:5-69' and '(1999)' where "
        "the published reference is 25:1-22 (2001), and it claims 3D volume per wax mass where G2D_HALES covers a "
        "2D perimeter. Both differences stand in the entity file; this trace does not edit it.")

# CY_WILDFLOWER: retired status mapped
w = C["CY_WILDFLOWER"]
history(w, "changed in v0.4: PROPOSED_UNSOURCED is retired; written PROPOSED with unsourced true.")
w["legacy_status"] = w["status"]
w["status"] = "PROPOSED"
w["unsourced"] = True

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(t, fh, indent=1, ensure_ascii=False)
print("wrote", OUT, "nodes", len(t["nodes"]), "cycles", len(t["cycles"]))
