# ============================================================
# BUILD THE CUT TRACKS
# What : turns the two raw videos into three files that are already cut,
#        already in step with each other, and all exactly the same length:
#          face_cut.mp4   your face, colour-corrected
#          screen_cut.mp4 the phone screen, names and emails blurred (make_mask.py), lined up to your voice
#          voice_cut.wav  your cleaned voice
#        plus timeline.json, which says where every kept word lands.
# Why  : Remotion (the effects step) then only has to play three straight files.
# Never: never change the cut list here. It lives in edl.py.
# ============================================================
import json, subprocess, wave, numpy as np
FPS=30
P=json.load(open("project.json"))
SCREEN_OFFSET=P["screen_offset"]  # face time when the screen recording starts (03_sync.py)
SCREEN_RATE=P["screen_rate"]      # how much faster the screen clock runs (03_sync.py)
STATUS_BAR=P.get("status_bar_px", 0)
SPEED=P.get("speed", 1.0)   # his speech speed: 1.1 since 2026-11-05 (his choice), pitch kept  # height of the phone status bar to crop off the top
EDL=json.load(open("edl.json"))
WORDS=json.load(open("aligned_words.json"))

# --- 1. Turn the edit list into exact frame ranges ---
pieces=[]; out_n=0
for p in EDL:
    na,nb=round(p["a"]*FPS),round(p["b"]*FPS)
    if nb<=na: continue
    step=p.get("speed",1)
    count=len(range(na,nb,step))
    pieces.append({"type":p["type"],"na":na,"nb":nb,"step":step,"out":out_n,"count":count})
    out_n+=count
total_frames=out_n
terms=[]
for p in pieces:
    if p["step"]==1: terms.append(f"between(n,{p['na']},{p['nb']-1})")
    else: terms.append(f"between(n,{p['na']},{p['nb']-1})*not(mod(n-{p['na']},{p['step']}))")
select="select='"+"+".join(terms)+"',setpts=N/30/TB"+(f",setpts=PTS/{SPEED},fps=30" if SPEED!=1 else "")

# --- 2. Face video: steady 30 fps, cut, gentle colour and sharpening ---
open("face_filter.txt","w").write(
  f"[0:v]fps=30,{select},eq=contrast=1.06:brightness=0.015:saturation=1.10:gamma=1.03,unsharp=5:5:0.5,format=yuv420p[v]")
import os
if not os.environ.get("SKIP_FACE"): subprocess.run(["ffmpeg","-v","error","-y","-i",P["face_video"],"-filter_complex_script","face_filter.txt",
  "-map","[v]","-an","-c:v","libx264","-preset","fast","-crf","16","face_cut.mp4"],check=True)

# --- 3. Screen video: blur names and emails (mask.mkv, see make_mask.py), line up, cut ---
open("screen_filter.txt","w").write(
  "[0:v]split[a][b];[b]boxblur=16:4[bl];[1:v]format=gray[m];[bl][m]alphamerge[bm];[a][bm]overlay=0:0,"
  f"crop=iw:ih-{STATUS_BAR}:0:{STATUS_BAR},"   # cut off the phone status bar (time, signal, battery)
  f"setpts=PTS*{SCREEN_RATE},tpad=start_duration={SCREEN_OFFSET}:color=black:stop_mode=clone:stop_duration=60,"
  f"fps=30,{select},format=yuv420p[v]")
subprocess.run(["ffmpeg","-v","error","-y","-i",P["screen_video"],"-i","mask.mkv","-filter_complex_script","screen_filter.txt",
  "-map","[v]","-an","-c:v","libx264","-preset","fast","-crf","16","screen_cut.mp4"],check=True)

# --- 4. Voice: copy the kept pieces, silence for fast-forward, tiny fades at every join ---
w=wave.open("face48k_clean.wav"); SR=w.getframerate()
x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)
out=[]; F=int(0.008*SR)
for p in pieces:
    n=int(round(p["count"]/FPS*SR))
    if p["type"]=="fast": out.append(np.zeros(n,np.float32)); continue
    s=int(round(p["na"]/FPS*SR)); seg=x[s:s+n].copy()
    if len(seg)<n: seg=np.pad(seg,(0,n-len(seg)))
    ramp=np.linspace(0,1,F); seg[:F]*=ramp; seg[-F:]*=ramp[::-1]
    out.append(seg)
y=np.concatenate(out)
wo=wave.open("_voice_1x.wav","w"); wo.setnchannels(1); wo.setsampwidth(2); wo.setframerate(SR)
wo.writeframes(np.clip(y,-32768,32767).astype(np.int16).tobytes()); wo.close()
# speed the voice up with atempo (keeps the pitch), to exactly the picture's length
subprocess.run(["ffmpeg","-v","error","-y","-i","_voice_1x.wav","-af",f"atempo={SPEED}",
                "-t",f"{round(total_frames/SPEED)/FPS}","voice_cut_raw.wav"],check=True)

# --- 5. Timeline: where each kept word lands in the finished video ---
def to_out(t):
    for p in pieces:
        if p["type"]=="talk" and p["na"]/FPS-0.05<=t<=p["nb"]/FPS+0.05:
            return round((p["out"]+(t*FPS-p["na"]))/FPS/SPEED,3)
    return None
tw=[]
for i,wd in enumerate(WORDS):
    s,e=to_out(wd["s"]),to_out(wd["e"])
    if s is not None and e is not None and e>s: tw.append({"i":i,"w":wd["w"],"s":s,"e":e})
screen_out=next(p["out"] for p in pieces if p["na"]/FPS>=SCREEN_OFFSET)/FPS/SPEED
json.dump({"fps":FPS,"frames":round(total_frames/SPEED),"screenStart":screen_out,"speed":SPEED,
           "pieces":[{"type":p["type"],"src":p["na"]/FPS,"out":p["out"]/FPS/SPEED,"len":p["count"]/FPS/SPEED} for p in pieces],
           "words":tw},open("timeline.json","w"))
print("frames",round(total_frames/SPEED),"=",round(total_frames/SPEED/FPS,1),"s; screen appears at",round(screen_out,2),"s; words placed",len(tw))
