#!/usr/bin/env python3
"""
export_reference.py -- runtime reference built from the provenance chain. Stdlib only.

  python3 scripts/export_reference.py            # write reference/lid_reference.jsonl
  python3 scripts/export_reference.py --check    # verify the written file against the chain
  python3 scripts/export_reference.py --test     # 10 planted questions + 1 planted wrong record

Rules: registry/DECLARED.json, amendment "physics usage: runtime reference".
Values come from head steps under provenance/ only. No status is assigned or
raised here. How to read the output: reference/READING_PROTOCOL.md.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import provenance_chain as pc  # noqa: E402

ROOT = pc.ROOT
OUT = ROOT / "reference" / "lid_reference.jsonl"
QUESTIONS = ROOT / "reference" / "planted_questions.json"
READINGS = ("OBSERVED", "DERIVED", "PROPOSED", "NOT_ASSESSED", "UNSOURCED", "NO_INFORMATION")
BLOCKS = ("attributes", "coordination", "gate_sensing", "functional_intelligence")


def reading(step):
    """Derived label for one step. Void is read first, then status."""
    void = (step.get("void") or {}).get("state")
    if void in ("VOID", "LEXICAL_VOID"):
        return "NO_INFORMATION"
    if void == "UNMAPPED":
        return "UNSOURCED"
    status = step.get("status") or ""
    for tag in ("OBSERVED", "DERIVED", "PROPOSED"):
        if status.startswith(tag):
            return tag
    return "NOT_ASSESSED"


def field_row(step):
    p = step["params"]
    return {"field": p["field"], "reading": reading(step), "value": step["value"],
            "status": step["status"], "status_note": step["status_note"],
            "evidence_type": p.get("evidence_type"), "reproducibility": p.get("reproducibility"),
            "scope": step["scope"], "assumptions": step["assumptions"],
            "step_id": step["id"], "source_ids": list(step["inputs"]), "void": step["void"]}


def head_steps(root=ROOT):
    """{entity: (path, [head steps in stored order])} from provenance/*.json."""
    out = {}
    for p in sorted((root / "provenance").glob("*.json")):
        if p.name == "INDEX.json":
            continue
        doc = json.loads(p.read_text(encoding="utf-8"))
        hs = pc.heads(doc["steps"])
        out[doc["entity"]] = (doc["path"], [s for s in doc["steps"] if hs.get(s["params"]["field"]) is s])
    return out


def build_rows(root=ROOT):
    rows = []
    for ent, (path, steps) in sorted(head_steps(root).items()):
        try:
            d = json.loads((root / path).read_text(encoding="utf-8"))
        except Exception:
            d = {}
        fields = [field_row(s) for s in steps]
        rows.append({"id": ent, "name": d.get("name"), "ontology": d.get("ontology"), "path": path,
                     "snapshot_class": "SUMMARY_ONLY",
                     "readings": {r: sum(f["reading"] == r for f in fields) for r in READINGS},
                     "fields": fields})
    return rows


def write(rows, out=OUT):
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows),
                   encoding="utf-8")


def read(out=OUT):
    return [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line.strip()]


# ------------------------------------------------------------------ verify
def verify_field(entity, f, heads_by_entity, source_ids):
    """Reasons a reference field is refused; [] when it matches its head step."""
    why = []
    steps = {s["id"]: s for s in heads_by_entity.get(entity, (None, []))[1]}
    s = steps.get(f.get("step_id"))
    if s is None:
        return ["step_id is not a head step of this entity under provenance/"]
    if pc.step_id(s) != s["id"]:
        why.append("stored step fails its own hash")
    if s["params"]["field"] != f.get("field"):
        why.append("field differs from the step")
    if pc.canon(s["value"]) != pc.canon(f.get("value")):
        why.append("value differs from the step")
    if s["status"] != f.get("status"):
        why.append("status differs from the step")
    if s["void"] != f.get("void"):
        why.append("void differs from the step")
    if list(s["inputs"]) != list(f.get("source_ids") or []):
        why.append("source_ids differ from the step")
    if reading(s) != f.get("reading"):
        why.append("reading differs from the one the step gives")
    for sid in f.get("source_ids") or []:
        if sid not in source_ids:
            why.append("source id not in registry/sources.json: %s" % sid[:12])
    return why


def verify_rows(rows, root=ROOT):
    hb = head_steps(root)
    srcs = {e["id"] for e in pc.load(root / "registry" / "sources.json", {"sources": []})["sources"]}
    bad = []
    for r in rows:
        for f in r["fields"]:
            why = verify_field(r["id"], f, hb, srcs)
            if why:
                bad.append((r["id"], f.get("field"), why))
    return bad


# ------------------------------------------------------------------ answer
def _say(f):
    """One sentence for one field. Status is read before the value."""
    rd, v = f["reading"], f["value"]
    val = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
    if rd == "NO_INFORMATION":
        reason = (f["void"] or {}).get("reason")
        return "no information: the field is null" + (" (%s)" % reason if reason else " (no reason recorded)")
    if rd == "UNSOURCED":
        return "recorded without a source, not usable as a finding: " + val
    if rd == "NOT_ASSESSED":
        return "recorded with a source, status not assessed: " + val
    if rd == "PROPOSED":
        return "PROPOSED, not established: " + val
    if rd == "DERIVED":
        return "%s: %s" % (f["status"], val)
    return "OBSERVED: " + val


def answer(rows, q, checker=None):
    """Answer one question from the reference rows only.
    q = {entity, field} or {entity, label, function_fields}. `checker`, when
    given, is verify_field bound to the chain; a refused field is not answered."""
    row = next((r for r in rows if r["id"] == q["entity"]), None)
    if row is None:
        return {"reading": "NO_RECORD", "statement": "no record for this entity", "cites": [], "source_ids": []}
    by = {f["field"]: f for f in row["fields"]}

    def use(name):
        f = by.get(name)
        if f is None:
            return None, ["field not in the reference"]
        return f, (checker(row["id"], f) if checker else [])

    if "label" in q:   # label slots stay open; the function fields decide
        cites, src, parts, readings, refused = [], [], [], [], []
        for name in q["function_fields"]:
            f, why = use(name)
            if why:
                refused.append((name, why))
                continue
            cites.append(f["step_id"])
            src += f["source_ids"]
            readings.append(f["reading"])
            parts.append("%s: %s" % (name.split(".")[-1], _say(f)))
        labels = [f for f in row["fields"] if ".contested_label[" in f["field"]
                  and isinstance(f["value"], str) and q["label"].lower() in f["value"].lower()]
        for f in labels:
            cites.append(f["step_id"])
            src += f["source_ids"]
        decided = sorted(set(readings))
        rd = decided[0] if len(decided) == 1 else "MIXED"
        if refused:
            rd = "REFUSED"
        return {"reading": rd, "label_listed": bool(labels),
                "statement": "The label %r is %s; a label does not decide. Function fields: %s"
                             % (q["label"], "recorded as contested" if labels else "not recorded", "; ".join(parts)),
                "cites": cites, "source_ids": src, "refused": refused}

    f, why = use(q["field"])
    if why:
        return {"reading": "REFUSED", "statement": "refused: " + "; ".join(why),
                "cites": [f["step_id"]] if f and f.get("step_id") else [], "source_ids": [], "refused": why}
    out = {"reading": f["reading"], "statement": _say(f), "cites": [f["step_id"]],
           "source_ids": f["source_ids"], "status": f["status"], "scope": f["scope"]}
    if f["reading"] != "NO_INFORMATION":
        out["value"] = f["value"]
    return out


# -------------------------------------------------------------------- test
def run_test(root=ROOT):
    """A3. Returns (lines, failed)."""
    rows = read()
    hb = head_steps(root)
    srcs = {e["id"] for e in pc.load(root / "registry" / "sources.json", {"sources": []})["sources"]}

    def checker(ent, f):
        return verify_field(ent, f, hb, srcs)

    spec = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    lines, failed = [], 0
    for i, q in enumerate(spec["questions"], 1):
        a = answer(rows, q, checker)
        ok = a["reading"] == q["expect"]["reading"] and bool(a["cites"])
        if "value" in q["expect"]:
            ok = ok and a.get("value") == q["expect"]["value"]
        if "status" in q["expect"]:
            ok = ok and a.get("status") == q["expect"]["status"]
        if "reason" in q["expect"]:
            row = next(r for r in rows if r["id"] == q["entity"])
            f = next(f for f in row["fields"] if f["field"] == q["field"])
            ok = ok and (f["void"] or {}).get("reason") == q["expect"]["reason"]
        if "label_listed" in q["expect"]:
            ok = ok and a.get("label_listed") == q["expect"]["label_listed"]
        ok = ok and all(c in {s["id"] for s in hb[q["entity"]][1]} for c in a["cites"])
        failed += not ok
        lines.append("%s Q%02d %-13s %-14s %s" % ("ok  " if ok else "FAIL", i, q["entity"], a["reading"],
                                                    ",".join(c[:12] for c in a["cites"])))
        lines.append("        %s" % q["q"])
        lines.append("        -> %s" % a["statement"][:200])

    # the planted wrong record: a copy of a real field, status raised, value changed
    w = spec["planted_wrong_record"]
    bad_rows = json.loads(json.dumps(rows))
    row = next(r for r in bad_rows if r["id"] == w["entity"])
    f = next(f for f in row["fields"] if f["field"] == w["field"])
    true_status = f["status"]
    f.update(value=w["value"], status=w["status"], reading=w["status"])
    naive = answer(bad_rows, w)                 # without the chain: it would be read as given
    checked = answer(bad_rows, w, checker)      # with the chain
    caught = checked["reading"] == "REFUSED" and "value differs from the step" in checked["refused"] \
        and "status differs from the step" in checked["refused"]
    whole = verify_rows(bad_rows, root)
    caught = caught and whole == [(w["entity"], w["field"], checked["refused"])]
    clean = verify_rows(rows, root) == []
    failed += (not caught) + (not clean)
    lines.append("%s planted wrong record %s %s: says %s, step says %s"
                 % ("ok  " if caught else "FAIL", w["entity"], w["field"], naive["reading"], true_status))
    lines.append("        refused by: %s" % "; ".join(checked.get("refused", [])))
    lines.append("%s unmodified reference: every field matches its head step" % ("ok  " if clean else "FAIL"))
    lines.append("questions: %d   planted wrong records: 1   failed: %d" % (len(spec["questions"]), failed))
    return lines, failed


def main(argv):
    if "--test" in argv:
        lines, failed = run_test()
        print("\n".join(lines))
        return 1 if failed else 0
    if "--check" in argv:
        rows = read()
        bad = verify_rows(rows)
        current = rows == build_rows()
        for ent, field, why in bad:
            print("REFUSED %s %s: %s" % (ent, field, "; ".join(why)))
        print("entities: %d   fields: %d   refused: %d   matches a fresh export: %s"
              % (len(rows), sum(len(r["fields"]) for r in rows), len(bad), current))
        return 1 if bad or not current else 0
    rows = build_rows()
    write(rows)
    tot = {r: sum(x["readings"][r] for x in rows) for r in READINGS}
    print("wrote %s" % OUT.relative_to(ROOT))
    print("entities: %d   fields: %d" % (len(rows), sum(len(r["fields"]) for r in rows)))
    for r in READINGS:
        print("  %-15s %d" % (r, tot[r]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
