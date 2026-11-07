# ============================================================
# VO 04 MIX: voice + pops for the pictures (+ music only with --music), then loudness for the platforms
# What : - a picture arrives: a pop. Back to the post: a lower pop. No whooshes, no swipes.
#        - hook: one camera shutter. End card: shutter and a warm tick.
#        - music only if asked (--music): music/make_music.py, 20 dB under the voice, ducked while he
#          speaks. Off by default: the first bed sounded "ting ting, fake" (his note, 2026-11-07).
#        - two-pass loudnorm to -14 LUFS, true peak under -1.5 dB, measured on the AAC file
# In   : voice_cut.wav, video_silent.mp4, shots.json, music.wav   Out: vo_final.mp4
# Never: never change the voice itself. His voice is always the loudest thing.
# ============================================================
import json, os, subprocess, sys

SH = json.load(open("shots.json")); S = "/home/user/videos/sfx/"
# --- 1. Cues: (time, file, gain in dB) ---
# Pops only, no whooshes, no swipes (his note, 2026-11-07: "I can hear whoosh whoosh, no pop").
# A picture arrives: a pop. It goes back to the post: a lower pop. One camera shutter on the hook and
# one on the end card, with a warm tick. The pops must be easy to hear over speech: check below.
cues = [(0.08, S + "camera-shutter.wav", -18)]
for s in SH[1:]:
    if s["kind"] == "end":
        cues += [(s["s"] + 0.05, S + "camera-shutter.wav", -18), (s["s"] + 0.6, S + "tick-warm.wav", -14)]
    elif s.get("ret"):
        cues += [(s["s"] + 0.05, S + "pop-low.wav", -5)]
    else:
        cues += [(s["s"] + 0.12, S + "pop-soft.wav", -4)]

# --- 2. Mix: voice, effects, and music only if asked (python3 vo_04_mix.py --music) ---
USE_MUSIC = "--music" in sys.argv and os.path.exists("music.wav")
inp = ["-i", "voice_cut.wav"] + (["-i", "music.wav"] if USE_MUSIC else []); base = len(inp) // 2; f = []
for i, (t, p, g) in enumerate(cues):
    inp += ["-i", p]; f.append(f"[{i + base}]aresample=48000,aformat=channel_layouts=stereo,volume={g}dB,adelay={int(t * 1000)}:all=1[c{i}]")
if USE_MUSIC:
    f.append("[0]aresample=48000,aformat=channel_layouts=stereo,asplit=2[v][key]")
    f.append("[1]aresample=48000,volume=-20dB[mu]")
    f.append("[mu][key]sidechaincompress=threshold=0.03:ratio=4:attack=40:release=400[duck]")
    f.append("[v][duck]" + "".join(f"[c{i}]" for i in range(len(cues))) + f"amix=inputs={len(cues) + 2}:normalize=0:duration=longest[m]")
else:
    f.append("[0]aresample=48000,aformat=channel_layouts=stereo[v]")
    f.append("[v]" + "".join(f"[c{i}]" for i in range(len(cues))) + f"amix=inputs={len(cues) + 1}:normalize=0:duration=longest[m]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(f), "-map", "[m]", "-t", str(SH[-1]["e"]), "mix.wav"], check=True)

# --- 3. Loudness: measure, then apply in one linear pass ---
r = subprocess.run(["ffmpeg", "-i", "mix.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
af = (f"loudnorm=I=-14:TP=-2.6:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample=48000")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "video_silent.mp4", "-i", "mix.wav", "-af", af, "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-crf", "22", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-movflags", "+faststart", "vo_final.mp4"], check=True)
r = subprocess.run(["ffmpeg", "-i", "vo_final.mp4", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
print(r[r.rindex("Summary"):])
