#!/usr/bin/env python3
"""Build reference trace v0.6 from v0.5 (2026-11-24). v0.5 is read, never written.

Python standard library only. Deterministic. By the owner's order 'close-out'
(registry/DECLARED.json, 'close-out: pinned label ...; divergence by identity; ...; trace v0.6').

What v0.6 changes:
  - P_HEX_CELL  the edge to G3D_BASE_NOT_OPTIMAL carries status 'DERIVED (basis: OBSERVED)'.
  - G2D_HALES   scope '2D cross-section perimeter' as a field (it was prose in the note), and the
                reference string 'Hales (2001) Discrete Comput Geom 25:1-22' added to its sources
                beside the two URLs. The divergence rule compares both with the entity's
                evidence.correction by identity; without them no trace could meet it.
Everything else is carried over unchanged.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "reference_trace_BE_hex_v0.5.json")
OUT = os.path.join(HERE, "reference_trace_BE_hex_v0.6.json")
DATE = "2026-11-24"
HALES_REF = "Hales (2001) Discrete Comput Geom 25:1-22"
HALES_SCOPE = "2D cross-section perimeter"

t = json.load(open(SRC, encoding="utf-8"))
t["version"] = "0.6"
t["date"] = DATE
t["supersedes_note"] = ("v0.1 to v0.5 files kept unchanged beside this one. v0.6 puts a status on the root's edge to "
                        "G3D_BASE_NOT_OPTIMAL and gives G2D_HALES its scope as a field and its reference string as a "
                        "source. Schema: schemas/reference_trace.schema.json, adopted 0.5.0 (pin in schema_pins.json).")
N = {n["id"]: n for n in t["nodes"]}


def history(x, text):
    x["status_history"] = x.get("status_history", []) + [{"version": "0.5", "status": x["status"], "date": DATE,
                                                           "note": text}]


r = N["P_HEX_CELL"]
assert "G3D_BASE_NOT_OPTIMAL" in r["depends_on"]
history(r, "changed in v0.6: the edge to G3D_BASE_NOT_OPTIMAL is written as an object with status "
           "'DERIVED (basis: OBSERVED)'. Status of the node unchanged.")
r["depends_on"] = [{"id": d, "status": "DERIVED (basis: OBSERVED)"} if d == "G3D_BASE_NOT_OPTIMAL" else d
                   for d in r["depends_on"]]
r["note"] += f" | v0.6 ({DATE}): the edge to G3D_BASE_NOT_OPTIMAL now carries status 'DERIVED (basis: OBSERVED)' (owner's order)."

g = N["G2D_HALES"]
history(g, "changed in v0.6: scope written as a field; the reference string added to source beside the two URLs. "
           "Status unchanged.")
g["scope"] = HALES_SCOPE
g["source"] = g["source"] + [HALES_REF]
g["note"] += (f" | v0.6 ({DATE}): the scope is now also the field scope. The source list gains the reference string, "
              "the same work the two URLs point to; it is the string ontology/animal/bee.json carries as "
              "evidence.correction.source, so the two can be compared by source id.")

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(t, fh, indent=1, ensure_ascii=False)
print("wrote", OUT, "nodes", len(t["nodes"]), "cycles", len(t["cycles"]))
