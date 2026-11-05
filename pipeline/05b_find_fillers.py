# ============================================================
# 05b FIND FILLERS
# What : lists every filler candidate, with times, for the cut list:
#        1. filler sounds Whisper wrote down ("uh", "um", "eh", "er", "ah", "hmm")
#        2. his own tics at a sentence edge ("okay?", "Okay,", "Yeah,", "alright", "right?")
#        3. "So now" and "All right" starting a sentence
#        4. short bursts of voice with no real word in them (a stray "eh")
# Why  : Anthony's note (2026-11-05): cut the fillers everywhere, including his own kind.
# In   : face_words_fillers.json (01b), aligned_words.json (02, aligned to 01b), vad.json (04)
# Out  : fillers.txt, to read and turn into project.json "cuts" (word numbers) and
#        "cut_times" (seconds), then shown to Anthony with the rest of the cut list.
# Never: never cut automatically from this list. Read each one: "it it" can be real speech
#        ("out of it, it will..."), and a tic inside a phrase may clip the words around it.
# ============================================================
import json
import re

M = json.load(open("face_words_fillers.json"))["words"]
T = json.load(open("aligned_words.json"))
V = json.load(open("vad.json"))["regions"]
norm = lambda x: re.sub(r"[^a-z']", "", x.lower())
SOUNDS = {"uh", "um", "umm", "eh", "er", "erm", "ah", "hmm", "mm"}
TICS = {"okay", "yeah", "alright", "right"}
out = []

# --- 1. Filler sounds ---
for w in M:
    if norm(w["w"]) in SOUNDS:
        out.append(f"time  {w['s']:7.2f}-{w['e']:7.2f}  sound      [{w['w']}]")

# --- 2. Tics at a sentence edge, in his own transcript (word numbers) ---
for i, w in enumerate(T):
    prev = T[i - 1]["w"] if i else "."
    edge = re.search(r"[.?!,]$", w["w"]) or re.search(r"[.?!]$", prev)
    if norm(w["w"]) in TICS and edge:
        ctx = " ".join(x["w"] for x in T[max(0, i - 3):i]) + f" [{w['w']}] " + " ".join(x["w"] for x in T[i + 1:i + 4])
        out.append(f"word  {i:5d}  {w['s']:7.2f}  tic        {ctx}")

# --- 3. "So now" / "All right" opening a sentence ---
for i in range(len(M) - 1):
    a, b = norm(M[i]["w"]), norm(M[i + 1]["w"])
    if (a, b) in {("so", "now"), ("all", "right")} or a == "alright":
        out.append(f"time  {M[i]['s']:7.2f}-{M[i + 1]['e']:7.2f}  opener     [{M[i]['w']} {M[i + 1]['w']}]")

# --- 4. Short voice bursts with no real word ---
for s, e in V:
    if e - s < 0.5:
        inside = [x for x in M if x["s"] < e and x["e"] > s and norm(x["w"]) not in SOUNDS]
        if not inside:
            out.append(f"time  {s:7.2f}-{e:7.2f}  stray      (no word)")

open("fillers.txt", "w").write("\n".join(sorted(out, key=lambda r: float(r.split()[1].split("-")[0]) if r.startswith("time") else float(r.split()[2]))) + "\n")
print(len(out), "candidates written to fillers.txt")
