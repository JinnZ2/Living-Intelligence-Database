import json, random, collections, statistics, sys
idx=json.load(open(sys.argv[1])); S=sorted(e['id'] for e in idx['entities']); n=len(S); P=n*(n-1)
G=[(r['source'],r['target'],r['relation']) for r in idx['relations'] if r['source'] in set(S) and r['target'] in set(S)]
def reach(edges, recip=lambda e:False, undirected=False):
    adj=collections.defaultdict(set)
    for e in edges:
        adj[e[0]].add(e[1])
        if undirected or recip(e): adj[e[1]].add(e[0])
    tot=0
    for s in S:
        v={s}; st=[s]
        while st:
            x=st.pop()
            for y in adj[x]:
                if y not in v: v.add(y); st.append(y)
        tot+=len(v)-1
    return tot/P
def wcc(edges):
    p={s:s for s in S}
    def f(x):
        while p[x]!=x: p[x]=p[p[x]]; x=p[x]
        return x
    for a,b,_ in edges: p[f(a)]=f(b)
    c=collections.Counter(f(s) for s in S); return len(c), max(c.values())
types=sorted(set(t for *_,t in G)); cnt=collections.Counter(t for *_,t in G)
out={'baseline_directed':round(100*reach(G),1),'ablation':{}}
for t in types:
    H=[e for e in G if e[2]!=t]
    out['ablation'][t]={'edges_removed':cnt[t],'directed_pct':round(100*reach(H),1),'undirected_pct':round(100*reach(H,undirected=True),1),'weak_components':wcc(H)[0],'largest_wcc':wcc(H)[1]}
# T06.4 reciprocity control: reciprocate k random existing edges (k=78 = geometry count)
rng=random.Random(20261124); k=cnt['geometry_link']; obs=reach(G,lambda e:e[2]=='geometry_link')
null=[]
for _ in range(500):
    pick=set(rng.sample(range(len(G)),k)); null.append(reach(G,lambda e,_p=pick,_G=G: _G.index(e) in _p) if False else None)
# faster: index-based
null=[]
for _ in range(500):
    pick=set(map(tuple,rng.sample(G,k)))
    null.append(reach(G,lambda e,_p=pick: e in _p))
null.sort()
out['T06.4_reciprocity_control']={'k':k,'trials':500,'seed':20261124,'observed_geometry_pct':round(100*obs,1),
 'null_mean_pct':round(100*statistics.mean(null),1),'null_sd_pct':round(100*statistics.pstdev(null),2),
 'null_p2.5':round(100*null[12],1),'null_p97.5':round(100*null[487],1),'null_max':round(100*null[-1],1),
 'empirical_p_ge_observed':(sum(1 for x in null if x>=obs)+1)/(len(null)+1)}
# same control for every type with equal count
per={}
for t in types:
    o=reach(G,lambda e,_t=t:e[2]==_t); kk=cnt[t]; nl=[]
    for _ in range(200):
        pick=set(map(tuple,rng.sample(G,kk))); nl.append(reach(G,lambda e,_p=pick:e in _p))
    per[t]={'k':kk,'observed':round(100*o,1),'null_mean':round(100*statistics.mean(nl),1),'null_max':round(100*max(nl),1),'p':(sum(1 for x in nl if x>=o)+1)/201}
out['reciprocate_one_type_vs_random_same_k']=per
# T06.2 degree-preserving directed rewiring (edge swaps), then reciprocate geometry-labelled edges
def rewire(edges,swaps,rng):
    E=[list(e) for e in edges]; es=set((a,b) for a,b,_ in E)
    for _ in range(swaps):
        i,j=rng.randrange(len(E)),rng.randrange(len(E))
        a,b,_=E[i]; c,d,_=E[j]
        if len({a,b,c,d})<4 or (a,d) in es or (c,b) in es: continue
        es-={(a,b),(c,d)}; es|={(a,d),(c,b)}; E[i][1]=d; E[j][1]=b
    return [tuple(e) for e in E]
dp=[];dd=[]
for _ in range(100):
    H=rewire(G,10*len(G),rng); dd.append(reach(H)); dp.append(reach(H,lambda e:e[2]=='geometry_link'))
out['T06.2_degree_preserving']={'trials':100,'directed_null_mean':round(100*statistics.mean(dd),1),'directed_null_range':[round(100*min(dd),1),round(100*max(dd),1)],
 'geometry_recip_null_mean':round(100*statistics.mean(dp),1),'geometry_recip_null_range':[round(100*min(dp),1),round(100*max(dp),1)],'observed_directed':out['baseline_directed'],'observed_geometry_recip':round(100*obs,1)}
# geometry endpoint structure: how many entities touched, cross-ontology share
ont={e['id']:e['ontology'] for e in idx['entities']}
def stats(es):
    nodes=set(); cross=0
    for a,b,_ in es: nodes|={a,b}; cross+= ont[a]!=ont[b]
    return {'edges':len(es),'entities_touched':len(nodes),'cross_ontology_frac':round(cross/len(es),2)}
out['edge_structure']={t:stats([e for e in G if e[2]==t]) for t in types}
out['geometry_targets']=collections.Counter(b for a,b,t in G if t=='geometry_link').most_common(8)
print(json.dumps(out,indent=1))
