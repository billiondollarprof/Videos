---
name: reaction-clips
description: Catalogue Anthony's reaction clips (Nollywood and Nigerian skit moments he downloads) once, by time, expression, words and what kind of line each suits, and drop the right 1 to 2.5 s moment into a video on the exact words. Use when he uploads new clips, asks for "surprise" or reaction inserts, or a video needs lively cutaways.
---

# Reaction clips

The library is `clips/CATALOGUE.md`. **Read it first.** Only watch a clip that is not in it.

## A. New clips arrive (catalogue them once)
1. Download them (skill `drive-footage`) into `projects/<video>/clips/`, with short snake_case names.
   Ask him to share the **folder** ("Anyone with the link"): a new folder is private.
2. `HF_HUB_DISABLE_XET=1 python3 ../../pipeline/15_clip_scan.py` (words with times, and a grid of
   stills every 0.5 s per clip, in `work/clips/`). Whisper must be set to English: left to guess,
   it wrote Kannada and Thai for Pidgin over music.
3. Read each grid and the words together. For each clip write in the catalogue:
   - the Drive title, size, a one-line scene, what is **burned in** (titles, logos, handles, captions)
     and where, so it can be cropped off;
   - a table of moments, 1 to 2.5 s each: time, what you see (the expression) and hear, and the
     **kind of line it suits** ("making sales", "shock", "ignoring opinions");
   - "(own sound)" where the clip's words are worth hearing.
4. Flag care cases: a real private person (a vox pop), **a real child** (not an actor): avoid by
   default and ask him. Never mock a real private person.
5. Never put Drive ids or the clips in the repo (it is public). File names and titles only.

## B. Using clips in a video
1. Go through his transcript and mark the lines with a clear feeling (surprise, a win, a no, doubt,
   pride). Match each to a catalogue moment by the feeling, not by the topic.
2. **At most one clip every 15 to 20 s.** Clips are the spice. Pictures and his face carry the video.
3. Cut on the exact word: the clip starts on the word it answers, lasts 1 to 2.5 s, then straight
   back to him (a zoom jump on the way back reads well).
4. Crop off everything burned in; fit the clip to 1080 x 1920 (crop to the face, or a card over his
   blurred picture).
5. Sound: silent, or the clip's own words where marked "(own sound)": then his voice pauses or dips
   under it, and the clip's words get a caption.
6. Say in the cut list which clips go where, before building. They are other people's films: he has
   chosen to use them (2026-11-25), keep each under 3 s.
7. Add any new use to the clip's row ("used in: <video>") so later videos can vary.
