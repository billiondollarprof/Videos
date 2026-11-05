# ============================================================
# 13 SHORT CUT: turn a finished video into a short that stops at a hook
# What : cuts the finished long video at a chosen moment (a hook: the question just asked,
#        the choice on screen, the result about to come), then adds the "Watch the full video
#        on YouTube" end card, with its sounds, and sets the loudness for the platforms.
# Why  : Anthony posts the full video on YouTube and a shorter version on Instagram Reels,
#        YouTube Shorts and TikTok, to send people to his channel. No long re-render: the
#        finished video is only trimmed, and the end card is a 5 second Remotion render.
# Use  : python3 13_short_cut.py full.mp4 113.83 endcard.mp4 short.mp4
#        113.83 = where to cut, in seconds of the finished video. Pick it with skill short-cut:
#        a moment inside a silence, so no word is clipped.
# Never: never cut inside a word, and never fade the last word. The cut sits in a silence.
# ============================================================
import json
import os
import re
import subprocess
import sys

SRC, CUT, CARD, OUT = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4]
HERE = os.path.dirname(os.path.abspath(__file__))
SFX = os.path.join(HERE, "..", "sfx")


def probe(path, entries):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", entries, "-of", "json", path],
                       capture_output=True, text=True).stdout
    return json.loads(r)["streams"][0]


# --- 1. The end card must be the same size as the video ---
vs = probe(SRC, "stream=width,height")
W, H = vs["width"], vs["height"]
card_len = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", CARD],
                                capture_output=True, text=True).stdout)

# --- 2. Sounds on the end card: a whoosh as it appears, a tap as the page lands, a tick on the name ---
cues = [(CUT + 0.00, "whoosh-air.wav", 0.30), (CUT + 0.55, "tap-soft.wav", 0.30), (CUT + 1.35, "tick-warm.wav", 0.26)]

inputs = ["-i", SRC, "-i", CARD]
parts = []
for k, (t, name, gain) in enumerate(cues):
    inputs += ["-i", os.path.join(SFX, name)]
    ms = int(t * 1000)
    parts.append(f"[{k + 2}:a]aresample=48000,aformat=channel_layouts=mono,adelay={ms},volume={gain}[s{k}]")
labels = "".join(f"[s{k}]" for k in range(len(cues)))

# --- 3. Picture: the video up to the cut, then the end card. Sound: the video up to the cut
#        (a 0.06 s fade inside the silence, never on a word), padded with silence under the card,
#        plus the card sounds. ---
fc = (f"[0:v]trim=0:{CUT},setpts=PTS-STARTPTS,fps=30[v0];"
      f"[1:v]scale={W}:{H},fps=30,setpts=PTS-STARTPTS[v1];[v0][v1]concat=n=2:v=1:a=0[v];"
      f"[0:a]atrim=0:{CUT},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=mono,"
      f"afade=t=out:st={CUT - 0.06}:d=0.06,apad=pad_dur={card_len}[a0];"
      + ";".join(parts) + ";"
      f"[a0]{labels}amix=inputs={len(cues) + 1}:normalize=0:duration=first,pan=stereo|c0=c0|c1=c0[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le",
                "_short_raw.mkv"], check=True)


# --- 4. Loudness: -14 LUFS, true peak at or below -1.5 dB, measured on the ENCODED sound ---
def measure(path):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-af", "ebur128=peak=true:framelog=quiet", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1]), float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)[-1])


def loudnorm_stats(path, target, tp):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-vn", "-af",
                        f"loudnorm=I={target}:TP={tp}:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return json.loads(r[r.rindex("{"):r.rindex("}") + 1])


target, tp = -14.0, -2.0
for attempt in range(3):
    m = loudnorm_stats("_short_raw.mkv", target, tp)
    ln = (f"loudnorm=I={target}:TP={tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']},aresample=48000")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "_short_raw.mkv", "-c:v", "copy", "-af", ln,
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], check=True)
    i, pk = measure(OUT)
    print(f"  sound pass {attempt + 1}: {i} LUFS, peak {pk} dB")
    if abs(i + 14.0) <= 0.5 and pk <= -1.5:
        break
    if pk > -1.5:
        tp -= 0.5
    target += -14.0 - i
print(f"short: cut at {CUT} s + {card_len:.0f} s end card -> {OUT}")
