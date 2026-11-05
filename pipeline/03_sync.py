# ============================================================
# 03 SYNC: line up the screen recording with the face recording, by sound
# What : finds where the screen recording starts inside the face recording, and how
#        fast its clock runs compared with the face one (the "drift").
# Why  : two phones (or two apps) never start at the same moment, and their clocks
#        differ slightly. On video 1 the drift was 0.19 s by the end: enough to see the
#        lips miss the voice. Measure it along the whole length, never only at the start.
# Use  : python3 03_sync.py [rough start in seconds, if Anthony gave one]
# Out  : writes screen_offset and screen_rate into project.json
# Never: never accept a weak match. If the match score is under 0.6, stop and say so.
# ============================================================
import json
import subprocess
import sys
import wave

import numpy as np
from scipy.signal import butter, filtfilt

P = json.load(open("project.json"))
SR = 16000
HOP = 80                                # loudness measured 200 times a second
R = SR // HOP


# --- 1. Load both sounds, keep the voice band, measure loudness over time ---
def loudness_curve(video):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vn", "-ac", "1", "-ar", str(SR), "_tmp.wav"], check=True)
    w = wave.open("_tmp.wav")
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    b, a = butter(3, [300 / (SR / 2), 3400 / (SR / 2)], "band")
    x = filtfilt(b, a, x)
    n = len(x) // HOP
    return np.abs(x[:n * HOP]).reshape(n, HOP).mean(1)


face = loudness_curve(P["face_video"])
screen = loudness_curve(P["screen_video"])


def norm(v):
    return (v - v.mean()) / (v.std() + 1e-9)


# --- 2. Rough start: slide the first 60 s of the screen sound along the face sound ---
guess = float(sys.argv[1]) if len(sys.argv) > 1 else None
lo, hi = (max(0, guess - 30), guess + 30) if guess else (0, len(face) / R - 60)
seg = norm(screen[:60 * R])
best = (-1, 0)
for off in range(int(lo * R), int(hi * R)):
    f = face[off:off + len(seg)]
    if len(f) < len(seg):
        break
    c = float(np.corrcoef(f, seg)[0, 1])
    if c > best[0]:
        best = (c, off)
print(f"rough start {best[1] / R:.2f} s, match {best[0]:.2f}")
if best[0] < 0.6:
    sys.exit("STOP: the two sounds do not match well. Check the files, or ask Anthony for a rough start time.")
base = best[1] / R

# --- 3. Drift: check the match at many points along the recording ---
points = []
for t in range(5, int(len(screen) / R) - 15, 30):
    seg = norm(screen[t * R:(t + 12) * R])
    b2 = (-1, 0)
    for d in range(-R, R + 1):
        st = int((base + t) * R) + d
        f = face[st:st + len(seg)]
        if len(f) < len(seg):
            continue
        c = float(np.corrcoef(f, seg)[0, 1])
        if c > b2[0]:
            b2 = (c, d)
    if b2[0] > 0.6:
        points.append((t, b2[1] / R))
    print(f"  screen {t:4d} s: shift {b2[1] / R:+.3f} s (match {b2[0]:.2f})")

# --- 4. Fit a straight line: shift = intercept + slope * time ---
ts = np.array([p[0] for p in points])
sh = np.array([p[1] for p in points])
slope, intercept = np.polyfit(ts, sh, 1)
P["screen_offset"] = round(base + intercept, 3)
P["screen_rate"] = round(1 + slope, 6)
json.dump(P, open("project.json", "w"), indent=2)
print(f"screen starts at {P['screen_offset']} s of the face video; screen clock rate {P['screen_rate']}")
