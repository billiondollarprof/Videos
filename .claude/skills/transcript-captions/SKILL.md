---
name: transcript-captions
description: Get a time for every word Anthony said, using his own word-for-word transcript for the spelling and Whisper for the timing, then build the captions. Use for every edit with captions.
---

# His words, our timing

Whisper (free speech-to-text) mishears his accent sometimes. His transcript is right
about the words. Together they give correct words at the right times.

1. `ffmpeg -i <face video> -vn -ac 1 -ar 16000 voice16k.wav`
2. `python3 ../../pipeline/01b_transcribe_fillers.py voice16k.wav face_words_fillers.json medium`
   (about 8 minutes for 9 minutes of talk; the medium model and a filler prompt write the "um"s
   down and get the opening timings right. `01_transcribe.py` with the small model is faster but
   hears "cool" for "full" and skips fillers.)
3. `python3 ../../pipeline/02_align.py` (read `face_words_fillers.json`). Expect 85% or more of words matched exactly.
   Under 70%: the transcript may be cleaned up or from another take. Ask him.
4. Captions are built later by `10_captions.py`, from the cut timeline: 1 to 3 words,
   the spoken word in yellow, fillers ("uh", "um") left out of the captions.
5. After the final render, transcribe the cut voice again and compare with the kept
   words. Differences that are only accent mishearing are fine. A missing word is not.

## Caption style for his talking videos (his samples, 2026-11-25)
Plain one-line captions were "too boring". Use the kinetic style in `pipeline/room/kinetic.py`: words
build up one by one into a short stacked phrase in the upper third (below TikTok's top buttons, never
over his mouth); small lowercase for little words, one big bold key word per phrase in an accent colour
(yellow; red for hard words like "distress"; peach for life words), a warm glowing italic serif for
feeling words; each word lands on its spoken time, the key word pops; the phrase clears together.

## Where the captions sit and how they look (his note on life video 1 v4, 2026-11-26)
- **Low on the screen, never over his face.** The stack of words ends at y = 1560 of 1920 (over the chest and stomach),
  above the platforms' bottom buttons. Check a close shot (zoom 1.6): the top of the stack must stay below his chin.
- A soft dark gradient (up to 38%) under the captions keeps them readable; it never reaches the face.
- Key words (Anton display face): crisp outline, a light top edge, a coloured glow, a small overshoot pop and a thin
  underline that grows out from the middle. Colours: bright white, bright yellow, bright red, silver only.
- **No sound on the captions.** The pop on each key word distracted him. A caption never gets a sound effect.

## Change the captions a little on every video (his rule, 2026-11-28)
Read `docs/CAPTION-IDEAS.md`. Each video uses our base plus ONE new idea from the bank (never the whole of one reference),
and a different mix from the video before. Log the recipe and his note there. When he shares a caption video, study it
(skill `study-reference`), pick its ONE best idea, add it to the bank, and use it next.
