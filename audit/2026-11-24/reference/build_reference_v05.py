#!/usr/bin/env python3
"""Build reference trace v0.5 from v0.4 (2026-11-24). v0.4 is read, never written.

Python standard library only. Deterministic. By the owner's order 'pins + entity correction'
(registry/DECLARED.json, 'schema 0.2.0 and 0.4.0; ENTITY_TRACE_DIVERGENCE; ...').

What v0.5 changes, on the root node P_HEX_CELL only:
  - the three edges added in v0.4 on a reading (REGIME_HEX, C_MELT, D4_HOT_WORKERS) carry their
    status and note ON THE EDGE, as schema 0.4.0 allows: {id, status: PROPOSED, note}. In v0.4
    this was written in the node's note, because schema 0.3.0 had no place for it.
  - a dated line: the entity file now carries scope.evidence.correction for this attribute.
Every other node, every cycle and every other edge is carried over unchanged.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "reference_trace_BE_hex_v0.4.json")
OUT = os.path.join(HERE, "reference_trace_BE_hex_v0.5.json")
DATE = "2026-11-24"
EDGE_NOTE = "used by record, previously unreachable"
ON_EDGE = ["REGIME_HEX", "C_MELT", "D4_HOT_WORKERS"]

t = json.load(open(SRC, encoding="utf-8"))
t["version"] = "0.5"
t["date"] = DATE
t["supersedes_note"] = ("v0.1 to v0.4 files kept unchanged beside this one. v0.5 moves the status of three edges "
                        "from the root's note onto the edges and notes the entity correction. "
                        "Schema: schemas/reference_trace.schema.json, adopted 0.4.0 (pin in schema_pins.json).")
r = next(n for n in t["nodes"] if n["id"] == "P_HEX_CELL")
assert all(k in r["depends_on"] for k in ON_EDGE)
r["status_history"] = r.get("status_history", []) + [{
    "version": "0.4", "status": r["status"], "date": DATE,
    "note": "changed in v0.5: the edges to REGIME_HEX, C_MELT and D4_HOT_WORKERS are written as objects carrying "
            "status PROPOSED and their note. Status of the node unchanged. The v0.4 note text stays in note."}]
r["depends_on"] = [{"id": d, "status": "PROPOSED", "note": EDGE_NOTE} if d in ON_EDGE else d for d in r["depends_on"]]
r["note"] = r["note"] + (f" | v0.5 ({DATE}): the status of the edges to REGIME_HEX, C_MELT and D4_HOT_WORKERS is now on "
                         "the edges. ontology/animal/bee.json now carries scope.evidence.correction for this "
                         "attribute (source: Hales (2001) Discrete Comput Geom 25:1-22; scope: 2D cross-section "
                         "perimeter); its original source string is unchanged. The sentence above, 'Both "
                         "differences stand in the entity file', describes the file before that correction.")

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(t, fh, indent=1, ensure_ascii=False)
print("wrote", OUT, "nodes", len(t["nodes"]), "cycles", len(t["cycles"]))
