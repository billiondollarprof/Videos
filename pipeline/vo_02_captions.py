# ============================================================
# VO 02 CAPTIONS: his words (script.txt) with Whisper's timing on the CUT voice
# What : opening words timed by hand (vo_opening.json, optional, for where Whisper hears
#        laughter), then difflib matches script words to cut_words.json. Unmatched words
#        share the time of the Whisper words they replace.
# In   : script.txt, cut_words.json, vo_opening.json   Out: caps.json
# Never: never take the spelling from Whisper. Expect 90% matched or more.
# ============================================================
import json,re,difflib
S=open('script.txt').read().split()
W=json.load(open('cut_words.json'))
# opening by hand (first 8 s, checked by ear-level transcription)
op=json.load(open('vo_opening.json')) if __import__('os').path.exists('vo_opening.json') else []
k=len(op); W=[w for w in W if w['s']>=(op[-1][2]-0.05 if op else 0)]
n=lambda t:re.sub(r'[^a-z0-9]','',t.lower())
a=[n(x) for x in S[k:]]; b=[n(w['w']) for w in W]
out=[{'w':w,'s':s,'e':e} for w,s,e in op]; m=difflib.SequenceMatcher(None,a,b,autojunk=False)
tim=[None]*len(a)
for t,i1,i2,j1,j2 in m.get_opcodes():
    if t=='equal':
        for d in range(i2-i1): tim[i1+d]=(W[j1+d]['s'],W[j1+d]['e'])
    elif j2>j1:
        s0,e0=W[j1]['s'],W[j2-1]['e']; L=i2-i1
        for d in range(L): tim[i1+d]=(s0+(e0-s0)*d/L,s0+(e0-s0)*(d+1)/L)
print('matched',sum(t=='equal' and i2-i1 for t,i1,i2,_,_ in m.get_opcodes()),len(a))
for i,x in enumerate(S[k:]):
    if tim[i] is None:
        p=tim[i-1]; tim[i]=(p[1],p[1]+0.2)
    out.append({'w':x,'s':float(tim[i][0]),'e':float(tim[i][1])})
# words whose time jumps ahead of later words (Whisper missed them) are spread evenly in the gap
later=[0]*len(out); m=1e9
for i in range(len(out)-1,-1,-1): later[i]=m; m=min(m,out[i]['s'])
bad=[out[i]['s']>later[i]+0.3 for i in range(len(out))]
i=0
while i<len(out):
    if bad[i]:
        j=i
        while j<len(out) and bad[j]: j+=1
        t0=out[i-1]['e'] if i else 0.0; t1=out[j]['s'] if j<len(out) else t0+0.3*(j-i); step=(t1-t0)/(j-i)
        for k in range(i,j): out[k]['s']=t0+step*(k-i); out[k]['e']=t0+step*(k-i+1)
        i=j
    else: i+=1
json.dump(out,open('caps.json','w'))
print('words',len(out))
