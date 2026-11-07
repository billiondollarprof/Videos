# ============================================================
# VO 01 CUT: cut a voiceover recording (no video) into the final voice track
# What : 1. finds where his voice is (loudness, every 10 ms)
#        2. keeps the voice inside [start, end], minus the approved cuts
#        3. puts a real breath at each joint: short inside a sentence, longer between
#           sentences, a little longer again where content was cut (that is where the picture
#           changes), using the room tone from the recording itself, never digital silence
#        4. plays it at his speed (atempo keeps the pitch: his voice is never changed)
# Why  : a voiceover has no picture to keep in step, so it is cut as sound alone. The pause
#        caps come from his own cut of video 1: tight, with real breaths.
# In   : face48k_clean.wav (04b), words.json (01b), vo_config.json (cuts, speed, pauses)
# Out  : voice_cut.wav, vo_timeline.json (where every source second lands in the output)
# Use  : python3 vo_01_cut.py
# Never: never cut inside a word. Cuts are approved by Anthony and listed in vo_config.json.
# ============================================================
import json
import subprocess
import wave

import numpy as np

C = json.load(open("vo_config.json"))
W = json.load(open("words.json"))["words"]
SPEED = C.get("speed", 1.1)
PZ = C.get("pauses", {"within": 0.06, "between": 0.16, "after_cut": 0.22})

# --- 1. The cleaned voice, and where the voice is (loudness above the room) ---
w = wave.open("face48k_clean.wav"); SR = w.getframerate()
x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)
hop = SR // 100
n = len(x) // hop
db = 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)) / 32768 + 1e-9)
floor, peak = np.percentile(db, 15), np.percentile(db, 95)
voiced = db > floor + 0.35 * (peak - floor)
regions, i = [], 0
while i < n:                                           # voiced runs, small holes (<150 ms) closed
    if voiced[i]:
        j = i
        while j < n and (voiced[j] or (j + 15 < n and voiced[j:j + 15].any())):
            j += 1
        if j - i >= 8:
            regions.append([i / 100, j / 100])
        i = j
    else:
        i += 1

# --- 2. Keep the voice inside [start, end] minus the cuts ---
keep = [[C["start"], C["end"]]]
for a, b, *_ in C["cuts"]:
    nxt = []
    for s, e in keep:
        if b <= s or a >= e: nxt.append([s, e])
        else:
            if a > s: nxt.append([s, a])
            if b < e: nxt.append([b, e])
    keep = nxt
pieces = []
for s, e in keep:
    for rs, re_ in regions:
        a, b = max(s, rs - 0.03), min(e, re_ + 0.08)    # a hair of air before, a little after
        if b - a > 0.08: pieces.append([a, b])
pieces.sort()

# --- 3. Breaths at every joint, from real room tone ---
def ends_sentence(t):
    last = [w_ for w_ in W if w_["e"] <= t + 0.25]
    return bool(last) and last[-1]["w"].rstrip()[-1:] in ".?!"
cut_edges = [b for _, b, *_ in C["cuts"]]
# Room tone = the quietest 10 ms slices joined together. NEVER one second taken from a single
# spot: that spot was his voice in voiceover 1, and every joint said "Obi" (his note, 2026-11-07).
quiet = np.sort(np.argsort(db)[:200])                   # the 200 quietest slices, in time order
room = np.concatenate([x[q * hop:(q + 1) * hop] for q in quiet])
assert 20 * np.log10(np.sqrt((room ** 2).mean()) / 32768 + 1e-9) < floor + 3, "room tone is not quiet"
sm = int(0.002 * SR)                                    # tiny fades so the joins in the tone do not click
for k in range(1, len(quiet)): room[k * hop - sm:k * hop + sm] *= 0.6
out, timeline, t_out = [], [], 0.0
FADE = int(0.008 * SR)
for k, (a, b) in enumerate(pieces):
    seg = x[int(a * SR):int(b * SR)].copy()
    ramp = np.linspace(0, 1, FADE); seg[:FADE] *= ramp; seg[-FADE:] *= ramp[::-1]
    timeline.append({"src": round(a, 3), "len": round(b - a, 3), "out": round(t_out, 3)})
    out.append(seg); t_out += len(seg) / SR
    if k + 1 < len(pieces):
        gap = pieces[k + 1][0] - b
        after_cut = any(b - 0.1 <= c <= pieces[k + 1][0] + 0.1 for c in cut_edges)
        target = PZ["after_cut"] if after_cut else (PZ["between"] if ends_sentence(b) else PZ["within"])
        pause = min(target, gap) if not after_cut else target
        if pause > 0.005:
            tone = np.resize(room, int(pause * SR)) * 0.9
            out.append(tone); t_out += len(tone) / SR
y = np.concatenate(out)
wo = wave.open("_voice_1x.wav", "w"); wo.setnchannels(1); wo.setsampwidth(2); wo.setframerate(SR)
wo.writeframes(np.clip(y, -32768, 32767).astype(np.int16).tobytes()); wo.close()

# --- 4. His speed (atempo keeps the pitch) ---
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "_voice_1x.wav", "-af", f"atempo={SPEED}", "voice_cut.wav"], check=True)
for p in timeline:
    p["out"] = round(p["out"] / SPEED, 3); p["len_out"] = round(p["len"] / SPEED, 3)
total = len(y) / SR / SPEED
json.dump({"speed": SPEED, "total": round(total, 3), "pieces": timeline}, open("vo_timeline.json", "w"))
print(f"{len(pieces)} pieces; voice {total:.1f} s = {int(total // 60)}:{int(total % 60):02d} at {SPEED}x")
