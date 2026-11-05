---
name: sound-mix
description: Clean the voice, place sound effects on visible actions, mix, set loudness for TikTok and Shorts, add the camera flash, and make the final MP4. Use after the silent render, or when Anthony gives a note about sound.
---

# Sound

## Voice (before the cut, done once per video: `python3 ../../pipeline/04b_clean_voice.py raw/face.mov`)
`ffmpeg -i <face video> -vn -ac 1 -ar 48000 voice48k_raw.wav`, then clean it with
RNNoise (a free voice noise remover; the model file is `sh.rnnn` from
GregorR/rnnoise-models), a gentle noise floor, a little warmth taken out at 200 Hz,
a little clarity at 3.5 kHz, and light compression:

`highpass=f=80,arnndn=m=sh.rnnn:mix=0.9,afftdn=nr=8:nf=-45,equalizer=f=200:t=q:w=1:g=-2,equalizer=f=3500:t=q:w=1.5:g=2.5,acompressor=threshold=-20dB:ratio=3:attack=10:release=150:makeup=2`

Video 1: room noise went down 16 dB, the voice ended up 40 dB above the room.

## Sound effects
- The palette is in `sfx/`. `make_sfx.py` makes our own (whooshes, taps, a warm tick,
  paper, a camera shutter). The mouse click is CC0 from Wikimedia Commons.
- One sound per **visible** action. Not every cut. Vary them.
- The cue list is in `11_finish.py`, section 1. Change it there, not by hand.

## Finish
`python3 ../../pipeline/11_finish.py video_silent.mp4 voice_cut_raw.wav final.mp4 remotion/src/data.json`
(`finish_all.sh` runs it after the render, then `12_check_final.py`.)

It mixes in stereo, sets -14 LUFS (the loudness unit the platforms use) with peaks at
or below -1.5 dB, measured on the stereo file (a mono file reads 3 dB quieter), adds
the camera flash on the end card only (never on the first frame: it washed the first frame white),
and prints the measured result. Report those numbers.

## Music
Not in the file unless he asks. TikTok and Instagram have licensed music in the app.
For long-form YouTube, YouTube Studio has a free **Audio Library**. If he asks for music
in the file, it sits 11 dB under the voice (9 to 14) and dips under speech.
