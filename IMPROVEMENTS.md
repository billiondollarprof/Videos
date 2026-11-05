# Improvements

What made each video better than the one before. One block per video, newest at the
bottom. Read it before every edit, so the next video starts from the best so far.

`LESSONS.md` holds the rules (what to always or never do). This file holds the wins
(what we added or did better, and what it did for the video).

## Video 1: Clean your Gmail with Claude (2026-11-05)

First edit. The starting point:
- Raw footage instead of a pre-cut video, so every cut is ours and the pace is even.
- His own transcript for the caption words, Whisper only for the timing.
- Face and screen lined up by sound, with the clock drift corrected.
- Brand layout: face full frame for the opening, then a face circle and a framed phone screen.
- Hook title, step labels, tip cards, progress bar, end card.
- Voice cleaned (room noise down 16 dB), loudness set for the platforms.
- Sound effects on visible actions, and a camera shutter with a flash at the start and end.
- Names, emails and codes blurred by a text scan of every frame.

### Version 2 (in progress)
- B-roll in the opening 30 seconds: his real inbox recording, and animations.
- Phone status bar cropped out of every screen recording.
- Opening re-cut to the last clean start, found with the medium model's exact timings.
- Fillers and his own tics cut all through (`05b_find_fillers.py` finds them).
- His speech at 1.1 times, applied in the same pass as the cuts.
- Nothing about the editing on screen (the "Speeding up" badge is gone).
- Face tracked and centred in the circle.
- Background softly blurred with a warm glow behind him.
- Skills `cut-plan` (rewritten) and `speed-change` (new) hold all of this for the next video.
