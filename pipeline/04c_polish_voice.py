# ============================================================
# 04c POLISH VOICE: take the last of the background noise out of his cleaned voice
# What : a second, gentle pass over face48k_clean.wav (from 04b):
#        1. adeclick   mends small clicks (lip smacks, tiny crackles) by redrawing a few samples
#        2. afftdn     a light spectral noise remover (nr=9, a little: more sounds watery)
#        3. agate      a soft downward expander: between words the noise drops by up to 20 dB,
#                      but a word is never cut (slow release, soft knee)
#        4. delay      the chain delays the sound by 25 ms: measured and removed, so cuts do not move
#        5. gain       puts his voice back to the level it had before, so nothing sounds quieter
# Why  : after the final loudness step the pauses come up by about 7 dB, and the low rumble
#        (120 to 250 Hz) in the pauses became audible, with small crackles here and there
#        (his note, 2026-11-07: "an underlying sound ... a little cracks"). On voiceover 1 this took
#        the pauses from -64 dB to -83 dB and moved the voice's tone by 4 Hz out of 505.
# Use  : python3 04c_polish_voice.py                  (reads face48k_clean.wav, writes face48k_polish.wav)
# Out  : face48k_polish.wav (the voice to cut and mix), a printed before and after
# Never: never change the voice: no pitch, no formant, no EQ here. If the voice sounds watery or
#        swallowed, lower nr (9) or raise the gate range. Never cut a word: check the gate by ear.
#        The cutter still finds the words on face48k_clean.wav (same timing), so cuts do not move.
# ============================================================
import subprocess
import wave

import numpy as np

SRC, DST = "face48k_clean.wav", "face48k_polish.wav"


def load(p):
    w = wave.open(p); sr = w.getframerate()
    return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32), sr


def measure(p):
    """Returns (pause floor in dB, average level of the voiced parts in dB, voice centre in Hz)."""
    x, sr = load(p); hop = sr // 100; n = len(x) // hop
    db = 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)) / 32768 + 1e-9)
    return db, x, sr


# --- 1. The polish chain ---
chain = ("adeclick=w=55:o=75:a=2:t=2:b=2,"
         "afftdn=nr=9:nf=-62,"
         "agate=threshold=0.0035:ratio=3:attack=6:release=160:range=0.1:knee=3")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-af", chain, "tmp_polish.wav"], check=True)

# --- 2. The chain delays the sound a little (afftdn: 25 ms). Measure it and take it out. ---
db0, x0, sr = measure(SRC); db1, x1, _ = measure("tmp_polish.wav")


def lag_of(a, b):
    """How many samples b is later than a, by cross-correlation of a stretch from the middle."""
    st = len(a) // 2; A = a[st:st + sr * 8]; B = b[st:st + sr * 8]
    n = 1 << int(np.ceil(np.log2(len(A) * 2)))
    c = np.fft.irfft(np.fft.rfft(A, n) * np.conj(np.fft.rfft(B, n))); c = np.concatenate([c[-len(A) + 1:], c[:len(A)]])
    return -(int(np.argmax(c)) - (len(A) - 1))


lag = lag_of(x0, x1)
x1 = np.concatenate([x1[lag:], np.zeros(lag, np.float32)]) if lag > 0 else x1
assert abs(lag_of(x0, x1)) <= 2, "STOP: could not line the polished voice up with the clean one"

# --- 3. Put the voice back to its old level (the cleaner takes about 1 dB off) ---
ref = db0 > np.percentile(db0, 15) + 0.35 * (np.percentile(db0, 95) - np.percentile(db0, 15))   # the voiced parts
hop = sr // 100; n = min(len(db0), len(x1) // hop)
db1 = 20 * np.log10(np.sqrt((x1[:n * hop].reshape(n, hop) ** 2).mean(1)) / 32768 + 1e-9)   # level after lining up
gain = float(db0[:n][ref[:n]].mean() - db1[:n][ref[:n]].mean())
y = np.clip(x1 * 10 ** (gain / 20), -32768, 32767).astype(np.int16)
with wave.open(DST, "w") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(y.tobytes())

# --- 4. Report ---
db2, _, _ = measure(DST)
print(f"delay of {lag} samples removed, gain restored {gain:+.2f} dB")
for name, d in (("before", db0), ("after", db2)):
    print(f"  {name}: pause floor {np.percentile(d, 10):6.1f} dB   voiced average {d[ref].mean():6.1f} dB")
