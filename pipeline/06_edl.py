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
# --- 1b. Fillers cut by time (seconds of the face video), from 05b_find_fillers.py ---
CUT_TIMES=[tuple(c[:2]) for c in P.get("cut_times",[])]
cut=set()
for a,b in CUT_WORDS: cut.update(range(a,b+1))
for i,w in enumerate(W):     # a transcript word inside a cut time is cut too, so captions match
    mid=(w["s"]+w["e"])/2
    if any(a<=mid<=b for a,b in CUT_TIMES): cut.add(i)
# --- 2. Kept word runs -> time ranges ---
runs=[];cur=None
for i,w in enumerate(W):
    if i in cut:
        if cur: runs.append(cur); cur=None
    else:
        cur=[w["s"],w["e"]] if cur is None else [cur[0],w["e"]]
if cur: runs.append(cur)
# --- 3. Inside each kept run, keep only where the voice is (with a little air) ---
PAD_START=0.03   # a hair of air before a phrase (the pause rule below adds the real pauses)
PAD_END=0.06     # and a little more after it, so soft word endings are not clipped
def minus(regs, cuts):
    """Voice regions with the cut times taken out."""
    out=[]
    for s0,e0 in regs:
        segs=[(s0,e0)]
        for a,b in cuts:
            nxt=[]
            for x,y in segs:
                if b<=x or a>=y: nxt.append((x,y))
                else:
                    if a>x: nxt.append((x,a))
                    if b<y: nxt.append((b,y))
            segs=nxt
        out+=segs
    return out
V=minus(V,CUT_TIMES)
pieces=[]
for a,b in runs:
    for s,e in V:
        s2,e2=max(a-0.15,s-PAD_START),min(b+0.15,e+PAD_END)
        if e2-s2>0.12: pieces.append([s2,e2])
pieces.sort()
# merge pieces closer than 0.06 s
m=[]
for p in pieces:
    if m and p[0]-m[-1][1]<0.06: m[-1][1]=max(m[-1][1],p[1])
    else: m.append(p)

# --- 3b. Pauses: keep a natural breath at every joint (learned from Anthony's own cut of
# video 1, 2026-11-05: "I think it's not good for us not to have small pauses... it gives room
# for breathing"; version 3 had none and felt rushed). His cut: pauses of about 0.15 s between
# phrases, 0.3 to 0.5 s between sentences, and longer ones (0.5 to 2 s) only where the screen
# is doing something worth watching (typing, Claude starting to work). Waits are shortened
# but left at normal speed. The pause is REAL room tone taken from beside the phrase (the
# face keeps its natural still moment), never an inserted blank.
PAUSE=dict(scale=0.05,        # keep this share of each natural pause...
           within=0.06,       # ...but never more than this inside a sentence
           between=0.18,      # ...or this between sentences
           typing=0.30,       # ...or this when the screen is busy (typing, Claude writing)
           long_wait=0.8,     # a very long wait (Claude working): keep this much, normal speed
           long_wait_from=5.0,# a silence at least this long counts as a long wait
           active_level=0.5)  # how much the screen must change to count as busy
# Calibrated on Anthony's own cut of video 1: a tight cut with about 10 s of extra pauses in
# 3 minutes. Most joints tight; a few breaths; the longer ones where he was typing or waiting.
# Is the screen changing? (typing, Claude writing.) Measured on a small 4 frames-a-second copy.
import subprocess, numpy as np
_scr=globals().get("P",{}).get("screen_video","raw/screen.mp4")
_raw=subprocess.run(["ffmpeg","-v","error","-i",_scr,"-vf","fps=4,scale=108:240,format=gray","-f","rawvideo","-"],
                    capture_output=True).stdout
_fr=np.frombuffer(_raw,dtype=np.uint8).reshape(-1,240,108).astype(np.float32)
_act=np.abs(np.diff(_fr,axis=0)).mean(axis=(1,2))             # change between neighbouring frames
_rate=globals().get("P",{}).get("screen_rate") or 1.000424
def screen_activity(t0,t1):
    """Average change on the screen between two face-video times."""
    a=int(max(0,(t0-SCREEN_START)/_rate)*4); b=max(a+1,int(max(0,(t1-SCREEN_START)/_rate)*4))
    return float(_act[a:b].mean()) if a<len(_act) else 0.0
Vall=json.load(open("vad.json"))["regions"]        # all voice, including the parts cut out
kept_words=[w for i,w in enumerate(W) if i not in cut]
def free_after(t):                                 # silence after t, up to the next voice (kept or cut)
    nxt=[s for s,e in Vall if s>t-0.001]
    return (min(nxt)-t) if nxt else 5.0
def free_before(t):
    prv=[e for s,e in Vall if e<t+0.001]
    return (t-max(prv)) if prv else 5.0
def ends_sentence(t):
    last=[w for w in kept_words if w["e"]<=t+0.3]
    return bool(last) and last[-1]["w"].rstrip()[-1:] in ".?!"
def joint_cap(t_end, t_start):
    """How long a pause to keep at this joint, in seconds."""
    screen=t_end>SCREEN_START
    nat=free_after(t_end)+free_before(t_start)            # the silence that was really there
    busy=screen and nat>=0.8 and screen_activity(t_end, t_end+nat)>=PAUSE["active_level"]
    if busy and nat>=PAUSE["long_wait_from"]: return PAUSE["long_wait"]
    cap=PAUSE["typing"] if busy else (PAUSE["between"] if ends_sentence(t_end) else PAUSE["within"])
    return min(cap, max(0.0, nat*PAUSE["scale"]*(2.5 if busy else 1.0)))
for k in range(len(m)-1):
    cap=joint_cap(m[k][1], m[k+1][0])
    e_ext=max(0.0,min(cap*0.6, free_after(m[k][1])-0.02))
    s_ext=max(0.0,min(cap*0.4, free_before(m[k+1][0])-0.02))
    m[k][1]+=e_ext; m[k+1][0]-=s_ext
m2=[]
for p in m:                                        # pieces that now touch or overlap join up
    if m2 and p[0]-m2[-1][1]<0.03: m2[-1][1]=max(m2[-1][1],p[1])
    else: m2.append(p)
m=m2
# --- 4. Long silent stretches inside kept talk, while the screen is showing: fast-forward ---
edl=[]
for k,p in enumerate(m):
    edl.append({"type":"talk","a":round(p[0],3),"b":round(p[1],3)})
    if k+1<len(m):
        gap_a,gap_b=p[1],m[k+1][0]
        same_run=any(a-0.2<=gap_a and gap_b<=b+0.2 for a,b in runs)
        if P.get("fast_forward", False) and same_run and gap_a>SCREEN_START and gap_b-gap_a>=1.5:   # off by default: no silences (his note)
            edl.append({"type":"fast","a":round(gap_a,3),"b":round(gap_b,3),"speed":4})
tot=sum((e["b"]-e["a"])/(e.get("speed",1)) for e in edl)
json.dump(edl,open("edl.json","w"),indent=0)
print("pieces",len(edl),"fast",sum(e["type"]=="fast" for e in edl),"length %.1fs = %d:%02d"%(tot,tot//60,tot%60))
kept=" ".join(w["w"] for i,w in enumerate(W) if i not in cut)
open("kept_text.txt","w").write(kept); print(len(kept.split()),"words kept")
