---
name: transcript-captions
description: Get a time for every word Anthony said, using his own word-for-word transcript for the spelling and Whisper for the timing, then build the captions. Use for every edit with captions.
---

# His words, our timing

Whisper (free speech-to-text) mishears his accent sometimes. His transcript is right
about the words. Together they give correct words at the right times.

1. `ffmpeg -i <face video> -vn -ac 1 -ar 16000 voice16k.wav`
2. `pip install faster-whisper` if missing, then
   `python3 ../../pipeline/01_transcribe.py voice16k.wav face_words.json small`
   (about 2 minutes for 9 minutes of talk).
3. `python3 ../../pipeline/02_align.py`. Expect 85% or more of words matched exactly.
   Under 70%: the transcript may be cleaned up or from another take. Ask him.
4. Captions are built later by `10_captions.py`, from the cut timeline: 1 to 3 words,
   the spoken word in yellow, fillers ("uh", "um") left out of the captions.
5. After the final render, transcribe the cut voice again and compare with the kept
   words. Differences that are only accent mishearing are fine. A missing word is not.
