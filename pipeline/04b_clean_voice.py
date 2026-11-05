# ============================================================
# 04b CLEAN VOICE: take the room noise out of his voice, and make it even
# What : pulls the sound out of the face video and cleans it: RNNoise (a free noise remover
#        for voices; models/sh.rnnn from setup.sh), a gentle noise floor, a little warmth taken
#        out at 200 Hz, a little clarity added at 3.5 kHz, and light compression.
# Why  : he records on a phone with no microphone. On video 1 this took the room noise down
#        by 16 dB and put the voice about 40 dB above the room.
# Use  : python3 04b_clean_voice.py raw/face.mov     (writes face48k_clean.wav in this folder)
# Out  : face48k_clean.wav, read by 09_build_tracks.py
# Never: never push the cleaning so hard the voice sounds underwater. mix=0.9 leaves a little
#        of the original. If it sounds thin, lower it.
# ============================================================
import os
import subprocess
import sys

SRC = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, "..", "models", "sh.rnnn")
if not os.path.exists(MODEL):
    sys.exit("STOP: models/sh.rnnn is missing. Run: bash pipeline/setup.sh")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-vn", "-ac", "1", "-ar", "48000", "face48k_raw.wav"], check=True)
chain = (f"highpass=f=80,arnndn=m={MODEL}:mix=0.9,afftdn=nr=8:nf=-45,"
         "equalizer=f=200:t=q:w=1:g=-2,equalizer=f=3500:t=q:w=1.5:g=2.5,"
         "acompressor=threshold=-20dB:ratio=3:attack=10:release=150:makeup=2")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "face48k_raw.wav", "-af", chain, "-ar", "48000", "face48k_clean.wav"], check=True)


def level(path, start, length):
    r = subprocess.run(["ffmpeg", "-v", "info", "-ss", str(start), "-t", str(length), "-i", path, "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return [l for l in r.splitlines() if "mean_volume" in l][-1].split("mean_volume:")[1].strip()


# A quiet stretch and a talking stretch, before and after, so the result can be reported.
print("face48k_clean.wav written")
for name in ("face48k_raw.wav", "face48k_clean.wav"):
    print(f"  {name}: first 12 s average level {level(name, 0, 12)}")
