#!/usr/bin/env python3
"""
build_crosswalk.py -- writes crosswalk_D_L.json: PROPOSED L-layer tags for the 28 nodes of
reference trace v0.3 (bee hexagonal cell). Stdlib only. Deterministic. Fails if the trace's
node set and the tag table differ in any id, so a node cannot be added or dropped silently.

Two axes, held separately (option (b) of OPEN_QUESTIONS #3):
  D = role in the dependency chain  (D0 law, D1 energy, D2 condition, D3 material, D4 entity, D5 pattern)
  L = substrate layer               (docs/GROUNDING_LAYERS.md: L0 classical physics, L1 thermodynamics,
                                     L2 planetary, L3 ecological, L4 biological, Lε epistemic membrane,
                                     L5 social/cultural)
A node keeps its D tag (OBSERVED in the trace) and gets one or more PROPOSED L tags with a reason.
"""
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRACE = HERE.parent / "reference" / "reference_trace_BE_hex_v0.3.json"

# id: (L tags, reason, flag or None)
TAGS = {
 "P_HEX_CELL": (["Lε.enc"], "the recorded attribute value: the point where a measured pattern becomes a database number", None),
 "G2D_HALES": (["L0"], "GROUNDING_LAYERS.md places geometric invariants and HEX at L0", "MATH_NOT_SUBSTRATE"),
 "G3D_FEJES": (["L0"], "geometric optimum of the 3D cell; same placement as G2D_HALES", "MATH_NOT_SUBSTRATE"),
 "G3D_DAUTER": (["L0"], "improved geometric optimum; same placement as G2D_HALES", "MATH_NOT_SUBSTRATE"),
 "C_WALL": (["L4"], "real wall thickness is a property of what workers build", None),
 "F_FLOW": (["L1"], "visco-elastic flow and surface-energy minimisation are thermodynamic mechanisms", "D0_HOLDS_A_MECHANISM"),
 "C_FLOW_T": (["L1"], "a material temperature at which wax flows", None),
 "C_MELT": (["L1"], "a phase transition of a material", None),
 "C_BROOD_T": (["L4", "L3"], "temperature held by colony physiology (L4) across ambient conditions (L3)", None),
 "REGIME_HEX": (["L1", "L4"], "derived from wax temperatures (L1) and colony-held nest temperature (L4)", "SPANS_LAYERS"),
 "M_WAX": (["L4"], "a biosynthesised material; its chemistry is set by the organism", None),
 "M_GLANDS": (["L4"], "worker anatomy and age", None),
 "E_WAX_COST": (["L4"], "metabolic conversion of sugar to wax", None),
 "E_BODY_HEAT": (["L4"], "thoracic muscle metabolism", None),
 "E_NECTAR": (["L4", "L3"], "plant photosynthesis (L4) supplying a pollinator (L3 relation)", None),
 "E_SUN": (["L2"], "irradiance at 1 AU: the planetary energy input; L2 is the nearest layer in the stack", "NO_ASTRONOMICAL_LAYER"),
 "L_CONSERVE": (["L1"], "open far-from-equilibrium systems: thermodynamics", None),
 "D4_FLOWERS": (["L3"], "flowering plants as forage: an ecological relation", None),
 "D4_HOT_WORKERS": (["L4"], "workers' bodies as the heat source", None),
 "E_SURFACE": (["L2"], "atmospheric attenuation: a planetary constraint", None),
 "E_PHOTO_MAX": (["L4", "L1"], "photosynthetic conversion limit: biological, bounded thermodynamically", None),
 "I_SUNCOMPASS": (["L4", "L2"], "a sensing behaviour (L4) that reads a sky pattern made by the atmosphere (L2)", None),
 "L_SCATTER": (["L0"], "scattering optics: classical physics", None),
 "D4_MANUKA": (["L4", "L3"], "a plant species (L4) whose nectar is the forage (L3)", None),
 "E_NECTARY_PHOTO": (["L4"], "photosynthesis inside the nectary", None),
 "D4_WILDFLOWER": (["L3"], "a multi-species forage community", None),
 "H_DHA_MGO": (["L1"], "non-enzymatic first-order chemical kinetics in stored honey", None),
 "P_BUILT_MEASURED": (["Lε.obs", "L4"], "a measurement (Lε.obs) of what bees built (L4)", None),
}

FLAGS = {
 "MATH_NOT_SUBSTRATE": "a theorem holds whatever the physical conditions are. GROUNDING_LAYERS.md puts geometric invariants at L0, so the tag follows the document, but a theorem is not a substrate that can change. Owner decides whether mathematics gets its own marker outside L.",
 "D0_HOLDS_A_MECHANISM": "the trace tags F_FLOW as D0_law, but it is a mechanism (wax flows when heated) that depends on D2 conditions. D0 then holds both laws and mechanisms.",
 "SPANS_LAYERS": "a derived regime draws on more than one layer; one L tag would hide that.",
 "NO_ASTRONOMICAL_LAYER": "the stack starts at L0 physics and has no layer for the star; the solar input is filed at L2, where it meets the planet.",
}


def main(out):
    trace = json.loads(TRACE.read_bytes())
    ids = [n["id"] for n in trace["nodes"]]
    missing, extra = sorted(set(ids) - set(TAGS)), sorted(set(TAGS) - set(ids))
    if missing or extra or len(ids) != len(set(ids)):
        sys.exit(f"FAIL: trace/tag mismatch missing={missing} extra={extra}")
    nodes = []
    for n in trace["nodes"]:
        L, why, flag = TAGS[n["id"]]
        nodes.append({"id": n["id"], "D": n["layer"], "D_status": "OBSERVED (in trace v0.3)",
                      "L": L, "L_status": "PROPOSED", "L_reason": why, "flag": flag})
    pairs = {}
    for x in nodes:
        for l in x["L"]:
            pairs.setdefault(x["D"], {}).setdefault(l, 0)
            pairs[x["D"]][l] += 1
    doc = {"record": "CROSSWALK_D_L", "status": "PROPOSED", "date": "2026-11-24",
           "option": "OPEN_QUESTIONS #3 option (b): two axes, declared crosswalk; D and L are not aliases",
           "axes": {"D": "role in the dependency chain", "L": "substrate layer (docs/GROUNDING_LAYERS.md)"},
           "membrane_reading": "Lε is where a measured node becomes a recorded D5 attribute (P_HEX_CELL is Lε.enc; P_BUILT_MEASURED carries Lε.obs).",
           "trace": {"path": "reference/reference_trace_BE_hex_v0.3.json",
                     "sha256": hashlib.sha256(TRACE.read_bytes()).hexdigest(), "nodes": len(ids)},
           "existing_field_note": "120 entity files carry substrate_layer with values substrate_primary / language_primary / both (OBSERVED). That is a third, coarser axis (substrate L0-L4 vs language L5) and is not changed here.",
           "biosphere_placement": {
               "id": "BIOSPHERE", "source": "ontology/relational/biosphere_reference.json (PROPOSED, unindexed)",
               "D": "D4_entity at earth scale; its state (temperature, water, oxygen, carbon, soil, season) acts as D2 conditions for every contained entity",
               "L": ["L3", "L2"], "L_reason": "the record's scope is 'life-sustaining zone, not planetary energy balance' (owner's order): ecological (L3), bounded by planetary constraints (L2)",
               "status": "PROPOSED",
               "note": "In the bee trace, E_SUN, E_SURFACE and L_SCATTER sit outside or at the edge of the biosphere and the D4 forage nodes sit inside it. A BIOSPHERE node would sit between them: the sun feeds it, and it holds the conditions the bee depends on."},
           "layer_document_note": "GROUNDING_LAYERS.md files BE at L3 as an entity. The node-level tags here put colony physiology at L4. Both can hold, the entity in its web and its body as carrier, but the two placements differ and the owner should know.",
           "flags": FLAGS, "D_by_L_counts": pairs, "nodes": nodes}
    Path(out).write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({"nodes": len(nodes), "D_by_L_counts": pairs,
                      "flagged": {f: [x["id"] for x in nodes if x["flag"] == f] for f in FLAGS}}, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(HERE / "crosswalk_D_L.json"))
