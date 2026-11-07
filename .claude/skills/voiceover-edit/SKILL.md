---
name: voiceover-edit
description: The whole job for a voiceover video (his voice only, no face video) over a post, photos and a map - cut the voice tight with real breaths, time captions, draw moving shots with light sweeps and flashes, add shutter sounds, master the loudness. Use when Anthony sends a voice recording with pictures or a screen recording to talk over.
---

# Voiceover video

Built on voiceover video 1 (2026-11-07). Scripts: `pipeline/vo_01_cut.py` to `vo_04_mix.py`.
Work in `projects/<name>/`. Never commit his voice, the script or the shot list.

1. **Get the files** (skill `drive-footage`). If a download comes back as HTML, the file is not
   shared: ask him to share the folder. Sharing it yourself may be refused.
2. **Clean the voice**: `04b_clean_voice.py`, then `01b_transcribe_fillers.py` (medium) for
   `words.json`.
3. **Under the length he asked for.** Keep the post he reads whole. Cut his own commentary first.
   List the cuts with times and words for him (skill `cut-plan`).
   - **Check every claim** in his commentary against what he gave you. Video 1: he said Benue,
     his own research said Plateau. Cut it and tell him plainly.
4. **Cut**: `vo_config.json` (copy `vo_config.example.json`), then `python3 vo_01_cut.py`.
5. **Listen for restarts after the cut.** Transcribe the cut voice with the medium model and
   **no** filler prompt (with it, Whisper invented "Obi," tokens). A gap in the raw word times
   (a word lasting 2 s) hides a false start: plot the loudness every 50 ms, find the restart,
   cut the first take, keep the second. Then cut again.
6. **Captions**: write his words in `script.txt` (the post's own wording where he reads it,
   quotes where he means someone, numbers as he said them). Transcribe the cut voice with word
   times (`cut_words.json`). If Whisper calls the opening laughter, time the first words by hand
   in `vo_opening.json`. `python3 vo_02_captions.py`. Expect 90% matched or more.
7. **Pictures**:
   - Post: grab stills from the screen recording, crop the status bar, find the y of each key
     line with `tesseract <still> - --psm 4 tsv`.
   - Photos: no faces of private people, no watermarks, no graphics with claims he did not make.
     A map is drawn from Natural Earth (public domain).
   - Shot list in `vo_shots.py`: one `add('<spoken phrase>', kind, file, kick=..., y=..., hl=...)`
     per shot. A shot starts when the phrase is said. A kicker is a few words in capitals.
8. **Look before rendering**: `python3 vo_03_render.py 0 <frame> <frame>` writes stills. Check
   the highlight sits on the line, text is not cut at the sides, captions are readable.
9. **Render**: `python3 vo_03_render.py` (about 10 minutes for 3 minutes).
10. **Mix**: `python3 vo_04_mix.py`. Report the loudness (-14 LUFS) and true peak (under -1.5 dB).
11. **Check**: transcribe the final with the medium model; no missing words, no repeats. Stills at
    every shot. Send it with the caption, titles and photo credits (say which licences are unknown).
