#!/usr/bin/env python3
"""Loud validation suite for the four proposed LID schemas.

Design rule (owner preference): fail loudly. Every check is directional:
positive cases must validate, negative cases must be REJECTED, the two
cycle definitions must be byte-identical across schema files. Any
violation exits non-zero with a named failure. No warnings, no averages.

Usage: python3 tests/validate_loud.py [base_dir]
Exit 0 = all checks behaved as asserted. Exit 1 = at least one did not.
"""
import copy, json, os, sys

BASE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMAS = os.path.join(BASE, "schemas")
EXAMPLES = os.path.join(BASE, "examples")
TRACE_DIR = "/tmp/audit/lid_audit/reference"

from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError

failures = []
checks = 0

def check(name, ok, detail=""):
    global checks
    checks += 1
    if not ok:
        failures.append((name, detail))
        print(f"FAIL  {name}  {detail}")
    else:
        print(f"pass  {name}")

def load(p):
    with open(p) as f:
        return json.load(f)

ref_schema = load(os.path.join(SCHEMAS, "reference_trace.schema.json"))
cyc_schema = load(os.path.join(SCHEMAS, "cycle_registry.schema.json"))
read_schema = load(os.path.join(SCHEMAS, "attribute_reading.schema.json"))
blocks_schema = load(os.path.join(SCHEMAS, "translation_loss_blocks.schema.json"))

# ── 0. schemas are themselves valid draft-07 ───────────────────────
for n, s in [("reference_trace", ref_schema), ("cycle_registry", cyc_schema),
             ("attribute_reading", read_schema), ("translation_loss_blocks", blocks_schema)]:
    try:
        Draft7Validator.check_schema(s)
        check(f"schema self-valid draft-07: {n}", True)
    except Exception as e:
        check(f"schema self-valid draft-07: {n}", False, str(e)[:200])

def validates(schema, inst):
    return Draft7Validator(schema).is_valid(inst)

def first_error(schema, inst):
    return next(iter(Draft7Validator(schema).iter_errors(inst)), None)

# ── 1. cycle definition drift guard (cross-file) ───────────────────
check("cycle definition byte-identical across reference_trace and cycle_registry",
      ref_schema["definitions"]["cycle"] == cyc_schema["definitions"]["cycle"],
      "the two definitions diverged; edit both or neither")

# ── 2. positive: real trace files validate ─────────────────────────
v01 = load(os.path.join(TRACE_DIR, "reference_trace_BE_hex.json"))
v02 = load(os.path.join(TRACE_DIR, "reference_trace_BE_hex_v0.2.json"))
check("v0.1 trace validates", validates(ref_schema, v01),
      str(first_error(ref_schema, v01))[:300] if not validates(ref_schema, v01) else "")
check("v0.2 trace validates", validates(ref_schema, v02),
      str(first_error(ref_schema, v02))[:300] if not validates(ref_schema, v02) else "")

# ── 3. positive: cycle registry extracted from the v0.2 cycles ─────
registry = {"record": "CYCLE_REGISTRY_BE_HEX", "version": "0.2", "date": "2026-11-24",
            "status": "PROPOSED", "baseline_commit": v02["baseline_commit"],
            "cycles": v02["cycles"]}
check("cycle registry (12 real cycles) validates", validates(cyc_schema, registry),
      str(first_error(cyc_schema, registry))[:300] if not validates(cyc_schema, registry) else "")

# ── 4. positive: the outside-reader readings file validates ────────
readings = load(os.path.join(EXAMPLES, "attribute_readings.2026-11-25.json"))
check("attribute_readings example validates", validates(read_schema, readings),
      str(first_error(read_schema, readings))[:300] if not validates(read_schema, readings) else "")

# ── 5. positive: constructed translation-loss blocks file ──────────
blocks = {
  "record": "TRANSLATION_LOSS_BLOCKS_EXAMPLE", "version": "0.1", "date": "2026-11-25",
  "status": "PROPOSED",
  "regime_blocks": [{
      "id": "REGIME_HEX", "attribute": "hexagonal_cell_efficiency",
      "variables": ["wax_local_T_C", "nest_T_C"],
      "bounds": {"wax_local_T_C": [45, 62], "nest_T_C": [33, 36]},
      "timescale": "CY_SCALE", "status": "OPERATIONAL",
      "source": ["https://doi.org/10.1098/rsif.2013.0299"]}],
  "coupling_records": [{
      "source": "hive_temperature", "target": "wax_flow_rate",
      "relation": "thermal_softening",
      "regimes": [{"bounds": {"e": [0.0, 1.0]}, "form": "rate = 1 - 2*e"},
                  {"bounds": {"e": [1.0, 2.0]}, "form": None}],
      "couples": {"hive_temperature": "wax_flow_rate"},
      "outcome_state": "IN_REGIME"}],
  "dependency_records": [{
      "target": "G2D_HALES", "layer": "D0_law", "role": "governing_law",
      "required_in_regime": ["REGIME_HEX"], "equation_ref": "Hales 2001, DCG 25:1-22",
      "status": "TRACED", "source": ["https://doi.org/10.1007/s004540010071"]}],
  "confidence_records": [{
      "scope_ref": "REGIME_HEX",
      "deviation": {"value": 0.01, "kind": "expanded", "asymmetric": None},
      "certainty": {"coverage": 0.9545, "basis": "repeated measurement, coverage factor k=2"},
      "recurrence": {"cycle_type": "CY_YEAR", "cycles_observed": 3, "span": "3 seasons"}}],
  "reciprocity_records": [{
      "subject": "BE <-> MANUKA",
      "structural": {"regime": None, "timescale": None, "note": "no structural coupling"},
      "physical": {"regime": "bloom window", "timescale": "CY_MANUKA_BLOOM"},
      "functional": {"regime": "flowering", "timescale": "CY_MANUKA_BLOOM", "via": "POLLINATION"}}],
}
check("translation-loss blocks example validates", validates(blocks_schema, blocks),
      str(first_error(blocks_schema, blocks))[:300] if not validates(blocks_schema, blocks) else "")

# ── 6. negative tests: each mutation must be REJECTED ──────────────
def neg(name, schema, inst):
    check(f"rejects: {name}", not validates(schema, inst),
          "invalid instance was ACCEPTED (silent drift)")

# trace: TRACED node without source
bad = copy.deepcopy(v02)
bad["nodes"][2].pop("source", None)
bad["nodes"][2]["status"] = "TRACED"
neg("TRACED node without source", ref_schema, bad)

# trace: unknown status
bad = copy.deepcopy(v02)
bad["nodes"][0]["status"] = "VERIFIED"
neg("node with out-of-vocabulary status", ref_schema, bad)

# trace: extra property (closed object)
bad = copy.deepcopy(v02)
bad["nodes"][0]["confidence"] = 0.9
neg("node with undeclared property", ref_schema, bad)

# cycle: TRACED without source
bad = copy.deepcopy(registry)
bad["cycles"][0] = {k: v for k, v in bad["cycles"][0].items() if k != "source"}
neg("TRACED cycle without source", cyc_schema, bad)

# cycle: unknown kind
bad = copy.deepcopy(registry)
bad["cycles"][0]["kind"] = "spiral"
neg("cycle with out-of-vocabulary kind", cyc_schema, bad)

# cycle: non-positive period
bad = copy.deepcopy(registry)
bad["cycles"][0]["period_s"] = -1
neg("cycle with negative period_s", cyc_schema, bad)

# differential: variant node with non-string regime column
bad = copy.deepcopy(v02)
bad["environment_differential"]["variant_nodes"][0]["MANUKA"] = {"nested": 1}
neg("variant node with structured (non-string) regime column", ref_schema, bad)

# differential: sensitivity without scope
bad = copy.deepcopy(v02)
del bad["environment_differential"]["sensitivities"][0]["scope"]
neg("sensitivity without scope", ref_schema, bad)

# readings: 26-word quote
bad = copy.deepcopy(readings)
bad["readings"][0]["works"][0]["quote"] = " ".join(["word"] * 26)
neg("26-word quote", read_schema, bad)

# readings: out-of-vocabulary claim_support
bad = copy.deepcopy(readings)
bad["readings"][0]["claim_support"] = "MAYBE"
neg("reading with out-of-vocabulary claim_support", read_schema, bad)

# readings: source_id not a 64-hex
bad = copy.deepcopy(readings)
bad["readings"][0]["works"][0]["source_id"] = "abc"
neg("work with short source_id", read_schema, bad)

# readings: read other than 'abstract'
bad = copy.deepcopy(readings)
bad["readings"][0]["read"] = "full_text"
neg("reading with read=full_text", read_schema, bad)

# blocks: unknown outcome state
bad = copy.deepcopy(blocks)
bad["coupling_records"][0]["outcome_state"] = "SORT_OF_IN_REGIME"
neg("coupling record with out-of-vocabulary outcome state", blocks_schema, bad)

# blocks: confidence record without certainty
bad = copy.deepcopy(blocks)
del bad["confidence_records"][0]["certainty"]
neg("confidence record without certainty", blocks_schema, bad)

# blocks: regime block with invented status
bad = copy.deepcopy(blocks)
bad["regime_blocks"][0]["status"] = "GOOD_ENOUGH"
neg("regime block with out-of-vocabulary status", blocks_schema, bad)

# ── 7. known-answer: nesting invariant holds on the real cycles ────
C = {c["id"]: c for c in v02["cycles"]}
viol = []
for c in v02["cycles"]:
    p = C.get(c.get("parent"))
    if p and c.get("period_s") and p.get("period_s") and p["period_s"] / c["period_s"] <= 1:
        viol.append((c["id"], p["id"]))
check("nesting invariant holds on all 12 real cycles", not viol, str(viol))

# ── 8. known-answer: every depends_on / binds_to target exists ─────
N = {n["id"] for n in v02["nodes"]}
dangling = [d for n in v02["nodes"] for d in n.get("depends_on", []) if d not in N]
missing_binding = [t for b in v02["repo_bindings"] for t in b["binds_to"] if t not in N and t not in C]
check("no dangling depends_on in v0.2", not dangling, str(dangling))
check("no missing repo_binding targets in v0.2", not missing_binding, str(missing_binding))

print()
print(f"{checks - len(failures)}/{checks} checks behaved as asserted")
if failures:
    print("LOUD FAILURE:")
    for n, d in failures:
        print(f"  - {n}: {d}")
    sys.exit(1)
print("ALL CHECKS PASS")
sys.exit(0)
