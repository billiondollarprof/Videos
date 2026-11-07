# ============================================================
# MAKE MUSIC: our own background music bed, built from code, so there is never a licence question
# What : a steady groove in A minor (Am F C G), 92 beats a minute: soft kick, light clap, hi-hats,
#        sub bass, a warm pad and a soft pluck arpeggio. Fades in and out. Any length.
# Why  : without music the voiceover did not flow (his note, 2026-11-07). TikTok music is added
#        by him in the app; this bed is for the file itself (Shorts, Reels, YouTube).
# Use  : python3 make_music.py <seconds> out.wav [bpm]
# Never: never louder than the voice: the mix (vo_04_mix.py) sits it about 18 dB under and ducks it.
# ============================================================
import sys, wave
import numpy as np

DUR = float(sys.argv[1]); OUT = sys.argv[2]; BPM = float(sys.argv[3]) if len(sys.argv) > 3 else 92
SR = 48000; beat = 60 / BPM; N = int(DUR * SR); t_all = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)

def put(sig, at, pan=0.0):
    """Add a sound at a time (seconds), panned -1 (left) .. 1 (right)."""
    i = int(at * SR); j = min(N, i + len(sig))
    if i >= N: return
    L[i:j] += sig[:j - i] * (1 - pan) / 2 * 2 ** 0.5; R[i:j] += sig[:j - i] * (1 + pan) / 2 * 2 ** 0.5

def env(n, a=0.005, d=0.3):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / d)

# --- 1. Drums ---
def kick():
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 45 + 90 * np.exp(-t / 0.04); return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.16) * 0.9
def clap():
    n = int(0.3 * SR); return rng.normal(0, 1, n) * env(n, 0.001, 0.07) * 0.18
def hat(open_=False):
    n = int(0.2 * SR); s = rng.normal(0, 1, n); s = np.diff(s, prepend=0)   # bright noise
    return s * env(n, 0.001, 0.09 if open_ else 0.025) * 0.06

# --- 2. Notes ---
def note(freq, dur, kind):
    n = int(dur * SR); t = np.arange(n) / SR
    if kind == "pad":
        s = sum(np.sin(2 * np.pi * freq * m * t + m) / m for m in (1, 2, 3)) * 0.5
        s += 0.5 * np.sin(2 * np.pi * freq * 1.003 * t)
        return s * np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.6) * 0.07
    if kind == "bass":
        return np.sin(2 * np.pi * freq * t) * env(n, 0.01, 0.5) * 0.35
    if kind == "pluck":
        s = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t)
        return s * env(n, 0.003, 0.18) * 0.07
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
CHORDS = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]      # Am F C G
bar = 4 * beat; nbars = int(DUR / bar) + 1
for b in range(nbars):
    t0 = b * bar; ch = CHORDS[b % 4]
    for m in ch: put(note(hz(m), bar + 0.3, "pad"), t0, pan=(m % 3 - 1) * 0.4)
    put(note(hz(ch[0] - 24), bar * 0.9, "bass"), t0)
    put(note(hz(ch[0] - 24), beat * 0.9, "bass"), t0 + 2.5 * beat)
    if b >= 2:                                                           # the pluck joins after 2 bars
        arp = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 12]
        for k in range(8): put(note(hz(arp[k % 4]), 0.4, "pluck"), t0 + k * beat / 2, pan=0.5 if k % 2 else -0.5)
    for k in range(4):
        if b >= 1 and k in (0, 2): put(kick(), t0 + k * beat)
        if b >= 1 and k in (1, 3): put(clap(), t0 + k * beat)
        for half in (0, 0.5): put(hat(half == 0.5 and k == 3), t0 + (k + half) * beat, pan=0.3)

# --- 3. Fade, level, write ---
fade = np.minimum(1, t_all / 2.0) * np.minimum(1, (DUR - t_all) / 2.5)
y = np.stack([L, R], 1) * fade[:, None]; y = y / np.abs(y).max() * 0.7
w = wave.open(OUT, "w"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((y * 32767).astype(np.int16).tobytes()); w.close()
print(f"music {DUR:.1f} s at {BPM:.0f} bpm -> {OUT}")
