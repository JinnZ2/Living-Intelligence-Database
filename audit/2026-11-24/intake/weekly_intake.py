#!/usr/bin/env python3
"""
weekly_intake.py -- weekly intake of newly indexed literature for the Living Intelligence Database.
Python standard library only. Status: PROPOSED (not adopted; not yet declared in registry/DECLARED.json).

  python3 weekly_intake.py fetch  --repo R --queries Q --out DIR [--since YYYY-MM-DD --until YYYY-MM-DD]
  python3 weekly_intake.py offline --repo R --queries Q --out DIR --snapshots DIR
  python3 weekly_intake.py --selftest

Stages. Only stage 1 touches the network; stages 2-5 run offline on the saved bytes, so any
run can be repeated from its snapshots and gives the same output.

 1 FETCH     Europe PMC REST search (no key), one request per query in the owner-editable
             queries file, restricted to works first indexed in the window. Every response is
             saved byte-for-byte with its sha256 before it is parsed. A failed request is
             recorded as NOT_RUN for that query and the run exits non-zero: nothing is skipped
             quietly.
 2 FILTER    Deterministic, every removed item kept with its reason:
               F1 NO_ABSTRACT          no abstract text in the record
               F2 ALREADY_REGISTERED   PMID already in registry/sources.json
               F3 DUPLICATE            same PMID/DOI already taken from an earlier query
               F4 SEEN_IN_EARLIER_INTAKE  PMID/DOI already a candidate in an earlier week's
                                       intake/weekly/<date>/intake.json (date before until)
             Flags (the item is kept, the flag is shown):
               G1 RETRACTION_OR_NOTICE pubType names a retraction, erratum, correction or
                                       expression of concern
               G2 PREPRINT             source PPR or pubType preprint
 3 CANDIDATES One record per kept work and touched field. The field's claim is its
             scope.definition copied verbatim with its sha256; the field's value is copied, not
             coerced. Quote candidates are verbatim sentences of the abstract that contain a
             query term, cut to 25 words (a cut quote is marked TRUNCATED). Numbers in the
             abstract are listed with the deviation extractor's roles. reading_state is
             AWAITING_READER: no claim_support or number_support is written by this script,
             because the declared reading contract (amendments 'claim/number split' and
             'NOT_ADDRESSED + reading queue') gives that judgment to an outside reader.
 4 HYPOTHESES Rule-generated stubs, each {id, rule, touches, statement, falsifier,
             status: PROPOSED, generated_by: rule id}. They say what a reader could check,
             not what is true:
               HX1 NUMBER_ON_VALUE_SCALE  a unitless 0-1 decimal or a percent in the abstract
               HX2 CONDITION_UNIT_SHARED  a unit in the abstract also bounds a condition in the
                                          field's measurement_limits (regime raw material)
               HX3 DEVIATION_OFFERED      a ± in the abstract for a field with no deviation
                                          candidate in its own prose
               HX4 BIOSPHERE_CONDITION    the abstract names a biosphere-carried condition
                                          term and the touched entity is a BIOSPHERE candidate;
                                          only terms that also occur in the touched field's
                                          scope.dependencies are kept (none kept, no stub)
 5 REPORT    intake.json and intake.md in the output directory, for a pull request that a
             person reviews. Nothing is merged and nothing in ontology/ or registry/ is written.

An optional language-model reading slot is declared in the workflow and not implemented
here. If it is ever filled, its output must carry the model name, the prompt sha256 and
reading_state MACHINE_READ_NOT_REVIEWED, and it must not write claim_support.

Amendments of 2026-11-27 (registry/DECLARED.json, one entry each; evidence in
intake/weekly/2026-11-24/machine_reading_2026-11-27/proposal_evidence.json):
  - window: the default window is until minus 14 days, not 7, so consecutive weekly runs
    overlap by 7 days; F4 drops works already taken as candidates in an earlier week.
  - HX4: a term is kept only if it also occurs in the touched field's scope.dependencies.
  - HX1: numbers the deviation extractor tags CONDITIONAL_CHANGE do not raise HX1.
  The my_phosphorus query change is in intake_queries.json.
"""
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "deviation"))
sys.path.insert(0, str(HERE.parent / "biosphere"))
import deviation_extract as dx  # noqa: E402
import biosphere_candidates as bc  # noqa: E402

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
PAGE = 100
NOTICE = re.compile(r"retract|erratum|correction|corrigendum|expression of concern", re.I)
WORD = re.compile(r"\S+")
TAG = re.compile(r"<[^>]+>")
WINDOW_DAYS = 14   # amendment 2026-11-27 "intake window overlap and F4"; was 7


def sha(b):
    return hashlib.sha256(b).hexdigest()


# ------------------------------------------------------------------ stage 1
def window(since, until):
    u = date.fromisoformat(until) if until else date.today()
    # 14 days since the amendment of 2026-11-27 (was 7); explicit --since is unchanged.
    s = date.fromisoformat(since) if since else u - timedelta(days=WINDOW_DAYS)
    if s > u:
        raise SystemExit(f"FAIL: since {s} is after until {u}")
    return s.isoformat(), u.isoformat()


def query_string(q, since, until):
    return f"({q['query']}) AND FIRST_IDATE:[{since} TO {until}]"


def fetch(queries, since, until, snapdir):
    snapdir = Path(snapdir)
    snapdir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for q in queries:
        params = {"query": query_string(q, since, until), "format": "json", "resultType": "core",
                  "pageSize": PAGE, "cursorMark": "*"}
        url = EPMC + "?" + urllib.parse.urlencode(params)
        entry = {"query_id": q["id"], "url": url}
        body = None
        for attempt in range(3):
            try:
                body = urllib.request.urlopen(urllib.request.Request(
                    url, headers={"User-Agent": "LID-weekly-intake/0.1 (proposal)"}), timeout=60).read()
                json.loads(body)
                break
            except Exception as ex:  # recorded, never swallowed
                entry["error"] = f"{type(ex).__name__}: {ex}"
                body = None
                time.sleep(2 + 2 * attempt)
        if body is None:
            entry["state"] = "NOT_RUN"
        else:
            name = f"{q['id']}.json"
            (snapdir / name).write_bytes(body)
            entry.update(state="SAVED", file=name, bytes=len(body), sha256=sha(body))
            entry.pop("error", None)
            hit = json.loads(body).get("hitCount", 0)
            entry["hit_count"] = hit
            if hit > PAGE:
                entry["truncated"] = f"hitCount {hit} > page {PAGE}; only the first page is kept"
        manifest.append(entry)
        time.sleep(0.5)
    (snapdir / "manifest.json").write_text(json.dumps(
        {"since": since, "until": until, "source": EPMC, "entries": manifest}, indent=1) + "\n")
    return manifest


# ------------------------------------------------------------------ stage 2
def registered_pmids(repo):
    d = json.load(open(Path(repo) / "registry" / "sources.json"))
    out = set()
    for s in d["sources"]:
        out.update(re.findall(r"PMID:?\s*(\d{4,9})", s.get("string", "")))
        for w in ((s.get("existence") or {}).get("works") or []):
            m = w.get("matched_record") or {}
            if m.get("pmid"):
                out.add(str(m["pmid"]))
    return out


def earlier_candidates(repo, until):
    """PMIDs and DOIs taken as candidates by earlier weeks' intakes (folder date < until).
    Removed items of earlier weeks are not counted: a record without an abstract is tried again."""
    seen = set()
    base = Path(repo) / "intake" / "weekly"
    for f in sorted(base.glob("*/intake.json")) if base.is_dir() else []:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", f.parent.name) or f.parent.name >= until:
            continue
        for c in json.loads(f.read_text(encoding="utf-8")).get("candidates", []):
            w = c.get("work") or {}
            for k in ("pmid", "doi"):
                if w.get(k):
                    seen.add(str(w[k]).lower())
    return seen


def load_snapshots(snapdir):
    snapdir = Path(snapdir)
    man = json.load(open(snapdir / "manifest.json"))
    out = []
    for e in man["entries"]:
        if e.get("state") != "SAVED":
            out.append((e, None))
            continue
        body = (snapdir / e["file"]).read_bytes()
        if sha(body) != e["sha256"]:
            raise SystemExit(f"FAIL: snapshot {e['file']} sha256 does not match its manifest")
        out.append((e, json.loads(body)))
    return man, out


def filter_items(snaps, registered, earlier=frozenset()):
    kept, removed, seen = [], [], set()
    for entry, body in snaps:
        if body is None:
            continue
        for r in body.get("resultList", {}).get("result", []):
            key = r.get("pmid") or r.get("doi") or r.get("id")
            base = {"query_id": entry["query_id"], "pmid": r.get("pmid"), "doi": r.get("doi"),
                    "title": r.get("title")}
            if not (r.get("abstractText") or "").strip():
                removed.append({**base, "reason": "F1 NO_ABSTRACT"}); continue
            if r.get("pmid") and str(r["pmid"]) in registered:
                removed.append({**base, "reason": "F2 ALREADY_REGISTERED"}); continue
            if key in seen:
                removed.append({**base, "reason": "F3 DUPLICATE"}); continue
            if any(str(r.get(k) or "").lower() in earlier for k in ("pmid", "doi") if r.get(k)):
                removed.append({**base, "reason": "F4 SEEN_IN_EARLIER_INTAKE"}); continue
            seen.add(key)
            types = (r.get("pubTypeList") or {}).get("pubType") or []
            types = [types] if isinstance(types, str) else types
            flags = []
            if any(NOTICE.search(t) for t in types):
                flags.append("G1 RETRACTION_OR_NOTICE")
            if r.get("source") == "PPR" or any("preprint" in t.lower() for t in types):
                flags.append("G2 PREPRINT")
            kept.append({"query_id": entry["query_id"], "record": r, "pub_types": types, "flags": flags})
    return kept, removed


# ------------------------------------------------------------------ stage 3/4
def sentences(text):
    return [m.group(0).strip() for m in dx.SENT.finditer(text) if m.group(0).strip()]


def quote_of(sentence):
    words = WORD.findall(sentence)
    if len(words) <= 25:
        return sentence, False
    return " ".join(words[:25]), True


def attr_index(repo):
    repo = Path(repo)
    idx = json.load(open(repo / "ontology_index.json"))
    out = {}
    for ent in idx["entities"]:
        d = json.load(open(repo / ent["path"]))
        out[ent["id"]] = d
    # BIOSPHERE is not in the index (relational/ has no schema; re-check finding N2). It is
    # loaded by its path so queries can touch it, and every candidate on it is flagged.
    bio = repo / "ontology" / "relational" / "biosphere_reference.json"
    if bio.exists() and "BIOSPHERE" not in out:
        d = json.load(open(bio))
        d["_unindexed"] = True
        out["BIOSPHERE"] = d
    return out


def candidates(kept, queries, records, bio_ids):
    qmap = {q["id"]: q for q in queries}
    cands, hyps = [], []
    for k in kept:
        r, q = k["record"], qmap[k["query_id"]]
        abstract = TAG.sub("", r["abstractText"])
        terms = [t.lower() for t in q["terms"]]
        sents = sentences(abstract)
        quotes = []
        for s in sents:
            if any(t in s.lower() for t in terms):
                text, cut = quote_of(s)
                quotes.append({"quote": text, "truncated": cut})
        nums = []
        for s in sents:
            for m in dx.EXPR.finditer(s):
                if not dx.re.search(r"\d", m.group(0)) or m.group(0)[0].isspace():
                    continue
                role, rule = dx.classify(s, m, None)
                nums.append({"span": m.group(0).strip(), "role": role, "rule": rule,
                             "unit": (m.group(5) or "").strip() or None, "pm": bool(m.group(1)),
                             "pct": bool(m.group(3))})
        for t in q["touches"]:
            rec = records.get(t["entity"])
            if rec is None:
                raise SystemExit(f"FAIL: query {q['id']} touches unknown entity {t['entity']}")
            av = (rec.get("attributes") or {}).get(t["field"]) if t.get("field") else None
            if t.get("field") and av is None:
                raise SystemExit(f"FAIL: query {q['id']} touches unknown field {t['entity']}.{t['field']}")
            sc = (av or {}).get("scope") or {}
            claim = sc.get("definition")
            ml = sc.get("measurement_limits") if isinstance(sc.get("measurement_limits"), str) else ""
            cid = f"C:{r.get('pmid') or r.get('id')}:{t['entity']}:{t.get('field') or '-'}"
            cands.append({
                "id": cid, "query_id": q["id"],
                "work": {"pmid": r.get("pmid"), "doi": r.get("doi"), "title": r.get("title"),
                         "first_index_date": r.get("firstIndexDate"),
                         "first_publication_date": r.get("firstPublicationDate"),
                         "pub_types": k["pub_types"], "flags": k["flags"],
                         "abstract_sha256": sha(r["abstractText"].encode())},
                "touches": {"entity": t["entity"], "field": t.get("field"),
                            "claim": claim, "claim_sha256": sha(claim.encode()) if claim else None,
                            "value": (av or {}).get("value")},
                "touched_record_unindexed": bool(rec.get("_unindexed")),
                "quote_candidates": quotes, "numbers": nums,
                "reading_state": "AWAITING_READER"})
            own = dx.extract(ml, (av or {}).get("value"))[0] if av else []
            own_units = set()
            for e in own:
                if e["role"] == "CONDITION_NUMBER":
                    mm = dx.EXPR.match(e["span"])
                    if mm and mm.group(5):
                        own_units.add(mm.group(5).strip())
            own_dev = any(e["role"] == "DEVIATION_CANDIDATE" for e in own)
            touch = {"entity": t["entity"], "field": t.get("field"), "candidate": cid}
            def hyp(rule, statement, falsifier, evidence):
                hyps.append({"id": f"H:{rule}:{cid}", "rule": rule, "touches": touch, "statement": statement,
                             "falsifier": falsifier, "evidence_spans": evidence,
                             "status": "PROPOSED", "generated_by": rule})
            if av is not None:
                # CONDITIONAL_CHANGE numbers are skipped (amendment 2026-11-27 "HX1 skips CONDITIONAL_CHANGE")
                scale = [n["span"] for n in nums if (n["pct"] or (not n["unit"] and "." in n["span"]))
                         and n["role"] != "CONDITIONAL_CHANGE"]
                if scale:
                    hyp("HX1", f"The abstract gives numbers on a value-like scale; one may bear on {t['entity']}.{t['field']} = {(av or {}).get('value')}.",
                        "A reader finds each number measures a different quantity from the field's scope.definition.", scale)
                shared = sorted({n["unit"] for n in nums if n["unit"]} & own_units)
                if shared:
                    hyp("HX2", f"The abstract reports quantities in {', '.join(shared)}, a unit that also bounds a condition in this field's measurement_limits; the regime bound may be informed by this work.",
                        "A reader finds the abstract's quantity in that unit is not the same condition, or not a bound.", shared)
                pm = [n["span"] for n in nums if n["pm"]]
                if pm and not own_dev:
                    hyp("HX3", "The abstract states a ± spread; the field's own prose has no deviation candidate.",
                        "A reader finds the ± is for a different quantity than the field's value.", pm)
            if t["entity"] in bio_ids:
                # only terms that the field's own dependencies also name
                # (amendment 2026-11-27 "HX4 on field dependencies")
                deps = sc.get("dependencies") if isinstance(sc.get("dependencies"), list) else []
                dep_terms = set(bc.terms_in(" ".join(str(d) for d in deps).replace("_", " ")))
                bt = [x for x in bc.terms_in(abstract) if x in dep_terms]
                if bt:
                    hyp("HX4", f"The abstract names biosphere-carried conditions ({', '.join(bt)}) for {t['entity']}, a BIOSPHERE dependency candidate.",
                        "A reader finds the condition is not one the entity depends on, or the dependency runs the other way.", bt)
    return cands, hyps


# ------------------------------------------------------------------ stage 5
def report(man, snaps, kept, removed, cands, hyps, queries_sha):
    not_run = [e["query_id"] for e, b in snaps if b is None]
    out = {"record": "WEEKLY_INTAKE", "status": "PROPOSED; nothing here is reviewed",
           "window": {"since": man["since"], "until": man["until"]}, "source": man["source"],
           "queries_sha256": queries_sha, "snapshots": man["entries"], "not_run": not_run,
           "counts": {"kept": len(kept), "removed": len(removed), "candidates": len(cands),
                      "hypotheses": len(hyps),
                      "hypotheses_by_rule": {r: sum(1 for h in hyps if h["rule"] == r) for r in ("HX1", "HX2", "HX3", "HX4")},
                      "removed_by_reason": {x: sum(1 for r in removed if r["reason"] == x) for x in sorted({r["reason"] for r in removed})}},
           "removed": removed, "candidates": cands, "hypotheses": hyps}
    md = [f"# Weekly intake {man['since']} to {man['until']}", "",
          "Status: PROPOSED. Machine output; nothing in this file has been read or judged by a person.", "",
          f"Queries file sha256 `{queries_sha}`. Source: Europe PMC REST.", "",
          "| Query | State | Hits | Snapshot sha256 |", "|---|---|---|---|"]
    for e in man["entries"]:
        md.append(f"| {e['query_id']} | {e['state']} | {e.get('hit_count', '')} | {e.get('sha256', e.get('error', ''))[:64]} |")
    md += ["", f"Kept {len(kept)}, removed {len(removed)} " + json.dumps(out["counts"]["removed_by_reason"]) +
           f", candidates {len(cands)}, hypotheses {len(hyps)} " + json.dumps(out["counts"]["hypotheses_by_rule"]), ""]
    if not_run:
        md += [f"NOT_RUN queries: {', '.join(not_run)}. The run is incomplete.", ""]
    md += ["## Candidates awaiting a reader", "", "| Work | Flags | Touches | Value | First quote candidate |", "|---|---|---|---|---|"]
    for c in cands:
        w = c["work"]
        q0 = (c["quote_candidates"][0]["quote"] if c["quote_candidates"] else "(no sentence contains a query term)").replace("|", "/")
        md.append(f"| PMID {w['pmid']}: {(w['title'] or '').replace('|', '/')[:90]} | {', '.join(w['flags']) or '-'} | "
                  f"{c['touches']['entity']}.{c['touches']['field']} | {c['touches']['value']} | {q0} |")
    md += ["", "## Hypothesis stubs (rule-generated, PROPOSED)", "", "| Rule | Touches | Statement | Falsifier |", "|---|---|---|---|"]
    for h in hyps:
        md.append(f"| {h['rule']} | {h['touches']['entity']}.{h['touches']['field']} | {h['statement']} | {h['falsifier']} |")
    return out, "\n".join(md) + "\n"


def run_offline(repo, queries_path, snapdir, outdir):
    qbytes = Path(queries_path).read_bytes()
    queries = json.loads(qbytes)["queries"]
    man, snaps = load_snapshots(snapdir)
    kept, removed = filter_items(snaps, registered_pmids(repo), earlier_candidates(repo, man["until"]))
    records = attr_index(repo)
    bio = bc.run(repo)
    bio_ids = {r["id"] for r in bio["rows"] if r["rules"]}
    cands, hyps = candidates(kept, queries, records, bio_ids)
    out, md = report(man, snaps, kept, removed, cands, hyps, sha(qbytes))
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "intake.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    (outdir / "intake.md").write_text(md)
    print(json.dumps({"window": out["window"], "not_run": out["not_run"], **out["counts"]}))
    return 3 if out["not_run"] else 0


def selftest():
    ok = True
    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print("PASS" if cond else "FAIL", name)
    q, cut = quote_of(" ".join(f"w{i}" for i in range(30)))
    check("quote cut to 25 words and marked", len(q.split()) == 25 and cut)
    q, cut = quote_of("Short sentence here.")
    check("short quote kept whole", q == "Short sentence here." and not cut)
    fake = [({"query_id": "q1"}, {"resultList": {"result": [
        {"pmid": "1", "abstractText": "", "title": "a"},
        {"pmid": "2", "abstractText": "x.", "title": "b"},
        {"pmid": "3", "abstractText": "y.", "title": "c", "pubTypeList": {"pubType": ["Retraction of Publication"]}},
        {"pmid": "3", "abstractText": "y.", "title": "c"},
        {"id": "PPR9", "source": "PPR", "abstractText": "z.", "title": "d"}]}})]
    kept, removed = filter_items(fake, {"2"})
    check("F1 no abstract removed", any(r["reason"] == "F1 NO_ABSTRACT" and r["pmid"] == "1" for r in removed))
    check("F2 registered removed", any(r["reason"] == "F2 ALREADY_REGISTERED" and r["pmid"] == "2" for r in removed))
    check("F3 duplicate removed", any(r["reason"] == "F3 DUPLICATE" and r["pmid"] == "3" for r in removed))
    check("G1 retraction flagged, kept", any("G1 RETRACTION_OR_NOTICE" in k["flags"] for k in kept))
    check("G2 preprint flagged, kept", any("G2 PREPRINT" in k["flags"] for k in kept))
    # was "window default is 7 days"; changed by the amendment of 2026-11-27
    check("window default is 14 days", window(None, "2026-11-24") == ("2026-11-10", "2026-11-24"))
    check("explicit since is kept", window("2026-11-17", "2026-11-24") == ("2026-11-17", "2026-11-24"))
    kept4, removed4 = filter_items([({"query_id": "q1"}, {"resultList": {"result": [
        {"pmid": "7", "abstractText": "a.", "title": "e"}, {"pmid": "8", "doi": "10.1/X", "abstractText": "b.", "title": "f"},
        {"pmid": "9", "abstractText": "c.", "title": "g"}]}})], set(), {"7", "10.1/x"})
    check("F4 earlier candidate removed (PMID and DOI)",
          sorted(r["pmid"] for r in removed4 if r["reason"] == "F4 SEEN_IN_EARLIER_INTAKE") == ["7", "8"]
          and [k["record"]["pmid"] for k in kept4] == ["9"])
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        for d, pm in (("2026-11-17", "11"), ("2026-11-24", "12")):
            (Path(td) / "intake" / "weekly" / d).mkdir(parents=True)
            (Path(td) / "intake" / "weekly" / d / "intake.json").write_text(json.dumps(
                {"candidates": [{"work": {"pmid": pm, "doi": None}}], "removed": [{"pmid": "13"}]}))
        check("F4 reads only weeks before until, candidates only",
              earlier_candidates(td, "2026-11-24") == {"11"})
    recs = {"X": {"attributes": {"f": {"value": 0.5, "scope": {"definition": "d", "measurement_limits": "",
                                                                "dependencies": ["ambient_temperature", "soil_phosphorus_availability"]}}}}}
    qx = [{"id": "q", "terms": ["t"], "touches": [{"entity": "X", "field": "f"}]}]
    kx = [{"query_id": "q", "flags": [], "pub_types": [], "record": {"pmid": "5", "title": "t", "abstractText":
          "Oxygen and temperature and soil were measured. Yield rose by 40% under drought. The share was 0.42."}}]
    _, hx = candidates(kx, qx, recs, {"X"})
    h4 = [h for h in hx if h["rule"] == "HX4"]
    check("HX4 keeps only terms named in the field's dependencies", len(h4) == 1 and h4[0]["evidence_spans"] == ["soil", "temperature"])
    kx[0]["record"]["abstractText"] = "Oxygen was measured."
    _, hx = candidates(kx, qx, recs, {"X"})
    check("HX4 not raised when no term is a dependency", not [h for h in hx if h["rule"] == "HX4"])
    kx[0]["record"]["abstractText"] = "Yield increased by ~\u200940% under drought."
    _, hx = candidates(kx, qx, recs, {"X"})
    roles = [n["role"] for c in _ for n in c["numbers"]]
    check("HX1 not raised by a CONDITIONAL_CHANGE number", "CONDITIONAL_CHANGE" in roles and not [h for h in hx if h["rule"] == "HX1"])
    kx[0]["record"]["abstractText"] = "Yield increased by ~\u200940% under drought. A fraction (0.42) was retained."
    _, hx = candidates(kx, qx, recs, {"X"})
    check("HX1 still raised by the other number", [h["evidence_spans"] for h in hx if h["rule"] == "HX1"] == [["0.42"]])
    try:
        window("2026-11-25", "2026-11-24"); check("reversed window fails", False)
    except SystemExit:
        check("reversed window fails", True)
    print("selftest", "PASS" if ok else "FAIL")
    return ok


def arg(name, default=None):
    a = sys.argv
    return a[a.index(name) + 1] if name in a else default


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(0 if selftest() else 1)
    if len(sys.argv) < 2 or sys.argv[1] not in ("fetch", "offline"):
        sys.exit(__doc__)
    repo, qp, out = arg("--repo"), arg("--queries"), arg("--out")
    if not (repo and qp and out):
        sys.exit("FAIL: --repo, --queries and --out are required")
    if sys.argv[1] == "fetch":
        s, u = window(arg("--since"), arg("--until"))
        snap = Path(out) / "snapshots"
        fetch(json.loads(Path(qp).read_text())["queries"], s, u, snap)
        sys.exit(run_offline(repo, qp, snap, out))
    sys.exit(run_offline(repo, qp, arg("--snapshots"), out))
