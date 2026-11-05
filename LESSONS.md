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
