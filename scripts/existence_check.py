#!/usr/bin/env python3
"""
existence_check.py -- source pass, stage 1: can a cited work be found as cited?
Stdlib only.

  python3 scripts/existence_check.py run [--cache DIR]   # search PubMed, write the registry
  python3 scripts/existence_check.py resort              # apply UNDERSPECIFIED / MATCH_SUSPECT (offline)
  python3 scripts/existence_check.py second [--cache DIR] # Europe PMC, NOT_FOUND_INDEXED works only
  python3 scripts/existence_check.py report              # write docs/existence_check.md (offline)
  python3 scripts/existence_check.py --selftest          # parsing and comparison, offline

Rules: registry/DECLARED.json, amendment "existence states (source pass, stage 1)".
Uses NCBI esearch and esummary only: bibliographic summary records. It reads no
abstract and no full text, edits no source string and sets no status on any field.
No state means "does not exist".
"""

import hashlib
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import provenance_chain as pc   # noqa: E402
import export_reference as er   # noqa: E402

ROOT = pc.ROOT
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
TOP_ENTITIES = 10
STATES = ("FOUND_AS_CITED", "FOUND_DIFFERS", "MATCH_SUSPECT", "NOT_FOUND_INDEXED", "NOT_INDEXED",
          "UNDERSPECIFIED")
WEAKEST_FIRST = ("UNDERSPECIFIED", "NOT_FOUND_INDEXED", "NOT_INDEXED", "MATCH_SUSPECT", "FOUND_DIFFERS",
                 "FOUND_AS_CITED")
MISSES = ("NOT_FOUND_INDEXED", "NOT_INDEXED")
TITLE_HOLD, TITLE_COVER, MAX_RECORDS, MAX_TITLE_WORDS = 0.8, 0.5, 5, 8
STOP = set("the a an of and in on for to by with from at as is are its their this that into "
           "during using between among under over via not does can".split())
BOOK_MARKERS = (r"\bPress\b", r"\bUP\b", r"\bUniv\.", r"\bSpringer\b", r"McGraw-Hill", r"\bWiley\b",
                r"Harper", r"Chapman", r"\bBooks\b", r"\bed\.", r",\s+in\s+['A-Z]", r"\bvol \d")
NON_BIOMED = ("NeurIPS", "ACL", "EMNLP", "NAACL", "CHI", "ECCV", "ICML", "ICLR", "IEEE", "arXiv",
              "Machine Learning", "Discrete", "Geometry", "Physical Review", "Palaeogeography",
              "Artificial Life")

_PART = r"(?:(?:von der|von|van der|van|de|der)\s+)?"
_NAME = r"[A-ZÀ-Ý][\w\-]*(?:['’][\w\-]+)*"
WORK = re.compile(r"(%s%s(?:\s*(?:&|and)\s+%s%s|\s+et al\.)?)\s*,?\s*\((\d{4})\)" % (_PART, _NAME, _PART, _NAME))
_TITLE = re.compile(r"'(.+?)'(?=[\s,;.)]|$)")
_LOC = re.compile(r"(\d{1,4})\s*(?:\(\w+\))?\s*:\s*([A-Za-z]?\d+)(?:\s*[-–]\s*(\d+))?")


# ----------------------------------------------------------------- parsing
def fold(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s or "") if not unicodedata.combining(c)).lower()


def tokens(s, n=3):
    return [t for t in re.findall(r"[a-z0-9]+", fold(s)) if len(t) >= n]


def surname(author):
    first = re.split(r"\s*(?:&|\band\b|et al\.)", author)[0].strip()
    return first.split()[-1]


def parse_works(text):
    """Each 'Surname (YYYY)' occurrence is one work; its text runs to the next."""
    ms = list(WORK.finditer(text))
    out = []
    for i, m in enumerate(ms):
        span = text[m.start():ms[i + 1].start() if i + 1 < len(ms) else len(text)]
        rest = span[m.end() - m.start():]
        t = _TITLE.search(rest)
        after = rest[t.end():] if t else ""
        after = after.split(";")[0]
        loc = _LOC.search(after)
        venue = (after[:loc.start()] if loc else after)
        venue = re.sub(r"\s*\b(?:and|replicated by)\s*$", "", venue.split("(")[0].strip(" ,.")).strip(" ,.")
        desc = rest.split(";")[0] if not t else ""
        out.append({"author": m.group(1), "surname": surname(m.group(1)), "year": m.group(2),
                    "title": t.group(1) if t else None, "venue": venue or None,
                    "volume": loc.group(1) if loc else None,
                    "pages": (loc.group(2) + ("-" + loc.group(3) if loc.group(3) else "")) if loc else None,
                    "description": desc.strip(" ,.") or None, "text": span.strip(" ;")})
    return out


def looks_non_indexed(text):
    m = WORK.search(text)
    text = text[m.end():] if m else text      # markers are read after "(year)", not in author names
    return any(re.search(p, text) for p in BOOK_MARKERS) or any(
        re.search(r"(?<![A-Za-z])%s(?![a-z])" % re.escape(v), text) for v in NON_BIOMED)


def title_words(title):
    seen = []
    for t in tokens(title, 4):
        if t not in STOP and t not in seen:
            seen.append(t)
    return seen[:MAX_TITLE_WORDS]


# -------------------------------------------------------------- comparison
def expand_pages(p):
    """'1845-8' -> ('1845', '1848'); '929' -> ('929', None)."""
    if not p:
        return None, None
    m = re.match(r"\s*([A-Za-z]?\d+)(?:\s*[-–]\s*([A-Za-z]?\d+))?", p)
    if not m:
        return p.strip(), None
    a, b = m.group(1), m.group(2)
    if b and len(b) < len(a):
        b = a[:len(a) - len(b)] + b
    return a, b


def venue_agrees(cited, journal, abbrev):
    c = [t for t in tokens(cited, 1) if t not in STOP]
    for name in (journal, abbrev):
        r = [t for t in tokens(name, 1) if t not in STOP]
        if not r:
            continue
        if set(c) <= set(r) or set(r) <= set(c):
            return True
        if len(c) == 1 and "".join(w[0] for w in r).startswith(c[0]):   # acronym, e.g. PNAS
            return True
    return False


def title_fit(cited, record):
    c, r = set(tokens(cited)), set(tokens(record))
    if not c or not r:
        return 0.0, 0.0
    return len(c & r) / len(c), len(c & r) / len(r)


def record_view(rec):
    doi = next((a["value"] for a in rec.get("articleids", []) if a.get("idtype") == "doi"), None)
    return {"pmid": rec.get("uid"), "doi": doi, "title": (rec.get("title") or "").rstrip("."),
            "first_author": rec.get("sortfirstauthor"), "year": (rec.get("pubdate") or "")[:4] or None,
            "journal": rec.get("fulljournalname"), "journal_abbrev": rec.get("source"),
            "volume": rec.get("volume") or None, "pages": rec.get("pages") or None}


def compare(work, rv):
    """Returns (differs, not_compared). Items the string does not give are not compared."""
    differs, skipped = [], []

    def diff(item, cited, record):
        differs.append({"item": item, "cited": cited, "record": record})

    if fold(work["surname"]) not in fold(rv["first_author"] or ""):
        diff("author", work["author"], rv["first_author"])
    if work["year"] != rv["year"]:
        diff("year", work["year"], rv["year"])
    if work["title"] is None:
        diff("title", None, rv["title"])
    elif set(tokens(work["title"])) != set(tokens(rv["title"])):
        diff("title", work["title"], rv["title"])
    if work["venue"] is None:
        skipped.append("venue")
    elif not venue_agrees(work["venue"], rv["journal"], rv["journal_abbrev"]):
        diff("venue", work["venue"], rv["journal"])
    if work["volume"] is None:
        skipped.append("volume")
    elif not rv["volume"]:
        skipped.append("volume (record gives none)")
    elif work["volume"] != rv["volume"]:
        diff("volume", work["volume"], rv["volume"])
    if work["pages"] is None:
        skipped.append("pages")
    elif not rv["pages"]:
        skipped.append("pages (record gives none)")
    else:
        ca, cb = expand_pages(work["pages"])
        ra, rb = expand_pages(rv["pages"])
        if ca != ra or (cb and rb and cb != rb):
            diff("pages", work["pages"], rv["pages"])
    return differs, skipped


def same_work(work, rv):
    """Amended rule: first author agrees, or equal title with an agreeing year."""
    if fold(work["surname"]) in fold(rv["first_author"] or ""):
        return True
    return set(tokens(work["title"])) == set(tokens(rv["title"])) and work["year"] == rv["year"]


def pick(work, records, view=None):
    """(identified record or None, candidate or None). A candidate passes the
    title thresholds but is not accepted as the cited work."""
    best = cand = None
    for rec in records:
        rv = (view or record_view)(rec)
        hold, cover = title_fit(work["title"], rv["title"])
        if hold >= TITLE_HOLD and cover >= TITLE_COVER:
            key = (hold + cover, fold(work["surname"]) in fold(rv["first_author"] or ""), work["year"] == rv["year"])
            if same_work(work, rv):
                if best is None or key > best[0]:
                    best = (key, rv)
            elif cand is None or key > cand[0]:
                cand = (key, rv)
    return (best[1] if best else None), (cand[1] if cand else None)


def contiguous(cited_title, record_title):
    """The cited title's tokens appear, in order and adjacent, inside the record's title."""
    c, r = tokens(cited_title), tokens(record_title)
    return bool(c) and any(r[i:i + len(c)] == c for i in range(len(r) - len(c) + 1))


def is_suspect(cited, record, differs):
    """MATCH_SUSPECT: first author agrees, the cited title is not a contiguous
    run inside the record's title, and the year or the venue differs."""
    if record is None or not cited.get("title"):
        return False
    items = {d["item"] for d in differs}
    return "author" not in items and bool(items & {"year", "venue"}) \
        and not contiguous(cited["title"], record["title"])


def is_underspecified(cited):
    return not cited.get("title") and not cited.get("venue")


def resort_work(w, leads=()):
    """Apply the two added states to one stored work result. Returns the prior
    state when the state changed, else None. Nothing is searched."""
    before = w["state"]
    if before in MISSES and is_underspecified(w["cited"]):
        w["state"] = "UNDERSPECIFIED"
        w["note"] = "no title and no venue in the string: not searchable"
    elif before in ("FOUND_AS_CITED", "FOUND_DIFFERS") and is_suspect(w["cited"], w["matched_record"], w["differs"]):
        w["state"] = "MATCH_SUSPECT"
        w["note"] = "the record may be a different work by the same author; not counted as found"
    for ld in leads:
        if (ld["surname"], ld["year"], ld["title"]) == (surname(w["cited"]["author"]), w["cited"]["year"], w["cited"]["title"]):
            w["lead"] = ld["lead"]
    if w["state"] != before:
        w["resorted_from"] = before
        return before
    return None


def resort_entry(ex, leads=()):
    """Re-sort one registry existence block in place; recompute the string state."""
    for w in ex["works"]:
        resort_work(w, leads)
    before = ex["state"]
    ex["state"] = string_state([w["state"] for w in ex["works"]])
    if not ex["works"]:
        ex["note"] = "names no work"
    ex["matched_record"] = [w["matched_record"] for w in ex["works"]
                            if w["matched_record"] and w["state"] in ("FOUND_AS_CITED", "FOUND_DIFFERS")]
    if ex["state"] != before:
        ex["resorted_from"] = before
    return ex


def string_state(work_states):
    if not work_states:
        return "UNDERSPECIFIED"
    return next(s for s in WEAKEST_FIRST if s in work_states)


# ----------------------------------------------------------------- network
class Client:
    def __init__(self, cache):
        self.cache = Path(cache)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.log = []

    def get(self, endpoint, params, base=EUTILS):
        url = base + endpoint + "?" + urllib.parse.urlencode(params)
        f = self.cache / (hashlib.sha256(url.encode("utf-8")).hexdigest() + ".json")
        if f.exists():
            body = f.read_bytes()
        else:
            for attempt in range(4):
                try:
                    body = urllib.request.urlopen(url, timeout=40).read()
                    json.loads(body)
                    break
                except Exception:
                    if attempt == 3:
                        raise
                    time.sleep(2 + 2 * attempt)
            f.write_bytes(body)
            time.sleep(0.4)
        self.log.append({"endpoint": endpoint or base, "params": {k: v for k, v in params.items() if k != "retmode"},
                         "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()})
        return json.loads(body)

    def search(self, term):
        r = self.get("esearch.fcgi", {"db": "pubmed", "retmode": "json", "retmax": MAX_RECORDS, "term": term})
        res = r.get("esearchresult", {})
        return int(res.get("count", 0) or 0), res.get("idlist", [])

    def summaries(self, ids):
        if not ids:
            return []
        r = self.get("esummary.fcgi", {"db": "pubmed", "retmode": "json", "id": ",".join(ids)})
        return [r["result"][i] for i in ids if i in r.get("result", {})]


def check_work(work, client):
    queries, rv, cand = [], None, None
    words = title_words(work["title"]) if work["title"] else []
    if words:
        ti = " AND ".join("%s[ti]" % w for w in words)
        for term in ("%s[au] AND %s[pdat] AND %s" % (work["surname"], work["year"], ti),
                     "%s[au] AND %s" % (work["surname"], ti), ti):
            n, ids = client.search(term)
            queries.append({"term": term, "count": n})
            if n:
                rv, c = pick(work, client.summaries(ids))
                cand = cand or c
                if rv:
                    break
    else:
        desc = [w for w in title_words(work["description"] or "")][:4]
        term = "%s[au] AND %s[pdat]" % (work["surname"], work["year"]) + "".join(" AND %s[tiab]" % w for w in desc)
        n, ids = client.search(term)
        queries.append({"term": term, "count": n})
        if n == 1:
            rv = record_view(client.summaries(ids)[0])
    res = {"cited": {k: work[k] for k in ("author", "year", "title", "venue", "volume", "pages")},
           "text": work["text"], "queries": queries, "matched_record": None, "differs": [],
           "not_compared": [], "candidate": None, "note": None}
    if rv is not None:
        res["differs"], res["not_compared"] = compare(work, rv)
        res["matched_record"] = {k: rv[k] for k in ("pmid", "doi", "title", "first_author", "year", "journal", "volume", "pages")}
        res["state"] = "FOUND_DIFFERS" if res["differs"] else "FOUND_AS_CITED"
    else:
        res["state"] = "NOT_INDEXED" if looks_non_indexed(work["text"]) else "NOT_FOUND_INDEXED"
        if cand is not None:
            res["candidate"] = {k: cand[k] for k in ("pmid", "doi", "title", "first_author", "year", "journal")}
            res["note"] = "a record with a similar title and a different first author was returned; not accepted as the cited work"
        elif not work["title"]:
            res["note"] = "no title in the string; %d record(s) match the author, year and description words" % queries[-1]["count"]
        elif res["state"] == "NOT_INDEXED":
            res["note"] = "book, chapter or non-biomedical venue marker in the string; searched, no record identified"
    return res


# ------------------------------------------------------------ second index
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
EPMC_NAME = "Europe PMC"
VIEW_KEYS = ("pmid", "doi", "title", "first_author", "year", "journal", "volume", "pages")


def epmc_view(r):
    """One Europe PMC 'lite' result in the same shape as record_view."""
    return {"pmid": r.get("pmid"), "doi": r.get("doi"), "title": (r.get("title") or "").rstrip("."),
            "first_author": (r.get("authorString") or "").split(",")[0].strip(" .") or None,
            "year": r.get("pubYear"), "journal": r.get("journalTitle"), "journal_abbrev": None,
            "volume": r.get("journalVolume") or None, "pages": r.get("pageInfo") or None,
            "epmc_id": r.get("id"), "epmc_source": r.get("source")}


def epmc_terms(cited):
    """The same three steps as PubMed: author + year + title words; author + title words; title words."""
    words = title_words(cited["title"])
    ti = "TITLE:(%s)" % " AND ".join(words)
    au = 'AUTH:"%s"' % surname(cited["author"])
    return ["%s AND PUB_YEAR:%s AND %s" % (au, cited["year"], ti), "%s AND %s" % (au, ti), ti]


def epmc_search(client, term):
    r = client.get("", {"query": term, "format": "json", "resultType": "lite", "pageSize": MAX_RECORDS}, base=EPMC)
    return int(r.get("hitCount", 0) or 0), (r.get("resultList") or {}).get("result", [])


def second_index_work(cited, client):
    """Search Europe PMC for one titled work. Returns the second_index block."""
    work = dict(cited, surname=surname(cited["author"]))
    queries, rv, cand = [], None, None
    for term in epmc_terms(cited):
        n, results = epmc_search(client, term)
        queries.append({"term": term, "count": n})
        if n:
            rv, c = pick(work, results, view=epmc_view)
            cand = cand or c
            if rv:
                break
    out = {"index": EPMC_NAME, "queries": queries, "state": "NOT_FOUND_INDEXED", "matched_record": None,
           "differs": [], "not_compared": [], "candidate": None, "openalex": "NOT_REACHED"}
    if rv is not None:
        out["differs"], out["not_compared"] = compare(work, rv)
        out["matched_record"] = dict({k: rv[k] for k in VIEW_KEYS}, index=EPMC_NAME,
                                     epmc_id=rv["epmc_id"], epmc_source=rv["epmc_source"])
        out["state"] = "FOUND_DIFFERS" if out["differs"] else "FOUND_AS_CITED"
        if is_suspect(cited, out["matched_record"], out["differs"]):
            out["state"] = "MATCH_SUSPECT"
        out["openalex"] = "NOT_NEEDED"
    elif cand is not None:
        out["candidate"] = dict({k: cand[k] for k in VIEW_KEYS[:6]}, index=EPMC_NAME)
    return out


def apply_second(w, block):
    """Attach a second-index block to a work. A FOUND state replaces the work's
    state and record; the PubMed outcome is kept under 'pubmed'."""
    w["second_index"] = block
    if block["state"] in ("FOUND_AS_CITED", "FOUND_DIFFERS"):
        w["pubmed"] = {"state": w["state"], "matched_record": w["matched_record"], "differs": w["differs"]}
        w["state"], w["matched_record"] = block["state"], block["matched_record"]
        w["differs"], w["not_compared"] = block["differs"], block["not_compared"]
        w["note"] = "not identified in PubMed by the search; identified in %s" % block["index"]
    return w


def second(cache, scope=("NOT_FOUND_INDEXED",)):
    """Europe PMC search of the works in `scope`. Writes the registry."""
    reg_path = ROOT / "registry" / "sources.json"
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    client = Client(cache)
    n, results = epmc_search(client, epmc_terms({"author": "Sumbre et al.", "year": "2001",
                                                 "title": "Control of Octopus Arm Extension by a Peripheral Motor Program"})[0])
    ctl = epmc_view(results[0]) if results else {}
    if not (n == 1 and ctl.get("pmid") == "11546877" and ctl.get("first_author", "").startswith("Sumbre")
            and ctl.get("year") == "2001" and ctl.get("volume") == "293"):
        raise SystemExit("control failed: the adapter does not read the response shape; nothing written")
    print("control ok: Sumbre 2001 read as PMID %s, %s %s:%s" % (ctl["pmid"], ctl["journal"], ctl["volume"], ctl["pages"]))
    today = date.today().isoformat()
    for e in reg["sources"]:
        ex = e.get("existence")
        if not ex:
            continue
        for w in ex["works"]:
            if w["state"] in scope and "second_index" not in w and w["cited"]["title"]:
                apply_second(w, dict(second_index_work(w["cited"], client), checked=today))
                b = w["second_index"]
                print("%-18s %s (%s) %s" % (b["state"], w["cited"]["author"], w["cited"]["year"],
                                            [q["count"] for q in b["queries"]]))
        ex["state"] = string_state([w["state"] for w in ex["works"]])
        ex["matched_record"] = [w["matched_record"] for w in ex["works"]
                                if w["matched_record"] and w["state"] in ("FOUND_AS_CITED", "FOUND_DIFFERS")]
    pc.dump(reg_path, reg)
    seen, files = set(), []
    for item in client.log:
        if item["sha256"] not in seen:
            seen.add(item["sha256"])
            files.append(item)
    pc.dump(ROOT / "provenance" / "as_received" / "existence_second_index_MANIFEST.json", {
        "date": today, "status": "HASHES_ONLY_SPECIMENS_NOT_COMMITTED", "kept_in_repository": False,
        "provenance_note": "Responses of the Europe PMC REST search (resultType lite) received by "
                           "scripts/existence_check.py second. Bibliographic records only. Hashes identify "
                           "the received bytes; they do not authenticate the source. api.openalex.org was "
                           "not reached from this environment (egress proxy, HTTP 403 on CONNECT).",
        "requests": len(client.log), "distinct_responses": len(files), "files": files})
    print("requests: %d   distinct responses: %d" % (len(client.log), len(files)))


# ------------------------------------------------------------------- scope
def top_entities(root=ROOT, n=TOP_ENTITIES):
    """[(entity, attribute field count, [source ids])], count descending, id ascending."""
    rows = []
    for ent, (_, steps) in er.head_steps(root).items():
        at = [s for s in steps if s["params"]["field"].startswith("attributes.")]
        if at:
            src = []
            for s in at:
                src += [i for i in s["inputs"] if i not in src]
            rows.append((ent, len(at), src))
    rows.sort(key=lambda r: (-r[1], r[0]))
    return rows[:n]


def run(cache):
    reg_path = ROOT / "registry" / "sources.json"
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    by = {e["id"]: e for e in reg["sources"]}
    client = Client(cache)
    today = date.today().isoformat()
    for ent, _, src in top_entities():
        for sid in src:
            e = by[sid]
            works = [check_work(w, client) for w in parse_works(e["string"])]
            e["existence"] = {
                "state": string_state([w["state"] for w in works]),
                "matched_record": [w["matched_record"] for w in works if w["matched_record"]],
                "checked": today, "index": "PubMed (NCBI esearch + esummary)",
                "note": None if works else "no work with an author and a year in the string",
                "works": works}
            print("%-18s %-10s %s" % (e["existence"]["state"], ent, e["string"][:80]))
    out = []
    for e in reg["sources"]:
        e.setdefault("existence", None)
        out.append({k: e[k] for k in ("id", "string", "same_as", "opened", "fetched", "existence")})
    reg["sources"] = out
    pc.dump(reg_path, reg)
    seen, files = set(), []
    for item in client.log:
        if item["sha256"] not in seen:
            seen.add(item["sha256"])
            files.append(item)
    pc.dump(ROOT / "provenance" / "as_received" / "existence_MANIFEST.json", {
        "date": today, "status": "HASHES_ONLY_SPECIMENS_NOT_COMMITTED", "kept_in_repository": False,
        "provenance_note": "Responses of NCBI esearch and esummary (db=pubmed) received by scripts/existence_check.py. "
                           "Bibliographic summary records only; no abstract and no full text was fetched. "
                           "Hashes identify the received bytes; they do not authenticate the source.",
        "requests": len(client.log), "distinct_responses": len(files), "files": files})
    print("requests: %d   distinct responses: %d" % (len(client.log), len(files)))


def resort():
    """Offline: apply UNDERSPECIFIED and MATCH_SUSPECT to the stored results."""
    reg_path = ROOT / "registry" / "sources.json"
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    leads = pc.load(ROOT / "registry" / "existence_leads.json", {"leads": []})["leads"]
    moved = {}
    for e in reg["sources"]:
        ex = e.get("existence")
        if not ex:
            continue
        resort_entry(ex, leads)
        for w in ex["works"]:
            if "resorted_from" in w:
                k = "%s -> %s" % (w["resorted_from"], w["state"])
                moved[k] = moved.get(k, 0) + 1
    pc.dump(reg_path, reg)
    for k, v in sorted(moved.items()):
        print("works %-40s %d" % (k, v))


# ------------------------------------------------------------------ report
def report():
    reg = {e["id"]: e for e in json.loads((ROOT / "registry" / "sources.json").read_text(encoding="utf-8"))["sources"]}
    L = ["# Existence check, top 10 entities (source pass, stage 1)", "",
         "Status: PROPOSED. Written by `scripts/existence_check.py report` from",
         "`registry/sources.json`; do not edit by hand. Co-authored (JinnZ2 + Claude).", "",
         "What was checked: whether each cited work can be found in PubMed as cited,",
         "through NCBI esearch and esummary (bibliographic records). No abstract and",
         "no full text was read, so **no field gained a status** and no source is",
         "marked opened. A found record shows the work exists and how it is indexed.",
         "It does not show that the work supports the value it is cited for.", "",
         "No state means \"does not exist\".", "",
         "| state | meaning |", "|---|---|",
         "| FOUND_AS_CITED | a record is identified and every compared item agrees |",
         "| FOUND_DIFFERS | a record is identified and at least one item differs |",
         "| MATCH_SUSPECT | a record by the same first author was returned, but it may be a different work; not counted as found |",
         "| NOT_FOUND_INDEXED | a titled work was searched and no record identified |",
         "| NOT_INDEXED | a book, a chapter or a non-biomedical venue: PubMed is the wrong place to look |",
         "| UNDERSPECIFIED | no title and no venue in the string, or the string names no work: not searchable, so not a miss |", "",
         "A string's state is the weakest among the works it names",
         "(%s)." % ", ".join(WEAKEST_FIRST), "",
         "## Per entity", "",
         "| entity | attribute fields | sources | %s |" % " | ".join(STATES),
         "|---|---|---|" + "---|" * len(STATES)]
    tot = {s: 0 for s in STATES}
    wtot = {s: 0 for s in STATES}
    nsrc = nworks = nfields = 0
    seen = set()
    differs, misses, suspects = [], [], []
    before_w = {s: 0 for s in STATES}
    before_s = {s: 0 for s in STATES}
    for ent, nat, src in top_entities():
        c = {s: 0 for s in STATES}
        for sid in src:
            ex = reg[sid]["existence"]
            c[ex["state"]] += 1
            if sid in seen:
                continue
            seen.add(sid)
            before_s[ex.get("resorted_from", ex["state"])] += 1
            for w in ex["works"]:
                wtot[w["state"]] += 1
                before_w[w.get("resorted_from", w["state"])] += 1
                nworks += 1
                if w["state"] == "FOUND_DIFFERS":
                    differs.append((ent, sid, w))
                elif w["state"] == "MATCH_SUSPECT":
                    suspects.append((ent, sid, w))
                elif w["state"] != "FOUND_AS_CITED":
                    misses.append((ent, sid, w))
            if not ex["works"]:
                misses.append((ent, sid, None))
        for s in STATES:
            tot[s] += c[s]
        nsrc += len(src)
        nfields += nat
        L.append("| %s | %d | %d | %s |" % (ent, nat, len(src), " | ".join(str(c[s]) for s in STATES)))
    L.append("| total | %d | %d | %s |" % (nfields, nsrc, " | ".join(str(tot[s]) for s in STATES)))
    L += ["", "Per work (a string may name several): %d works in %d strings. %s." % (
        nworks, len(seen), ", ".join("%s %d" % (s, wtot[s]) for s in STATES)), "",
        "## Before and after the re-sort", "",
        "The re-sort (amendment \"UNDERSPECIFIED + MATCH_SUSPECT\") searched nothing. It",
        "relabeled stored results: a miss with no title and no venue became",
        "UNDERSPECIFIED, the string naming no work became UNDERSPECIFIED, and a match",
        "that may be a different work by the same author became MATCH_SUSPECT.", "",
        "| state | strings before | strings after | works before | works after |", "|---|---|---|---|---|"] + [
        "| %s | %d | %d | %d | %d |" % (s, before_s[s], sum(reg[i]["existence"]["state"] == s for i in seen),
                                       before_w[s], wtot[s]) for s in STATES] + [
        "| total | %d | %d | %d | %d |" % (len(seen), len(seen), nworks, nworks), "",
        "## MATCH_SUSPECT", ""] + [x for ent, sid, w in suspects for x in (
            "- **%s** `%s` %s (%s) '%s'" % (ent, sid[:12], w["cited"]["author"], w["cited"]["year"], w["cited"]["title"]),
            "  - record returned: PMID %s. %s (%s) %s. %s %s:%s" % (
                w["matched_record"]["pmid"], w["matched_record"]["first_author"], w["matched_record"]["year"],
                w["matched_record"]["title"], w["matched_record"]["journal"], w["matched_record"]["volume"],
                w["matched_record"]["pages"]),
            "  - differs in: %s" % ", ".join(d["item"] for d in w["differs"]),
            "  - lead: %s" % w.get("lead", "none"))] + ([] if suspects else ["None."]) + ["",
        "## FOUND_DIFFERS", "",
        "Each line: the work as cited, the record identified, and every item that",
        "differs. The source strings are unchanged; these are records of a",
        "difference, not corrections applied.", ""]
    for ent, sid, w in differs:
        m = w["matched_record"]
        L.append("- **%s** `%s` %s (%s)%s" % (ent, sid[:12], w["cited"]["author"], w["cited"]["year"],
                                              " '%s'" % w["cited"]["title"] if w["cited"]["title"] else " [no title in the string]"))
        L.append("  - record: PMID %s%s. %s (%s) %s. %s %s:%s" % (
            m["pmid"], ", DOI %s" % m["doi"] if m["doi"] else "", m["first_author"], m["year"], m["title"],
            m["journal"], m["volume"] or "[no volume]", m["pages"] or "[no pages in the record]"))
        for d in w["differs"]:
            L.append("  - %s: cited %s; record %s" % (d["item"], json.dumps(d["cited"], ensure_ascii=False),
                                                     json.dumps(d["record"], ensure_ascii=False)))
    if not differs:
        L.append("None.")
    L += ["", "## Found as cited", ""]
    for ent, _, src in top_entities():
        for sid in src:
            for w in reg[sid]["existence"]["works"]:
                if w["state"] == "FOUND_AS_CITED":
                    m = w["matched_record"]
                    L.append("- %s `%s` %s (%s): PMID %s%s%s" % (
                        ent, sid[:12], w["cited"]["author"], w["cited"]["year"], m["pmid"],
                        ", DOI %s" % m["doi"] if m["doi"] else "",
                        "; not compared: " + ", ".join(w["not_compared"]) if w["not_compared"] else ""))
    L += ["", "## Not identified", ""]
    for ent, sid, w in misses:
        if w is None:
            L.append("- UNDERSPECIFIED %s `%s`: names no work: %s"
                     % (ent, sid[:12], reg[sid]["string"]))
        else:
            L.append("- %s %s `%s` %s (%s)%s%s" % (
                w["state"], ent, sid[:12], w["cited"]["author"], w["cited"]["year"],
                " '%s'" % w["cited"]["title"] if w["cited"]["title"] else "",
                " [%s]" % w["note"] if w["note"] else ""))
    L += ["", "## Limits", "",
          "- One index. A work absent from PubMed may be in another index; nothing else was searched.",
          "- The match rule is mechanical (declared before the run). A work whose cited title is",
          "  paraphrased, or whose first author is cited differently, can be missed.",
          "- UNDERSPECIFIED says the string gives too little to search on. It says nothing about",
          "  the work. The works were searched once by description words before this state",
          "  existed; those searches identified nothing and are kept on each work under queries.",
          "- MATCH_SUSPECT is a mechanical test (title run, year or venue). It was written after",
          "  the one row it applies to was seen.",
          "- The book and non-biomedical test is a word list. It decides only the label of a miss.",
          ""]
    (ROOT / "docs" / "existence_check.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[L.index("## Per entity"):L.index("## Found as cited")]))


# ---------------------------------------------------------------- selftest
def selftest():
    cases = []

    def case(name, ok):
        cases.append((name, bool(ok)))

    w = parse_works("Sumbre et al. (2001) 'Control of Octopus Arm Extension by a Peripheral Motor Program', "
                    "Science 293:1845-1848; Hochner et al. (2006) 'A Unified View of Animal Body Movements', Science.")
    case("two works parsed", len(w) == 2 and w[0]["surname"] == "Sumbre" and w[1]["year"] == "2006")
    case("venue, volume, pages read", (w[0]["venue"], w[0]["volume"], w[0]["pages"]) == ("Science", "293", "1845-1848"))
    case("venue without a locator", w[1]["venue"] == "Science" and w[1]["volume"] is None)
    w = parse_works("von Frisch (1967) 'The Dance Language and Orientation of Bees' (Nobel Prize, 1973); replicated by "
                    "Seeley (1995) 'The Wisdom of the Hive' and Seeley (2010) 'Honeybee Democracy'; 50+ replications.")
    case("three works, particle surname", [x["surname"] for x in w] == ["Frisch", "Seeley", "Seeley"])
    w = parse_works("Askew et al. (2014) 'The kangaroo's tail propels and powers pentapedal locomotion', Biology Letters 10:20140381.")
    case("apostrophe inside a title", w[0]["title"] == "The kangaroo's tail propels and powers pentapedal locomotion"
         and w[0]["pages"] == "20140381")
    w = parse_works("Pratt et al. (2002) nest emigration studies; Temnothorax genus.")
    case("untitled work keeps a description", w[0]["title"] is None and w[0]["description"] == "nest emigration studies")
    case("no author-year: no work", parse_works("GPS collar data from Yellowstone packs, 2005-2020.") == [])
    case("abbreviated pages expanded", expand_pages("1845-8") == ("1845", "1848") and expand_pages("929") == ("929", None))
    case("venue: containment and acronym",
         venue_agrees("Current Biology", "Current biology : CB", "Curr Biol")
         and venue_agrees("PNAS", "Proceedings of the National Academy of Sciences of the United States of America", "Proc Natl Acad Sci U S A")
         and not venue_agrees("Nature", "Science (New York, N.Y.)", "Science"))
    rec = {"uid": "1", "title": "Control of octopus arm extension by a peripheral motor program.",
           "sortfirstauthor": "Sumbre G", "pubdate": "2001 Sep 7", "fulljournalname": "Science (New York, N.Y.)",
           "source": "Science", "volume": "293", "pages": "1845-8", "articleids": [{"idtype": "doi", "value": "10.1/x"}]}
    work = parse_works("Sumbre et al. (2001) 'Control of Octopus Arm Extension by a Peripheral Motor Program', Science 293:1845-1848")[0]
    rv = pick(work, [rec])[0]
    case("record picked by title", rv is not None and rv["pmid"] == "1" and rv["doi"] == "10.1/x")
    case("all items agree -> no difference", compare(work, rv) == ([], []))
    bad = parse_works("Sumbre et al. (2002) 'Control of Octopus Arm Extension by a Peripheral Motor Program', Nature 411:595-598")[0]
    d = [x["item"] for x in compare(bad, pick(bad, [rec])[0])[0]]
    case("year, venue, volume, pages differences listed", d == ["year", "venue", "volume", "pages"])
    other = parse_works("Sumbre et al. (2001) 'Octopus shows controlled arm coordination despite decentralized neural design', Nature 411:595-598")[0]
    case("a different title is not picked", pick(other, [rec]) == (None, None))
    wrong = parse_works("Jones et al. (1999) 'Control of Octopus Arm Extension by a Peripheral Motor Program', Science")[0]
    got, cand = pick(wrong, [rec])
    case("same title, other first author, other year: candidate only", got is None and cand["pmid"] == "1")
    coauthor = parse_works("Jones et al. (2001) 'Control of Octopus Arm Extension by a Peripheral Motor Program', Science")[0]
    got, _ = pick(coauthor, [rec])
    case("same title and year, other first author: identified, author listed as differing",
         got is not None and [x["item"] for x in compare(coauthor, got)[0]] == ["author"])
    nopages = dict(rv, pages=None, volume=None)
    case("an item the record does not give is not compared",
         compare(work, nopages) == ([], ["volume (record gives none)", "pages (record gives none)"]))
    case("a publisher name in the author position is not a marker",
         not looks_non_indexed("Wiley et al. (2011) Gulf of Maine bubble-net studies"))
    nt = parse_works("Mikolov et al. (2013) 'Distributed representations of words', NeurIPS (Word2Vec)")[0]
    case("items not given are not compared", compare(parse_works("Sumbre et al. (2001) 'Control of Octopus Arm Extension by a Peripheral Motor Program'")[0], rv)[1] == ["venue", "volume", "pages"])
    case("miss label: non-biomedical venue and book", looks_non_indexed(nt["text"])
         and looks_non_indexed("Seeley (2010) 'Honeybee Democracy', Princeton UP.")
         and not looks_non_indexed("Dawson & Taylor (1973) 'Energetic cost of locomotion in kangaroos', Nature 246:313-314"))
    case("string state is the weakest work", string_state(["FOUND_AS_CITED", "NOT_INDEXED"]) == "NOT_INDEXED"
         and string_state(["FOUND_DIFFERS", "FOUND_AS_CITED"]) == "FOUND_DIFFERS"
         and string_state(["NOT_INDEXED", "NOT_FOUND_INDEXED"]) == "NOT_FOUND_INDEXED"
         and string_state([]) == "UNDERSPECIFIED" and string_state(["FOUND_AS_CITED"]) == "FOUND_AS_CITED")
    case("no state says a work does not exist", not any("EXIST" in s for s in STATES))
    case("contiguous title run", contiguous("Evidence for distributed light-sensing in the skin of cuttlefish",
                                            "Evidence for distributed light sensing in the skin of cuttlefish, Sepia officinalis")
         and not contiguous("Ant colony system", "Ant system: optimization by a colony of cooperating agents"))
    dor = {"cited": {"author": "Dorigo & Gambardella", "year": "1997", "title": "Ant colony system", "venue": "IEEE TEC"},
           "state": "FOUND_DIFFERS", "note": None,
           "matched_record": {"title": "Ant system: optimization by a colony of cooperating agents"},
           "differs": [{"item": "year"}, {"item": "title"}, {"item": "venue"}]}
    lead = [{"surname": "Dorigo", "year": "1997", "title": "Ant colony system", "lead": "x"}]
    case("same author, other title, other year -> MATCH_SUSPECT, lead attached",
         resort_work(dor, lead) == "FOUND_DIFFERS" and dor["state"] == "MATCH_SUSPECT" and dor["lead"] == "x")
    ext = {"cited": {"author": "M", "year": "2008", "title": "Evidence for distributed light-sensing in the skin of cuttlefish", "venue": "J"},
           "state": "FOUND_DIFFERS", "note": None,
           "matched_record": {"title": "Evidence for distributed light sensing in the skin of cuttlefish, Sepia officinalis"},
           "differs": [{"item": "year"}, {"item": "title"}, {"item": "venue"}]}
    case("a longer record title that contains the cited one stays FOUND_DIFFERS",
         resort_work(ext) is None and ext["state"] == "FOUND_DIFFERS")
    bare = {"cited": {"author": "Pratt et al.", "year": "2002", "title": None, "venue": None},
            "state": "NOT_FOUND_INDEXED", "note": None, "matched_record": None, "differs": []}
    titled = {"cited": {"author": "A", "year": "2002", "title": "T", "venue": None},
              "state": "NOT_FOUND_INDEXED", "note": None, "matched_record": None, "differs": []}
    case("no title and no venue -> UNDERSPECIFIED; a titled miss stays a miss",
         resort_work(bare) == "NOT_FOUND_INDEXED" and bare["state"] == "UNDERSPECIFIED"
         and resort_work(titled) is None and titled["state"] == "NOT_FOUND_INDEXED")
    none = resort_entry({"state": "NOT_INDEXED", "works": [], "matched_record": [], "note": None})
    case("a string naming no work -> UNDERSPECIFIED, note 'names no work'",
         none["state"] == "UNDERSPECIFIED" and none["note"] == "names no work" and none["resorted_from"] == "NOT_INDEXED")
    er_ = {"id": "PMC1", "source": "MED", "pmid": "7", "doi": "10.1/y", "title": "Energetic cost of locomotion in kangaroos.",
           "authorString": "Dawson TJ, Taylor CR.", "pubYear": "1973", "journalTitle": "Nature",
           "journalVolume": "246", "pageInfo": "313-314"}
    ev = epmc_view(er_)
    case("Europe PMC result read into the common shape",
         (ev["pmid"], ev["first_author"], ev["year"], ev["journal"], ev["volume"], ev["pages"])
         == ("7", "Dawson TJ", "1973", "Nature", "246", "313-314"))
    cited = {"author": "Dawson & Taylor", "year": "1973", "title": "Energetic cost of locomotion in kangaroos",
             "venue": "Nature", "volume": "246", "pages": "313-314"}
    case("Europe PMC terms mirror the three PubMed steps",
         epmc_terms(cited) == ['AUTH:"Dawson" AND PUB_YEAR:1973 AND TITLE:(energetic AND cost AND locomotion AND kangaroos)',
                               'AUTH:"Dawson" AND TITLE:(energetic AND cost AND locomotion AND kangaroos)',
                               'TITLE:(energetic AND cost AND locomotion AND kangaroos)'])

    class Fake:
        def __init__(self, results):
            self.results, self.log = results, []

        def get(self, endpoint, params, base=None):
            return {"hitCount": len(self.results), "resultList": {"result": self.results}}

    b = second_index_work(cited, Fake([er_]))
    case("second index: found as cited", b["state"] == "FOUND_AS_CITED" and b["matched_record"]["index"] == "Europe PMC"
         and b["openalex"] == "NOT_NEEDED")
    b2 = second_index_work(cited, Fake([]))
    case("second index: a miss stays a miss, OpenAlex recorded as not reached",
         b2["state"] == "NOT_FOUND_INDEXED" and b2["openalex"] == "NOT_REACHED" and len(b2["queries"]) == 3)
    b3 = second_index_work(cited, Fake([dict(er_, authorString="Smith A.", pubYear="1990")]))
    case("second index: other author and year is a candidate, not a find",
         b3["state"] == "NOT_FOUND_INDEXED" and b3["candidate"]["first_author"] == "Smith A")
    b4 = second_index_work(cited, Fake([dict(er_, journalVolume="247")]))
    case("second index: a differing volume is listed", b4["state"] == "FOUND_DIFFERS"
         and [d["item"] for d in b4["differs"]] == ["volume"])
    w0 = {"state": "NOT_FOUND_INDEXED", "matched_record": None, "differs": [], "not_compared": [], "note": None}
    apply_second(w0, b)
    w1 = {"state": "NOT_FOUND_INDEXED", "matched_record": None, "differs": [], "not_compared": [], "note": None}
    apply_second(w1, b2)
    case("a find replaces the work's state and keeps the PubMed outcome; a miss changes nothing",
         w0["state"] == "FOUND_AS_CITED" and w0["pubmed"]["state"] == "NOT_FOUND_INDEXED"
         and w1["state"] == "NOT_FOUND_INDEXED" and "pubmed" not in w1 and w1["second_index"]["openalex"] == "NOT_REACHED")
    case("UNDERSPECIFIED is the weakest string state",
         string_state(["UNDERSPECIFIED", "NOT_FOUND_INDEXED", "FOUND_AS_CITED"]) == "UNDERSPECIFIED"
         and string_state(["MATCH_SUSPECT", "FOUND_DIFFERS"]) == "MATCH_SUSPECT")
    failed = 0
    for name, ok in cases:
        failed += not ok
        print("  %s  %s" % ("ok  " if ok else "FAIL", name))
    print("selftest checks: %d   failed: %d" % (len(cases), failed))
    return 1 if failed else 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if argv[:1] == ["run"]:
        cache = argv[argv.index("--cache") + 1] if "--cache" in argv else str(ROOT / ".existence_cache")
        run(cache)
        return 0
    if argv[:1] == ["second"]:
        cache = argv[argv.index("--cache") + 1] if "--cache" in argv else str(ROOT / ".existence_cache")
        second(cache)
        return 0
    if argv[:1] == ["resort"]:
        resort()
        return 0
    if argv[:1] == ["report"]:
        report()
        return 0
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
