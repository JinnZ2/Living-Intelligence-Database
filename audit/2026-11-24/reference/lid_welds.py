#!/usr/bin/env python3
"""lid_welds.py -- weld register for the LID bee audit, built on method-layer de_weld.py.

2026-11-24. Python standard library only; no network; deterministic.

What this is
------------
Each entry is one term, or one number, that the Living-Intelligence-Database
(commit 63d93c0) or this audit uses as a single unit while it carries
several independent quantities. The entries are declared as de_weld.Input
records so that method-layer's instrument, not this script, computes the
class, the cross-axis pairs, the flag and the void slots.

Reading status
--------------
The axis splits are one reader's: model-authored (Claude Opus 5.5 working
in Perplexity Computer), PROPOSED. The sentences are quoted from repository
files, or written by this audit where marked. Evidence slots carry the
source that supports each axis claim. A void evidence slot means no source
was attached, not that the claim is wrong. Couplings are declared only
where a source or the owner's statement supports them; every other pair
stays UNDECLARED, never INDEPENDENT. Nothing in the repository is renamed
or removed by this register.

Dependency
----------
Needs JinnZ2/method-layer de_weld.py. Set METHOD_LAYER to the checkout
path (default: ../../method-layer relative to this file). It was run
against method-layer commit 4636166350f46597b8566e225475ecc7412b18e9.
If the import fails, the script writes a NOT_TESTED record and exits 3.

Usage: METHOD_LAYER=/path/to/method-layer python3 lid_welds.py [out.json]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ML = os.environ.get("METHOD_LAYER", os.path.join(HERE, "..", "..", "method-layer"))
sys.path.insert(0, ML)

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "lid_welds_results.json")
try:
    from de_weld import (Axis, AxisClaim, Coupling, Input, Need, Relation, Residue,
                         Scope, de_weld, render)
except ImportError as e:  # pragma: no cover
    with open(OUT, "w") as f:
        json.dump({"status": "NOT_TESTED", "reason": f"de_weld import failed: {e}",
                   "method_layer_path": ML}, f, indent=1)
    print("NOT_TESTED: de_weld.py not importable from", ML)
    sys.exit(3)

P, O, D = "PROPOSED", "OBSERVED", "DERIVED"
DATE = "2026-11-24"
PROV = "model-authored reading (Claude Opus 5.5, Perplexity Computer), " + DATE
OTH = Axis.OTHER

HALES = "https://link.springer.com/article/10.1007/s004540010071"
FEJES = "https://projecteuclid.org/journalArticle/Download?urlid=bams/1183526078"
FAO_WAX = "https://www.fao.org/4/i0842e/i0842e12.pdf"
KARI = "https://www.ncbi.nlm.nih.gov/pmc/articles/3730681"
NAT26 = "https://www.nature.com/articles/s44434-026-00004-2"
GUM = "https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf"
TSI = "https://esdpubs.nasa.gov/sgpubs/content/A_new_lower_value_of_total_solar_irradiance_Evidence_and_climate_significance"
COMPASS = "https://pmc.ncbi.nlm.nih.gov/articles/PMC4667876/"
IJFST = "https://academic.oup.com/ijfst/article/54/12/3185/7805247"
ADAMS = "https://pubmed.ncbi.nlm.nih.gov/19368902/"
USDA = "https://fdc.nal.usda.gov/portal-data/external/169640"
WING = "https://www.pnas.org/doi/10.1073/pnas.0506590102"
DEV = "https://www.fao.org/4/X0083E/X0083E03.htm"
BEE = "ontology/animal/bee.json @ 63d93c0"


ENCODING = {"mode": "descriptive"}


def oth(name, claim, ev=None, st=P, **scope):
    """A named descriptive sub-quantity.

    de_weld counts every non-descriptive axis, OTHER included, as evaluative
    (EVALUATIVE_AXES in de_weld.py). These welds join descriptive quantities,
    so the primary encoding puts them on DESCRIPTIVE with the name in the
    claim text. The 'other' mode is kept as an encoding control.
    """
    if ENCODING["mode"] == "other":
        return AxisClaim(OTH, claim, Scope(**scope), evidence=ev, status=st, other_name=name)
    return AxisClaim(Axis.DESCRIPTIVE, f"[{name}] {claim}", Scope(**scope), evidence=ev, status=st)


def welds():
  return (
    # W01 -------------------------------------------------------------------
    ("W01", "the hexagon 'efficiency' number", Input(
        term="hexagonal_cell_efficiency = 0.97",
        sentence=("Ratio of honey volume stored per unit wax mass in hexagonal cells compared to "
                  "the next-best regular tessellation. Derives from the honeycomb conjecture"
                  f" [{BEE}, attributes.hexagonal_cell_efficiency.scope.definition]"),
        axes=(
            oth("geometry_2d", "the regular hexagonal partition minimises perimeter per unit area "
                "in the plane (a proof about 2D perimeter, not wax mass or volume)", HALES, O,
                where="the plane"),
            oth("geometry_3d", "a real cell is 3D; its rhombic-dodecahedral base is not the "
                "minimal-surface closure", FEJES, O, where="3D cell"),
            oth("material_energy_cost", "wax mass is paid for in honey, about 8 kg per kg wax",
                FAO_WAX, O, who="colony"),
            oth("formation_process", "how the hexagon forms is CONTESTED: wax flow vs thermal "
                "expansion vs self-organised angular redistribution", f"{KARI} ; {NAT26}", O,
                when="comb building"),
            AxisClaim(Axis.ABUNDANCE, "uses less wax per unit stored honey", Scope(use="storage"),
                      evidence=None, status=P),
            AxisClaim(Axis.QUALITY, "'efficiency' as a merit of the design, 0.97", Scope(),
                      evidence=BEE, status=O),
        ),
        couplings=(
            Coupling(0, 4, Relation.COUPLED, "the 2D perimeter result is what the economy claim borrows"),
            Coupling(0, 1, Relation.CONFLICTING, "the 2D optimum does not carry to the 3D closure"),
        ),
        residue=(Residue("which ratio 0.97 is, over which boundary (2D section, 3D cell, wax "
                         "mass, honey cost), against which comparison tessellation", DATE,
                         (Need.SCIENCE, Need.AUDIT)),),
        used_in_judgment=True, provenance=PROV)),
    # W02 -------------------------------------------------------------------
    ("W02", "one confidence number", Input(
        term="relational_confidence = 0.98",
        sentence=f"relational_confidence: 0.98 [{BEE}, attributes.hexagonal_cell_efficiency.scope.evidence]",
        axes=(
            oth("scope", "the conditions under which the value holds", None, O,
                who="owner resolution, 2026-11-24"),
            oth("deviation", "± around the value (GUM: expanded uncertainty U)", GUM, O),
            oth("certainty", "coverage probability attached to ±U", GUM, O),
            oth("recurrence", "how often the pattern recurs across domains; kept separate by owner",
                None, O, who="owner resolution, 2026-11-24"),
            AxisClaim(Axis.QUALITY, "a single 0-1 trust score", Scope(), evidence=BEE, status=O),
        ),
        couplings=(Coupling(1, 2, Relation.COUPLED, "U has meaning only with its coverage"),),
        residue=(Residue("which of the four the stored 0.98 encodes; it exceeds the repository's "
                         "own formula by +0.54 on average across entities (audit baseline)", DATE,
                         (Need.AUDIT,)),),
        used_in_judgment=True, provenance=PROV)),
    # W03 -------------------------------------------------------------------
    ("W03", "the dependencies field", Input(
        term="dependencies",
        sentence=(f"dependencies: [golden_ratio, pi] / [cell_type, construction_temperature, "
                  f"wax_purity] / [swarm_hunger_state, weather_window, ...] [{BEE}]"),
        axes=(
            oth("D0_constant", "mathematical constants (pi, golden_ratio)", BEE, O),
            oth("D2_condition", "physical conditions (construction_temperature)", BEE, O),
            oth("D3_material", "material state (wax_purity)", BEE, O),
            oth("D4_state", "organism or colony state (swarm_hunger_state)", BEE, O),
            oth("sensitivity_sign", "whether the value rises or falls with the dependency; "
                "not stated in the field", None, P),
        ),
        couplings=(),
        residue=(Residue("which layer each string belongs to, and its signed, scoped effect; "
                         "6 of 9 bound in trace v0.2, 3 UNKNOWN/UNCHECKED", DATE, (Need.AUDIT,)),),
        used_in_judgment=None, provenance=PROV)),
    # W04 -------------------------------------------------------------------
    ("W04", "the word 'cycle'", Input(
        term="cycle",
        sentence="'cycles are cycles of whatever within the context of that' (owner, this session)",
        axes=(
            oth("oscillation", "repeats with a period (wingbeat ≈230 Hz)", WING, O),
            oth("developmental_window", "runs once per life stage (21-day worker development)", DEV, O),
            oth("transient", "relaxes once and stops (circle→hexagon ≈6 s)", KARI, O),
            oth("superposition", "union of many cycles (multifloral season); unsourced", None, P),
            oth("nesting", "slow cycle's phase sets the fast cycle's regime (owner)", None, O,
                who="owner resolution, 2026-11-24"),
        ),
        couplings=(Coupling(0, 4, Relation.COUPLED, "nesting is between named cycles"),),
        residue=(Residue("which cycle, at what period, nested in which parent", DATE, (Need.AUDIT,)),),
        used_in_judgment=None, provenance=PROV)),
    # W05 -------------------------------------------------------------------
    ("W05", "the Sun", Input(
        term="sunlight",
        sentence="E_SUN in trace v0.2 (audit text): one node, two roles",
        axes=(
            oth("energy_source", "1360.8 ± 0.5 W/m² at 1 AU feeds photosynthesis → nectar sugar", TSI, O),
            oth("information_source", "the sun's azimuth is the compass reference the waggle "
                "dance encodes", COMPASS, O),
            oth("cycle_driver", "sets the day (CY_DAY entrainment) and the year", None, O),
        ),
        couplings=(Coupling(0, 1, Relation.INDEPENDENT,
                            "the compass reads direction, not flux: a cloudy-day energy drop "
                            "need not change the bearing (PROPOSED reading; NOT_TESTED)"),),
        residue=(Residue("no repository entity represents incoming solar radiation", DATE,
                         (Need.AUDIT,)),),
        used_in_judgment=None, provenance=PROV)),
    # W06 -------------------------------------------------------------------
    ("W06", "'honey' across forage regimes", Input(
        term="honey (mānuka vs wildflower)",
        sentence="audit text: same bee, same physics, different forage",
        axes=(
            oth("energy_layer", "total sugar alike: 59.11 ± 0.36 vs 56.02 ± 2.02 g/100 g, n=3",
                IJFST, O),
            oth("chemistry_layer", "DHA→MGO pathway in mānuka; absent in clover until DHA is added",
                ADAMS, O),
            AxisClaim(Axis.QUALITY, "'better honey' / grade", Scope(use="market"), status=P),
        ),
        couplings=(Coupling(0, 1, Relation.INDEPENDENT,
                            "sugar alike while chemistry diverges in the cited studies"),),
        residue=(Residue("whether wax composition or honey-per-wax differ by forage: no source", DATE,
                         (Need.SCIENCE,)),),
        used_in_judgment=None, provenance=PROV)),
    # W07 -------------------------------------------------------------------
    ("W07", "the energy content of honey", Input(
        term="1270 kJ / 100 g",
        sentence="USDA FoodData Central 169640, Energy, derivation 'Calculated'",
        axes=(
            oth("human_metabolizable", "energy a human derives, by conversion factors", USDA, O),
            oth("bee_usable", "energy a bee derives from the same honey; not found", None, P),
            oth("combustion", "bomb-calorimeter enthalpy; not looked up", None, P),
        ),
        couplings=(),
        residue=(Residue("which of the three the wax-power figure should use", DATE, (Need.SCIENCE,)),),
        used_in_judgment=None, provenance=PROV)),
    # W08 -------------------------------------------------------------------
    ("W08", "two layer stacks", Input(
        term="layer L0–L5 / D0–D5",
        sentence="docs/GROUNDING_LAYERS.md (L0 classical physics … L5 social) vs this audit's D0–D5",
        axes=(
            oth("repository_stack", "L0 physics, L1 thermodynamics, L2 planetary, L3 ecological, "
                "L4 biomechanics, Lε epistemic membrane, L5 social", "docs/GROUNDING_LAYERS.md @ 63d93c0", O),
            oth("audit_stack", "D0 physics … D5 relation, built from the owner's dependency answer",
                None, O, who="owner resolution, 2026-11-24"),
        ),
        couplings=(),
        residue=(Residue("whether D-n maps to L-n; same shape, mapping not declared by the owner",
                         DATE, (Need.AUDIT,)),),
        used_in_judgment=None, provenance=PROV)),
    # W09 -------------------------------------------------------------------
    ("W09", "verb to noun", Input(
        term="hexagonal_cell_efficiency (attribute)",
        sentence="'every noun is a verb in our language… there is no static noun' (owner)",
        axes=(
            oth("process", "building: secretion every 12 h, heating, a ≈6 s relaxation", FAO_WAX, O),
            oth("state", "a stored attribute value with no time index", BEE, O),
        ),
        couplings=(Coupling(0, 1, Relation.CONFLICTING,
                            "the attribute has no slot for the cycle the process runs on"),),
        residue=(Residue("how the schema would carry a process (rate, cycle, scope) without "
                         "forcing it into a static noun", DATE, (Need.ENGINEERING,)),),
        used_in_judgment=None, provenance=PROV)),
    # W10 -------------------------------------------------------------------
    ("W10", "the common denominator itself", Input(
        term="0.0188 W (wax-producing worker, CY_SCALE average)",
        sentence="common_denominator.py D_POWER_WAX (audit output)",
        axes=(
            oth("cycle_average", "throughput averaged over one 12 h scale cycle", None, D),
            oth("phase_profile", "how the throughput varies within the cycle; not sourced", None, P),
        ),
        couplings=(),
        residue=(Residue("averaging over a cycle hides its phases; the average must carry the "
                         "cycle's name", DATE, (Need.SCIENCE,)),),
        used_in_judgment=None, provenance=PROV)),
  )


def main():
    out = {"tool": "lid_welds.py", "date": DATE, "status": P,
           "instrument": "JinnZ2/method-layer de_weld.py",
           "method_layer_commit": "4636166350f46597b8566e225475ecc7412b18e9",
           "repository_commit": "63d93c00951b14ed7352891747468c9b65cca146",
           "welds": []}
    ENCODING["mode"] = "other"
    out["encoding_control"] = {
        "note": "same declarations with sub-quantities on Axis.OTHER; shows de_weld reading them as evaluative",
        "results": {w: {"term_class": de_weld(i).term_class.value,
                        "flags": [f.value for f in de_weld(i).flags]} for w, _, i in welds()}}
    ENCODING["mode"] = "descriptive"
    for wid, label, inp in welds():
        rec = de_weld(inp)
        out["welds"].append({"id": wid, "label": label, "record": rec.to_dict()})
        print(f"== {wid} {label}")
        print(render(rec))
        print()
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
