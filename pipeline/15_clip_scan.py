# ============================================================
# 15 CLIP SCAN: what is said and shown in each reaction clip, for clips/CATALOGUE.md
# What : for every clip in ./clips: the words with times (Whisper medium, English) and a grid of
#        stills every 0.5 s with the time printed on each, so the faces can be read without watching.
# Why  : Anthony's reaction clips are a library for every video (his note, 2026-11-25). Each clip is
#        catalogued once; later videos pick moments from the catalogue.
# Use  : cd projects/<video>; HF_HUB_DISABLE_XET=1 python3 ../../pipeline/15_clip_scan.py
#        writes work/clips/<name>.txt and work/clips/<name>_grid.jpg
# Never: never let Whisper guess the language (it wrote Kannada and Thai for Pidgin over music):
#        English is set. Never copy a clip's words into the repo beyond the short lines catalogued.
# ============================================================
import os, subprocess, wave
import numpy as np
os.makedirs('work/clips',exist_ok=True)
from faster_whisper import WhisperModel
m=WhisperModel('medium',device='cpu',compute_type='int8',cpu_threads=4)
for f in sorted(os.listdir('clips')):
    name=f[:-4]; p=f'clips/{f}'
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',p,'-ac','1','-ar','16000',f'work/clips/{name}.wav'])
    w_=wave.open(f'work/clips/{name}.wav'); au=np.frombuffer(w_.readframes(w_.getnframes()),np.int16).astype(np.float32)/32768
    segs,_=m.transcribe(au,language='en',word_timestamps=True,vad_filter=True,condition_on_previous_text=False)
    lines=[]
    for s in segs: lines.append(f"{s.start:5.1f}-{s.end:5.1f} {s.text.strip()}")
    open(f'work/clips/{name}.txt','w').write('\n'.join(lines))
    d=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p],capture_output=True,text=True).stdout)
    n=int(d/0.5)+1; cols=8; rows=(n+cols-1)//cols
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',p,'-vf',f"fps=2,scale=180:-2,drawtext=text='%{{pts\\:flt}}':x=4:y=4:fontsize=16:fontcolor=yellow:box=1:boxcolor=black,tile={cols}x{rows}",'-frames:v','1',f'work/clips/{name}_grid.jpg'])
    print(name, round(d,1), 'lines', len(lines), flush=True)
