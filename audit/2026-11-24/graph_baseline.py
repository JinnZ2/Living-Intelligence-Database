import json, sys, collections, hashlib, subprocess
def load(p):
    d=json.load(open(p)); return d
def measure(p):
    d=load(p); ents=d['entities']; rels=d['relations']
    ids=[e['id'] for e in ents]; S=set(ids)
    out={'file':p,'entities':len(ents),'unique_ids':len(S),'relations':len(rels)}
    unres=[(r['source'],r['target'],r['relation']) for r in rels if r['source'] not in S or r['target'] not in S]
    out['unresolved']=unres
    out['relation_types']=dict(collections.Counter(r['relation'] for r in rels))
    out['ontology_categories']=dict(collections.Counter(e.get('ontology') for e in ents))
    good=[r for r in rels if r['source'] in S and r['target'] in S]
    und=collections.defaultdict(set); dg=collections.defaultdict(set)
    for r in good:
        und[r['source']].add(r['target']); und[r['target']].add(r['source']); dg[r['source']].add(r['target'])
    out['isolated']=[i for i in S if not und[i]]
    seen=set(); comps=[]
    for i in S:
        if i in seen: continue
        st=[i]; c=set([i])
        while st:
            x=st.pop()
            for y in und[x]:
                if y not in c: c.add(y); st.append(y)
        seen|=c; comps.append(len(c))
    out['weak_components']=sorted(comps,reverse=True)
    def reach(adj):
        tot=0
        for i in S:
            st=[i]; v={i}
            while st:
                x=st.pop()
                for y in adj[x]:
                    if y not in v: v.add(y); st.append(y)
            tot+=len(v)-1
        return tot
    n=len(S); pairs=n*(n-1)
    out['ordered_pairs']=pairs; out['directed_reachable']=reach(dg); out['directed_pct']=round(100*reach(dg)/pairs,1)
    edges=set((r['source'],r['target']) for r in good)
    out['reciprocated_records']=sum(1 for (a,b) in edges if (b,a) in edges)
    def sym(types):
        adj=collections.defaultdict(set)
        for r in good:
            adj[r['source']].add(r['target'])
            if r['relation'] in types: adj[r['target']].add(r['source'])
        return round(100*reach(adj)/pairs,1)
    out['geom_recip_pct']=sym({'geometry_link'}); out['geom_syn_res_pct']=sym({'geometry_link','synergy','resonance'})
    # SCC via Tarjan iterative-ish (small n, recursion ok)
    sys.setrecursionlimit(10000); idx={}; low={}; stk=[]; on=set(); sccs=[]; c=[0]
    def sc(v):
        idx[v]=low[v]=c[0]; c[0]+=1; stk.append(v); on.add(v)
        for w in dg[v]:
            if w not in idx: sc(w); low[v]=min(low[v],low[w])
            elif w in on: low[v]=min(low[v],idx[w])
        if low[v]==idx[v]:
            comp=[]
            while True:
                w=stk.pop(); on.discard(w); comp.append(w)
                if w==v: break
            sccs.append(comp)
    for v in sorted(S):
        if v not in idx: sc(v)
    out['scc_count']=len(sccs); out['largest_scc']=max(map(len,sccs))
    return out, S, d
if __name__=='__main__':
    for p in sys.argv[1:]:
        o,S,d=measure(p)
        o['blob']=subprocess.run(['git','hash-object',p],capture_output=True,text=True).stdout.strip()
        print(json.dumps(o,indent=1))
