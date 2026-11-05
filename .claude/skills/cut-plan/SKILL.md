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
- **Prefer time cuts** (`cut_times`, exact seconds from `face_words_fillers.json`) for tics and
  fillers. A word-number cut only removes the caption and the words' own span: when his voice
  runs on from the tic into the next word, the sound stays in (video 1 version 3: "Yeah,",
  "Okay," and two "right?" survived a word cut). Word-number cuts (`cuts`) are for whole sentences.
- Cut whole phrases or fillers with silence around them. Never a single word from the
  middle of a phrase: it clips the words next to it.

## 5. The list for Anthony
Send a numbered list: time, the exact words, grouped (opening, sentences, fillers).
Give the length it comes to at his speed (`project.json` `speed`, 1.1 now). He can say
"just do it" for fillers; sentence cuts still go to him first.

## 6. Build and read back
1. `python3 ../../pipeline/06_edl.py`. **Tight, with a few real breaths** (learned by comparing
   his own hand-made cut of video 1 with my version 2 and my fully tight version 3):
   - Version 3 had no pauses at all and felt rushed: "I think I actually needed that little
     silence... it gives room for breathing". Version 2 had 82 pauses (22 s) and was too slow.
   - His cut: 60 pauses, 17 s in 3:27. Most joints tight, a breath of about 0.15 s between
     phrases, 0.25 to 0.5 s now and then, and longer ones **only where the screen is doing
     something worth watching**: while he types (0.5 s) and when Claude starts working (2 s and
     0.8 s, shortened from 10 s and 9 s, at normal speed, no fast-forward, no label).
   - So the script keeps a small share of each natural pause (`pauses.scale`, 5 percent),
     capped at 0.06 s inside a sentence, 0.18 s between sentences, 0.30 s while he types, and
     0.8 s for a very long wait (5 s or more) while the screen is busy. The pause is real room
     tone from beside the phrase (his face keeps its natural still moment), never a blank.
   - Result on video 1: 3:33 against his 3:27. Tune in `project.json` `"pauses"`:
     "a bit more room" = scale 0.08 and within 0.10; "too slow" = scale 0.03.
   - A silent stretch with the screen NOT changing never gets a long pause. Cut it.
   - `"fast_forward": true` brings the old 4 times fast-forward back (never labelled on screen).
2. Read `kept_text.txt` top to bottom. A sentence that no longer makes sense means a cut
   landed a few words off. A leftover "okay?" means a tic was missed.
3. After the final render run `python3 ../../pipeline/12_check_final.py final.mp4 kept_text.txt`.
   It transcribes the finished video with the medium model and lists every tic still in it,
   silences inside the talk, and the word match. Anything listed becomes a time cut; rebuild.
   A small-model transcript is not enough: it hears "cool" for "full" and hides real faults.
