# ============================================================
# 11 FINISH: sound effects, final mix, camera flash, final file
# What : 1. places sound effects on the visible actions (from remotion/src/data.json)
#        2. mixes them under the cleaned voice, in stereo
#        3. sets loudness to -14 LUFS with peaks at or below -1.5 dB, measured on the
#           stereo file the platforms will play
#        4. adds a white camera flash on the end card (never on the first frame)
#        5. joins picture and sound into the final MP4
# Use  : python3 11_finish.py video_silent.mp4 voice_cut_raw.wav final.mp4 [path to data.json]
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
D = json.load(open(sys.argv[4] if len(sys.argv) > 4 else os.path.join(HERE, "remotion", "src", "data.json")))
M = D["moments"]
END_CARD = 4.0                                   # seconds, must match Root.tsx

# --- 1. The cue list: (time in seconds, sound file, gain) ---
# Gains keep every effect well under the voice. Sounds follow something you can SEE.
cues = [
    (0.15, "tap-soft.wav", 0.35),                # hook card lands
]
# hook card leaves: a short whoosh, unless a layout change lands at the same moment
if not any(abs(seg["t"] - 3.4) < 1.0 for seg in M.get("segments", [])):
    cues.append((3.25, "whoosh-air-short.wav", 0.25))
# every change of layout: the face moving between full screen and the circle
for seg in M.get("segments", [{"t": M["screenStart"]}]):
    if seg["t"] > 0.5:
        cues.append((seg["t"] - 0.10, "whoosh-air.wav", 0.28))
for s in M["steps"][1:]:
    cues.append((s["t"] + 0.15, "paper-flick.wav", 0.30))   # step label slides in
for t in M["tips"]:
    cues.append((t["t"], "tick-warm.wav", 0.28))            # tip card pops
# (2026-11-05) No click on fast-forwards: the badge is gone, and a sound needs something to see.
for t, name, g in D.get("extra_cues", []):                 # B-roll moments, set per video
    cues.append((t, name, g))
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


# --- 3. Loudness: -14 LUFS, true peak at or below -1.5 dB, measured on the ENCODED sound ---
# AAC encoding (the sound compression every platform uses) pushes peaks up after the
# limiter. Video 1's first try came out at -0.2 dB. So: encode, measure, correct, repeat.
def measure(path):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-af", "ebur128=peak=true:framelog=quiet",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    i = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])
    pk = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)[-1])
    return i, pk


# The raw voice sits near -27 LUFS, so it needs about +13 dB. A plain limiter cannot
# hold the peaks against that much boost (video 1: peaks came out at +4 dB). loudnorm
# (FFmpeg's broadcast loudness filter) can: pass 1 measures, pass 2 applies.
def loudnorm_measure(path, target, tp):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-af",
                        f"loudnorm=I={target}:TP={tp}:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return json.loads(r[r.rindex("{"):r.rindex("}") + 1])


target, tp = -14.0, -2.0                 # aim the peaks at -2 dB, leaving room for the encoder
for attempt in range(3):
    m = loudnorm_measure("_mix.wav", target, tp)
    ln = (f"loudnorm=I={target}:TP={tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "_mix.wav", "-af", ln + ",aresample=48000",
                    "-c:a", "aac", "-b:a", "192k", "_final.m4a"], check=True)
    i, pk = measure("_final.m4a")
    print(f"  sound pass {attempt + 1}: {i} LUFS, peak {pk} dB")
    if abs(i + 14.0) <= 0.5 and pk <= -1.5:
        break
    if pk > -1.5:
        tp -= 0.5                         # the encoder still overshot: aim the peaks lower
    target += -14.0 - i                   # and nudge the level towards -14

# --- 4. Camera flash: white, fading out over 6 frames, at the start and on the end card ---
def flash(t0):
    # Frame numbers, not seconds: with seconds, rounding left one unflashed frame in the
    # middle of the flash on video 1, which showed as a flicker.
    n0 = round(t0 * 30)
    steps = [(0.85, 0, 1), (0.55, 2, 3), (0.25, 4, 5)]       # (strength, first frame, last frame)
    return ",".join(f"drawbox=x=0:y=0:w=iw:h=ih:color=white@{a}:t=fill:"
                    f"enable='between(n,{n0 + f0},{n0 + f1})'" for a, f0, f1 in steps)


# Only on the end card. A flash on frame 0 made the first frame (what people see before
# they press play) washed out white (his note on version 2, 2026-11-05).
vf = flash(M["end"] + 0.30)

# --- 5. The final file: H.264 picture, AAC stereo sound, ready for TikTok / Shorts / Reels ---
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SILENT, "-i", "_final.m4a", "-vf", vf,
                "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "12M", "-bufsize", "24M",
                "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart",
                "-shortest", OUT], check=True)
i2, pk2 = measure(OUT)
print(f"{len(cues)} sound effects. Final file: {i2} LUFS, peak {pk2} dBFS -> {OUT}")
