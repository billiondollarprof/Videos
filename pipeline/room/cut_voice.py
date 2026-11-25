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
out=[]
for it in E['items']:
    if it['type']=='room':
        a=voice[int(it['s']*SR):int(it['e']*SR)].copy()
    else:
        a=load(it['file'],it['s'],it['e'])
        n=int(round((it['e']-it['s'])*SR)); a=np.pad(a,(0,max(0,n-len(a))))[:n]
        a*=10**((v_db-3-rms_db(a))/20)                       # 3 dB under his voice
    f=min(int(0.012*SR),len(a)//4)
    a[:f]*=np.linspace(0,1,f); a[-f:]*=np.linspace(1,0,f)
    out.append(a)
y=np.concatenate(out)
subprocess.run(['ffmpeg','-loglevel','error','-y','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-c:a','pcm_f32le','work/voice_cut.wav'],input=y.astype(np.float32).tobytes())
print('voice_cut.wav',round(len(y)/SR,2),'s; edit list says',E['length'])
