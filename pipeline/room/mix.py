# MIX: his cut voice (with the clips' own sound in their slots), a faint room bed under the tail,
# the sound effects on their cues; loudness -14 LUFS, peaks at or under -1.5 dB, measured after.
import json, subprocess, numpy as np
SR=48000
def load(p):
    return np.frombuffer(subprocess.run(['ffmpeg','-loglevel','error','-i',p,'-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout,np.float32).copy()
C=json.load(open('work/cues.json')); L=int(C['length']*SR)
v=load('work/voice_cut.wav'); y=np.zeros(L,np.float32); y[:min(L,len(v))]=v[:L]
# the tail after his last word: a faint bed of his own room, never dead silence
bed=load('face48k_polish.wav')[int(30.6*SR):int(30.6*SR)+int(0.4*SR)]
n=len(v); 
while n<L:
    k=min(len(bed),L-n); y[n:n+k]+=bed[:k]*0.6; n+=k
vrms=np.sqrt((v[np.abs(v)>1e-3]**2).mean())
GAIN={'pop-soft-low':0.30,'camera-shutter':0.55,'pop-soft':0.8,'pop-low':0.6,'whoosh-air-short':0.35}   # share of his voice level
shutters=[c['t'] for c in C['cues'] if c['s']=='camera-shutter']
for c in C['cues']:
    # a whoosh right next to a shutter doubles the click (the encoder overshot to +2.6 dB): the shutter wins
    if c['s']!='camera-shutter' and any(abs(c['t']-t)<0.2 for t in shutters): continue
    s=load(f"/home/user/Videos/sfx/{c['s'].replace('-low-x','')}.wav") if c['s']!='pop-soft-low' else load('/home/user/Videos/sfx/pop-soft.wav'); srms=np.sqrt((s[np.abs(s)>1e-3]**2).mean())
    s=s*(vrms/srms)*GAIN[c['s']]
    f=int(0.006*SR); s[:f]*=np.linspace(0,1,f)          # a 6 ms soft start: the encoder overshot on the raw click
    i=int(c['t']*SR); k=min(len(s),L-i)
    if k>0: y[i:i+k]+=s[:k]
subprocess.run(['ffmpeg','-loglevel','error','-y','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-c:a','pcm_f32le','work/mix_raw.wav'],input=y.tobytes())
# loudness: a plain gain to -14 LUFS, then a peak limiter (the loudnorm filter held back to protect
# peaks and landed at -16.4). Measured on the result, and corrected once more if needed.
def lufs(path):
    o=subprocess.run(['ffmpeg','-hide_banner','-i',path,'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True).stderr
    import re
    return float(re.findall(r'I:\s+(-?[0-9.]+) LUFS',o)[-1]), float(re.findall(r'Peak:\s+(-?[0-9.]+) dBFS',o)[-1])
g=0.0
for _ in range(5):
    I,_p=lufs('work/mix_raw.wav') if g==0 else lufs('work/mix.wav')
    g+= -14.0-I
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i','work/mix_raw.wav','-af',f'volume={g:.2f}dB,alimiter=limit=0.69:attack=3:release=60:level=false','-ar',str(SR),'-c:a','pcm_f32le','work/mix.wav'])
    I2,P2=lufs('work/mix.wav'); print('gain',round(g,2),'-> I',I2,'peak',P2)
    if abs(I2+14)<0.3: break
print('mixed',round(L/SR,2),'s')
