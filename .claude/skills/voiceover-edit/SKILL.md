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
   Set `end` 0.4 s after the end of his last word on the loudness plot. Check the last word is whole.
5. **Listen for restarts after the cut, at the end too** (video 1 had one in the last line).
   List every raw word longer than 0.9 s inside the kept part. Transcribe each of those spots
   on its own (`condition_on_previous_text=False`) and plot its loudness every 100 ms. Video 1
   hid two repeats this way ("deserve to know how many" said twice, a restart before "if you do
   not fix power").
   - The gaps after the cut: `silencedetect=n=-40dB:d=0.25` must find nothing.
   - Set every cut edge in a silence on the 20 ms loudness plot, never inside a word (a cut
     inside "making" left an "m" sound).
   - Listen for a sound at the joints: the breaths must be room tone, never his voice. Transcribe the cut voice with the medium model and
   **no** filler prompt (with it, Whisper invented "Obi," tokens). A gap in the raw word times
   (a word lasting 2 s) hides a false start: plot the loudness every 50 ms, find the restart,
   cut the first take, keep the second. Then cut again.
6. **Captions**: write his words in `script.txt` (the post's own wording where he reads it,
   quotes where he means someone, numbers as he said them). Transcribe the cut voice with word
   times (`cut_words.json`). If Whisper calls the opening laughter, time the first words by hand
   in `vo_opening.json`. `python3 vo_02_captions.py`. Expect 90% matched or more.
7. **Pictures** (open on a moving picture with the hook, never on the post):
   - Post: grab a still at the top and one at the bottom of the screen recording
     (`ffmpeg -ss <t> -i post.mp4 -frames:v 1 post/top.png`). `python3 vo_02b_post_lines.py
     post/top.png post/bottom.png` stitches one tall page with the phone's top bar cut off,
     and maps every word he reads to its line. Look at `post/tall.png`: no status bar, no
     floating recorder button (paint it out with `post_blank`).
   - While the post is on screen, the line he is reading is highlighted and the page scrolls so
     that line sits a third of the way down, never under the captions.
   - Photos: no faces of private people, no watermarks, no graphics with claims he did not make.
     A map is drawn from Natural Earth (public domain).
   - **Short inserts while he reads the post.** `add('<phrase>', kind, file, dur=2.6, back=True)`:
     the picture arrives on the phrase, stays about 2 to 3 s, then the video goes back to the post
     on the line he is reading. While he comments (not reading), pictures run until the next one.
   - **Commentary needs its own pictures.** Offer him 2 to 4 AI image prompts, portrait 9:16, no
     face, no text, no real person (see the prompts in `voiceover-edit/prompts.md`).
   - Shot list in `vo_shots.py`: one `add('<spoken phrase>', kind, file, kick=..., y=..., hl=...)`
     per shot. A shot starts when the phrase it illustrates is said: the candle on "kidnapped", never a sentence early.
     A kicker says only what is said in the kept voice. A kicker is a few words in capitals.
8. **Look before rendering**: `python3 vo_03_render.py 0 <frame> <frame>` writes stills. Check
   the highlight is on the line he is reading, text is not cut at the sides, captions are readable.
8a. **Music**: `python3 ../../music/make_music.py <seconds> music.wav` (our own, no licence).
9. **Render**: `python3 vo_03_render.py` (about 10 minutes for 3 minutes).
10. **Mix**: `python3 vo_04_mix.py` (pops for pictures, one shutter on the hook, whoosh and tick on the end card). Report the loudness (-14 LUFS) and true peak (under -1.5 dB).
11. **Check**: transcribe the final with the medium model; no missing words, no repeats. Stills at
    every shot. Send it with the caption, titles and photo credits (say which licences are unknown).
