---
name: vertical-edit
description: The whole edit of a vertical talking video (Anthony's face, often with a phone screen recording) for TikTok, Shorts and Reels - footage from Drive, sync, captions from his transcript, cuts he approves, privacy blur, brand layout, sound effects, final file. Use when Anthony hands over raw footage and asks for an edit.
---

# Vertical edit

Runs every step in order. Each step names the skill or script that does it. Work in
`projects/<name>/` (git ignores it). Copy `pipeline/project.example.json` there as
`project.json` first. Stop at the first step that fails and say which step.

## Before anything
1. Read `CLAUDE.md` and `LESSONS.md`.
2. Say back what Anthony asked for, in a few lines, and wait for his yes.
3. Ask for his word-for-word transcript (ChatGPT, "word for word, including repeats and
   mistakes, do not clean it up"). Save it as `transcript.txt`.

## Steps
1. **Footage**: skill `drive-footage`. Check both files with ffprobe: length, size, rotation.
2. **Sync** (only when there is a separate screen recording): skill `sync-recordings`.
3. **Timing of every word**: skill `transcript-captions`, steps 1 and 2.
4. **Cuts**: skill `cut-plan`. **Wait for Anthony's yes** on the list before going on.
5. **Privacy**: skill `privacy-blur`. Agree the rules with Anthony if new names appear.
6. **Build the cut tracks**: `python3 ../../pipeline/09_build_tracks.py`. All three
   outputs must be exactly the same length. Re-transcribe the cut voice and compare
   with the kept words (every word whole).
7. **Captions and moments**: `python3 ../../pipeline/10_captions.py`. Pick the hook text,
   step labels and tips in `project.json` from what he actually says.
8. **Layout**: copy `pipeline/remotion/` into the project, `npm install`, copy the cut
   videos and the font into `public/`. Render 6 to 10 stills at key moments
   (`npx remotion still ... --frame=N --scale=0.4`) and **look at them**: hook, the face
   to screen change, each step, each tip, a fast-forward, the end card. Check the face
   is centred in the circle and nothing covers his mouth.
9. **Render**: `npm run render` (about 45 minutes for 4:40 on 4 cores). Run it in the
   background.
10. **Finish**: skill `sound-mix` (runs `11_finish.py`).
11. **Check** (CLAUDE.md section 6), then send the file to Anthony in the chat and say
    exactly what was checked.
12. **His notes**: skill `lesson` for every note. Then make the change.

## Known traps
- Remotion cannot download its own browser here. `remotion.config.ts` points at the
  installed Chromium.
- The browser does not trust this machine's network certificate, so Google Fonts fail.
  The font file is served from `public/`.
- An iPhone face video can have an uneven frame rate. `09_build_tracks.py` sets 30 fps
  first, so the cuts land on exact frames.
