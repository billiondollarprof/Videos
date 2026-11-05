---
name: cut-plan
description: Cut a talking video tight - the opening, repeats, false starts, asides, over-explaining, reading the screen aloud, his fillers and tics ("uh", "um", "eh", "okay?", "so now", "alright"), stray sounds and silences - list it for Anthony, then build the edit list. Use after the words have times and before any rendering, and whenever he says a video has awkward bits, repeats or fillers.
---

# Cut plan

Everything here was learned on video 1. Each round of his notes makes this skill better:
add the new lesson to the right step, in the same change (skill `lesson`).

## 1. Transcribe for cutting (not only for captions)
1. `python3 ../../pipeline/01b_transcribe_fillers.py voice16k.wav face_words_fillers.json medium`
   The filler prompt makes Whisper write the "um"s down. The medium model gets the
   opening timings right; the small model guessed them, and the repeated opening of
   video 1 survived because of it.
2. Align his transcript to it: `02_align.py` with `face_words_fillers.json` as input.
   Expect 90% or more matched.
3. `python3 ../../pipeline/04_vad.py` (where his voice is, from loudness).

## 2. The opening gets its own pass (the first 15 seconds)
Viewers leave in the first seconds, and he often restarts there.
1. Print every word of the first 15 s with its time.
2. Find the **last clean start** of the opening line. Cut everything before it, pauses
   included. Video 1: "Okay, so, your, okay, so your mailbox is full and... so" was cut;
   it starts on the clean "your mailbox is full and then you have...".
3. The hook title goes on that first clean word.

## 3. Whole sentences
`python3 ../../pipeline/05_sentences.py > sentences.txt`, then mark for cutting:
- repeats and false starts (keep the last clean take),
- asides to himself ("Do I have two accounts here?"),
- the same point said twice (keep the shorter, clearer one; on video 1 he kept the
  second telling of the interview tip, because the screen already shows it),
- reading options aloud that the screen already shows,
- a doubled ending (end on the first clean "thank you").

## 4. Fillers and tics
`python3 ../../pipeline/05b_find_fillers.py`, then read `fillers.txt` line by line:
- **Cut:** "uh", "um", "eh"; "okay?" / "Okay," / "Yeah," / "right?" at a sentence edge;
  "So now" and "All right" opening a sentence; stray short sounds with no word.
- **Keep:** real speech that only looks like a stutter ("out of it, it will notify you").
- Word-number cuts go in `project.json` `cuts`; time cuts go in `cut_times`.
- Cut whole phrases or fillers with silence around them. Never a single word from the
  middle of a phrase: it clips the words next to it.

## 5. The list for Anthony
Send a numbered list: time, the exact words, grouped (opening, sentences, fillers).
Give the length it comes to at his speed (`project.json` `speed`, 1.1 now). He can say
"just do it" for fillers; sentence cuts still go to him first.

## 6. Build and read back
1. `python3 ../../pipeline/06_edl.py`. It keeps only his voice, 0.1 s of air at each edge,
   closes gaps under 0.25 s, and fast-forwards silent screen stretches of 1.5 s or more.
2. Read `kept_text.txt` top to bottom. A sentence that no longer makes sense means a cut
   landed a few words off. A leftover "okay?" means a tic was missed.
3. After the tracks are built, transcribe the cut voice again and compare with the kept
   words: a missing word means a cut clipped speech.
