# ============================================================
# 04a FIX BOOSTED START: bring a clip that his phone app boosted back to match the rest of his voice
# What : for the first END seconds (the clip the app boosted), in TWO steps around the cleaner (04b):
#        pre  (on face48k_raw.wav, before 04b)
#          1. level  the voiced parts are set to the same average level as the rest (not a fixed number of dB:
#                    a clipped voice is quieter than it looks, so a fixed -21.4 dB left it 3.6 dB too quiet)
#          2. noise  one extra gentle noise pass on the clip only (the app boosted the room noise too)
#          3. joint  a 12 ms fade out and in at END, where the app spliced the two clips
#        post (on face48k_clean.wav, after 04b)
#          4. tone   a smooth EQ (within +-6 dB) that gives the clip the same overall tone as the rest of HIS OWN
#                    recording (the chopped, clipped waveform adds harsh high harmonics), and a last level match
# Why  : his note, 2026-11-26: "I can hear a voice breaking in the background ... the first 0 to 28 seconds, the
#        decibel to reduce to match the other one". On life video 1 the raw waveform in that clip is hard-clipped
#        (up to a third of the samples at full scale), so the distortion is in the recording itself.
#        Tone is matched AFTER the cleaner because the cleaner changes a loud clipped clip and a quiet clean one
#        differently (matching before it left the clip 5 dB duller than the rest).
# Use  : python3 04a_fix_boosted_start.py pre  [END_SECONDS=30.55]   then 04b, then
#        python3 04a_fix_boosted_start.py post [END_SECONDS=30.55]   then 04c
#        (04b_clean_voice.py runs both for you with --boosted-start END)
# Out  : face48k_raw.wav / face48k_clean.wav fixed in place; face48k_raw_before_fix.wav and face48k_clean_before_fix.wav keep the originals
# Never: never change his voice: no pitch, no formant, no effects. The EQ only brings the clipped clip's tone in line
#        with his own unclipped voice from the same recording. Clipping cannot be fully undone: say so to him.
# ============================================================
import os, shutil, subprocess, sys, wave
import numpy as np
from scipy.signal import firwin2, fftconvolve

MODE = sys.argv[1] if len(sys.argv) > 1 else "pre"
END = float(sys.argv[2]) if len(sys.argv) > 2 else 30.55
MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models", "sh.rnnn")


def load(p):
    w = wave.open(p); sr = w.getframerate()
    return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768, sr


def save(p, a, sr):
    with wave.open(p, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())


def voiced_db(a, sr):
    hop = sr // 100; n = len(a) // hop
    d = 20 * np.log10(np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    return d, d > np.percentile(d, 95) - 14, hop


def avg_spectrum(a, sr, mask, hop):
    win = sr // 20; acc = None; cnt = 0
    for i in np.where(mask)[0][::3]:
        s = a[i * hop:i * hop + win]
        if len(s) < win: continue
        P = np.abs(np.fft.rfft(s * np.hanning(win))) ** 2
        acc = P if acc is None else acc + P; cnt += 1
    return acc / max(cnt, 1), np.fft.rfftfreq(win, 1 / sr)


def band_db(P, f, centres):
    return np.array([10 * np.log10(P[(f >= c / 2 ** (1 / 6)) & (f < c * 2 ** (1 / 6))].mean() + 1e-20) for c in centres])


SRC = "face48k_raw.wav" if MODE == "pre" else "face48k_clean.wav"
BAK = "face48k_raw_before_fix.wav" if MODE == "pre" else "face48k_clean_before_fix.wav"
x, sr = load(SRC)
if not os.path.exists(BAK): shutil.copy(SRC, BAK)
e = int(END * sr); head = x[:e].copy(); ref = x[e + sr // 2:e + 60 * sr + sr // 2]
dh, vh, hop = voiced_db(head, sr); dr, vr, _ = voiced_db(ref, sr)
gain_db = float(dr[vr].mean() - dh[vh].mean()); head *= 10 ** (gain_db / 20)

if MODE == "pre":
    # --- 2. one extra gentle noise pass on the clip only ---
    save("tmp_head.wav", head, sr)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "tmp_head.wav", "-af", f"arnndn=m={MODEL}:mix=0.8,afftdn=nr=10:nf=-50", "tmp_head2.wav"], check=True)
    head2, _ = load("tmp_head2.wav"); head2 = np.concatenate([head2, np.zeros(max(0, e - len(head2)), np.float32)])[:e]
    d2, v2, _ = voiced_db(head2, sr); head2 *= 10 ** (float(dr[vr].mean() - d2[v2].mean()) / 20)
    for p in ("tmp_head.wav", "tmp_head2.wav"): os.remove(p)
    # --- 3. joint ---
    n = int(0.012 * sr); out = np.concatenate([head2, x[e:]]).astype(np.float32)
    out[e - n:e] *= np.linspace(1, 0, n); out[e:e + n] *= np.linspace(0, 1, n)
    save(SRC, out, sr)
    dh2, vh2, _ = voiced_db(out[:e], sr)
    print(f"pre: clip 0 to {END} s level {gain_db:+.1f} dB, one extra noise pass; voiced average {dh[vh].mean():.1f} -> {dh2[vh2].mean():.1f} dB (rest {dr[vr].mean():.1f})")
else:
    # --- 4. tone: smooth EQ from the average spectra (1/3-octave, 150 Hz to 10 kHz, within +-6 dB) ---
    Ph, f = avg_spectrum(head, sr, vh, hop); Pr, _ = avg_spectrum(ref, sr, vr, hop)
    centres = 150 * 2 ** (np.arange(0, 6.2, 1 / 3))
    diff = np.clip(band_db(Pr, f, centres) - band_db(Ph, f, centres), -6, 6)
    diff = np.convolve(np.pad(diff, 1, mode="edge"), [0.25, 0.5, 0.25], "valid")
    freqs = np.concatenate([[0], [centres[0] / 1.5], centres, [centres[-1] * 1.3, sr / 2]]); gains = np.concatenate([[0], [0], diff, [0, 0]])
    fir = firwin2(2049, freqs / (sr / 2), 10 ** (gains / 20)); h2 = fftconvolve(x[:e], fir, mode="same").astype(np.float32)
    d2, v2, _ = voiced_db(h2, sr); h2 *= 10 ** (float(dr[vr].mean() - d2[v2].mean()) / 20)          # last level match
    out = np.concatenate([h2, x[e:]]).astype(np.float32)             # the joint was already faded in the pre step
    save(SRC, out, sr)
    dh2, vh2, _ = voiced_db(out[:e], sr)
    print(f"post: tone EQ within +-6 dB (largest {np.abs(diff).max():.1f} dB); voiced average {dh[vh].mean():.1f} -> {dh2[vh2].mean():.1f} dB (rest {dr[vr].mean():.1f})")
