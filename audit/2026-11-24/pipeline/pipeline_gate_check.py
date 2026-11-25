#!/usr/bin/env python3
"""
pipeline_gate_check.py -- reproduces the pipeline.sh finding and measures what a resolver changes.
Read-only; edits nothing. Needs jsonschema >= 4.18 (referencing). Usage: pipeline_gate_check.py <repo> <out>

For every ontology/<type>/*.json that has schemas/<type>.schema.json, validates twice:
  bare      jsonschema.validate(), as pipeline.sh does (no resolver)
  resolved  a draft-07 validator with a referencing.Registry of every file in schemas/, keyed by
            bare filename, the same idea as scripts/build_index.py's _shared_registry()
Then runs `./pipeline.sh validate` and records exit code, PASS/FAIL line counts, whether a
Results line printed, and the last line. Exit 0 always; this is an instrument, not a gate.
"""
import glob, json, os, re, subprocess, sys, collections
import jsonschema
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7

repo, out = sys.argv[1], sys.argv[2]
S = {os.path.basename(p): json.load(open(p)) for p in sorted(glob.glob(os.path.join(repo, "schemas", "*.json")))}
reg = Registry().with_resources([(k, Resource.from_contents(v, default_specification=DRAFT7)) for k, v in S.items()])
rows, tally = [], collections.Counter()
for d in sorted(glob.glob(os.path.join(repo, "ontology", "*", ""))):
    t = os.path.basename(d.rstrip("/")); sn = f"{t}.schema.json"
    if sn not in S:
        tally["no_schema_dir"] += 1; continue
    for f in sorted(glob.glob(d + "*.json")):
        data = json.load(open(f))
        try:
            jsonschema.validate(data, S[sn]); bare = "OK"
        except jsonschema.ValidationError:
            bare = "INVALID"
        except Exception as e:
            bare = f"CRASH {type(e).__name__}: {str(e)[:80]}"
        errs = list(jsonschema.validators.validator_for(S[sn])(S[sn], registry=reg).iter_errors(data))
        res = "OK" if not errs else f"INVALID ({len(errs)})"
        tally[("bare OK" if bare == "OK" else "bare CRASH" if bare.startswith("CRASH") else "bare INVALID") + " / resolved " + res.split()[0]] += 1
        if bare != "OK" or res != "OK":
            rows.append({"file": os.path.relpath(f, repo), "bare": bare, "resolved": res,
                         "first_errors": [e.message[:120] for e in errs[:3]]})
p = subprocess.run(["bash", os.path.join(repo, "pipeline.sh"), "validate"], cwd=repo, capture_output=True, text=True)
txt = re.sub(r"\x1b\[[0-9;]*m", "", p.stdout + p.stderr)
lines = [l for l in txt.splitlines() if l.strip()]
doc = {"record": "PIPELINE_GATE_CHECK", "status": "OBSERVED", "jsonschema": __import__("importlib.metadata").metadata.version("jsonschema"),
       "per_file": dict(tally), "not_clean": rows,
       "pipeline_validate": {"exit": p.returncode, "pass_lines": txt.count("[PASS]"), "fail_lines": txt.count("[FAIL]"),
                             "results_line_printed": any(l.startswith("Results:") for l in lines),
                             "last_line": lines[-1].strip() if lines else None}}
open(out, "w").write(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
print(json.dumps({k: doc[k] for k in ("per_file", "pipeline_validate")}, ensure_ascii=False, indent=1))
