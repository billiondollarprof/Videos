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

### From Anthony's own cut (2026-11-05)
- Pause rule learned from his hand-made cut: tight, with a few real breaths, and longer pauses
  only where the screen is doing something (typing, Claude working). `06_edl.py`, `cut-plan`.
- Short version for Reels, Shorts and TikTok: the finished video cut at a hook, plus a 5 s
  "Watch the full video on YouTube" end card showing his channel page. `13_short_cut.py`, `short-cut`.
  No long re-render: about 2 minutes in total.
- Thumbnail from his real photo, background removed only, in his channel's style. `14_cutout.py`, `thumbnail`.

### Made ready for the next video (2026-11-05)
- One command sets up a fresh session (`pipeline/setup.sh`): tools, three models, Remotion packages.
- Voice cleaning, B-roll fitting and the B-roll sounds are scripts now (`04b`, `10b`), not steps done by hand.
- `build_all.sh` and `finish_all.sh` chain the build and the finish; `12_check_final.py` listens to the result.
- The end card and thumbnail folder is self-contained (`pipeline/endcard/`).
- New skill `publish-copy`: title options, description with chapters, short caption, hashtags.
- Checked: the repo's own `02_align` + `06_edl` rebuild video 1's exact edit list from `project.json`
  alone; `04b` ran on his real recording; `10b` reproduced the B-roll slot and 12 sound cues; the
  thumbnail renders from the repo folder identical to the one sent. Not yet run end to end on a new video:
  `build_all.sh` and `finish_all.sh` (syntax checked; each step they call was run on video 1).
