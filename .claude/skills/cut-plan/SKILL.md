---
name: cut-plan
description: Choose what to cut (repeats, false starts, asides, over-explaining, reading the screen aloud, silences), list it for Anthony's yes, then build the edit list. Use after the words have times and before any rendering.
---

# Cut plan

1. `python3 ../../pipeline/04_vad.py` (finds where his voice is, from loudness) and
   `python3 ../../pipeline/05_sentences.py > sentences.txt`.
2. Read every sentence. Mark for cutting:
   - repeats and false starts (keep the last clean take),
   - asides to himself ("Do I have two accounts here?"),
   - the same point said twice (keep the shorter, clearer one; on video 1 he kept the
     second telling of the interview tip, and said why: the screen already shows it),
   - reading options aloud that the screen already shows,
   - a doubled ending (end on the first clean "thank you").
   Cut whole phrases only. Never a single word from the middle of a phrase.
3. Send Anthony a numbered list: time, the exact words. Give the length it gives, and
   what more would have to go to reach his target length. **Wait for his yes.**
4. Put the approved ranges in `project.json` `cuts` as `[first word, last word, why]`.
5. `python3 ../../pipeline/06_edl.py`. It keeps only where his voice is, leaves 0.1 s of
   air at each edge, closes gaps under 0.25 s, and turns silent screen stretches of
   1.5 s or more into a 4 times fast-forward.
6. Read back the kept words (`kept_text.txt`) from top to bottom. A sentence that no
   longer makes sense means a cut landed a few words off. Fix the word numbers.
