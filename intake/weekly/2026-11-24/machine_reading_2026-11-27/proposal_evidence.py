#!/usr/bin/env python3
"""
proposal_evidence.py -- the read-only test of the nine intake proposals in MACHINE_READING.md,
run on 2026-11-27 by the machine reader (Claude Opus 5.5, working in Perplexity Computer).
Python standard library only.

  python3 proposal_evidence.py fetch RAW_DIR      # network: Europe PMC search, one file per
                                                  # (query, variant, window); never overwrites
  python3 proposal_evidence.py build RAW_DIR      # offline: writes proposal_evidence.json
  python3 proposal_evidence.py check              # offline: recomputes the query table from the
                                                  # id lists in proposal_evidence.json

Windows (FIRST_IDATE, both ends inclusive, as weekly_intake.py builds them):
  W1 2026-11-17..2026-11-24, W2 2026-11-10..2026-11-17, W3 2026-11-03..2026-11-10.
Raw responses are not committed (1.7 MB); each file's sha256 and the ordered id list are.

Relevance labels (LABELS below) are machine calls on the title and abstract against the touched
field's scope.definition, made by the same reader as machine_reading.json. They are
MACHINE_READ_NOT_REVIEWED and are not claim_support. No work was RELEVANT; PARTIAL counts as
relevant for precision and recall. Recall is against the relevant works the current query finds.

Filter proposals are measured by running weekly_intake.py offline on the current-query results
of each window, once with the code on main before 2026-11-27 (git show) and once with the
amended code in this branch.
"""
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
INTAKE = REPO / "audit" / "2026-11-24" / "intake"
OUT = HERE / "proposal_evidence.json"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
BASE_COMMIT = "c6c9789"   # main before the amendments of 2026-11-27
WINDOWS = {"W1": ("2026-11-17", "2026-11-24"), "W2": ("2026-11-10", "2026-11-17"),
           "W3": ("2026-11-03", "2026-11-10")}

TA = "TITLE_ABS:"
VARIANTS = {
    "be_comb_geometry": {
        "cur": '(honeycomb OR "comb building" OR "comb cell") AND (bee OR Apis)',
        "P1": f'{TA}(honeycomb OR "comb building" OR "comb cell") AND {TA}(bee OR Apis)'},
    "be_thermoregulation": {
        "cur": '(thermoregulation OR "brood temperature" OR "nest temperature") AND (Apis OR honeybee)',
        "P1": f'{TA}(thermoregulation OR "brood temperature" OR "nest temperature") AND {TA}(Apis OR honeybee)',
        "P3": f'{TA}(thermoregulation OR "brood temperature" OR "nest temperature" OR "brood nest" OR "cluster temperature") AND {TA}(Apis OR honeybee OR "honey bee")',
        "P3ft": '(thermoregulation OR "brood temperature" OR "nest temperature" OR "brood nest" OR "cluster temperature") AND (Apis OR honeybee OR "honey bee")'},
    "my_phosphorus": {
        "cur": "mycorrhiz* AND phosphorus AND transfer",
        "P1": f"{TA}(mycorrhiz*) AND {TA}(phosphorus) AND {TA}(transfer)",
        "P2": f'{TA}(mycorrhiz*) AND {TA}(phosphorus OR phosphate) AND {TA}(transfer OR uptake OR mobiliz* OR transloc* OR "32P" OR "33P" OR hyphal)',
        "P2ft": 'mycorrhiz* AND (phosphorus OR phosphate) AND (transfer OR uptake OR mobiliz* OR transloc* OR "32P" OR "33P" OR hyphal)'},
    "root_water_uptake": {
        "cur": '"root water uptake" AND ("soil water potential" OR drought)',
        "P1": f'{TA}("root water uptake") AND {TA}("soil water potential" OR drought)',
        "P4": f'{TA}("root water uptake" OR "root hydraulic conductivit*" OR "root system architecture") AND {TA}("soil water potential" OR drought)',
        "P4ft": '("root water uptake" OR "root hydraulic conductivit*" OR "root system architecture") AND ("soil water potential" OR drought)'},
    "biosphere_recycling": {
        "cur": 'biosphere AND ("nutrient recycling" OR "biogeochemical cycl*") AND (planetary OR Earth)',
        "P1": f'{TA}(biosphere) AND {TA}("nutrient recycling" OR "biogeochemical cycl*") AND {TA}(planetary OR Earth)'},
}
LABELS = {
    "PARTIAL": {"be_thermoregulation": ["43029483", "43048754"],
                "my_phosphorus": ["43041999", "43061600", "42985422", "42979373"],
                "root_water_uptake": ["43069007", "43075482", "42989086", "42985935"]},
    "PARTIAL_full_text_only": {"be_thermoregulation": ["43056305"]},
    "reasons": {
        "43029483": "BE thermo: multi-year smart-hive telemetry; inferred internal temperature 34.8 C and thermal buffer vs ambient (abstract).",
        "43048754": "BE thermo: Bombus brood incubation; off-genus (as in machine_reading.json).",
        "43056305": "BE thermo: brood-nest temperature only in the full text and S1/S2 Data.",
        "43041999": "MY: AMF-maize review on P exchange (as in machine_reading.json).",
        "43061600": "MY: ECM deep-soil review, nutrient mobilisation (as in machine_reading.json).",
        "42985422": "MY: AMF x P level x drought, N and P accumulation in oat organs.",
        "42979373": "MY: ECM tree masting; nutrient uptake by roots and mycorrhizas, equilibration across the mycorrhizal-root network.",
        "43069007": "ROOT_NET: AMF + PGPR maize under drought, root hydraulic conductivity.",
        "43075482": "ROOT_NET: review of legacies that constrain root water and nutrient uptake; hydraulic conductivity hysteresis.",
        "42989086": "ROOT_NET: water-uptake sources of a clonal wetland plant.",
        "42985935": "ROOT_NET: review of root system architecture under osmotic stress; drought lowers soil water potential."},
    "note": "Every other work returned by any variant in any window was judged NOT_RELEVANT on its abstract; records with no abstract were not judged and are counted apart.",
}
# Proposals 8 and 9: compared by hand, intake/weekly/2026-11-24/snapshots (fetched 2026-11-24)
# against the W1 re-fetch of 2026-11-27 (current queries). OBSERVED.
LATE_AND_PENDING = {
    "late_works_W1": {"note": "in the 2026-11-27 re-fetch of W1 but not in the 2026-11-24 snapshot; FIRST_IDATE 2026-11-21..2026-11-24",
                      "be_comb_geometry": ["43071390"],
                      "my_phosphorus": ["43075482", "43071297", "43073734", "43062364"],
                      "root_water_uptake": ["43069007", "43075482"],
                      "unreachable_by_next_7_day_window": {"43069007": "FIRST_IDATE 2026-11-23, PARTIAL (root)",
                                                           "43062364": "FIRST_IDATE 2026-11-21"},
                      "observed_lag_days_at_least": 3},
    "no_abstract_W1": {"PMC13781785": "now PMID 43082195 with an abstract, new FIRST_IDATE 2026-11-26 (inside the next window)",
                       "PMC13785964": "still no abstract", "PMC13787050": "still no abstract", "PMC13785933": "still no abstract"},
}
# The query clause groups as run on 2026-11-24 (for proposal 5, the flag).
GROUPS = {
    "be_comb_geometry": [r"honeycomb|comb building|comb cell", r"\bbee\b|\bApis\b"],
    "be_thermoregulation": [r"thermoregulation|brood temperature|nest temperature", r"\bApis\b|honeybee"],
    "my_phosphorus": [r"mycorrhiz", r"phosphorus", r"\btransfer"],
    "root_water_uptake": [r"root water uptake", r"soil water potential|drought"],
    "biosphere_recycling": [r"biosphere", r"nutrient recycling|biogeochemical cycl", r"planetary|Earth"],
}
ENTITY_NAMED = {"BE": r"\bbees?\b|\bApis\b|honey ?bee", "MY": r"mycorrhiz", "ROOT_NET": r"\broots?\b"}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def rid(r):
    return r.get("pmid") or r.get("pmcid") or r.get("id")


def fetch(raw):
    raw = Path(raw)
    raw.mkdir(parents=True, exist_ok=True)
    for w, (s, u) in WINDOWS.items():
        for q, vs in VARIANTS.items():
            for v, qs in vs.items():
                fn = raw / f"{q}__{v}__{w}.json"
                if fn.exists():
                    continue
                full = f"({qs}) AND FIRST_IDATE:[{s} TO {u}]"
                res, cur, hit = [], "*", None
                for _ in range(10):
                    url = EPMC + "?" + urllib.parse.urlencode({"query": full, "format": "json", "resultType": "core",
                                                               "pageSize": 100, "cursorMark": cur})
                    d = json.load(urllib.request.urlopen(url, timeout=180))
                    hit = d["hitCount"]
                    res += d["resultList"]["result"]
                    nc = d.get("nextCursorMark")
                    if len(res) >= hit or not nc or nc == cur:
                        break
                    cur = nc
                fn.write_text(json.dumps({"query": full, "fetched": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                          "hitCount": hit, "results": res}))
                print(fn.name, hit)


def query_table(ids, has_abs):
    P = {q: set(v) for q, v in LABELS["PARTIAL"].items()}
    PF = {q: set(v) for q, v in LABELS["PARTIAL_full_text_only"].items()}
    rows = {}
    for q, vs in VARIANTS.items():
        for v in vs:
            r = {"hits": 0, "with_abstract": 0, "relevant": 0, "current_relevant": 0,
                 "lost_vs_current": [], "gained_vs_current": [], "per_window_hits": {}}
            for w in WINDOWS:
                a, c = ids[f"{q}__{v}__{w}"], ids[f"{q}__cur__{w}"]
                both = P.get(q, set()) | PF.get(q, set())
                r["hits"] += len(a)
                r["with_abstract"] += sum(1 for x in a if has_abs[x])
                r["relevant"] += sum(1 for x in a if x in P.get(q, set()))
                r["current_relevant"] += sum(1 for x in c if x in P.get(q, set()))
                r["lost_vs_current"] += sorted({x for x in c if x in both} - set(a))
                r["gained_vs_current"] += sorted({x for x in a if x in both} - set(c))
                r["per_window_hits"][w] = len(a)
            kept = r["relevant"] - sum(1 for g in r["gained_vs_current"] if g in P.get(q, set()))
            r["precision"] = f"{r['relevant']}/{r['with_abstract']}"
            r["recall_vs_current"] = f"{kept}/{r['current_relevant']}"
            rows[f"{q}:{v}"] = r
    return rows


def run_intake(script, raw, w, variant_for, outdir):
    d = Path(outdir) / "snapshots"
    d.mkdir(parents=True)
    ents = []
    for q in VARIANTS:
        raw_d = json.loads((Path(raw) / f"{q}__{variant_for.get(q, 'cur')}__{w}.json").read_text())
        body = json.dumps({"hitCount": raw_d["hitCount"], "resultList": {"result": raw_d["results"]}}).encode()
        (d / f"{q}.json").write_bytes(body)
        ents.append({"query_id": q, "state": "SAVED", "file": f"{q}.json", "sha256": sha(body), "hit_count": raw_d["hitCount"]})
    (d / "manifest.json").write_text(json.dumps({"since": WINDOWS[w][0], "until": WINDOWS[w][1], "source": "evidence", "entries": ents}))
    subprocess.run([sys.executable, str(script), "offline", "--repo", str(REPO), "--queries", str(INTAKE / "intake_queries.json"),
                    "--out", str(outdir), "--snapshots", str(d)], check=True, capture_output=True)
    return json.loads((Path(outdir) / "intake.json").read_text())


def filter_tables(raw):
    P = {x for v in LABELS["PARTIAL"].values() for x in v}
    sys.path.insert(0, str(REPO / "audit" / "2026-11-24" / "biosphere"))
    import biosphere_candidates as bc
    res = {}
    with tempfile.TemporaryDirectory() as td:
        old = Path(td) / "weekly_intake_before.py"
        old.write_text(subprocess.run(["git", "-C", str(REPO), "show", f"{BASE_COMMIT}:audit/2026-11-24/intake/weekly_intake.py"],
                                      capture_output=True, text=True, check=True).stdout)
        # the old script finds its sibling tools relative to its own path; point it at the repo
        old_src = old.read_text().replace('HERE.parent / "deviation"', f'Path({str(INTAKE.parent / "deviation")!r})') \
                                  .replace('HERE.parent / "biosphere"', f'Path({str(INTAKE.parent / "biosphere")!r})')
        old.write_text(old_src)
        flag = {"flagged_relevant": 0, "flagged_not_relevant": 0, "unflagged_relevant": 0, "unflagged_not_relevant": 0}
        hx4 = {"stubs_before": 0, "on_partial_before": 0, "dependency_rule": 0, "dependency_rule_on_partial": 0,
               "dependency_and_entity_named": 0, "dependency_and_entity_named_on_partial": 0,
               "entity_rule_lost_partial": []}
        totals = {}
        for tag, script, variants in (("before", old, {}), ("amended_code_current_queries", INTAKE / "weekly_intake.py", {}),
                                      ("adopted", INTAKE / "weekly_intake.py", {"my_phosphorus": "P2"})):
            t = {"candidates": 0, "partial_candidates": 0, "HX1": 0, "HX1_on_partial": 0, "HX4": 0, "HX4_on_partial": 0}
            for w in WINDOWS:
                o = run_intake(script, raw, w, variants, Path(td) / f"{tag}_{w}")
                recs = {}
                for q in VARIANTS:
                    for r in json.loads((Path(raw) / f"{q}__{variants.get(q, 'cur')}__{w}.json").read_text())["results"]:
                        recs[r.get("pmid")] = r
                for c in o["candidates"]:
                    p = c["work"]["pmid"]
                    t["candidates"] += 1
                    t["partial_candidates"] += p in P
                    if tag == "before":
                        r = recs[p]
                        ta = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", (r.get("title") or "") + " " + r["abstractText"])).split())
                        f = not all(re.search(g, ta, re.I) for g in GROUPS[c["query_id"]])
                        flag[("flagged_" if f else "unflagged_") + ("relevant" if p in P else "not_relevant")] += 1
                for h in o["hypotheses"]:
                    p = h["touches"]["candidate"].split(":")[1]
                    if h["rule"] in ("HX1", "HX4"):
                        t[h["rule"]] += 1
                        t[h["rule"] + "_on_partial"] += p in P
                    if tag == "before" and h["rule"] == "HX4":
                        e, fld = h["touches"]["entity"], h["touches"]["field"]
                        ent = json.loads((REPO / next(x["path"] for x in json.loads((REPO / "ontology_index.json").read_text())["entities"] if x["id"] == e)).read_text())
                        deps = (ent["attributes"][fld].get("scope") or {}).get("dependencies") or []
                        dep = set(h["evidence_spans"]) & set(bc.terms_in(" ".join(deps).replace("_", " ")))
                        hx4["stubs_before"] += 1
                        hx4["on_partial_before"] += p in P
                        if dep:
                            hx4["dependency_rule"] += 1
                            hx4["dependency_rule_on_partial"] += p in P
                            if re.search(ENTITY_NAMED[e], re.sub(r"<[^>]+>", "", recs[p]["abstractText"]), re.I):
                                hx4["dependency_and_entity_named"] += 1
                                hx4["dependency_and_entity_named_on_partial"] += p in P
                            elif p in P:
                                hx4["entity_rule_lost_partial"].append(p)
            totals[tag] = t
        res = {"P5_flag_query_clause_not_in_abstract": flag, "P6_hx4": hx4, "pipeline_three_windows": totals}
    return res


def build(raw):
    raw = Path(raw)
    files, ids, has_abs = {}, {}, {}
    for f in sorted(raw.glob("*.json")):
        b = f.read_bytes()
        d = json.loads(b)
        files[f.name] = {"sha256": sha(b), "bytes": len(b), "query": d["query"], "fetched": d["fetched"], "hitCount": d["hitCount"]}
        ids[f.stem] = [rid(r) for r in d["results"]]
        for r in d["results"]:
            has_abs[rid(r)] = bool((r.get("abstractText") or "").strip())
    doc = {"record": "INTAKE_PROPOSAL_EVIDENCE", "date": "2026-11-27",
           "status": "PROPOSED evidence; MACHINE_READ_NOT_REVIEWED relevance labels; no claim_support",
           "reader": "Claude Opus 5.5 (Anthropic), working in Perplexity Computer",
           "windows": WINDOWS, "variants": VARIANTS, "labels": LABELS,
           "responses": files, "ids": ids, "has_abstract": has_abs,
           "query_table": query_table(ids, has_abs), "filters": filter_tables(raw),
           "late_and_pending": LATE_AND_PENDING}
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: (v["precision"], v["recall_vs_current"]) for k, v in doc["query_table"].items()}, indent=0))
    print(json.dumps(doc["filters"], indent=0))


def check():
    doc = json.loads(OUT.read_text(encoding="utf-8"))
    same = query_table(doc["ids"], doc["has_abstract"]) == doc["query_table"]
    print("query_table recomputed from the stored id lists matches:", same)
    return 0 if same else 1


if __name__ == "__main__":
    if sys.argv[1:2] == ["fetch"]:
        fetch(sys.argv[2])
    elif sys.argv[1:2] == ["build"]:
        build(sys.argv[2])
    elif sys.argv[1:2] == ["check"]:
        sys.exit(check())
    else:
        sys.exit(__doc__)
