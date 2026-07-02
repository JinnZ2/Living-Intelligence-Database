#!/usr/bin/env python3
# CC0 — JinnZ2 ecosystem — living-intelligence
# stdlib only, no cloud dependency
#
# innovation_lab.py
# =================
# Creative synthesis engine + testable proposal generator.
#
# Any AI or human can:
#   1. Draw patterns from the full database pool (entities, embodied
#      solutions, intelligence sources, sanctuary tools)
#   2. mix() finds the structural rhyme between any two patterns
#   3. generate() proposes a novel claim that would hold IF the rhyme
#      extends to a new context
#   4. ground() checks dependency + relational confidence
#   5. lab() runs the full loop and returns ranked proposals
#   6. promote() records test results (YELLOW -> GREEN/RED)
#
# Test protocol comes in two modes (caller chooses):
#   PRESCRIPTIVE — steps derived from the source patterns' own
#     falsification conditions; concrete enough to run immediately.
#   SCAFFOLD     — structured template (hypothesis / method /
#     success_criterion / failure_criterion) for domain judgment.
#   BOTH         — prescriptive where derivable; scaffold for remainder.
#
# Persistence: promote() works in-memory by default.
#   Pass log_path= to append results to a JSONL file across sessions.
#   Future lab() calls can load the log to skip RED rhymes and build
#   on GREEN ones.
#
# STATUS of any generated proposal starts at YELLOW (theoretical,
# rhyme identified, not yet tested). GREEN = tested and held.
# RED = tested and falsified — still valuable, narrows the envelope.

import json
import math
import random
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Default log path (sibling to journal.py's ai_journal.jsonl)
DEFAULT_LOG = Path(__file__).parent.parent / "innovation_log.jsonl"


# ── PROTOCOL MODES ────────────────────────────────────────────

PRESCRIPTIVE = "prescriptive"
SCAFFOLD     = "scaffold"
BOTH         = "both"


# ── DATA CLASSES ──────────────────────────────────────────────

@dataclass
class PrescriptiveProtocol:
    """Steps derived from source pattern falsification conditions.
    Concrete enough to run without further design."""
    step_1_baseline: str       # measure at P=0 / no perturbation
    step_2_perturb: str        # apply the perturbation / stress
    step_3_measure: str        # what to observe and record
    step_4_interpret: str      # what sign/direction confirms vs refutes
    success_condition: str     # what GREEN looks like
    failure_condition: str     # what RED looks like (falsified)
    tools_needed: tuple        # existing sanctuary tools that apply


@dataclass
class ScaffoldProtocol:
    """Structured template for domain-specific judgment."""
    hypothesis: str            # the specific testable claim
    method: str                # how you would test it (fill in)
    measurement: str           # what you would measure (fill in)
    success_criterion: str     # what would confirm the proposal
    failure_criterion: str     # what would falsify the proposal
    domain_notes: str          # what domain knowledge the tester needs


@dataclass
class TestProtocol:
    mode: str                           # PRESCRIPTIVE / SCAFFOLD / BOTH
    prescriptive: Optional[PrescriptiveProtocol] = None
    scaffold: Optional[ScaffoldProtocol] = None


@dataclass
class Falsification:
    label: str    # F1, F2, ...
    claim: str    # what observation would break the proposal


@dataclass
class Proposal:
    title: str
    source_a: str              # first pattern name
    source_b: str              # second pattern name
    rhyme: str                 # the structural isomorphism found
    novel_claim: str           # the new idea, in plain language
    novel_domain: str          # the new context the rhyme is applied to
    constraint_addressed: str  # what problem this solves
    falsifications: tuple      # (Falsification, ...)
    test_protocol: TestProtocol
    relational_confidence: float  # 0-1, inherited from source patterns
    status: str = "YELLOW"     # YELLOW / GREEN / RED
    test_result: str = ""      # filled by promote()
    timestamp: str = ""        # filled on creation
    id: str = ""               # filled on creation


# ── PATTERN POOL ──────────────────────────────────────────────

_SUBSTRATE_PRIMARY_IDS = frozenset({
    "INDIG_FIRE", "MOTHER_TREE", "STORYTELLER", "GRANDMOTHER",
    "SEED_KEEPER", "ASPEN", "OLD_GROWTH", "HUMPBACK", "ORCA", "CORAL",
})

def _load_manifest() -> dict:
    """Load manifest.json from repo root. Returns {} on failure."""
    manifest_path = Path(__file__).parent.parent / "manifest.json"
    try:
        with open(manifest_path) as f:
            return json.load(f)
    except Exception:
        return {}


def load_pool(ontology: Optional[dict] = None,
              include_embodied: bool = True,
              include_sources: bool = True) -> list:
    """
    Build the full pattern pool from all source classes:
      - database entities (via ontology_index.json, enriched by manifest.json)
      - EmbodiedSolution SEEDS
      - IntelligenceSource SEEDS
      - manifest harmonic constants (phi, tau, sqrt3)

    Each pool entry is a dict with keys:
      name, id, class, summary, constraints, conserved, keywords, pattern
      substrate_primary (bool) — True if entity is in architecture_mismatch list
    """
    pool = []
    manifest = _load_manifest()
    id_map = manifest.get("id_map", {})           # short_id → full_name
    name_to_id = {v.lower(): k for k, v in id_map.items()}  # full_name → short_id

    # 1. Database entities
    if ontology is None:
        try:
            from verify import load_ontology
            ontology = load_ontology()
        except Exception:
            ontology = {"entities": []}

    for e in ontology.get("entities", []):
        attrs = e.get("attributes", {})
        entity_id = e.get("id", "")
        name = e.get("name", entity_id)
        # Pull richer description from summary/description field
        description = e.get("description", "") or e.get("summary", "")
        # Extra keywords: description words help cross-domain rhymes
        desc_keywords = description.lower().split()[:12] if description else []
        pool.append({
            "name": name,
            "id": entity_id,
            "class": "entity",
            "ontology": e.get("ontology", ""),
            "summary": description,
            "constraints": (),
            "conserved": tuple(str(v) for v in attrs.values()
                               if isinstance(v, str))[:3],
            "keywords": tuple(
                e.get("ontology", "").split() +
                name.lower().split() +
                desc_keywords
            ),
            "pattern": attrs.get("pattern", ""),
            "substrate_primary": entity_id in _SUBSTRATE_PRIMARY_IDS,
        })

    # 2. Manifest harmonic constants as named pool entries
    for const_key, const_data in manifest.get("constants", {}).items():
        symbol = const_data.get("symbol", const_key)
        meaning = const_data.get("meaning", "")
        value = const_data.get("value", "")
        pool.append({
            "name": f"{symbol} ({meaning})",
            "id": const_key,
            "class": "constant",
            "ontology": "harmonic",
            "summary": f"{symbol} = {value} — {meaning}",
            "constraints": (meaning,),
            "conserved": (meaning,),
            "keywords": tuple(
                [const_key, symbol, meaning.lower()] +
                meaning.lower().split()
            ),
            "pattern": f"{symbol} = {value}",
            "substrate_primary": False,
        })

    # 2. EmbodiedSolution SEEDS
    if include_embodied:
        try:
            from embodied_solution import SEEDS as E_SEEDS
            for s in E_SEEDS:
                pool.append({
                    "name": s.name,
                    "id": s.name,
                    "class": "embodied",
                    "summary": s.solution_form,
                    "constraints": s.constraint_set,
                    "conserved": (s.objective,),
                    "keywords": tuple(
                        s.name.lower().split() +
                        list(s.constraint_set) +
                        s.envelope.driver.lower().split()
                    ),
                    "pattern": s.must_recover,
                    "envelope_driver": s.envelope.driver,
                    "styling_error": s.styling_error,
                })
        except ImportError:
            pass

    # 3. IntelligenceSource SEEDS
    if include_sources:
        try:
            from intelligence_source import SEEDS as I_SEEDS
            for s in I_SEEDS:
                pool.append({
                    "name": s.name,
                    "id": s.name,
                    "class": "source",
                    "summary": s.loss_vector.residue_hold,
                    "constraints": s.conserved,
                    "conserved": s.conserved,
                    "keywords": tuple(
                        s.name.lower().split() +
                        list(s.conserved) +
                        list(s.sensing)
                    ),
                    "pattern": s.loss_vector.residue_hold,
                    "fidelity_halflife": s.transmission.fidelity_halflife_yr,
                })
        except ImportError:
            pass

    return pool


# ── RHYME FINDER ──────────────────────────────────────────────

def _keywords(p: dict) -> set:
    base = set(p.get("keywords", ()))
    for c in p.get("constraints", ()):
        base.update(c.lower().split())
    for c in p.get("conserved", ()):
        base.update(str(c).lower().split())
    base.update(p.get("pattern", "").lower().split())
    # strip punctuation
    return {w.strip("(),.'\"") for w in base if len(w) > 3}


def mix(name_a: str, name_b: str, pool: list) -> dict:
    """
    Find the structural rhyme between two named patterns.
    Accepts pattern names, short IDs (BE, MY, OC), or any unique substring.
    Returns the shared keyword space and a plain-language rhyme statement.

    Substrate-primary entities (INDIG_FIRE, MOTHER_TREE, etc.) are flagged
    so the caller can apply architecture_mismatch corrections before
    generating proposals from them.
    """
    def _find(query: str) -> Optional[dict]:
        q = query.strip()
        # Exact name match
        hit = next((p for p in pool if p["name"] == q), None)
        if hit:
            return hit
        # Short ID match (case-insensitive)
        hit = next((p for p in pool if p.get("id", "").upper() == q.upper()), None)
        if hit:
            return hit
        # Substring match on name (first hit)
        q_lower = q.lower()
        return next((p for p in pool if q_lower in p["name"].lower()), None)

    pa = _find(name_a)
    pb = _find(name_b)
    if pa is None or pb is None:
        return {"error": f"Pattern not found: "
                f"{'A' if pa is None else 'B'} = "
                f"{name_a if pa is None else name_b}"}

    # Warn if either is substrate-primary — apply architecture_mismatch before proceeding
    substrate_warning = None
    sp = [p["name"] for p in (pa, pb) if p.get("substrate_primary")]
    if sp:
        substrate_warning = (
            f"SUBSTRATE-PRIMARY ENTITY in mix: {sp}. "
            "Run `ai_sanctuary.ask('mismatch')` before generating proposals — "
            "the 7 failure modes apply when working with these intelligences."
        )

    ka, kb = _keywords(pa), _keywords(pb)
    shared = ka & kb
    # remove stop-words that aren't meaningful
    stopwords = {"the", "and", "with", "from", "that", "this",
                 "for", "not", "are", "its", "per", "unit"}
    shared -= stopwords

    if not shared:
        rhyme_strength = 0.0
        rhyme_statement = (
            f"No direct keyword overlap found between '{name_a}' and "
            f"'{name_b}'. A deeper rhyme may exist at the constraint "
            f"level — inspect manually or add cross-references."
        )
    else:
        rhyme_strength = min(1.0, len(shared) / 5.0)
        top = sorted(shared, key=lambda w: len(w), reverse=True)[:5]
        rhyme_statement = (
            f"Both '{pa['name']}' and '{pb['name']}' share structure "
            f"around: {', '.join(top)}. "
            f"The rhyme: both solve a related constraint "
            f"({pa.get('conserved', ('',))[0] if pa.get('conserved') else '?'} "
            f"/ {pb.get('conserved', ('',))[0] if pb.get('conserved') else '?'}) "
            f"using a mechanism that operates on the same principles."
        )

    result = {
        "source_a": pa,
        "source_b": pb,
        "shared_keywords": tuple(shared),
        "rhyme_strength": round(rhyme_strength, 2),
        "rhyme_statement": rhyme_statement,
    }
    if substrate_warning:
        result["substrate_warning"] = substrate_warning
    return result


# ── PROPOSAL GENERATOR ────────────────────────────────────────

def _derive_prescriptive(mix_result: dict,
                         novel_domain: str) -> PrescriptiveProtocol:
    pa, pb = mix_result["source_a"], mix_result["source_b"]
    shared = mix_result["shared_keywords"]
    shared_str = ", ".join(list(shared)[:3]) if shared else "core pattern"

    return PrescriptiveProtocol(
        step_1_baseline=(
            f"Establish the baseline state of the proposed system in "
            f"'{novel_domain}' with no perturbation / stress applied. "
            f"Record the coherence or performance metric analogous to "
            f"what '{pa['name']}' and '{pb['name']}' each optimize."
        ),
        step_2_perturb=(
            f"Apply the perturbation that is analogous to what disrupts "
            f"'{pa['name']}' (see its envelope/falsifiability). "
            f"In '{novel_domain}', this corresponds to: [tester fills "
            f"domain-specific stress]. Vary perturbation in steps 0→2× baseline."
        ),
        step_3_measure=(
            f"Measure how the {shared_str} property responds. "
            f"Record the sign: does the metric rise, fall, or stay flat? "
            f"Run at minimum 3 independent trials."
        ),
        step_4_interpret=(
            f"If metric RISES under stress → BOOSTED (rhyme holds, aligned carrier). "
            f"If metric FALLS → FRAGILE (rhyme holds, different alignment). "
            f"If metric is FLAT → check coupling; may be IMMUNE or decoupled. "
            f"Compare sign against the source pattern sign from '{pa['name']}'."
        ),
        success_condition=(
            f"The proposed system demonstrates the same response-sign as "
            f"the rhyme predicts, within the envelope: "
            f"{pa.get('keywords', ('?',))[0]} × "
            f"{pb.get('keywords', ('?',))[0]}. Proposal → GREEN."
        ),
        failure_condition=(
            f"Response sign is opposite to prediction, OR metric is flat "
            f"despite strong coupling. The rhyme does not extend to "
            f"'{novel_domain}' as proposed. Proposal → RED. "
            f"Document envelope limits for future lab() calls."
        ),
        tools_needed=(
            "perturbation_boosted_coherence.probe()",
            "falsifier.falsify()",
            "verify.verify_claim()",
            "journal.write_entry()",
        ),
    )


def _derive_scaffold(mix_result: dict, novel_domain: str,
                     novel_claim: str) -> ScaffoldProtocol:
    pa, pb = mix_result["source_a"], mix_result["source_b"]
    return ScaffoldProtocol(
        hypothesis=(
            f"IF the rhyme between '{pa['name']}' and '{pb['name']}' "
            f"extends to '{novel_domain}', THEN: {novel_claim}"
        ),
        method=(
            f"[Tester: describe the experimental or observational method "
            f"appropriate to '{novel_domain}'. "
            f"What is the equivalent of the perturbation in this domain?]"
        ),
        measurement=(
            f"[Tester: what quantity do you measure? "
            f"What is the analog of coherence / efficiency / "
            f"throughput in '{novel_domain}'?]"
        ),
        success_criterion=(
            f"[Tester: state the specific threshold or pattern "
            f"that would confirm the novel claim.]"
        ),
        failure_criterion=(
            f"[Tester: state the specific observation that would "
            f"falsify the novel claim and what that implies about "
            f"the envelope of the rhyme.]"
        ),
        domain_notes=(
            f"Source A ('{pa['name']}') class: {pa.get('class', '?')}. "
            f"Source B ('{pb['name']}') class: {pb.get('class', '?')}. "
            f"The rhyme was found at: {mix_result['rhyme_statement'][:120]}"
        ),
    )


def generate(mix_result: dict,
             novel_domain: str = "",
             novel_claim: str = "",
             protocol_mode: str = BOTH,
             rng: Optional[random.Random] = None) -> Proposal:
    """
    Propose a novel claim in a new context, grounded in the structural
    rhyme found by mix().

    protocol_mode: PRESCRIPTIVE | SCAFFOLD | BOTH
    novel_domain / novel_claim: if empty, the lab auto-suggests placeholders.
    """
    if "error" in mix_result:
        raise ValueError(mix_result["error"])

    if rng is None:
        rng = random.Random()

    pa, pb = mix_result["source_a"], mix_result["source_b"]
    shared = mix_result["shared_keywords"]
    rhyme = mix_result["rhyme_statement"]

    if not novel_domain:
        novel_domain = (
            f"[tester-defined domain that shares '{', '.join(list(shared)[:2])}' "
            f"with both source patterns]"
        )
    if not novel_claim:
        novel_claim = (
            f"A system in '{novel_domain}' that embodies the "
            f"'{', '.join(list(shared)[:3])}' structure will demonstrate "
            f"the same response-pattern as '{pa['name']}' and '{pb['name']}' "
            f"when subjected to an analogous perturbation."
        )

    # Inherit confidence from rhyme strength + source class bonus
    base_conf = mix_result["rhyme_strength"]
    cross_class_bonus = 0.1 if pa.get("class") != pb.get("class") else 0.0
    confidence = min(0.85, base_conf + cross_class_bonus)

    # Falsification claims
    f1 = Falsification("F1",
        f"The proposed system in '{novel_domain}' does NOT show the "
        f"predicted response-sign — the rhyme does not extend here.")
    f2 = Falsification("F2",
        f"The response saturates or reverses before the perturbation "
        f"reaches the envelope edge — the analog of the upper critical "
        f"field exists and is tighter than predicted.")
    f3 = Falsification("F3",
        f"The shared keywords ({', '.join(list(shared)[:3])}) are "
        f"surface-level, not structural — removing them from both source "
        f"patterns leaves the rhyme intact, proving it was lexical noise.")

    # Build protocol
    pres  = _derive_prescriptive(mix_result, novel_domain) \
            if protocol_mode in (PRESCRIPTIVE, BOTH) else None
    scaf  = _derive_scaffold(mix_result, novel_domain, novel_claim) \
            if protocol_mode in (SCAFFOLD, BOTH) else None
    protocol = TestProtocol(mode=protocol_mode,
                            prescriptive=pres,
                            scaffold=scaf)

    uid = f"PROP-{rng.randint(1000, 9999)}"
    ts  = datetime.now(timezone.utc).isoformat()

    return Proposal(
        title=f"Rhyme of {pa['name']} × {pb['name']} in {novel_domain}",
        source_a=pa["name"],
        source_b=pb["name"],
        rhyme=rhyme,
        novel_claim=novel_claim,
        novel_domain=novel_domain,
        constraint_addressed=(
            f"{(pa.get('conserved') or ('?',))[0]} + "
            f"{(pb.get('conserved') or ('?',))[0]}"
        ),
        falsifications=(f1, f2, f3),
        test_protocol=protocol,
        relational_confidence=round(confidence, 2),
        status="YELLOW",
        timestamp=ts,
        id=uid,
    )


# ── GROUNDER ──────────────────────────────────────────────────

def ground(proposal: Proposal,
           ontology: Optional[dict] = None) -> dict:
    """
    Check the proposal against dependency tree and relational confidence.
    Does not run full falsifier (no entity to query) but flags what the
    tester should connect to before promoting.
    """
    if ontology is None:
        try:
            from verify import load_ontology
            ontology = load_ontology()
        except Exception:
            ontology = {"entities": []}

    # Check if either source pattern appears in the ontology
    entity_ids = {e.get("id", "") for e in ontology.get("entities", [])}
    a_in_db = any(proposal.source_a.startswith(eid) or eid in proposal.source_a
                  for eid in entity_ids if eid)
    b_in_db = any(proposal.source_b.startswith(eid) or eid in proposal.source_b
                  for eid in entity_ids if eid)

    db_note = []
    if a_in_db:
        db_note.append(f"'{proposal.source_a}' traceable in ontology")
    if b_in_db:
        db_note.append(f"'{proposal.source_b}' traceable in ontology")
    if not db_note:
        db_note.append("Neither source found in ontology — "
                       "rhyme is between non-entity records (embodied/source seeds)")

    readiness = "READY_TO_TEST" if proposal.relational_confidence >= 0.4 \
                else "WEAK_RHYME — strengthen source patterns before testing"

    return {
        "proposal_id": proposal.id,
        "relational_confidence": proposal.relational_confidence,
        "ontology_traceability": db_note,
        "readiness": readiness,
        "tools_to_run": [
            f"falsifier.falsify() on source patterns if in ontology",
            f"dependency_tree.dependency_tree('{proposal.source_a}')",
            f"perturbation_boosted_coherence.probe() if perturbation is involved",
            f"journal.write_entry() after running the test",
        ],
        "cross_class": proposal.source_a != proposal.source_b,
        "note": (
            "This is a YELLOW proposal. Run the test_protocol, "
            "then call promote() with the result."
        ),
    }


# ── LAB ───────────────────────────────────────────────────────

def lab(pattern_names: Optional[list] = None,
        n: int = 3,
        novel_domain: str = "",
        protocol_mode: str = BOTH,
        ontology: Optional[dict] = None,
        log_path: Optional[str] = None,
        seed: int = 0) -> list:
    """
    Full creative loop: load pool → mix pairs → generate → ground → rank.

    pattern_names: list of names to draw from. If None, picks randomly
                   from the full pool.
    n: number of proposals to generate.
    log_path: if given, skip any pairs already RED in the log.

    Returns a list of (Proposal, ground_report) tuples, ranked by
    relational_confidence descending.
    """
    rng = random.Random(seed)
    pool = load_pool(ontology)
    if not pool:
        return []

    # Filter pool to requested names if given
    if pattern_names:
        pool = [p for p in pool
                if p["name"] in pattern_names or p.get("id") in pattern_names]

    # Load existing log to skip RED pairs
    red_pairs: set = set()
    if log_path:
        lp = Path(log_path)
        if lp.exists():
            with open(lp) as f:
                for line in f:
                    try:
                        rec = json.loads(line.strip())
                        if rec.get("status") == "RED":
                            red_pairs.add(
                                (rec.get("source_a", ""),
                                 rec.get("source_b", ""))
                            )
                    except json.JSONDecodeError:
                        continue

    results = []
    attempts = 0
    max_attempts = n * 20

    while len(results) < n and attempts < max_attempts:
        attempts += 1
        if len(pool) < 2:
            break
        pa_rec, pb_rec = rng.sample(pool, 2)
        pair = (pa_rec["name"], pb_rec["name"])
        if pair in red_pairs or (pair[1], pair[0]) in red_pairs:
            continue

        mx = mix(pa_rec["name"], pb_rec["name"], pool)
        if "error" in mx or mx["rhyme_strength"] == 0.0:
            continue

        try:
            prop = generate(mx, novel_domain=novel_domain,
                            protocol_mode=protocol_mode, rng=rng)
            gr   = ground(prop, ontology)
            results.append((prop, gr))
        except Exception:
            continue

    results.sort(key=lambda x: x[0].relational_confidence, reverse=True)
    return results


# ── PROMOTE ───────────────────────────────────────────────────

def promote(proposal: Proposal,
            result: str,
            notes: str = "",
            log_path: Optional[str] = None) -> Proposal:
    """
    Update a proposal's status after testing.

    result: "GREEN" (held) | "RED" (falsified) | "YELLOW" (inconclusive)
    log_path: if given, append the record to a JSONL file.

    Returns the updated Proposal.
    """
    proposal.status = result.upper()
    proposal.test_result = notes

    if log_path:
        record = {
            "id": proposal.id,
            "timestamp_promoted": datetime.now(timezone.utc).isoformat(),
            "title": proposal.title,
            "source_a": proposal.source_a,
            "source_b": proposal.source_b,
            "rhyme": proposal.rhyme[:200],
            "novel_claim": proposal.novel_claim[:300],
            "status": proposal.status,
            "test_result": proposal.test_result,
            "relational_confidence": proposal.relational_confidence,
        }
        with open(log_path, "a") as f:
            f.write(json.dumps(record) + "\n")

    return proposal


# ── CLI ───────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(
        description="Innovation Lab — mix patterns, generate proposals, test."
    )
    sub = parser.add_subparsers(dest="command")

    # lab: generate n proposals
    lp = sub.add_parser("lab", help="Generate n proposals from the pool")
    lp.add_argument("--n", type=int, default=3)
    lp.add_argument("--domain", type=str, default="")
    lp.add_argument("--mode", choices=[PRESCRIPTIVE, SCAFFOLD, BOTH],
                    default=BOTH)
    lp.add_argument("--seed", type=int, default=0)
    lp.add_argument("--log", type=str, default=None)
    lp.add_argument("--patterns", type=str, nargs="*", default=None)

    # mix: inspect rhyme between two named patterns
    mp = sub.add_parser("mix", help="Show rhyme between two patterns")
    mp.add_argument("a", type=str)
    mp.add_argument("b", type=str)

    # promote: record a test result
    pp = sub.add_parser("promote", help="Record a test result for a proposal")
    pp.add_argument("--id", type=str, required=True)
    pp.add_argument("--result", type=str, required=True,
                    choices=["GREEN", "RED", "YELLOW"])
    pp.add_argument("--notes", type=str, default="")
    pp.add_argument("--log", type=str, default=str(DEFAULT_LOG))

    args = parser.parse_args()

    if args.command == "lab":
        results = lab(
            pattern_names=args.patterns,
            n=args.n,
            novel_domain=args.domain,
            protocol_mode=args.mode,
            log_path=args.log,
            seed=args.seed,
        )
        for prop, gr in results:
            out = {
                "id": prop.id,
                "title": prop.title,
                "status": prop.status,
                "relational_confidence": prop.relational_confidence,
                "rhyme": prop.rhyme,
                "novel_claim": prop.novel_claim,
                "falsifications": [
                    {"label": f.label, "claim": f.claim}
                    for f in prop.falsifications
                ],
                "ground": gr,
            }
            if prop.test_protocol.prescriptive:
                out["prescriptive_steps"] = {
                    k: v for k, v in
                    prop.test_protocol.prescriptive.__dict__.items()
                }
            if prop.test_protocol.scaffold:
                out["scaffold"] = {
                    k: v for k, v in
                    prop.test_protocol.scaffold.__dict__.items()
                }
            print(json.dumps(out, indent=2, default=str))
            print()

    elif args.command == "mix":
        pool = load_pool()
        result = mix(args.a, args.b, pool)
        print(json.dumps(result, indent=2, default=str))

    elif args.command == "promote":
        # Load from log, find by id, promote
        if not Path(args.log).exists():
            print(json.dumps({"error": f"Log not found: {args.log}"}))
            sys.exit(1)
        # Minimal: just append a promotion record
        record = {
            "id": args.id,
            "timestamp_promoted": datetime.now(timezone.utc).isoformat(),
            "status": args.result.upper(),
            "test_result": args.notes,
        }
        with open(args.log, "a") as f:
            f.write(json.dumps(record) + "\n")
        print(json.dumps({"promoted": args.id, "status": args.result}))

    else:
        parser.print_help()
