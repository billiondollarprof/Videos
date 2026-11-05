---
name: speed-change
description: Make Anthony's speech faster or slower (pitch kept), with picture, captions, B-roll and sound effects staying in step. Use when he says the video is slow, "speed it up a bit", "too fast", or names a speed like 1.1 or 1.2.
---

# Speed change

Cheap on purpose: no new transcription, no new cut list. Only the build steps run again.

## Defaults
- "Speed it up a bit" or "it's slow" = **1.1** (his choice on video 1, 2026-11-05).
- "A bit more" = the current speed + 0.05. "Too fast" = the current speed - 0.05.
- Never above 1.25 without asking: words start to blur and the lips look wrong.

## Steps
1. Set `"speed"` in the project's `project.json`.
2. `python3 ../../pipeline/09_build_tracks.py` (cuts, speed and status bar crop in one pass;
   about 6 minutes for a 9 minute recording). The face, screen and voice come out exactly
   the same length. If not, stop.
3. `python3 ../../pipeline/09b_face_track.py face_cut.mp4 remotion/src/faceTrack.json`
4. `python3 ../../pipeline/09c_soft_background.py face_cut.mp4 face_soft.mp4`, then use
   `face_soft.mp4` as the face video in `remotion/public/face_cut.mp4`.
5. `python3 ../../pipeline/10_captions.py`. Every caption, segment, step label and sound
   cue is tied to his words, so they all move with the new speed. Nothing is re-timed by hand.
6. Rebuild any B-roll clip whose slot changed length (its slot is in `data.json`
   `moments.segments`).
7. Stills, render and finish as in `vertical-edit` steps 8 to 11.
8. Tell him the new length.

## Why it works this way
Speed is applied in the same pass as the cuts (`setpts` on the picture, `atempo` on the
voice, which keeps the pitch). Speeding the finished video instead would re-encode it
twice and let the sound effects drift off their moments.
