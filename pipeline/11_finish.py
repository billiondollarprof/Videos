# ============================================================
# 11 FINISH: sound effects, final mix, camera flash, final file
# What : 1. places sound effects on the visible actions (from remotion/src/data.json)
#        2. mixes them under the cleaned voice, in stereo
#        3. sets loudness to -14 LUFS with peaks at or below -1.5 dB, measured on the
#           stereo file the platforms will play
#        4. adds a white camera flash at the start and on the end card
#        5. joins picture and sound into the final MP4
# Use  : python3 11_finish.py video_silent.mp4 voice_cut_raw.wav final.mp4
# Never: never let a sound effect cover a word. Voice stays the loudest thing.
# ============================================================
import json
import os
import re
import subprocess
import sys

SILENT, VOICE, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
HERE = os.path.dirname(os.path.abspath(__file__))
SFX = os.path.join(HERE, "..", "sfx")
D = json.load(open(os.path.join(HERE, "remotion", "src", "data.json")))
M = D["moments"]
END_CARD = 4.0                                   # seconds, must match Root.tsx

# --- 1. The cue list: (time in seconds, sound file, gain) ---
# Gains keep every effect well under the voice. Sounds follow something you can SEE.
cues = [
    (0.00, "camera-shutter.wav", 0.45),          # opening camera snap, with the flash
    (0.15, "tap-soft.wav", 0.35),                # hook card lands
    (3.25, "whoosh-air-short.wav", 0.25),        # hook card leaves
    (M["screenStart"] - 0.10, "whoosh-air.wav", 0.30),   # face shrinks, screen rises
]
for s in M["steps"][1:]:
    cues.append((s["t"] + 0.15, "paper-flick.wav", 0.30))   # step label slides in
for t in M["tips"]:
    cues.append((t["t"], "tick-warm.wav", 0.28))            # tip card pops
last_click = -99
for p in D["pieces"]:
    if p["type"] == "fast" and p["out"] - last_click > 6:   # "Speeding up" badge, not too often
        cues.append((p["out"], "mouse-click-cc0.ogg", 0.25))
        last_click = p["out"]
cues.append((M["end"] - 0.10, "whoosh-air.wav", 0.30))     # into the end card
cues.append((M["end"] + 0.30, "camera-shutter.wav", 0.45)) # end card snap, with the flash

# --- 2. Mix: voice (padded for the end card) + every cue, in stereo ---
inputs = ["-i", VOICE]
parts, labels = [], []
for k, (t, name, gain) in enumerate(cues):
    inputs += ["-i", os.path.join(SFX, name)]
    ms = int(max(0, t) * 1000)
    parts.append(f"[{k + 1}]aresample=48000,aformat=channel_layouts=mono,adelay={ms},volume={gain}[s{k}]")
    labels.append(f"[s{k}]")
mix = (";".join(parts) + f";[0]aresample=48000,apad=pad_dur={END_CARD}[v];"
       f"[v]{''.join(labels)}amix=inputs={len(cues) + 1}:normalize=0:duration=first,"
       f"pan=stereo|c0=c0|c1=c0[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", mix, "-map", "[a]",
                "-c:a", "pcm_s16le", "_mix.wav"], check=True)


# --- 3. Loudness, measured on the stereo mix, then corrected once ---
def measure(path):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-af", "ebur128=peak=true:framelog=quiet",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    i = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])
    pk = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)[-1])
    return i, pk


i, pk = measure("_mix.wav")
gain = -14.0 - i
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "_mix.wav", "-af",
                f"volume={gain:.2f}dB,alimiter=limit=0.84:level=false", "-c:a", "pcm_s16le", "_final.wav"], check=True)

# --- 4. Camera flash: white, fading out over 6 frames, at the start and on the end card ---
def flash(t0):
    steps = [(0.85, 0, 2), (0.55, 2, 4), (0.25, 4, 6)]       # (strength, from frame, to frame)
    return ",".join(f"drawbox=x=0:y=0:w=iw:h=ih:color=white@{a}:t=fill:"
                    f"enable='between(t,{t0 + f0 / 30:.3f},{t0 + f1 / 30 - 0.001:.3f})'" for a, f0, f1 in steps)


vf = flash(0.0) + "," + flash(M["end"] + 0.30)

# --- 5. The final file: H.264 picture, AAC stereo sound, ready for TikTok / Shorts / Reels ---
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SILENT, "-i", "_final.wav", "-vf", vf,
                "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "12M", "-bufsize", "24M",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                "-shortest", OUT], check=True)
i2, pk2 = measure(OUT)
print(f"{len(cues)} sound effects. Final file: {i2} LUFS, peak {pk2} dBFS -> {OUT}")
