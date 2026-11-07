# ============================================================
# VO 04 MIX: voice + music + sound effects (pops for pictures), then loudness for the platforms
# What : - music (music/make_music.py) about 20 dB under the voice, and ducked a further few dB
#          while he speaks (sidechain: the voice pushes the music down)
#        - a picture arrives: soft pop + tiny air swipe. Back to the post: a lower pop.
#        - hook: one camera shutter. End card: whoosh, shutter and a warm tick
#        - two-pass loudnorm to -14 LUFS, true peak under -1.5 dB, measured on the AAC file
# In   : voice_cut.wav, video_silent.mp4, shots.json, music.wav   Out: vo_final.mp4
# Never: never change the voice itself. His voice is always the loudest thing.
# ============================================================
import json, subprocess

SH = json.load(open("shots.json")); S = "/home/user/videos/sfx/"
# --- 1. Cues: (time, file, gain in dB) ---
# Voiceover sounds are pops, not whooshes (his note, 2026-11-07: there is no camera, the pictures
# are graphics). A picture arrives: soft pop with a tiny air swipe. It goes back to the post: a
# lower, quieter pop. One camera shutter on the hook, and the whoosh and tick on the end card.
cues = [(0.08, S + "camera-shutter.wav", -20)]
for s in SH[1:]:
    if s["kind"] == "end":
        cues += [(s["s"], S + "whoosh-air.wav", -16), (s["s"] + 0.8, S + "tick-warm.wav", -17), (s["s"] + 0.1, S + "camera-shutter.wav", -20)]
    elif s.get("ret"):
        cues += [(s["s"] + 0.05, S + "pop-low.wav", -21)]
    else:
        cues += [(max(0, s["s"] - 0.02), S + "swipe-soft.wav", -26), (s["s"] + 0.18, S + "pop-soft.wav", -18)]

# --- 2. Mix: voice, ducked music, effects ---
inp = ["-i", "voice_cut.wav", "-i", "music.wav"]; f = []
for i, (t, p, g) in enumerate(cues):
    inp += ["-i", p]; f.append(f"[{i + 2}]aresample=48000,aformat=channel_layouts=stereo,volume={g}dB,adelay={int(t * 1000)}:all=1[c{i}]")
f.append("[0]aresample=48000,aformat=channel_layouts=stereo,asplit=2[v][key]")
f.append("[1]aresample=48000,volume=-20dB[mu]")
f.append("[mu][key]sidechaincompress=threshold=0.03:ratio=4:attack=40:release=400[duck]")
f.append("[v][duck]" + "".join(f"[c{i}]" for i in range(len(cues))) + f"amix=inputs={len(cues) + 2}:normalize=0:duration=longest[m]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(f), "-map", "[m]", "-t", str(SH[-1]["e"]), "mix.wav"], check=True)

# --- 3. Loudness: measure, then apply in one linear pass ---
r = subprocess.run(["ffmpeg", "-i", "mix.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
af = (f"loudnorm=I=-14:TP=-2.0:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample=48000")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "video_silent.mp4", "-i", "mix.wav", "-af", af, "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-crf", "22", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-movflags", "+faststart", "vo_final.mp4"], check=True)
r = subprocess.run(["ffmpeg", "-i", "vo_final.mp4", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
print(r[r.rindex("Summary"):])
