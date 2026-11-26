# HANDOVER: read this before you say anything to Anthony (updated 2026-11-26)

You are taking over a video-editing job part way through. Anthony has already approved many decisions.
**Do not start again, do not re-ask what is answered here, do not re-plan what is approved.**
Read in this order: this file, `CLAUDE.md`, the bottom half of `LESSONS.md`, the "Life video 1" part of
`IMPROVEMENTS.md`. All of it lives on branch **`claude/sharp-allen-671eyb`** (check it out if you are on
`main`: `git fetch origin claude/sharp-allen-671eyb && git checkout claude/sharp-allen-671eyb`).
This repo is public: nothing private goes in it.

---

## 1. The jobs

| Job | State |
|---|---|
| Video 1, "Clean your Gmail with Claude" | Done (2026-11-05). |
| Voiceover video 1 (election post) | Approved, version 6 (2026-11-08). |
| **Life video 1, "Why Life is Beautiful"** | **Version 4 sent to him 2026-11-26 09:00 UTC. Waiting for his notes on v4.** |
| Vlog 1 (a hospital client story) | Not started. Comes after life video 1 is approved. Brief: private Google Doc (section 6). |

## 2. Life video 1: what it is

- A 2:18 talking-head video he filmed on his phone's front camera (4K, 60 fps, with a mic), sitting in his
  room holding an iPad. Raw file in Drive: **Video Editing / Life / "Why Life is Beautiful.mp4"**.
- First of a series of talking videos about life. Vertical 1080 x 1920, 30 fps, for TikTok, Reels, Shorts.
- He sent his own word-for-word transcript (saved as `transcript.txt` inside `life_01_work.tgz`, section 5).

## 3. Every version so far, and what he said about each

| Version | What it was | His notes (all also in `LESSONS.md`) |
|---|---|---|
| Room tests (2026-11-25) | Cut-out with the selfie model; then option A (own room polished, poster patched); option B (his ChatGPT picture of the empty room behind him, video-matting edge) | Selfie cut-out showed a fringe. A's poster patch shimmered. **Chose B**, but too bright, then too dark. |
| v1 (2:16) | Speed 1.0, picture cards floating over his blurred picture, plain captions | Speed 1.1. Pictures and clips must fill the **whole screen**. Captions boring. Too bright. Zooms too small and slow. Pauses at most 0.3 s. He regenerated 3 pictures. |
| v2 (2:03) | Speed 1.1, full-screen inserts, kinetic captions, cinematic grade | "Far better". Opening too long before the first picture. Pawpaw clip at the wrong moment: **removed**. Too dark. Some joints "flop". Better transitions. Speed 1.3. |
| v3 (1:42) | Speed 1.3, room brightened, clip at 4 s, clean joints, zoom-blur whips | Speed fine for the first 28 s, **then 1.1**. The edge still looks like a shadow on the ChatGPT room: **go back to his own room, blurred**, poster blurred not patched. One more picture early. **Caption colours: bright white, yellow, red, silver only. No peach, no dim red.** Stylish and italic fonts are fine if they read well. A soft pop sound when a key word lands. Render only the parts that change. |
| Own-room test (10 s) | His real room, softly blurred, poster blurred | **"Yes".** |
| **v4 (1:56), sent 2026-11-26** | All v3 notes done: own room; 1.3 then 1.1 from "even in times of distress"; his new opening picture at 7 s; bright captions with Anton display font for some key words; pop on each key word | **Waiting.** Checked: 20 stills, 0 fillers, 98% word match, -14.7 LUFS, peaks -2.1 dB. |

**Approved and must stay** (unless he says otherwise): only 3 content cuts ("a better day, a better" ->
"a better life today"; the first "you should be"; the middle "little"); pauses at most 0.3 s; his own room
blurred; full-screen pictures and clips with a 0.16 s zoom-blur in and out; a zoom change at every cut,
jumps up to 1.6x; clips: crying girl (`check_phone_one_person`) on "spiraling into depression", lawyer
laughing (`mr_ibu_lawyer` 12 to 14 s) on "That's an improvement", Aki "This is business!" with its own sound
after "make some sales"; 6 pictures (opening billboard man, scroller, student, report card, market,
sunrise); camera shutter + white flash at the start, "Start looking inward", "For example", the end;
-14 LUFS, peaks at or under -1.5 dB. **Never changed: his face, body, voice.**

## 4. When his notes on v4 arrive

1. Write every note into `LESSONS.md` first (date, note, where it lives). Commit and push.
2. Say back in a few lines what you will change. Small, clear changes: just do them. New or big: wait for "yes".
3. First line of every reply names the tier: **"Sonnet."** for changes after a draft.
4. Rebuild (section 5), only what changed if you can; send the new version in the chat; say what was
   checked and what was not.
5. When he approves: write the wins into `IMPROVEMENTS.md`, turn `pipeline/room/` into a skill, then the vlog.

## 5. Rebuilding in a fresh session (the container is wiped; `projects/` is not in git)

1. Environment **"Videos"** (allows Google Drive downloads and the model hosts). `bash pipeline/setup.sh`;
   `pip3 install torch fonttools brotli`; matting model:
   `curl -sSL -o models/rvm_mobilenetv3.torchscript https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.torchscript`.
   Whisper: always `HF_HUB_DISABLE_XET=1`.
2. From his Drive (find ids with the Drive connector, download with `curl`, skill `drive-footage`):
   - `Video Editing / Life / Why Life is Beautiful.mp4` -> `projects/life_01/raw/why_life_is_beautiful.mp4`
   - `Video Editing / Life / life_01_work.tgz` -> unpack in `projects/life_01/` (transcript, word times,
     edit list, face track, clean plate, scripts used for v3; take the newest scripts from `pipeline/room/`).
   - `Video Editing / Life/Pictures`: the newest 4 files (opening billboard man; sunrise; market; report card),
     plus "image collage" (cut into 5: the scroller and the student come from it).
   - `Video Editing / Life/Clips` -> `projects/life_01/clips/` (names in `clips/CATALOGUE.md`).
3. Voice: turn the first 30.55 s down 21.4 dB (his app boosted that clip), then `04b_clean_voice.py`,
   `04c_polish_voice.py`.
4. Fonts in `projects/life_01/work/`: PlusJakartaSans.ttf (from `pipeline/remotion/public/*.woff2` via
   fontTools), InstrumentSerif-Italic.ttf and Anton-Regular.ttf (github.com/google/fonts, `ofl/`).
5. Copy `pipeline/room/*.py` to `projects/life_01/scripts/`. Order: `room_own_full.py` (two halves side by
   side, about 1 hour, see `pipeline/room/README.md`), `edl.py`, `cut_voice.py`, `assemble.py`
   (`STILLS=1.5,8 python3 scripts/assemble.py` = check stills only), `mix.py`; or `finish_v4.sh` after the room.
6. Checks before sending: 20 stills looked at; `12_check_final.py`; loudness and peaks on the sent file.
   Send in the chat (Drive uploads from the container are limited to 10 MB).

## 6. Next job: Vlog 1

A private Google Doc in his **Video Editing** folder, title starting **"Vlog 1 brief"**: his voice note
word for word, the story angle, and rules (no hospital name on screen, no contract amount, optional
WhatsApp/SMS shown as extras, not as delivered). Never copy it into this repo. When life video 1 is approved:
read the brief, look at the vlog footage and pictures in his Drive, tell him which pictures to generate,
send a plan and the cut list, wait for his yes. Skills: `voiceover-edit`, `reaction-clips`,
`privacy-blur`, `sound-mix`. Bring what life video 1 taught (captions, full-screen inserts, whips, zooms,
crossfaded joints, short pauses).

## 7. How he works (the short version; the rest is `CLAUDE.md`)

- Phone and iPad only. He watches every draft on his phone. Never ask him to run anything.
- British English, no em dashes, answer first, short sentences, plain meanings for technical words.
- Anything he does himself: a numbered list of taps.
- He gives each note once. It goes into `LESSONS.md` and the script it belongs to, so he never repeats it.
- Long renders: run in the background, tell him roughly when, send the file when it is checked.
