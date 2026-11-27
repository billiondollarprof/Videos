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

### To try on the next video (Anthony, 2026-11-06)
- **Studio background instead of his room.** A first test frame worked but was rough: a faint curtain
  fringe round his hair, a flat backdrop, and a light that did not match his face. For a good result:
  a better video cut-out (hair edges), a proper studio picture he makes in ChatGPT (write him the
  prompt), the backdrop's colour and light matched to his face, a 10 second test clip for him to
  judge before any full video. Build it as a style option next to `09c_soft_background.py`.
- **Shirt colour change** is possible (the model can find the shirt). A different garment is not,
  and it touches his body: ask first.

### Plans from Anthony (2026-11-06): keep making the content better
**1. His own background, improved (the "clean plate").** What he used to do by hand: take himself out of
his own background, improve that background, put himself back. The plan:
- Build a **clean plate**: the empty background, with him removed. While the camera is still, the
  parts of the wall he covers in some frames are visible in others: a per-pixel median over the
  frames where the person mask says "background" gives the empty wall. Areas he always covers get
  filled in (inpainting).
- **Several backgrounds in one video:** if he moves or the phone moves, build one plate per camera
  position (up to 4 or 5), and switch at the cuts. A video where he does not move needs one.
- **Improve the plate once, not frame by frame:** remove stains and marks, denoise, sharpen, brighten
  and lift the colour (an upscaling model such as Real-ESRGAN for real extra sharpness). Then put
  him back on top of the improved plate, every frame, with the person mask.
- Honest limits: a phone's soft background gets sharper and cleaner, but not studio-grade. A
  handheld phone drifts, so the plate must be aligned first. His edge (hair) needs a good mask.
- Build it as a style option next to `09c_soft_background.py`: test on a 10 second clip first.

**2. Better light at the source.** He is getting a light: a darker room, white light on his face.
That makes everything easier: a cleaner face, less fixing. A darker room is also what makes
coloured background light believable (it looked fake in a lit room).

**3. Voice: a mic, and the sound made to feel like a strong mic, still his voice.**
- He is getting a microphone. Whatever the mic, the chain makes it feel solid: noise removal (done in
  `04b_clean_voice.py`), a little low warmth for body, presence around 3 to 5 kHz, a gentle
  de-esser, compression, loudness. **No pitch or formant shift, ever.**
- Make a **voice profile** he approves: three versions of the same 15 seconds (natural, warm,
  broadcast). He picks one by ear. The choice goes in the repo and becomes the default.
- Honest limit: EQ and compression get a cheap mic much closer to a good one, but not equal. Mic
  distance (a hand's width from his mouth, slightly off to the side) matters more than any filter.

### Next job (Anthony, 2026-11-07): a voiceover video, no face
A test post about an election in Nigeria: an opposition party's questions to the president about how
funds were mismanaged. His voice read over screen recordings of the party's posts and 5 to 7 free
photos, with camera-shutter sounds, a film-style colour grade and his voice enhanced (still his own).
Order: he records the voice and uploads it, pastes the word-for-word transcript, screen-records the
posts and uploads them. I pick the pictures from the script, he approves, I build, he posts.
Ground rules proposed (to confirm with him before they become rules): questions stay questions and are
attributed on screen; photos are free-licence only, each licence checked and credited; no AI images of
real people or real events (AI only for generic, labelled illustration); private people's names in the
recorded posts are blurred. Make it a skill (`voiceover-edit`) once it works.

## Voiceover video 1 (2026-11-07)

- A new kind of video: his voice only. New skill `voiceover-edit` and scripts `vo_01` to `vo_04`.
- Breaths at every joint come from his own room tone, never digital silence.
- Every shot moves: alternating zoom in and out, a slow pan, a drifting backdrop, a band of
  light across each picture and each highlighted line, kickers that slide in.
- Shot changes: a soft 5-frame flash with a camera shutter. End card with a whoosh and a tick.
- Frames drawn in Python straight into x264: no Remotion needed for this kind of video.
- Version 2: our own music bed, ducked under the voice. Room tone fixed (no more voice at the joints).
  Pictures rise and leave with easing, cards float, the post floats while it scrolls with his reading.
- Version 3: pictures are short inserts on the exact words, then back to the post line being read.
  Pops (and a tiny swipe) instead of whooshes for graphics; shutter only on hook and end card.
  AI pictures for the commentary, prompts kept in `voiceover-edit/prompts.md`.
- Voiceover 1, voice: `04c_polish_voice.py` (pauses -64 to -83 dB, voice untouched), longer cut lead-in so no
  word starts with a tick, and the 25 ms delay of the cleaner measured and removed.
- Voiceover 1 was approved by him on 2026-11-08 at version 6. Best so far for a voiceover: start from it
  (skill `voiceover-edit`, scripts `04c`, `vo_01` to `vo_04`, pops, no music, short inserts back to the post).

## Life video 1: "Why Life is Beautiful" (in progress, 2026-11-25)
- First of a new series: his talking videos about life, filmed on the front camera with a mic.
- His loud first clip (21 dB hotter) levelled down to the rest before cleaning: both parts now match.
- Room tests: a cut-out with the selfie model showed a fringe and he rejected it. What worked:
  - **Option A**: no cut-out at all. Flipped, gentle tone, fine sharpening, corners darker and softer,
    the poster covered with the door's own surface (seamless clone from 200 px below, fitted shape).
  - **Option B**: his ChatGPT picture of the empty room behind him, edge from Robust Video Matting
    (clean, steady), the iPad and lap kept as filmed (the model drops them). A ChatGPT room is not an
    exact copy of the real one, so it can only replace the whole background, never patch a part.
- **Option B chosen and made calmer** (his notes): room darker (55%), less green (62%), warm, slightly
  soft, a pool of light behind his head and darker corners: the light is on him. Edge: Robust Video
  Matting, pulled in where he is solid and softened by a pixel, the old room's light taken out of the
  thin edge band, then a little of the new room's light wrapped onto his edge. No rim, no specks.
- Cuts: only the 3 approved cuts, each at the quietest 10 ms near its edge, all three checked by
  listening. Pauses shortened only where the sound is truly quiet and no word's middle is inside
  (a plain loudness test swallowed soft words like "and" and "a"). His pauses were already short.
- Speed left at 1.0: he speaks about 170 words a minute, already brisk.
- Reaction clips are now a library: `clips/CATALOGUE.md`, skill `reaction-clips`, `15_clip_scan.py`.
- Next job after this one: a vlog (his voice note over his own footage). The brief is a private Google
  Doc in his Video Editing folder, "Vlog 1 brief"; it names a client, so it never comes into this repo.
- Version 1 delivered (2:16, 1080 x 1920, 30 fps): calm ChatGPT room behind him, wide and close shots
  in turn at each sentence with a slow push-in, 5 picture cards and 3 reaction clips on their exact
  words (2 with their own sound and their own captions), title hook, 4 camera flashes, captions in
  his brand font. Checked: 20 stills, edge at 16 moments, 0 fillers, 96% word match, -14.6 LUFS,
  peaks -1.7 dB. Scripts kept in `pipeline/room/` for the next talking video in a room.
- Version 2 (2:03): speed 1.1; pauses at most 0.3 s; pictures and clips full screen with a quick settle
  then a slow push; zoom jumps every 1.6 to 2.6 s (1.0 s in the opening) up to 1.6x with a 0.12 s punch;
  kinetic captions from his samples; cinematic grade and darker edges; the 3 pictures he regenerated.
  Mix: a whoosh next to a shutter is dropped (the doubled click made the encoder overshoot to +2.6 dB).
  Checked: 20 stills, 0 fillers, 96% word match, -14.7 LUFS, peaks -1.5 dB.
- Version 3 (1:42): speed 1.3; the room back near his ChatGPT picture's own light (the calm comes from
  softness, not darkness); a clip in the first 4 s; Pawpaw removed (wrong moment). Joints: approved cuts
  spliced between matching sounds ("better | life", "you | should"), every joint a 25 ms equal-power
  crossfade with the length kept (fade out then in had left an audible dip); a zoom change at every cut;
  a 0.16 s zoom-blur whip into and out of every insert; caption shadows doubled so text reads on the
  bright curtain. Checked: 20 stills, 0 fillers, 96% word match, -14.7 LUFS, peaks -2.1 dB.
- Version 4 (1:56): his own room, softly blurred, poster blurred (no rim: the colours at his edge match);
  speed 1.3 then 1.1 from "even in times of distress"; his opening picture at 7 s; captions bright white,
  yellow, red, silver small words, Anton for some key words, a soft pop on every key word.
  Checked: 20 stills, 0 fillers, 98% word match, -14.7 LUFS, peaks -2.1 dB.
- Voice: `04c_polish_voice.py` now ends with a faint room bed, so no pause is dead silent (559 slices on the life video).


## Hospital vlog (voiceover video 2), 2026-11-26

- **Render time.** New `vlog_render.py`: 3 second pieces, cached by fingerprint, drawn on all 4 cores, joined with no
  re-encode. First render 4 minutes; one change 20 seconds (voiceover 1 took about an hour for any change).
- **Shots tied to words, not times.** A re-cut moved every picture in the first attempt; word numbers fixed that for good.
- **Soft blur.** A feathered blur that is fully blurred inside the box and fades out beyond it (the first version only
  half-blurred and the sign stayed readable).
- **Clean voice notes.** `vo_01_cut.py` now compresses pauses from the voice's peak when the recording's floor is
  extremely low.

## Hospital vlog version 2, 2026-11-27

- A name board is painted out cleanly (per-column colour from the board's own dark pixels) instead of smudged: it reads as a blank board.
- Screens full screen at 9:16, hero pages zoom in and out, photos have a push, pan and drift, long shots are split. 45 shots in 2:45 (mean 3.7 s).
- Generated pictures (Canva) cover "building my own software"; StellaXafe's own screen record plays only where he names it.
- The render cache is keyed on the renderer's own fingerprint, so a stale piece can never be reused.
