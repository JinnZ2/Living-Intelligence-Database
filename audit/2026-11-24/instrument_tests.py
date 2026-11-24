"""Isolated execution tests of LID validation instruments. Run from a COPY of the repo root."""
import json, sys, os, collections, subprocess
from pathlib import Path
ROOT=Path.cwd(); sys.path.insert(0,str(ROOT/'validation'))
import verify, falsifier, dependency_tree as dt, audit, scope_checker as sc
idx=json.load(open(ROOT/'ontology_index.json'))
R={}
def rec(k,v): R[k]=v; print(f'== {k}:', json.dumps(v)[:900])

# ---------- Entity loading ----------
load_fail=[]; attrs_count=collections.Counter(); scoped_ents=0
for e in idx['entities']:
    p=e.get('path')
    try: full=json.load(open(ROOT/p))
    except Exception as ex: load_fail.append((e['id'],p,type(ex).__name__)); continue
    a=full.get('attributes',{}); 
    if any(sc.is_scoped(v) for v in a.values()): scoped_ents+=1
rec('T03.load.unloadable_index_paths',load_fail)
rec('T03.load.entities_with_scoped_attributes',scoped_ents)
rec('T03.load.thin_index_has_attributes',sum(1 for e in idx['entities'] if 'attributes' in e))

# ---------- verify.py ----------
r=subprocess.run([sys.executable,'validation/verify.py','--claim','no_such_claim'],capture_output=True,text=True)
o=json.loads(r.stdout); rec('T03.verify.unknown_claim_on_real_index',{k:o[k] for k in ['entities_consulted','tests_gathered','tests_passed','prior_probability','posterior_probability']})
# fixture: hydrated entity with N identical scoped attributes, same claim fn
def fx(n,conf=0.9):
    return {'entities':[{'id':'FX','attributes':{f'a{i}':{'value':1,'scope':{'definition':'x','evidence':{'relational_confidence':conf}}} for i in range(n)}}]}
calls=[0]
def claim(): calls[0]+=1; return True
curve=[]
for n in [0,1,2,5,10,20]:
    calls[0]=0; o=verify.verify_claim(claim,ontology=fx(n),prior=0.5)
    curve.append({'n_attrs':n,'claim_calls':calls[0],'tests':o['tests_gathered'],'posterior':o['posterior_probability']})
rec('T03.verify.same_function_repeated_as_evidence',curve)
o=verify.verify_claim(lambda: True,ontology=fx(1),prior=0.5,claim_scope_text='')
rec('T03.verify.empty_scope_text_overlap',sc.scope_match('', 'anything'))
# hydrated real index
hyd={'entities':[json.load(open(ROOT/e['path'])) for e in idx['entities'] if (ROOT/e['path']).exists()]}
calls[0]=0; o=verify.verify_claim(claim,ontology=hyd,prior=0.5)
rec('T03.verify.hydrated_real_always_true',{'tests':o['tests_gathered'],'claim_calls':calls[0],'posterior':o['posterior_probability']})
o=verify.verify_claim(lambda: False,ontology=hyd,prior=0.5)
rec('T03.verify.hydrated_real_always_false',{'tests':o['tests_gathered'],'posterior':o['posterior_probability']})

# ---------- falsifier.py ----------
res=collections.Counter(); zero=[]; perfect=[]; nomatch_survived=0; total_ce=0; errs=collections.Counter()
for e in idx['entities']:
    try: o=falsifier.falsify(e['id'],ontology=idx)
    except Exception as ex: errs[type(ex).__name__]+=1; continue
    if 'error' in o: res['error:'+o['error'].split(' ')[0]]+=1; continue
    res['ran']+=1; total_ce+=o['counterexamples_generated']
    if o['counterexamples_generated']==0: zero.append(e['id'])
    if o['falsification_resistance']==1.0: perfect.append(e['id'])
    for d in o['details']:
        if not d['matches_in_db']: nomatch_survived+=1
rec('T03.falsifier.summary',{'outcomes':dict(res),'exceptions':dict(errs),'counterexamples_total':total_ce,'no_match_counted_as_survived':nomatch_survived,'zero_tests_entities':len(zero),'resistance_1.0':len(perfect)})
# fixture: scoped attr with no constraints/env/deps/falsifiability/limits
import tempfile
fxdir=Path(tempfile.mkdtemp()); (fxdir/'e.json').write_text(json.dumps({'id':'FZ','attributes':{'k':{'value':1,'scope':{}}}}))
o=falsifier.falsify('FZ',ontology={'entities':[{'id':'FZ','path':str(fxdir/'e.json')}]})
rec('T03.falsifier.zero_tests_fixture',{k:o.get(k) for k in ['counterexamples_generated','tests_survived','falsification_resistance']})
o=falsifier.falsify('FZ',ontology={'entities':[{'id':'FZ','path':'does/not/exist.json'}]})
rec('T03.falsifier.missing_file_silent_fallback',o)

# ---------- dependency_tree.py ----------
g=dt.build_dependency_graph(idx)
link_edges=sum(1 for s,v in g.items() for t,rt in v if rt!='dependency')
dep_edges=sum(1 for s,v in g.items() for t,rt in v if rt=='dependency')
idx_set=collections.Counter((r['source'],r['target'],r['relation']) for r in idx['relations'])
tr_set=collections.Counter((s,t,rt) for s,v in g.items() for t,rt in v if rt!='dependency')
rec('T03.dep.edges',{'index_relations':len(idx['relations']),'tracer_link_edges':link_edges,'tracer_scope_dependency_edges':dep_edges,'in_index_not_tracer':[list(k) for k in (idx_set-tr_set)],'in_tracer_not_index':[list(k) for k in list(tr_set-idx_set)[:10]]})
# unresolved scope deps silently dropped
dropped=[]; ids={e['id'] for e in idx['entities']}
for e in hyd['entities']:
    for an,av in e.get('attributes',{}).items():
        if sc.is_scoped(av):
            for d in av['scope'].get('dependencies',[]):
                if d not in ids and d not in dt.ROSETTA_STONE: dropped.append((e['id'],an,d))
rec('T03.dep.scope_dependencies_silently_dropped',{'count':len(dropped),'sample':dropped[:8]})
o=dt.dependency_tree('WOLF_PACK',ontology=idx,max_depth=1)
rec('T03.dep.WOLF_PACK_children',[(c['id'],c.get('relation'),c['type'] if 'type' in c else 'entity') for c in o['tree']['dependencies']])

# ---------- audit.py ----------
a=audit.audit(idx,repo_root=ROOT)
rec('T03.audit.summary',{'total':a['total_entities'],'unscoped_numerics':len(a['unscoped_numerics']),'noun_pretenders':len(a['noun_pretenders']),'contradictions':len(a['possible_contradictions']),'missing_deps':len(a['dependency_checks']),'scoped_ratio':a['scoped_ratio'],'confidence_distribution':dict(a['confidence_distribution'])})
# confidence fallback inconsistency: attr with computed confidence (no explicit relational_confidence)
av={'value':1,'scope':{'evidence':{}}}
rec('T03.conf.fallback_mismatch',{'scope_checker.extract_confidence':sc.extract_confidence(av),'audit_bucket_default':0.5})
# count real attributes where they differ
diff=0;tot=0
for e in hyd['entities']:
    for an,av in e.get('attributes',{}).items():
        if sc.is_scoped(av):
            tot+=1; ev=av['scope'].get('evidence',{})
            if 'relational_confidence' not in ev and 'relational_confidence' not in av['scope']: diff+=1
rec('T03.conf.real_scoped_attrs_without_explicit_confidence',{'scoped_attrs':tot,'audit_assigns_0.5_scope_checker_computes':diff})
# audit missing file fallback
a=audit.audit({'entities':[{'id':'GHOST','path':'nope.json'}]},repo_root=ROOT)
rec('T03.audit.missing_file_silent_fallback',{'total_entities':a['total_entities'],'scoped_ratio':a['scoped_ratio'],'any_warning_key':[k for k in a if 'load' in k or 'missing_file' in k]})
json.dump(R,open(os.environ.get('OUT','results.json'),'w'),indent=1)
