# ============================================================
# 10b ASSETS: fit the B-roll to its slot, add the B-roll sounds, copy everything into the layout
# What : 1. cuts the B-roll clip so it fills exactly the time its layout slot lasts, with the
#           phone's top bar cropped off and any private list lightly blurred
#        2. adds sound cues for the B-roll moments (a pop, a tap per email deleted, ticks) to
#           remotion/src/data.json as "extra_cues", which 11_finish.py mixes in
#        3. copies the face, screen and B-roll videos into remotion/public/
# Why  : the layout changes with every re-cut or speed change, so the B-roll must be re-fitted
#        each time. On video 1 this was done by hand three times.
# In   : project.json ("broll" block, see project.example.json), remotion/src/data.json (10)
# Use  : python3 10b_assets.py       (from the project folder, after 10_captions.py)
# Never: never show a readable email, name or code in the B-roll. A scrolling list is blurred
#        as a whole (text reading misses words on moving lists). Check stills of it.
# ============================================================
import json
import os
import shutil
import subprocess

P = json.load(open("project.json"))
DATA = "remotion/src/data.json"
D = json.load(open(DATA))
segs = D["moments"]["segments"]
M = D["moments"]

# --- 1. The B-roll clip, fitted to its slot ---
B = P.get("broll")
if B:
    i = next(k for k, s in enumerate(segs) if s.get("card") == "broll")
    slot = round(segs[i + 1]["t"] - segs[i]["t"], 3)
    wins = B["windows"]
    fixed = wins[:-1]
    last_start = wins[-1][0]
    last_len = round(slot - sum(b - a for a, b in fixed), 3)
    top, keep = B.get("crop_top", 0), B.get("keep_bottom_px", 0)
    windows = fixed + [[last_start, last_start + last_len]]
    # The cropped clip feeds one copy per window ("split"). Each window is lightly blurred
    # everywhere except the bottom bar (nothing private there), then trimmed.
    n = len(windows)
    fc = f"[0:v]crop=iw:ih-{top}:0:{top},split={n}" + "".join(f"[v{k}]" for k in range(n)) + ";"
    fc += ";".join(f"[v{k}]split[a{k}][b{k}];[b{k}]crop=iw:ih-{keep}:0:0,boxblur=9:3[bl{k}];"
                   f"[a{k}][bl{k}]overlay=0:0,trim={a}:{b},setpts=PTS-STARTPTS[x{k}]" for k, (a, b) in enumerate(windows))
    fc += ";" + "".join(f"[x{k}]" for k in range(n)) + f"concat=n={n}:v=1:a=0,scale=864:-2,fps=30,format=yuv420p[o]"
    os.makedirs("broll", exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", B["clip"], "-filter_complex", fc, "-map", "[o]", "-an",
                    "-c:v", "libx264", "-crf", "16", "-preset", "fast", "broll/broll_cut.mp4"], check=True)
    print(f"B-roll fitted to its {slot} s slot")

# --- 2. Sound cues for the B-roll moments (10_captions.py clears these every run) ---
cues = []
broll = next((s for s in segs if s.get("card") == "broll"), None)
mock = next((k for k, s in enumerate(segs) if s.get("card") == "mock"), None)
if broll:
    cues.append([broll["t"] + 0.35, "tap-soft.wav", 0.32])                  # the number label pops
if mock is not None:                                                         # one tap or click per email deleted
    t, k = segs[mock]["t"] + 0.16, 0
    while t < segs[mock + 1]["t"] - 0.2:
        cues.append([round(t + 0.28, 3), "tap-soft.wav" if k % 2 == 0 else "mouse-click-cc0.ogg", 0.16])
        t += 0.8; k += 1
for name, snd, gain in (("connectAt", "tap-soft.wav", 0.30), ("cleanAt", "tick-warm.wav", 0.28)):
    if name in M: cues.append([M[name], snd, gain])
if "notifyAt" in M: cues.append([M["notifyAt"] + 0.2, "tick-warm.wav", 0.24])
D["extra_cues"] = cues
json.dump(D, open(DATA, "w"))

# --- 3. Assets into the layout project ---
os.makedirs("remotion/public", exist_ok=True)
face = "face_soft.mp4" if os.path.exists("face_soft.mp4") else "face_cut.mp4"
for src, dst in ((face, "face_cut.mp4"), ("screen_cut.mp4", "screen_cut.mp4"), ("broll/broll_cut.mp4", "broll_cut.mp4")):
    if os.path.exists(src): shutil.copy(src, "remotion/public/" + dst)
print(f"{len(cues)} sound cues; face video used: {face}")
