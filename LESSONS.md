# Lessons

Every note Anthony gives, with the date and where it now lives as a rule.
Newest at the bottom. Read this before every edit.

## Video 1: Clean your Gmail with Claude (2026-11-05)

| Note | Now lives in |
|---|---|
| Give me the raw videos, not my own cut, so you can make every cut yourself. | `vertical-edit` |
| Whisper may mishear my accent. Use my ChatGPT transcript for the words, Whisper for the timing. | `transcript-captions`, CLAUDE.md 5 |
| The screen share started at 0:58 on "So you open your Claude account". Ask for a cue like this. | `sync-recordings` |
| About 5 minutes. Cut over-explaining and repeats. | `cut-plan` |
| Keep the second telling of a point, not the first, when the screen already shows it. | `cut-plan` |
| End on the first "thank you". Do not keep the awkward line after it. | `cut-plan` |
| Blur names that are not mine, fully, in a greeting. | CLAUDE.md 5, `privacy-blur` |
| Every Gmail address: blur the start, keep "@gmail.com" so people see it is Gmail. Blur half of each name. The business account may show. | CLAUDE.md 5, `privacy-blur` |
| Use my website's colours: yellow, bright blue, navy, white. | CLAUDE.md 5 |
| Sound effects are important. Camera sound and camera effect at the start and towards the end. Those little professional touches. | `sound-mix`, `11_finish.py` |
| Background music: I add it in TikTok, then reuse that file on other platforms. | `sound-mix` |
| I want the skills to keep getting better. | `lesson` |

## Found while editing video 1 (not notes from Anthony, but they cost time)

- The face video and screen video drifted 0.19 s apart over 8 minutes. Measure drift along the whole length.
- The face circle first showed mostly curtain. Check the circle is centred on his face.
- The account chooser on the Google sign-in screen shows other people's names and emails.
  Always scan sign-in screens.
- Text reading at double size took 47 s a frame and found nothing more. Read at normal size.
- A mono file measures 3 dB quieter than stereo. Measure loudness on the stereo delivery.
- The raw voice sits near -27 LUFS. Boosting it 13 dB into a plain limiter left peaks at +4 dB
  after AAC encoding. `11_finish.py` now uses two-pass loudnorm and measures the encoded sound.

## Video 1, round 2 (2026-11-05)

| Note | Now lives in |
|---|---|
| Keep a record of every improvement, so the next video is better than the last. | `IMPROVEMENTS.md`, CLAUDE.md 1 |
| The phone's status bar (time, network, battery) must not show. Crop it out. | CLAUDE.md 5 (Look) |
| The video needs B-roll. Plan it yourself; ask me for a ChatGPT image only if one is needed. | `vertical-edit`, `IMPROVEMENTS.md` |
- Text reading misses words on a scrolling list (it read "Copy code: 852029" as "coe )"), and
  tracking the scroll locks onto the wrong row because rows look alike. For scrolling B-roll of
  an inbox or feed: blur the whole list lightly and keep only bars with nothing private sharp.
  Then check the bottom strip too: when the tab bar hides while scrolling, real emails show there.
- A flash timed in seconds left one unflashed frame (a flicker). Time flashes in frame numbers.

## Video 1, notes on version 1 (2026-11-05)

| Note | Now lives in |
|---|---|
| The first 5 seconds repeat "so your mailbox is full" with an awkward silence. Re-transcribe the opening carefully, start where he starts cleanly, and move the title there. | `cut-plan` (the opening gets its own careful pass) |
| Never write what the editing is doing on screen ("Speeding up"). On screen is only his message, the B-roll and what concerns the video. Speed-ups stay, silently. | CLAUDE.md 5 (Look), Overlays |
| His speech at 1.1 times speed. | CLAUDE.md 5 (Cutting), `09_build_tracks.py` |
| Cut fillers all through: "uh", "um", "eh", "so now", "alright", "so so", repeated starts. They are his own kind of fillers, not only the usual ones. | `cut-plan`, `filler` step |
| The face drifts right inside the circle when he moves. Track the face and keep it centred. | `People.tsx` face tracking |
| A little blur on my background before the screen share, and a soft light behind me, so the focus is on me. Keep it subtle. | `09c_soft_background.py`, CLAUDE.md 5 (Look) |

## Video 1, notes on version 2 (2026-11-05)

| Note | Now lives in |
|---|---|
| Remove every silence, completely. No gaps between phrases. Aim for about 3 minutes. | CLAUDE.md 5 (2a), `06_edl.py`, `cut-plan` |
| Do not speed up again once the silences are gone. | `speed-change` (1.1 stays) |
| The first frames are washed white (it was the camera flash on frame 0). | `11_finish.py`, CLAUDE.md 5 (Look 7) |
| Less blur on the background. The light did not show: darken the background a bit and use a coloured light, blue to red. (Tried, then reversed: see the next row.) | `09c_soft_background.py` |
| The coloured light looks fake because the room is not dark. Remove it. Tone the blur down and brighten the background a tiny bit. | `09c_soft_background.py`, CLAUDE.md 5 (Look 6) |
| "filling in, filling up" said twice. Cut the repeat. | `cut-plan` step 3 |

## Found while checking version 3 of video 1 (2026-11-05)

- The word-number cuts missed 4 tics ("Yeah,", "Okay," and two "right?"): his voice runs on from the
  tic into the next word, so the sound stayed in while the caption went. Cut tics by exact time.
- The small Whisper model heard "cool" for "full" and "jobs" for "junk". Check the final video with the
  medium model (`12_check_final.py`), and look at the sound level before blaming a cut.
- The only silence left in version 3 was the end card. A silence check must ignore it.

## Anthony's own cut of video 1 (2026-11-05)

He did not use version 3. He cut version 2 by hand, because version 3 "was too much... I actually needed that little silence".

| What his cut shows | Now lives in |
|---|---|
| Keep small pauses: "it gives room for breathing, even if less than 1 second". His cut: 60 pauses, 17 s in 3:27 (median 0.15 s). Fully tight (v3) felt rushed; v2's 82 pauses felt slow. | CLAUDE.md 5 (2a), `06_edl.py` pause rule, `cut-plan` |
| Longer pauses only where the screen is doing something: while he types, and when Claude starts working (long waits shortened from 10 s to 2 s and 0.8 s, normal speed). | `06_edl.py` (screen activity), `cut-plan` |
| He stammers a lot at the start: the opening needs a careful pass. He found it manageable. | `cut-plan` step 2 |
| He left an "uh" and an "um" in his own cut, and kept "filling in, filling up". Tics are his call: list them, do not hide them. | `cut-plan` step 4 |
| He wants a short version (about the first half) for Instagram, Shorts and TikTok that stops at a hook and sends people to his YouTube, and a long version for YouTube. No 35 minute re-render for that. | skill `short-cut` |
