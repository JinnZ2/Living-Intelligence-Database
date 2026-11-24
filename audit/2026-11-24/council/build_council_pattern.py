#!/usr/bin/env python3
"""
build_council_pattern.py -- writes council_pattern.json, a pattern-only COUNCIL record.
Python standard library only. Deterministic. No network.

The owner said on 2026-11-24 that the pattern of the council is what matters, not the
people. This record holds the pattern and names no tribe, nation or person, following the
convention of ontology/social/stone_art_ledger.json. The example file
validation/example/council.json is not edited; its unsourced attributions stay held there.

The owner's words are kept verbatim, spelling included, and are not defined further. The
owner says the English terms "dont quite fit", so each structural field below is a reading
of them, tagged PROPOSED, and the words stay the primary text.

The 'coordination' block is checked with the repository's own
validation/coordination_check.py check_block(); the build fails if that check reports any
failure. Pass the repository root as the first argument.
"""
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OWNER = "contributor statement in conversation, 2026-11-24 (contributor-held; not a published citation)"
EXAMPLE = "validation/example/council.json (repository example; description_source_status UNSOURCED)"
ARENA = "JinnZ2/AI-arena@bb9ab96 protocol/arena_protocol.md"

OWNER_WORDS = [
    {"text": "Thé pattern of the council is what’s important, not the people.", "date": "2026-11-24"},
    {"text": "It would be similar to an Oracle in AI terms i guess", "date": "2026-11-24"},
    {"text": "Ones who looks to things at the Root dependancy, Long cycles, wisdom Accounting, or whatever other English terms dont quite fit", "date": "2026-11-24"},
]

COORD = {
    "carrier": "A question that cannot be settled inside the cycle that raises it, carried with its map of agreement and disagreement (in AI terms, an arena convergence map).",
    "signal": "A proposed action whose consequences reach the root dependencies or outlast the cycle that proposes it. Objection is a signal: 'Objection is a form of teaching, not obstruction.'",
    "record": "The decision, held with the root dependencies it was traced to, the horizon it was weighed against, and the objections that taught it.",
    "closure": "'the council does not close until the silence is comfortable.' A zero-sum outcome does not close: it is read as a scope error and the scope is widened toward the root dependency before deliberation continues.",
    "trust_basis": "Decisions that hold across long cycles. The account is kept by how many decisions are reversed or significantly modified within a generation; legitimacy is 'earned through demonstrated long-view reasoning, memory of precedent, and willingness to absorb short-term cost for long-term coherence.'",
    "energy_cost": {"joules": None, "per": None, "note": "unmeasured. The cost the example file names is time and short-term cost absorbed for long-term coherence."},
    "loop_topology": {
        "cycles": [
            {"id": "L1", "path": "question with its map -> deliberation, objection read as teaching -> comfortable silence -> decision recorded with roots, horizon and objections -> consequences seen -> reversal or durability counted -> trust adjusted"},
            {"id": "L2", "path": "outcome found zero-sum -> read as scope error -> scope widened toward the root dependency -> deliberation reopens"},
            {"id": "L3", "path": "decision -> held across generations up to the horizon -> those who inherit the record review it against what came to pass"},
        ],
        "observer_cuts": [
            {"cut": "one meeting observed, answer taken as output (a one-shot oracle reading)", "cycles_surviving": [],
             "note": "no cycle closes inside the cut: the pattern reads as slow consensus, and the accounting and the horizon are invisible"},
            {"cut": "followed for one generation (25 years)", "cycles_surviving": ["L1", "L2"],
             "note": "the reversal count becomes visible; the horizon cycle does not close"},
            {"cut": "followed across generations to the horizon", "cycles_surviving": ["L1", "L2", "L3"], "note": None},
        ],
    },
    "assumption_trace": [
        "a decision closes on a majority vote",
        "authority comes from office or election",
        "a decision is judged when it is made",
        "disagreement is noise to be removed",
        "one party's gain is another party's loss",
    ],
    "sources": {
        "carrier": [OWNER, ARENA],
        "signal": [EXAMPLE + ": consensus_protocol"],
        "record": [OWNER],
        "closure": [EXAMPLE + ": consensus_protocol", OWNER + " (zero-sum outcomes are scope errors; source beyond the owner UNKNOWN)"],
        "trust_basis": [EXAMPLE + ": decision_reversal_rate, legitimacy_source"],
        "energy_cost": [EXAMPLE + ": legitimacy_source"],
        "loop_topology": [OWNER, EXAMPLE],
        "assumption_trace": [OWNER, EXAMPLE],
    },
    "status": {
        "carrier": "PROPOSED", "signal": "PROPOSED", "record": "PROPOSED", "closure": "PROPOSED",
        "trust_basis": "PROPOSED", "energy_cost": None, "loop_topology": "DERIVED (basis: PROPOSED)",
        "assumption_trace": "PROPOSED",
    },
    "notes": {
        "_source": "Quoted lines come from the repository example file, whose description is UNSOURCED; the pattern lines in it are kept, the attributions are not carried. Everything else is a reading of the owner's words, PROPOSED.",
        "loop_topology": "The three cycles and the observer cuts are this record's reading, not the owner's statement. The first cut is why a plain oracle reading loses the pattern.",
        "assumption_trace": "What an outside reader is likely to bring that the pattern does not hold. Not tested.",
    },
}

DOC = {
    "id": "COUNCIL_PATTERN",
    "name": "Council pattern (no people named)",
    "ontology": "social",
    "status": "PROPOSED",
    "date": "2026-11-24",
    "co_creation": True,
    "description": "The council as a pattern: those who look to the root dependency, the long cycle, and the accounting of wisdom, in the owner's words, which the owner says English does not quite fit. No specific tribe, nation or person is named in this record.",
    "owner_words": OWNER_WORDS,
    "english_fit": {
        "state": "APPROXIMATE",
        "statement": "The owner's phrases are the primary text. The functions and the coordination block are readings of them and carry PROPOSED. If a reading and the owner's words differ, the words hold.",
    },
    "functions": [
        {"owner_term": "Root dependancy",
         "reading": "before a decision closes, trace what it rests on down the dependency chain, to the biosphere and physics, not only to the parties present",
         "where_in_repo": ["audit D0-D5 dependency chain and crosswalk_D_L.json", "validation/dependency_tree.py", "ontology/relational/biosphere_reference.json (BIOSPHERE)"],
         "status": "PROPOSED"},
        {"owner_term": "Long cycles",
         "reading": "weigh a decision against the cycles it will outlast, nested inside one another, with a declared horizon",
         "where_in_repo": [EXAMPLE + ": intergenerational_decision_horizon = 7", "ontology/temporal/cycle.json (CYCLE)"],
         "owner_context": "earlier in this session the owner described cycles as named and nested, and said AI has its own cycles (wording as summarised, not verbatim)",
         "status": "PROPOSED"},
        {"owner_term": "wisdom Accounting",
         "reading": "keep an account of how decisions held up: what was reversed, what lasted, what was owed and completed; trust follows the account",
         "where_in_repo": [EXAMPLE + ": decision_reversal_rate (reversed or modified within 25 years)", "ontology/social/stone_art_ledger.json (STONE_LEDGER: an obligation is recorded until it completes)"],
         "status": "PROPOSED"},
    ],
    "oracle_analogy": {
        "stated_by": "owner, tentatively ('i guess')",
        "fits": "the council is what the arena consults when its convergence map cannot settle what to do, and the arena acts on the answer",
        "differs": [
            "authority is earned and can be lost, not given by construction",
            "an answer can be objected to, and the objection becomes content",
            "the answer carries a horizon of generations",
            "the oracle is scored over time by the reversal account",
        ],
        "reading": "an accountable oracle",
        "status": "PROPOSED",
    },
    "coordination": COORD,
    "complements": {
        "repo": "JinnZ2/AI-arena", "pinned_commit": "bb9ab96", "path": "protocol/arena_protocol.md",
        "roles": "the arena maps ('A session ends with a convergence map, not a verdict'); the council decides",
        "weld": "the arena does not collapse disagreement into consensus; the council closes on comfortable silence. Neither protocol is changed; the hand-off is the weld.",
        "status": "PROPOSED",
    },
    "links": [
        {"rel": "connected_to", "to": "STONE_LEDGER", "status": "PROPOSED", "note": "accounting: what is owed is recorded until it completes"},
        {"rel": "connected_to", "to": "CYCLE", "status": "PROPOSED", "note": "long cycles"},
    ],
    "held_links": {
        "_note": "Not in links: neither target is in the index, so the build would stop on them, and 'pattern_of' is not in the schema's rel list. Held here; they move into links when their targets are indexed (owner's decision). registry/known_held_links.json is not edited.",
        "items": [
            {"rel": "pattern_of", "to": "COUNCIL", "where": "validation/example/council.json (unindexed; not edited)", "status": "PROPOSED"},
            {"rel": "connected_to", "to": "BIOSPHERE", "where": "ontology/relational/biosphere_reference.json (unindexed: relational/ has no schema)", "note": "root dependency", "status": "PROPOSED"},
        ],
    },
    "not_carried": "The names of peoples and the cross-domain examples in validation/example/council.json. They remain there, held under its _audit_note ('unsourced; not consented; not promoted').",
    "metadata": {"scope_note": "Name no specific tribe, nation or person in this record.",
                 "placement": "ontology/social/council_pattern.json, placed on the owner's yes of 2026-11-24. The copy at audit/2026-11-24/council/council_pattern.json is byte-identical. The record's content stays PROPOSED."},
}


def main(repo, out):
    sys.path.insert(0, str(Path(repo) / "validation"))
    import coordination_check as cc
    fails = cc.check_block(DOC["coordination"])
    if fails:
        sys.exit("FAIL: coordination_check.check_block: " + json.dumps(fails, ensure_ascii=False))
    banned = [w for w in json.load(open(Path(repo) / "validation/example/council.json"))["attributes"]["intergenerational_decision_horizon"]["scope"]["evidence"]["cross_domain_examples"]]
    names = ["Haudenosaunee", "Iroquois", "Māori", "Maori", "Igbo", "Tibetan", "Aboriginal", "Welsh", "Quaker"]
    text = json.dumps(DOC, ensure_ascii=False)
    hit = [n for n in names if n in text] + [b for b in banned if b in text]
    if hit:
        sys.exit(f"FAIL: a people or example from the held file appears in the pattern record: {hit}")
    Path(out).write_text(json.dumps(DOC, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({"coordination_check_failures": 0, "names_found": 0, "out": str(out),
                      "sha256": hashlib.sha256(Path(out).read_bytes()).hexdigest()}))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else str(HERE / "council_pattern.json"))
