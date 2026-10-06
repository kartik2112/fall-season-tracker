#!/usr/bin/env python3
"""Rebuild roads.json: motorways, trunk and primary roads for the six New England states.

Downloads the ways from OpenStreetMap via an Overpass mirror (~70 MB), joins them into long lines,
simplifies them (Douglas-Peucker, ~30 m) and writes delta-encoded integer coordinates:
  {"motorway": [[lat0*1e4, lon0*1e4, dlat, dlon, ...], ...], "trunk": [...], "primary": [...]}

Usage:  python3 tools/build_roads.py            (run from the repo root; takes a few minutes)
"""
import json, math, collections, sys, urllib.request, urllib.parse

QUERY = """[out:json][timeout:240];
area["ISO3166-2"~"^US-(ME|NH|VT|MA|CT|RI)$"]->.a;
way["highway"~"^(motorway|trunk|primary)$"](area.a);
out tags geom;"""
MIRRORS = ["https://overpass-api.de/api/interpreter", "https://overpass.private.coffee/api/interpreter",
           "https://maps.mail.ru/osm/tools/overpass/api/interpreter"]   # the first two often time out on this query
TOL = 0.0003   # degrees

def download():
    for url in MIRRORS:
        try:
            req = urllib.request.Request(url, data=urllib.parse.urlencode({"data": QUERY}).encode(),
                                         headers={"User-Agent": "fall-season-tracker/1.0"})   # Overpass rejects requests with no UA
            return json.load(urllib.request.urlopen(req, timeout=300))["elements"]
        except Exception as e:
            print("failed:", url, e, file=sys.stderr)
    sys.exit("no Overpass mirror answered")

d = download()
K=math.cos(math.radians(44))
def dp(pts,tol):
    if len(pts)<3: return pts
    keep=[False]*len(pts); keep[0]=keep[-1]=True; st=[(0,len(pts)-1)]
    while st:
        a,b=st.pop()
        (y1,x1),(y2,x2)=pts[a],pts[b]; dx=(x2-x1)*K; dy=y2-y1; L=math.hypot(dx,dy); m=0; mi=-1
        for i in range(a+1,b):
            px=(pts[i][1]-x1)*K; py=pts[i][0]-y1
            dist=abs(px*dy-py*dx)/L if L else math.hypot(px,py)
            if dist>m: m=dist; mi=i
        if m>tol: keep[mi]=True; st+= [(a,mi),(mi,b)]
    return [p for p,k in zip(pts,keep) if k]
out={}
for cls in ('motorway','trunk','primary'):
    ways=[[(g['lat'],g['lon']) for g in w['geometry']] for w in d if w['tags']['highway']==cls]
    ends=collections.defaultdict(list)
    for i,w in enumerate(ways): ends[w[0]].append(i); ends[w[-1]].append(i)
    used=[False]*len(ways); lines=[]
    def grow(line):
        while True:
            nxt=[j for j in ends[line[-1]] if not used[j]]
            if not nxt: return line
            j=nxt[0]; used[j]=True; w=ways[j]
            line += (w[1:] if w[0]==line[-1] else w[-2::-1])
    for i,w in enumerate(ways):
        if used[i]: continue
        used[i]=True; line=grow(list(w)); line=grow(line[::-1]); lines.append(line)
    enc=[]; n=0
    for l in lines:
        s=dp(l,TOL); q=[(round(a*1e4),round(b*1e4)) for a,b in s]
        q=[p for i,p in enumerate(q) if i==0 or p!=q[i-1]]
        if len(q)<2: continue
        flat=[q[0][0],q[0][1]]
        for (a,b),(c,e) in zip(q,q[1:]): flat+=[c-a,e-b]
        enc.append(flat); n+=len(q)
    out[cls]=enc; print(cls,len(ways),'ways ->',len(enc),'lines',n,'pts',file=sys.stderr)
json.dump(out,open('roads.json', 'w'),separators=(',',':'))
