---
name: vertical-edit
description: The whole job for one of Anthony's vertical talking videos (his face, often with a phone screen recording) from raw footage to the finished video, the short for Reels, Shorts and TikTok, the thumbnail and the description. Use when Anthony hands over raw footage, or asks for an edit, a short, a thumbnail or the post copy.
---

# Vertical edit

The master checklist. Each step names the skill or script that does it, so nothing is worked out
again. Work in `projects/<name>/` (git ignores it). Stop at the first step that fails and say
which. **Model tier:** the first full edit (cut choices, layout, pace) is worth Opus. Changes after
he has watched a draft are Sonnet, and most need no re-render (see the end).

## 0. Every session
1. Read `CLAUDE.md`, `LESSONS.md`, `IMPROVEMENTS.md`.
2. `bash pipeline/setup.sh` (about 3 minutes: tools, 3 small models, Remotion packages). A cloud
   session starts empty, so this is needed every time. Network access must be Full, or the hosts
   listed at the top of that script.
3. Say back what he asked for in a few lines and wait for his yes (new or big work).

## 1. Footage and words
1. Footage from Drive: skill `drive-footage`. `ffprobe` both files: length, size, rotation.
2. His word-for-word transcript (ChatGPT: "word for word, including repeats and mistakes, do not
   clean it up"). Save as `transcript.txt`. Copy `pipeline/project.example.json` to `project.json`.
3. Sync two recordings: skill `sync-recordings` (`03_sync.py`; ask for a clap or the cue words).
4. Word timing: `01b_transcribe_fillers.py` (medium model, writes fillers down), `02_align.py`.
5. Clean voice: `04b_clean_voice.py raw/face.mov` (writes `face48k_clean.wav`).

## 2. Cuts (get his yes before building)
Skill `cut-plan`: `04_vad.py`, `05_sentences.py`, `05b_find_fillers.py`; opening pass, sentences,
fillers by exact time; the numbered list to him; then `06_edl.py` (the pause rule keeps real
breaths: tight, with longer pauses only while the screen is busy). Read `kept_text.txt` back.

## 3. Privacy
Skill `privacy-blur`: list the private details, fill `project.json` `privacy`, `07_ocr.py`,
`08_make_mask.py`. A scrolling clip used as B-roll is blurred as a whole.

## 4. Layout and build
1. Copy `pipeline/remotion/` to `projects/<name>/remotion/`, `npm install`. Fill `project.json`:
   hook text, steps, tips, `layout` (opening B-roll, tied to word numbers), `moments`, `broll`,
   `speed` (1.1). Speed changes: skill `speed-change`.
2. `bash ../../pipeline/build_all.sh` (cut tracks, face track, soft background, captions, B-roll).
   All four tracks must come out the same length.
3. Stills at 8 to 12 key moments (`npx remotion still src/Root.tsx Gmail s.png --frame=N --scale=0.3`)
   and look at them: hook, each layout change, steps, tips, the first frame (not white), the end
   card, his face centred in the circle, nothing over his mouth.

## 5. Render, sound, check
`bash ../../pipeline/finish_all.sh name.mp4` (run it in the background, about 35 minutes): render,
sound effects and mix (skill `sound-mix`), then `12_check_final.py` listens to the finished video.
Anything it lists (a tic, a silence) becomes a time cut; rebuild. Send the file in the chat and say
exactly what was checked and what was not.

## 6. Short, thumbnail, post copy (about 5 minutes together)
- The short for Reels, Shorts and TikTok: skill `short-cut` (cut at a hook, 6 s end card).
- The YouTube thumbnail: skill `thumbnail` (real photo, background removed only).
- Title, description, chapters, caption: skill `publish-copy`.

## 7. His notes
Skill `lesson` for every note: write it in `LESSONS.md`, put the rule where it belongs, then fix.
**Do not re-render the long video for a small note.** Most notes touch one layer: a caption
colour, a sound, a label. Collect his notes first, change them together, render once.

## Known traps
- Remotion cannot download its own browser here: `remotion.config.ts` uses the installed one.
- The browser does not trust this machine's network certificate, so Google Fonts fail: the font is
  served from `public/`.
- An iPhone face video can have an uneven frame rate: `09_build_tracks.py` sets 30 fps first.
- Small Whisper mishears his accent ("cool" for "full"). Check the finished video with the
  medium model before blaming a cut.
