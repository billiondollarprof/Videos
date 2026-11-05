---
name: sync-recordings
description: Line up a screen recording with a face recording of the same session by their sound, and measure the clock drift between them. Use whenever two recordings of one session must play together.
---

# Sync two recordings

1. Ask Anthony roughly where the screen recording starts in the face video, and on
   which words (on video 1: 0:58, "So you open your Claude account"). A clap at the
   start of recording makes this certain. Suggest it for next time.
2. Run `python3 ../../pipeline/03_sync.py <rough start>`. It writes `screen_offset`
   and `screen_rate` into `project.json`.
3. Check the printout: every match should be 0.8 or more, and the shifts should climb
   in a straight line (that is the drift). Video 1: start 57.92 s, drift 0.19 s over 8 min.
4. Cross-check with the words: the time of his cue words in `aligned_words.json`
   should be within 0.2 s of `screen_offset`.
5. Stop if a match is under 0.6. The files may not be the same session.
