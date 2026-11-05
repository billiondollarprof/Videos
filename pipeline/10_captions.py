# ============================================================
# 10 CAPTIONS AND ON-SCREEN MOMENTS
# What : turns the placed words into caption groups (1 to 3 words on screen at once)
#        and finds the moments for the step labels and tip cards.
# Why  : the words come from Anthony's own transcript, so the spelling is his, not the
#        speech tool's guesses. Only the timing comes from the speech tool.
# In   : timeline.json (09), aligned_words.json (02), project.json
# Out  : remotion/src/data.json
# Never: never show a word before it is said.
# ============================================================
import json
import re

P = json.load(open("project.json"))
T = json.load(open("timeline.json"))
W = json.load(open("aligned_words.json"))

# --- 1. The kept words, in order ---
cut = set()
for c in P["cuts"]:
    cut.update(range(c[0], c[1] + 1))
placed = {w["i"]: w for w in T["words"]}
order = [i for i in range(len(W)) if i not in cut]
words = []
for i in order:
    if i in placed:
        words.append(dict(placed[i]))
    else:
        words.append({"i": i, "w": W[i]["w"], "s": None, "e": None})

# --- 2. Words lost when short pauses were trimmed: spread them between their neighbours ---
for k, w in enumerate(words):
    if w["s"] is None:
        prev = next((words[j]["e"] for j in range(k - 1, -1, -1) if words[j]["s"] is not None), 0)
        nxt = next((words[j]["s"] for j in range(k + 1, len(words)) if words[j]["s"] is not None), prev + 0.3)
        w["s"] = prev
        w["e"] = max(prev + 0.05, min(nxt, prev + 0.3))

# --- 3. Group into captions: up to 3 words, break on a pause or at the end of a phrase ---
FILLERS = {"uh", "um", "umm"}
groups, cur = [], []
for w in words:
    if re.sub(r"[^a-z]", "", w["w"].lower()) in FILLERS:
        continue
    gap = (w["s"] - cur[-1]["e"]) if cur else 0
    too_long = len(" ".join(x["w"] for x in cur + [w])) > 18
    if cur and (len(cur) >= 3 or gap > 0.35 or too_long):
        groups.append(cur)
        cur = []
    cur.append(w)
    if re.search(r"[.?!,]$", w["w"]):
        groups.append(cur)
        cur = []
if cur:
    groups.append(cur)
caps = [{"s": g[0]["s"], "e": g[-1]["e"],
         "words": [{"t": re.sub(r"[,.]$", "", x["w"]), "s": x["s"], "e": x["e"]} for x in g]} for g in groups]
# hold each caption until the next one starts (at most 0.6 s extra)
for a, b in zip(caps, caps[1:]):
    a["e"] = min(b["s"], a["e"] + 0.6)


# --- 4. Moments: step labels and tip cards appear on a chosen word ---
def at(i):
    return next(w["s"] for w in words if w["i"] >= i)


# --- 4a. Layout segments, tied to words (project.json "layout"), so they follow any re-cut
# or speed change. Each: {"word": n, "face": "full" or "bubble", "card": "broll"/"mock"/"screen"}.
HOOK_END = 3.6                                     # the hook title needs the face full until here
segments = [{"t": 0, "face": "full"}]
for s in P.get("layout", []):
    t = max(at(s["word"]), HOOK_END) if s["word"] > 0 else 0
    segments.append({"t": t, "face": s["face"], **({"card": s["card"]} if "card" in s else {})})
segments.append({"t": T["screenStart"], "face": "bubble", "card": "screen"})
card_windows, open_at = [], None
for s in segments:
    if s.get("card") and open_at is None:
        open_at = s["t"]
    if not s.get("card") and open_at is not None:
        card_windows.append([open_at, s["t"]]); open_at = None
if open_at is not None:
    card_windows.append([open_at, T["frames"] / T["fps"]])
# named moments for B-roll animations: project.json "moments": {"name": [word, seconds offset]}
named = {k: at(w) + off for k, (w, off) in P.get("moments", {}).items()}

steps = []
if len(segments) > 2:                              # an opening with B-roll gets "THE PROBLEM"
    steps.append({"t": segments[1]["t"], "n": 0, "label": P.get("problem_label", "The problem")})
    full_again = next((s["t"] for s in segments[2:] if s["face"] == "full"), None)
    if full_again is not None:
        steps.append({"t": full_again, "n": -1, "label": ""})
steps.append({"t": T["screenStart"], "n": 1, "label": P["first_step_label"]})
for n, (word, label) in enumerate(P["steps"], start=2):
    steps.append({"t": at(word), "n": n, "label": label})
moments = {
    **named,
    "segments": segments,
    "cardWindows": card_windows,
    "screenStart": T["screenStart"],
    "steps": steps,
    "tips": [{"t": at(w), "d": d, "title": title, "text": text} for w, d, title, text in P["tips"]],
    "end": T["frames"] / T["fps"],
}
json.dump({"captions": caps, "moments": moments, "frames": T["frames"], "fps": T["fps"],
           "pieces": T["pieces"], "text": P["text"]}, open("remotion/src/data.json", "w"))
print(len(caps), "caption groups,", len(steps), "steps,", len(moments["tips"]), "tips")
