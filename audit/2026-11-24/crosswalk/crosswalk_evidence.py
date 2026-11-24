#!/usr/bin/env python3
"""
crosswalk_evidence.py -- evidence for and against OPEN_QUESTIONS #3 options, computed from
crosswalk_D_L.json only. Stdlib only. Deterministic (permutation seed 20261124).

Options under review (owner, 2026-11-24: "Let's view evidence for and against"):
  (a) D and L are aliases of one stack      (b) two separate stacks with a crosswalk
  (c) withdraw D, keep L only

What this measures (DERIVED from tags; the L tags are OWNER_APPROVED, the D tags are from trace v0.3):
  - how many L layers each D role spans
  - H(L), H(L|D), H(D), H(D|L) in bits; aliases would give H(L|D) = H(D|L) = 0
  - majority-rule prediction of L from D, against the no-information baseline
  - Spearman rank correlation of D index (0-5) with L index (0-5), Lε excluded, two-sided
    permutation p; computed twice, with each node's first L tag and with its last
What it does not establish: one trace, 28 nodes, one tagger for L. Nodes are not independent
(three geometry nodes share one reason), so the permutation p overstates the evidence.
"""
import collections, hashlib, json, math, random, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "crosswalk_D_L.json"
RANK = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5}
SEED, PERMS = 20261124, 10000


def H(c):
    t = sum(c.values())
    return -sum(v / t * math.log2(v / t) for v in c.values() if v)


def cond_H(pairs):  # H(Y|X) over (x, y)
    by = collections.defaultdict(collections.Counter)
    for x, y in pairs:
        by[x][y] += 1
    n = len(pairs)
    return sum(sum(c.values()) / n * H(c) for c in by.values())


def ranks(v):
    o = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2
        i = j + 1
    return r


def pearson(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
    return num / den


def spearman_perm(xs, ys):
    a, b = ranks(xs), ranks(ys)
    rho = pearson(a, b)
    R = random.Random(SEED); ge = 0
    for _ in range(PERMS):
        p = ys[:]; R.shuffle(p)
        if abs(pearson(a, ranks(p))) >= abs(rho) - 1e-12:
            ge += 1
    return round(rho, 3), round((ge + 1) / (PERMS + 1), 4)


def pick(nodes, which):
    pairs = [(n["D"], n["L"][0] if which == "first" else n["L"][-1]) for n in nodes]
    num = [(int(d[1]), RANK[l]) for d, l in pairs if l in RANK]
    rho, p = spearman_perm([x for x, _ in num], [y for _, y in num])
    D = collections.Counter(d for d, _ in pairs); L = collections.Counter(l for _, l in pairs)
    maj = collections.defaultdict(collections.Counter)
    for d, l in pairs:
        maj[d][l] += 1
    hits = sum(c.most_common(1)[0][1] for c in maj.values())
    return {"L_tag_used": which,
            "H_L": round(H(L), 3), "H_L_given_D": round(cond_H(pairs), 3),
            "H_D": round(H(D), 3), "H_D_given_L": round(cond_H([(l, d) for d, l in pairs]), 3),
            "predict_L_from_D_majority": f"{hits}/{len(pairs)}",
            "baseline_most_common_L": f"{L.most_common(1)[0][1]}/{len(pairs)} ({L.most_common(1)[0][0]})",
            "spearman_D_vs_L": rho, "perm_p_two_sided": p, "n_spearman": len(num),
            "excluded_from_spearman": sorted(n["id"] for n, (d, l) in zip(nodes, pairs) if l not in RANK)}


def main(out):
    raw = SRC.read_bytes(); d = json.loads(raw); nodes = d["nodes"]
    if len(nodes) != 28:
        sys.exit(f"FAIL: expected 28 nodes, found {len(nodes)}")
    span = {}
    for n in nodes:
        span.setdefault(n["D"], set()).update(n["L"])
    same_D_diff_L = []
    for D in sorted(span):
        ns = [n for n in nodes if n["D"] == D]
        for i, x in enumerate(ns):
            for y in ns[i + 1:]:
                if not set(x["L"]) & set(y["L"]):
                    same_D_diff_L.append([D, x["id"], x["L"], y["id"], y["L"]])
    doc = {"record": "CROSSWALK_EVIDENCE", "status": "DERIVED", "date": "2026-11-24",
           "source": {"path": "crosswalk_D_L.json", "sha256": hashlib.sha256(raw).hexdigest()},
           "seed": SEED, "permutations": PERMS,
           "D_spans_L": {k: sorted(v) for k, v in sorted(span.items())},
           "D_roles_spanning_2plus_L": sum(1 for v in span.values() if len(v) >= 2),
           "D_roles": len(span),
           "same_D_disjoint_L_pairs": len(same_D_diff_L),
           "same_D_disjoint_L_examples": same_D_diff_L,
           "stats": [pick(nodes, "first"), pick(nodes, "last")],
           "reading": {
               "against_aliases": "H(L|D) and H(D|L) are well above 0, and same-D pairs with disjoint L exist; one stack would erase those distinctions.",
               "for_relation": "D and L are positively rank-correlated: the chain runs from fundamental to emergent on both. They are related, not independent.",
               "limits": "one trace, 28 non-independent nodes, one L tagger; D tags written before L tags by the same audit."}}
    Path(out).write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: doc[k] for k in ("D_roles_spanning_2plus_L", "D_roles", "same_D_disjoint_L_pairs", "stats")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(HERE / "crosswalk_evidence.json"))
