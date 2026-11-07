# ============================================================
# SOUND EFFECTS, MADE IN CODE
# What : builds a small, soft sound-effect palette as WAV files in this folder.
# Why  : sounds made here belong to us outright. No licence, no credit, no account.
#        The palette follows one rule from Nate Herk's editing playbook (MIT licence):
#        soft taps, dry clicks, paper and air. No laser zaps, no pitch-drop plops.
# Use  : python3 make_sfx.py      (writes the files next to this script)
# Never: never make a sound louder than the voice will sit. Levels are set at mix time.
# ============================================================
import os
import wave

import numpy as np

SR = 48000                                   # samples per second
HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)               # fixed seed, so every run makes the same sounds


# --- 1. Small helpers ---
def save(name, x):
    """Normalise to a safe peak and write a 16-bit mono WAV."""
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.7
    with wave.open(os.path.join(HERE, name), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def noise(sec):
    return rng.standard_normal(int(sec * SR))


def lowpass(x, cutoff):
    """One-pole low-pass filter (softens a sound by removing high hiss)."""
    a = np.exp(-2 * np.pi * cutoff / SR); y = np.zeros_like(x); s = 0.0
    for i, v in enumerate(x):
        s = (1 - a) * v + a * s; y[i] = s
    return y


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


def env(n, attack, release):
    """A volume shape: rises over `attack` seconds, then dies away over `release`."""
    t = np.arange(n) / SR
    up = np.clip(t / max(attack, 1e-4), 0, 1)
    down = np.exp(-np.maximum(t - attack, 0) / release)
    return up * down


# --- 2. Air whoosh: for a real movement on screen (the face shrinking, a card sliding) ---
def whoosh(sec=0.55, lo=300, hi=2600):
    x = noise(sec); n = len(x)
    # sweep a soft band of noise upward, then back down, like air passing
    t = np.linspace(0, 1, n)
    centre = lo + (hi - lo) * np.sin(np.pi * t) ** 1.5
    out = np.zeros(n); block = 480
    for i in range(0, n, block):
        seg = x[i:i + block]
        c = centre[i]
        out[i:i + block] = highpass(lowpass(seg, c * 1.4), c * 0.6)
    shape = np.sin(np.pi * t) ** 2          # swell in and out
    return out * shape


# --- 3. Soft tap: a card or label landing ---
def soft_tap():
    n = int(0.12 * SR); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * 170 * t) * env(n, 0.002, 0.03)
    knock = lowpass(noise(0.12), 1800) * env(n, 0.0005, 0.008)
    return body + 0.5 * knock


# --- 4. Warm tick: a tip or a success, one short tone (not a chime) ---
def warm_tick():
    n = int(0.35 * SR); t = np.arange(n) / SR
    tone = (np.sin(2 * np.pi * 660 * t) + 0.35 * np.sin(2 * np.pi * 990 * t)) * env(n, 0.004, 0.09)
    tap = 0.25 * soft_tap()                  # a small tap under the tone gives it a start
    tap = np.pad(tap, (0, n - len(tap)))     # make the tap as long as the tone
    return tone + tap


# --- 5. Camera shutter: two mechanical clicks (curtain open, curtain close) ---
def shutter():
    n = int(0.22 * SR); x = np.zeros(n)
    def clack(at, bright, level):
        m = int(0.03 * SR); s = int(at * SR)
        c = highpass(noise(0.03), bright) * env(m, 0.0003, 0.004)
        c += 0.6 * np.sin(2 * np.pi * 2300 * np.arange(m) / SR) * env(m, 0.0002, 0.003)
        x[s:s + m] += level * c
    clack(0.000, 1500, 1.0)                  # first curtain
    clack(0.075, 1100, 0.8)                  # second curtain, a little duller
    thump = np.sin(2 * np.pi * 95 * np.arange(n) / SR) * env(n, 0.001, 0.02)
    return x + 0.25 * thump


# --- 6. Paper: a quick page flick, for a list or a document appearing ---
def paper():
    x = highpass(noise(0.18), 2500); n = len(x)
    grain = (rng.random(n) < 0.02) * rng.standard_normal(n) * 3     # little crackles
    return (x * 0.5 + grain) * env(n, 0.01, 0.05)


# --- 7. Pops: for a picture that appears or goes away in a voiceover video (no face on camera) ---
# A pop is a short sine that starts high and falls fast, with a tiny click on top: a soft bubble.
def pop(f_start=260, f_end=820, glide=0.012, sec=0.2, tail=0.045):
    """A bubble pop: a round tone that rises fast then dies, a soft thump under it and a tiny click.
    Loud enough to hear over speech once mixed at about -4 dB (his note, 2026-11-07: "I can't hear any pop")."""
    n = int(sec * SR); t = np.arange(n) / SR
    f = f_end + (f_start - f_end) * np.exp(-t / glide)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.0015, tail)
    thump = np.sin(2 * np.pi * 110 * t) * env(n, 0.001, 0.05) * 0.5
    click = lowpass(noise(sec), 6000) * env(n, 0.0002, 0.003) * 0.35
    return body + thump + click

def swipe():
    # a very short breath of air, so the pop has a little movement around it
    x = highpass(lowpass(noise(0.2), 4200), 900); n = len(x)
    return x * np.sin(np.pi * np.linspace(0, 1, n)) ** 2


# --- 8. Make them all ---
if __name__ == "__main__":
    save("whoosh-air.wav", whoosh())
    save("whoosh-air-short.wav", whoosh(0.32, 500, 3200))
    save("tap-soft.wav", soft_tap())
    save("tick-warm.wav", warm_tick())
    save("camera-shutter.wav", shutter())
    save("paper-flick.wav", paper())
    save("pop-soft.wav", pop())                       # a picture arrives
    save("pop-low.wav", pop(190, 520, 0.012, 0.22, 0.06))      # the picture goes, back to the post
    save("swipe-soft.wav", swipe())
    print("made:", sorted(f for f in os.listdir(HERE) if f.endswith(".wav")))
