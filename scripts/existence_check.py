#!/usr/bin/env python3
"""
existence_check.py -- source pass, stage 1: can a cited work be found as cited?
Stdlib only.

  python3 scripts/existence_check.py run [--cache DIR]   # search PubMed, write the registry
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
STATES = ("FOUND_AS_CITED", "FOUND_DIFFERS", "NOT_FOUND_INDEXED", "NOT_INDEXED")
WEAKEST_FIRST = ("NOT_FOUND_INDEXED", "NOT_INDEXED", "FOUND_DIFFERS", "FOUND_AS_CITED")
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


def pick(work, records):
    """(identified record or None, candidate or None). A candidate passes the
    title thresholds but is not accepted as the cited work."""
    best = cand = None
    for rec in records:
        rv = record_view(rec)
        hold, cover = title_fit(work["title"], rv["title"])
        if hold >= TITLE_HOLD and cover >= TITLE_COVER:
            key = (hold + cover, fold(work["surname"]) in fold(rv["first_author"] or ""), work["year"] == rv["year"])
            if same_work(work, rv):
                if best is None or key > best[0]:
                    best = (key, rv)
            elif cand is None or key > cand[0]:
                cand = (key, rv)
    return (best[1] if best else None), (cand[1] if cand else None)


def string_state(work_states):
    if not work_states:
        return "NOT_INDEXED"
    return next(s for s in WEAKEST_FIRST if s in work_states)


# ----------------------------------------------------------------- network
class Client:
    def __init__(self, cache):
        self.cache = Path(cache)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.log = []

    def get(self, endpoint, params):
        url = EUTILS + endpoint + "?" + urllib.parse.urlencode(params)
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
        self.log.append({"endpoint": endpoint, "params": {k: v for k, v in params.items() if k != "retmode"},
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
         "No state means \"does not exist\". NOT_FOUND_INDEXED says one search of one",
         "index identified no record. NOT_INDEXED says the work is a book, a chapter",
         "or from a non-biomedical venue, or the string names no work, so PubMed is",
         "the wrong place to look.", "",
         "A string's state is the weakest among the works it names",
         "(NOT_FOUND_INDEXED, NOT_INDEXED, FOUND_DIFFERS, FOUND_AS_CITED).", "",
         "## Per entity", "",
         "| entity | attribute fields | sources | FOUND_AS_CITED | FOUND_DIFFERS | NOT_FOUND_INDEXED | NOT_INDEXED |",
         "|---|---|---|---|---|---|---|"]
    tot = {s: 0 for s in STATES}
    wtot = {s: 0 for s in STATES}
    nsrc = nworks = nfields = 0
    seen = set()
    differs, misses = [], []
    for ent, nat, src in top_entities():
        c = {s: 0 for s in STATES}
        for sid in src:
            ex = reg[sid]["existence"]
            c[ex["state"]] += 1
            if sid in seen:
                continue
            seen.add(sid)
            for w in ex["works"]:
                wtot[w["state"]] += 1
                nworks += 1
                if w["state"] == "FOUND_DIFFERS":
                    differs.append((ent, sid, w))
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
            L.append("- NOT_INDEXED %s `%s`: no work with an author and a year in the string: %s"
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
          "- A string with no quoted title is identified only when its description query returns",
          "  exactly one record; that is a weak identification and is listed under FOUND_DIFFERS",
          "  with the title cited as null.",
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
         and string_state([]) == "NOT_INDEXED" and string_state(["FOUND_AS_CITED"]) == "FOUND_AS_CITED")
    case("no state says a work does not exist", not any("EXIST" in s for s in STATES))
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
    if argv[:1] == ["report"]:
        report()
        return 0
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
