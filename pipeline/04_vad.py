# Finds where the voice is, from loudness, every 10 ms.
import numpy as np, wave, json
from scipy.signal import butter, filtfilt
w=wave.open("face16k.wav"); sr=16000
x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
b,a=butter(4,[150/(sr/2),4000/(sr/2)],'band'); x=filtfilt(b,a,x)
hop=160; n=len(x)//hop
db=20*np.log10(np.sqrt((x[:n*hop].reshape(n,hop)**2).mean(1))+1e-9)
floor=np.percentile(db,15); peak=np.percentile(db,95)
thr=floor+0.35*(peak-floor)
sp=db>thr
# close tiny holes (<150 ms) and drop tiny blips (<80 ms)
def runs(m):
    r=[];i=0
    while i<len(m):
        j=i
        while j<len(m) and m[j]==m[i]: j+=1
        r.append((m[i],i,j)); i=j
    return r
for v,i,j in runs(sp):
    if not v and j-i<15: sp[i:j]=True
for v,i,j in runs(sp):
    if v and j-i<8: sp[i:j]=False
regs=[(i/100,j/100) for v,i,j in runs(sp) if v]
json.dump({"regions":regs,"db":db.round(1).tolist(),"thr":float(thr)},open("vad.json","w"))
print("floor %.1f peak %.1f thr %.1f regions %d speech %.1fs"%(floor,peak,thr,len(regs),sum(b-a for a,b in regs)))
