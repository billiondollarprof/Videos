# ============================================================
# EDIT DECISION LIST (the list of what stays, and in what order)
# Input : aligned_words.json, vad.json, project.json (the approved cuts)
# Output: edl.json, a list of pieces of the face timeline to keep.
# Each piece is either "talk" (normal speed) or "fast" (screen sped up, muted).
# ============================================================
import json,re
W=json.load(open("aligned_words.json")); V=json.load(open("vad.json"))["regions"]
# --- 1. Word ranges to CUT, from project.json (approved by Anthony) ---
P=json.load(open("project.json"))
SCREEN_START=P["screen_offset"] or 0
CUT_WORDS=[(c[0],c[1]) for c in P["cuts"]]
cut=set()
for a,b in CUT_WORDS: cut.update(range(a,b+1))
# --- 2. Kept word runs -> time ranges ---
runs=[];cur=None
for i,w in enumerate(W):
    if i in cut:
        if cur: runs.append(cur); cur=None
    else:
        cur=[w["s"],w["e"]] if cur is None else [cur[0],w["e"]]
if cur: runs.append(cur)
# --- 3. Inside each kept run, keep only where the voice is (with a little air) ---
PAD=0.10
pieces=[]
for a,b in runs:
    for s,e in V:
        s2,e2=max(a-0.15,s-PAD),min(b+0.15,e+PAD)
        if e2-s2>0.12: pieces.append([s2,e2])
pieces.sort()
# merge pieces closer than 0.25 s
m=[]
for p in pieces:
    if m and p[0]-m[-1][1]<0.25: m[-1][1]=max(m[-1][1],p[1])
    else: m.append(p)
# --- 4. Long silent stretches inside kept talk, while the screen is showing: fast-forward ---
edl=[]
for k,p in enumerate(m):
    edl.append({"type":"talk","a":round(p[0],3),"b":round(p[1],3)})
    if k+1<len(m):
        gap_a,gap_b=p[1],m[k+1][0]
        same_run=any(a-0.2<=gap_a and gap_b<=b+0.2 for a,b in runs)
        if same_run and gap_a>SCREEN_START and gap_b-gap_a>=1.5:
            edl.append({"type":"fast","a":round(gap_a,3),"b":round(gap_b,3),"speed":4})
tot=sum((e["b"]-e["a"])/(e.get("speed",1)) for e in edl)
json.dump(edl,open("edl.json","w"),indent=0)
print("pieces",len(edl),"fast",sum(e["type"]=="fast" for e in edl),"length %.1fs = %d:%02d"%(tot,tot//60,tot%60))
kept=" ".join(w["w"] for i,w in enumerate(W) if i not in cut)
open("kept_text.txt","w").write(kept); print(len(kept.split()),"words kept")
