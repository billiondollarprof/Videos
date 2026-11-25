# EDIT LIST for life video 1: approved cuts, tight pauses with real breaths, clip inserts.
# Writes work/edl.json: items in play order. "room" items are stretches of his video (raw seconds);
# "clip" items are reaction clips with their own sound (his voice waits). Also maps every kept
# word to its time in the finished video, for captions and pictures.
import json, subprocess, numpy as np
W=json.load(open('words_fillers.json'))['words']
raw=subprocess.run(['ffmpeg','-loglevel','error','-i','face48k_polish.wav','-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout
x=np.frombuffer(raw,np.float32); SR=16000; HOP=160                       # 10 ms
env=np.array([np.sqrt((x[i:i+HOP]**2).mean()+1e-12) for i in range(0,len(x)-HOP,HOP)])
db=20*np.log10(env)
def t2i(t): return int(round(t*100))
def quietest(t,span=0.05):
    a,b=t2i(t-span),t2i(t+span); k=a+int(np.argmin(db[a:b])); return k/100
# --- 1. Approved content cuts (his yes, 2026-11-25), cut at the quietest 10 ms near each edge ---
CUTS=[(quietest(48.46),quietest(49.84,0.04)),       # "a better day," -> "You are living a better life today"
      (quietest(87.00),quietest(87.68)),            # first "you should be"
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
# Real pauses from the sound (quieter than -50 dB for 0.2 s or more). Whisper stretches words over the
# silence after them, so its gaps miss most pauses. A pause is only shortened when no word's middle
# falls inside it (soft words like "and" stay whole).
SIL=-50
q=db<SIL; i=0; mids=np.array([(w_['s']+w_['e'])/2 for w_ in W])
while i<len(q):
    if not q[i]: i+=1; continue
    j=i
    while j<len(q) and q[j]: j+=1
    s_,e_=i/100,j/100; i=j
    if e_-s_<0.2 or ((mids>s_+0.03)&(mids<e_-0.03)).any(): continue
    k=max([n for n,w_ in enumerate(W) if (w_['s']+w_['e'])/2<s_] or [0]); p=W[k]['w'][-1]
    tg=0.26 if p in '.?!' else 0.18 if p in ',;:' else 0.14
    if e_-s_>tg+0.04:
        tail=tg*0.55; lead=tg-tail
        cuts2.append((s_+tail,e_-lead))
for c in cuts2: keep=subtract(keep,c)
keep=[(round(s,3),round(e,3)) for s,e in keep if e-s>0.02]
# --- 4. Reaction clips with their own sound, after the sentence they answer (approved plan) ---
INSERT_AFTER={70.24:('clips/pawpaw_skit.mp4',0.25,2.95),          # after "...to evaluate your life."
              120.16:('clips/aki_pawpaw_best_of.mp4',1.18,2.50)} # after "...make some sales"
items=[]
for s,e in keep:
    items.append({'type':'room','s':s,'e':e})
    for t,(f,cs,ce) in INSERT_AFTER.items():
        if s<t<=e+0.3 and not any(it.get('at')==t for it in items):
            # split the room item at the end of the sentence + a short breath
            cut=min(e,t+0.12)
            items[-1]['e']=round(cut,3)
            items.append({'type':'clip','file':f,'s':cs,'e':ce,'at':t})
            if cut<e: items.append({'type':'room','s':round(cut,3),'e':e})
# --- 5. Timeline: when each kept word is heard in the finished video ---
tl=0; words=[]
for it in items:
    it['t0']=round(tl,3)
    if it['type']=='room':
        for k,w_ in enumerate(W):
            mid=(w_['s']+w_['e'])/2
            if it['s']<=mid<it['e']:
                words.append({'i':k,'w':w_['w'],'s':round(tl+max(w_['s'],it['s'])-it['s'],3),'e':round(tl+min(w_['e'],it['e'])-it['s'],3)})
    tl+=it['e']-it['s']
    it['t1']=round(tl,3)
json.dump({'items':items,'words':words,'length':round(tl,3)},open('work/edl.json','w'),indent=1)
print('items',len(items),'pauses shortened',len(cuts2),'length',round(tl,2),'s (raw 137.6)')
print(' '.join(w['w'] for w in words))
