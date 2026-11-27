# ============================================================
# VLOG MIX: voice + a clip's own sound + soft effects, loudness for the platforms, and the final MP4
# What : - the clip sound(s) in vlog_shots.py SOUND_CLIPS play in the gap left in the voice (cleaned, levelled)
#        - effects follow a visible action: a soft air whoosh when a phone or TV arrives, a soft tap on each
#          tap ring, a camera shutter on a flash, shutter and a warm tick on the last shot. NOTHING on a caption
#          (his note, 2026-11-26: the caption pop distracted him)
#        - music only if he gives music.wav and asks (--music)
#        - two-pass loudnorm to -14 LUFS, true peak under -1.5 dB, measured on the AAC file
#        - the picture is NOT re-encoded: the finished pieces are joined, so the audio is simply added
# In   : voice_final.wav, video_silent.mp4, vlog_shots.py   Out: vlog_final.mp4
# Never: never change the voice itself. His voice is always the loudest thing.
# ============================================================
import importlib.util, json, os, subprocess, sys
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sfx") + "/"
spec = importlib.util.spec_from_file_location("vlog_shots", "vlog_shots.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
SH = sorted(m.SHOTS, key=lambda x: x["t0"]); LENGTH = m.LENGTH
DEVICE = ("phone", "phonevid", "tv", "screen", "wide")

# --- 1. Cues: (time, file, gain in dB) ---
cues = [(0.10, S + "camera-shutter.wav", -17)]
for i, sh in enumerate(SH):
    prev = SH[i - 1]["kind"] if i else None
    if sh["kind"] in DEVICE and prev not in DEVICE: cues.append((sh["t0"] + 0.02, S + "whoosh-air-short.wav", -21))
    if sh.get("flash") and i: cues.append((sh["t0"] + 0.05, S + "camera-shutter.wav", -19))
    for _, ti, tap in sh.get("screens", []):
        if tap: cues.append((ti - 0.30, S + "tap-soft.wav", -14))
cues += [(SH[-1]["t0"] + 0.6, S + "tick-warm.wav", -15)]

# --- 2. The clip sounds, cleaned and levelled ---
inp = ["-i", "voice_final.wav"]; f = []; n_in = 1                 # n_in = how many inputs are listed so far (input 0 is the voice)
for i, c in enumerate(m.SOUND_CLIPS):
    inp += ["-ss", str(c["ss"]), "-t", str(c["dur"]), "-i", c["file"]]
    f.append(f"[{n_in}]aresample=48000,aformat=channel_layouts=stereo,highpass=f=100,afftdn=nr=10:nf=-45,volume={c['gain']}dB,"
             f"afade=t=in:d=0.04,afade=t=out:st={c['dur'] - 0.08}:d=0.08,adelay={int(c['t'] * 1000)}:all=1[k{i}]")
    n_in += 1
nk = len(m.SOUND_CLIPS)
base = n_in
for i, (t, p, g) in enumerate(cues):
    inp += ["-i", p]; f.append(f"[{i + base}]aresample=48000,aformat=channel_layouts=stereo,volume={g}dB,adelay={int(t * 1000)}:all=1[c{i}]")
f.append("[0]aresample=48000,aformat=channel_layouts=stereo[v]")
labels = "".join(f"[k{i}]" for i in range(nk)) + "".join(f"[c{i}]" for i in range(len(cues)))
f.append(f"[v]{labels}amix=inputs={1 + nk + len(cues)}:normalize=0:duration=longest[m]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(f), "-map", "[m]", "-t", str(LENGTH), "mix.wav"], check=True)

# --- 3. Loudness: hold the voice's few loud peaks down softly, measure, add the exact gain to reach -14 LUFS, then a last limiter at -1.5 dB ---
LIM = "alimiter=limit=0.5:attack=3:release=90:level=disabled"
r = subprocess.run(["ffmpeg", "-i", "mix.wav", "-af", LIM + ",ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float(r[r.rindex("I:"):].split()[1])
gain = -13.1 - I                                   # aims a little above -14: the encoder and the last limiter take about 0.4 dB
lim_out = 0.78
for attempt in range(3):                                # the AAC encoder can add a little peak: tighten the last limiter until the true peak is under -1.5 dB
    af = f"{LIM},volume={gain:.2f}dB,alimiter=limit={lim_out:.2f}:attack=2:release=60:level=disabled,aresample=48000"
    print(f"measured {I:.1f} LUFS, gain {gain:+.2f} dB, last limiter {lim_out:.2f}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "video_silent.mp4", "-i", "mix.wav", "-af", af, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", "vlog_final.mp4"], check=True)
    r = subprocess.run(["ffmpeg", "-i", "vlog_final.mp4", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    summary = r[r.rindex("Summary"):]
    tp = float(summary[summary.index("Peak:"):].split()[1])
    if tp <= -1.5: break
    lim_out -= 0.06
print(summary)
