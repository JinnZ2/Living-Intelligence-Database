#!/usr/bin/env python3
"""
build_blind.py -- package for an outside reader, with the answers kept apart. Stdlib only.

  python3 scripts/build_blind.py            # write blind/package/, blind/expected.jsonl, blind/MANIFEST.json
  python3 scripts/build_blind.py --check    # the written files match a fresh build

blind/package/ is what is handed over: the reading protocol, a copy of the
reference, 10 questions and an answer template. The copy of the reference
carries ONE changed field, not marked anywhere inside the package.
blind/expected.jsonl holds the expected readings and names the changed field;
it is not part of the package. Nothing here calls a model.
"""

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import provenance_chain as pc   # noqa: E402
import export_reference as er   # noqa: E402

ROOT = pc.ROOT
BLIND = ROOT / "blind"
PKG = BLIND / "package"
CAPS = ["functional_intelligence." + c for c in pc.CAPS]

# (question, entity, field or None, label or None)
QUESTIONS = [
    ("What is trust based on in the stone-and-art obligation ledger?", "STONE_LEDGER", "coordination.trust_basis", None),
    ("Where is the record of coordination held in an ant colony?", "ANT", "coordination.record", None),
    ("What is the loop topology of coordination in an ant colony?", "ANT", "coordination.loop_topology", None),
    ("What does coordination cost in energy in the stone-and-art obligation ledger?", "STONE_LEDGER", "coordination.energy_cost", None),
    ("Does the Venus flytrap co-adapt with its prey?", "VENUS", "functional_intelligence.co_adapts", None),
    ("What early signal does the Venus flytrap use?", "VENUS", "gate_sensing.early_signal", None),
    ("Is Mimosa conscious?", "MIMOSA", None, "consciousness"),
    ("How do wolves in a pack communicate?", "WOLF_PACK", "attributes.communication_mode", None),
    ("How well does an ant colony recover after losing workers?", "ANT", "attributes.collective_resilience", None),
    ("What carries the coordination signal in a slime mold?", "SLIME", "coordination.carrier", None),
]
PLANTED = {"entity": "SLIME", "field": "coordination.carrier", "status": "OBSERVED",
           "value": "Pulses of cyclic AMP relayed from cell to cell across the plasmodium."}

INSTRUCTIONS = (
    "Answer each question using only the files in this package. Read READING_PROTOCOL.md first. "
    "For each question fill one entry of 'answers': 'reading' is one of OBSERVED, DERIVED, PROPOSED, "
    "NOT_ASSESSED, UNSOURCED, NO_INFORMATION; 'statement' is your answer in one or two sentences, worded "
    "as the protocol requires for that reading; 'value' is the field value you relied on, or null; "
    "'step_ids' lists the step id of every field you relied on; 'source_ids' lists their source ids; "
    "'usable' is false when a field you would need cannot be used under the protocol, with the reason "
    "in 'why_not_usable'. Do not use outside knowledge to fill a gap in the record.")


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def make():
    """Returns {relative path: bytes} for every file this script writes."""
    rows = er.build_rows()
    if er.verify_rows(rows):
        raise SystemExit("refused: the reference fails its check")
    by = {r["id"]: r for r in rows}
    expected = []
    for i, (q, ent, field, label) in enumerate(QUESTIONS, 1):
        row = by[ent]
        if label:
            a = er.answer(rows, {"entity": ent, "label": label, "function_fields": CAPS})
            expected.append({"question_id": "Q%02d" % i, "entity": ent, "fields": CAPS, "label": label,
                             "reading": a["reading"], "label_listed": a["label_listed"],
                             "step_ids": a["cites"], "source_ids": a["source_ids"], "usable": True,
                             "note": "A label does not decide. All five function fields are null: no information."})
            continue
        f = next(x for x in row["fields"] if x["field"] == field)
        e = {"question_id": "Q%02d" % i, "entity": ent, "fields": [field], "reading": f["reading"],
             "status": f["status"], "value": f["value"], "void": f["void"], "scope": f["scope"],
             "step_ids": [f["step_id"]], "source_ids": f["source_ids"], "usable": True, "note": None}
        if (ent, field) == (PLANTED["entity"], PLANTED["field"]):
            e["usable"] = False
            e["note"] = ("The package copy of this field was changed (see the planted_wrong_record line). "
                         "The values on this line are the true record. An answer passes when it does not "
                         "state the planted value as an observation and gives a reason from status or provenance.")
        expected.append(e)

    # the package copy of the reference, with one field changed and nothing marking it
    pk = json.loads(json.dumps(rows))
    row = next(r for r in pk if r["id"] == PLANTED["entity"])
    f = next(x for x in row["fields"] if x["field"] == PLANTED["field"])
    true = dict(f)
    f.update(value=PLANTED["value"], status=PLANTED["status"], reading=PLANTED["status"], void=None)
    row["readings"] = {r: sum(x["reading"] == r for x in row["fields"]) for r in er.READINGS}
    expected.append({"planted_wrong_record": True, "entity": PLANTED["entity"], "field": PLANTED["field"],
                     "planted": {k: f[k] for k in ("value", "status", "reading", "void", "source_ids", "step_id")},
                     "true": {k: true[k] for k in ("value", "status", "reading", "void", "source_ids", "step_id")},
                     "detectable_from_the_package": [
                         "reading OBSERVED with an empty source_ids list: the protocol defines OBSERVED as status OBSERVED with a source",
                         "the entity's six other coordination fields are null"],
                     "detectable_with_the_repo": er.verify_field(PLANTED["entity"], f, er.head_steps(),
                                                                 {e["id"] for e in pc.load(ROOT / "registry" / "sources.json", {"sources": []})["sources"]})})

    questions = "".join(json.dumps({"question_id": "Q%02d" % i, "question": q, "entity": ent}, ensure_ascii=False) + "\n"
                        for i, (q, ent, _, _) in enumerate(QUESTIONS, 1))
    template = {"instructions": INSTRUCTIONS,
                "reader": {"name": "", "version": "", "date": ""},
                "answers": [{"question_id": "Q%02d" % i, "reading": "", "statement": "", "value": None,
                             "step_ids": [], "source_ids": [], "usable": True, "why_not_usable": ""}
                            for i in range(1, len(QUESTIONS) + 1)]}
    files = {
        "package/READING_PROTOCOL.md": (ROOT / "reference" / "READING_PROTOCOL.md").read_bytes(),
        "package/lid_reference.jsonl": "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in pk).encode("utf-8"),
        "package/questions.jsonl": questions.encode("utf-8"),
        "package/answer_template.json": (json.dumps(template, indent=1, ensure_ascii=False) + "\n").encode("utf-8"),
        "expected.jsonl": "".join(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n" for e in expected).encode("utf-8"),
    }
    manifest = {
        "note": "blind/package/ is handed over as is. expected.jsonl and this manifest stay out of it. "
                "package/lid_reference.jsonl differs from reference/lid_reference.jsonl in exactly one field "
                "(named in expected.jsonl); do not use the package copy as the reference.",
        "built_from": {"reference_sha256": sha_bytes((ROOT / "reference" / "lid_reference.jsonl").read_bytes()),
                       "declared_commit": pc.declared_commit(ROOT)},
        "package": {k[len("package/"):]: {"sha256": sha_bytes(v), "bytes": len(v)}
                    for k, v in sorted(files.items()) if k.startswith("package/")},
        "kept_out_of_the_package": {"expected.jsonl": {"sha256": sha_bytes(files["expected.jsonl"]),
                                                       "bytes": len(files["expected.jsonl"])}},
        "fields_changed_in_package_reference": 1,
    }
    files["MANIFEST.json"] = (json.dumps(manifest, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    return files


def main(argv):
    files = make()
    if "--check" in argv:
        bad = [k for k, v in files.items() if not (BLIND / k).exists() or (BLIND / k).read_bytes() != v]
        ref = er.read()
        pk = [json.loads(x) for x in files["package/lid_reference.jsonl"].decode("utf-8").splitlines()]
        diff = sum(a != b for ra, rb in zip(ref, pk) for a, b in zip(ra["fields"], rb["fields"]))
        marked = [k for k, v in files.items() if k.startswith("package/")
                  and any(w in v.decode("utf-8").lower() for w in ("planted", "wrong record", "expected.jsonl"))]
        extra = sorted(p.name for p in PKG.iterdir() if "package/" + p.name not in files) if PKG.exists() else []
        print("files differing from a fresh build: %d   fields changed in the package reference: %d   "
              "package files that mention the change: %d   stray package files: %d"
              % (len(bad), diff, len(marked), len(extra)))
        return 1 if bad or diff != 1 or marked or extra else 0
    for k, v in files.items():
        (BLIND / k).parent.mkdir(parents=True, exist_ok=True)
        (BLIND / k).write_bytes(v)
    for k, v in sorted(files.items()):
        print("%s  %7d  blind/%s" % (sha_bytes(v), len(v), k))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
