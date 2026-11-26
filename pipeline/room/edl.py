# EDIT LIST for life video 1: approved cuts, tight pauses with real breaths, clip inserts.
# Writes work/edl.json: items in play order. "room" items are stretches of his video (raw seconds);
# "clip" items are reaction clips with their own sound (his voice waits). Also maps every kept
# word to its time in the finished video, for captions and pictures.
import json, subprocess, numpy as np
SPEED=1.3      # kept for older readers
# v4 (his note on v3): 1.3 for the opening, 1.1 from "even in times of distress" (raw 37.7 s, the pause
# after "...worth living,") to the end. Clips keep their own speed.
SPLIT=37.7
def speed_at(t): return 1.3 if t < SPLIT else 1.1
W=json.load(open('words_fillers.json'))['words']
raw=subprocess.run(['ffmpeg','-loglevel','error','-i','face48k_polish.wav','-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout
x=np.frombuffer(raw,np.float32); SR=16000; HOP=160                       # 10 ms
env=np.array([np.sqrt((x[i:i+HOP]**2).mean()+1e-12) for i in range(0,len(x)-HOP,HOP)])
db=20*np.log10(env)
def t2i(t): return int(round(t*100))
def quietest(t,span=0.05):
    a,b=t2i(t-span),t2i(t+span); k=a+int(np.argmin(db[a:b])); return k/100
# --- 1. Approved content cuts (his yes, 2026-11-25), cut at the quietest 10 ms near each edge ---
# v3: the splice sits between two matching sounds, so the join is seamless (v2 joins "flopped")
CUTS=[(48.94,50.24),                                # "living a better [day, a better] life today": both edges right after "better"
      (87.20,87.78),                                # "you [should be you] should be thankful": both edges right before "should"
      (quietest(121.70),quietest(122.34))]          # one "little": "so the little things that matter"
print('content cuts',CUTS)
# --- 2. Keep from the first word to 0.5 s after the last ---
keep=[(max(W[0]['s']-0.05,0),W[-1]['e']+0.5)]
def subtract(segs,c):
    out=[]
    for s,e in segs:
        if c[1]<=s or c[0]>=e: out.append((s,e)); continue
        if c[0]>s: out.append((s,c[0]))
        if c[1]<e: out.append((c[1],e))
    return out
for c in CUTS: keep=subtract(keep,c)
# --- 3. Pauses: every silence longer than its target is shortened, keeping a real breath ---
SIL=-48
end_punct={w_['e']:w_['w'][-1] for w_ in W}
def target(t_before):
    # the word that ends just before this silence decides the pause
    k=min(end_punct,key=lambda e:abs(e-t_before)); p=end_punct[k]
    if abs(k-t_before)>0.4: return 0.14
    return 0.26 if p in '.?!' else 0.18 if p in ',;:' else 0.12
cuts2=[]
# Pauses (his note on version 1: about 0.3 s at most). Quiet = under -42 dB, which also counts his
# breaths (the -50 dB test left 0.66 and 0.8 s gaps that were breaths). Never where a word's middle is.
SIL=-42; MAXP=0.33*SPEED/1.1
q=db<SIL; i=0; mids=np.array([(w_['s']+w_['e'])/2 for w_ in W])
while i<len(q):
    if not q[i]: i+=1; continue
    j=i
    while j<len(q) and q[j]: j+=1
    s_,e_=i/100,j/100; i=j
    if e_-s_<0.2 or ((mids>s_+0.03)&(mids<e_-0.03)).any(): continue
    k=max([n for n,w_ in enumerate(W) if (w_['s']+w_['e'])/2<s_] or [0]); p=W[k]['w'][-1]
    tg=min(MAXP, 0.30 if p in '.?!' else 0.22 if p in ',;:' else 0.16)
    if e_-s_>tg+0.03:
        tail=tg*0.55; lead=tg-tail
        cuts2.append((s_+tail,e_-lead))
for c in cuts2: keep=subtract(keep,c)
keep=[(round(s,3),round(e,3)) for s,e in keep if e-s>0.02]
keep=[p for s_,e_ in keep for p in ([(s_,SPLIT),(SPLIT,e_)] if s_<SPLIT<e_ else [(s_,e_)])]
# --- 4. Reaction clips with their own sound, after the sentence they answer (approved plan) ---
INSERT_AFTER={  # Pawpaw removed (his note on v2: it came at the wrong moment)
              120.16:('clips/aki_pawpaw_best_of.mp4',1.18,2.50)} # after "...make some sales"
items=[]
for s,e in keep:
    items.append({'type':'room','s':s,'e':e,'speed':speed_at((s+e)/2)})
    for t,(f,cs,ce) in INSERT_AFTER.items():
        if s<t<=e+0.3 and not any(it.get('at')==t for it in items):
            # split the room item at the end of the sentence + a short breath
            cut=min(e,t+0.12)
            items[-1]['e']=round(cut,3)
            items.append({'type':'clip','file':f,'s':cs,'e':ce,'at':t})
            if cut<e: items.append({'type':'room','s':round(cut,3),'e':e,'speed':speed_at((cut+e)/2)})
# --- 5. Timeline: when each kept word is heard in the finished video ---
tl=0; words=[]
for it in items:
    it['t0']=round(tl,3)
    if it['type']=='room':
        for k,w_ in enumerate(W):
            mid=(w_['s']+w_['e'])/2
            if it['s']<=mid<it['e']:
                words.append({'i':k,'w':w_['w'],'s':round(tl+(max(w_['s'],it['s'])-it['s'])/it['speed'],3),'e':round(tl+(min(w_['e'],it['e'])-it['s'])/it['speed'],3)})
    tl+=(it['e']-it['s'])/(it['speed'] if it['type']=='room' else 1.0)
    it['t1']=round(tl,3)
json.dump({'items':items,'words':words,'length':round(tl,3),'speed':SPEED},open('work/edl.json','w'),indent=1)
print('items',len(items),'pauses shortened',len(cuts2),'length',round(tl,2),'s (raw 137.6)')
print(' '.join(w['w'] for w in words))
