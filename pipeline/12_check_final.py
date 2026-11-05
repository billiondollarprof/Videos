# ============================================================
# 12 CHECK FINAL: listen to the finished video the way a viewer would
# What : transcribes the FINAL video's sound with the bigger Whisper model (which writes
#        fillers down) and reports:
#        1. every filler or tic still in it ("uh", "um", "eh", "okay?", "Yeah,", "right?",
#           "so now", "alright"), with the time and the words around it
#        2. the longest silences inside the talk (the end card is ignored)
#        3. how well the words match the kept words (89 to 92 percent is normal: the rest is
#           the speech tool mishearing his accent)
# Why  : on video 1 the word-based cuts missed 4 tics, because his voice runs on from one
#        word into the next. Only listening to the final shows what is really in it.
# Use  : python3 12_check_final.py final.mp4 kept_text.txt
# Out  : a list. Zero tics is the goal. Anything listed goes into project.json "cut_times"
#        (exact seconds of the face video), then rebuild.
# Never: never say "no fillers" without running this on the final file.
# ============================================================
import json
import os
import re
import subprocess
import sys

import numpy as np

FINAL, KEPT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
norm = lambda x: re.sub(r"[^a-z']", "", x.lower())

# --- 1. The final sound, transcribed with the filler-friendly prompt ---
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", FINAL, "-vn", "-ac", "1", "-ar", "16000", "_final16k.wav"], check=True)
subprocess.run([sys.executable, os.path.join(HERE, "01b_transcribe_fillers.py"), "_final16k.wav", "_final_words.json", "medium"],
               check=True, capture_output=True)
C = json.load(open("_final_words.json"))["words"]

# --- 2. Fillers and tics still in it ---
SOUNDS = {"uh", "um", "umm", "eh", "er", "erm", "ah", "hmm", "mm"}
found = 0
for i, w in enumerate(C):
    a = norm(w["w"])
    b = norm(C[i + 1]["w"]) if i + 1 < len(C) else ""
    prev = C[i - 1]["w"] if i else "."
    edge = bool(re.search(r"[.?!,]$", w["w"]) or re.search(r"[.?!]$", prev))
    kind = None
    if a in SOUNDS:
        kind = "sound"
    elif a in ("okay", "yeah", "alright", "right") and edge:
        kind = "tic"
    elif (a, b) in {("so", "now"), ("all", "right")}:
        kind = "opener"
    elif a == b and a in ("so", "the", "i", "you", "and", "it", "to"):
        kind = "repeat?"          # may be real speech ("out of it, it will..."): read it
    if kind:
        found += 1
        ctx = " ".join(x["w"] for x in C[max(0, i - 3):i]) + f" [{w['w']}] " + " ".join(x["w"] for x in C[i + 1:i + 4])
        print(f"{w['s']:7.1f}s {kind:8s} ...{ctx}")
print(f"{found} filler or tic candidates")

# --- 3. Silences inside the talk ---
r = subprocess.run(["ffmpeg", "-v", "info", "-i", FINAL, "-vn", "-af", "silencedetect=noise=-42dB:d=0.25", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
durs = [float(x) for x in re.findall(r"silence_duration: ([\d.]+)", r)]
end = C[-1]["e"] if C else 0
inside = [(s, d) for s, d in zip(starts, durs) if s < end - 0.5]
print(f"{len(inside)} silences of 0.25 s or more inside the talk", inside[:10])

# --- 4. Match with the kept words ---
import difflib
K = open(KEPT).read().split()
sm = difflib.SequenceMatcher(None, [norm(x) for x in K], [norm(w["w"]) for w in C], autojunk=False)
print(f"words match the kept words: {sm.ratio():.2f}")
