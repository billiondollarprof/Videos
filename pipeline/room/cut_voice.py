# Cut his cleaned voice to the edit list, in one pass, with short fades at every joint; reaction
# clips' own sound goes in their slots, levelled a little under his voice.
import json, subprocess, numpy as np
SR=48000
E=json.load(open('work/edl.json'))
def load(path,ss=None,to=None):
    cmd=['ffmpeg','-loglevel','error']+(['-ss',str(ss),'-to',str(to)] if ss is not None else [])+['-i',path,'-ac','1','-ar',str(SR),'-f','f32le','-']
    return np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,np.float32).copy()
voice=load('face48k_polish.wav')
def rms_db(a): return 20*np.log10(np.sqrt((a[np.abs(a)>1e-4]**2).mean())+1e-9)
v_db=rms_db(voice)
SPEED=E.get('speed',1.0)
def tempo(a,sp):
    # speed his voice up, pitch kept (ffmpeg atempo), in one piece per stretch of one speed
    if sp==1.0: return a
    r=subprocess.run(['ffmpeg','-loglevel','error','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-af',f'atempo={sp}','-f','f32le','-'],input=a.astype(np.float32).tobytes(),capture_output=True).stdout
    return np.frombuffer(r,np.float32).copy()
out=[]; run=[]; run_sp=[None]
XF=0.025
def join(pieces):
    n=int(XF*SR); t=np.linspace(0,np.pi/2,n); fo,fi=np.cos(t),np.sin(t)
    y=pieces[0].copy()
    for p in pieces[1:]:
        y[-n:]=y[-n:]*fo+p[:n]*fi; y=np.concatenate([y,p[n:]])
    return y
def flush():
    global run
    if run:
        y=join(run); f=int(0.012*SR)
        y=y[int(XF/2*SR):len(y)-int(XF/2*SR)]          # trim the outer extra halves
        y[:f]*=np.linspace(0,1,f); y[-f:]*=np.linspace(1,0,f)
        out.append(tempo(y,run_sp[0])); run=[]
for it in E['items']:
    if it['type']=='room':
        if run and it['speed']!=run_sp[0]: flush()
        run_sp[0]=it['speed']
        # v3: every joint is a 25 ms equal-power crossfade (a fade out then in left a dip that "flopped").
        # Each piece takes 12.5 ms extra on both sides, so the overlap keeps the length exact (lips in sync).
        a=voice[max(0,int((it['s']-XF/2)*SR)):int((it['e']+XF/2)*SR)].copy()
        run.append(a)
    else:
        flush()
        a=load(it['file'],it['s'],it['e'])
        n=int(round((it['e']-it['s'])*SR)); a=np.pad(a,(0,max(0,n-len(a))))[:n]
        a*=10**((v_db-3-rms_db(a))/20)
        f=int(0.012*SR); a[:f]*=np.linspace(0,1,f); a[-f:]*=np.linspace(1,0,f)
        out.append(a)
flush()
y=np.concatenate(out)
subprocess.run(['ffmpeg','-loglevel','error','-y','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-c:a','pcm_f32le','work/voice_cut.wav'],input=y.astype(np.float32).tobytes())
print('voice_cut.wav',round(len(y)/SR,2),'s; edit list says',E['length'])
