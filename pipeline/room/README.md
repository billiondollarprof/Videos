# Room pipeline (life video 1, 2026-11-25)

For a talking video filmed in one place, where his room is replaced by his own ChatGPT picture of
the empty room, made calm (option B, chosen by him). Run from `projects/<video>/`, in this order:

1. `plate.py`: the real empty room, from frames where he does not cover each part (for un-mixing the edge).
2. `room_full.py T0 DUR OUT SKIP`: the room behind him for the whole video, edge from Robust Video
   Matting (models/rvm_mobilenetv3.torchscript, torch from PyPI). About 0.6 frames a second per run:
   run two halves side by side, the second starting 1 s early with SKIP 1.0 (see the Room reader in assemble.py).
3. `face_track.py`: his face centre in every frame, mirrored, smoothed (close shots).
4. `edl.py`: approved cuts at the quietest 10 ms, pauses shortened only where truly quiet and no word inside,
   reaction clips with their own sound after the sentence they answer.
5. `cut_voice.py`: his cleaned voice (04b, 04c) cut to the edit list, clips' sound in their slots.
6. `assemble.py`: one pass: shots (wide with the iPad, close on his face), picture cards, clips as cards,
   captions (his spelling, `FIX` for words checked by listening), title, camera flashes, darker corners.
   `STILLS=1.5,17.6 python3 assemble.py` writes check stills only.
7. `mix.py`: sound effects on cues (6 ms soft start, or AAC overshoots on the shutter click), gain to
   -14 LUFS, limiter; measure the delivered file. Then `12_check_final.py`.

The paths, word numbers and times inside are video 1's: change them for the next video.
