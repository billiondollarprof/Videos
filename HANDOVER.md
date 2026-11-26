# Handover (updated 2026-11-26)

For the next agent. Read `CLAUDE.md`, then `LESSONS.md` (every note Anthony has given, newest at the
bottom), then `IMPROVEMENTS.md`, then this file. This repo is public: nothing private goes in it.

## 1. Where things stand

| Job | State |
|---|---|
| Video 1, "Clean your Gmail with Claude" | Done (2026-11-05). |
| Voiceover video 1 (election post) | Approved at version 6 (2026-11-08). Skill `voiceover-edit`. |
| **Life video 1, "Why Life is Beautiful"** | **Version 3 sent and watched. His notes on v3 are in. Version 4 plan approved. Not built yet.** |
| Vlog 1 (a client story, voiceover over his footage) | Not started. Brief is a private Google Doc (see section 5). Start only after life video 1 is approved. |

## 2. Life video 1: what version 4 must be (his approved plan, 2026-11-26)

1. **Speed**: 1.3 from the start to about 28 s of v3 (the pause at "...worth living, | even in times of
   distress"); 1.1 from there to the end. `pipeline/room/edl.py` has one `SPEED`; make it per item
   (speed by raw time: 1.3 before raw ~37.5 s, 1.1 after) and use it in `cut_voice.py` (atempo per run)
   and in `assemble.py` (`raw_frame_at`, which reads `E['speed']`).
2. **Background: his own room again, softly blurred, with the video-matting edge.** The edge "shadow"
   came from putting a different (ChatGPT) room behind him. Plan: the real room plate (`work/plate_raw.png`,
   or simply the frame's own background) blurred a little, same colours, no darkening, poster blurred so
   its text cannot be read (no clone patch: it shimmered). **Send him a 10 s test first** (raw 36 to 46 s),
   then render the room (`room_full.py`, two halves side by side, about 1 hour).
3. **One more picture in the opening**, on "the single reason why a lot of persons cannot appreciate the
   little things" (finished-word index about 21 to 32). He made it: Drive `Life/Pictures`, newest file,
   saved locally as `pictures/not_noticing_little_things.png` (a man staring at a luxury billboard, a
   smiling child, a gift and a sprouting plant beside him). Add it to `CARDS` in `assemble.py`.
4. **Captions** (`pipeline/room/kinetic.py`): colours only bright white, bright yellow, bright red, silver
   for small words. **No peach, no dim red.** Mixed, stylish fonts are welcome (bold, italic, a stylish
   display face) chosen by what is said, but every word must read easily: strong shadow, no thin dim
   italic on the bright curtain. Words build up one by one; the key word pops in big.
5. **A soft pop sound each time a key word pops in** (cue list from `kinetic.py`, mixed low in `mix.py`).
6. **Render in pieces from now on**: render the picture in chunks of about 10 s, keep them, and re-render
   only the chunks a change touches; join them frame-exact (concat of video-only chunks, then the
   whole sound mixed once). This round still needs a full render (speed, room and captions change everywhere).

Keep from v3 (he liked these): full-screen pictures and clips with a 0.16 s zoom-blur whip in and out,
a zoom change at every cut, zoom jumps (up to 1.6x), the crying-girl clip on "spiraling into depression",
the lawyer laughing on "That's an improvement", Aki "This is business!" with its own sound, joints
crossfaded and spliced at matching sounds, pauses at most 0.3 s, captions upper third, -14 LUFS, peaks
at or under -1.5 dB. **Pawpaw is removed** (wrong moment).

## 3. How to rebuild the working files in a fresh session

The container is wiped between sessions. `projects/` is not in git.

1. Use the cloud environment **"Videos"** (it allows Google Drive downloads and the model hosts).
2. `bash pipeline/setup.sh`, then `pip3 install torch` (from PyPI; download.pytorch.org is blocked), then
   download the matting model:
   `curl -sSL -o models/rvm_mobilenetv3.torchscript https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.torchscript`
3. Whisper models: run with `HF_HUB_DISABLE_XET=1` (the new Hugging Face download path is blocked).
4. In his Drive, folder **Video Editing / Life** (shared by link): the raw video "Why Life is Beautiful.mp4",
   and **`life_01_work.tgz`**: transcript, word times, edit list, face track, clean plate, lineup matrix,
   and the project scripts. Unpack it into `projects/life_01/`. Pictures: **Video Editing / Life/Pictures**
   (newest 3 replace the collage's report card, market, sunrise; `image collage` holds the first 5;
   `My room background.png` is his ChatGPT room). Clips: **Video Editing / Life/Clips** (catalogued in
   `clips/CATALOGUE.md`). Find ids with the Drive connector, download with `curl` (skill `drive-footage`).
   Uploads from here to Drive are limited to 10 MB: finished videos go to him in the chat.
5. Re-make the voice: `04b_clean_voice.py` on the raw video with the first 30.55 s turned down 21.4 dB
   (his app boosted that clip), then `04c_polish_voice.py`. See `IMPROVEMENTS.md`, life video 1.
6. The order of the room pipeline is in `pipeline/room/README.md`. Fonts: `work/PlusJakartaSans.ttf` is made
   from `pipeline/remotion/public/PlusJakartaSans-latin.woff2` (fontTools); Instrument Serif from google/fonts.

## 4. How to work with Anthony (short)

Everything is in `CLAUDE.md` section 2 and 4. The points that matter most this week:
- Name the model tier on the first line (Sonnet for changes after a draft). British English, no em
  dashes, the answer first, plain meanings for technical words.
- Every note goes into `LESSONS.md` the moment he gives it, then into the skill or script.
- New or big work: say the plan back and wait for his yes. He asked "what's your plan?" before v4.
- Before sending: stills, `12_check_final.py` (fillers, silences, word match), loudness and peaks on the
  delivered file. Say what was checked and what was not.
- He watches on his phone. Send the file in the chat (under about 150 MB).
- Long renders: run in the background and use a Monitor; tell him roughly when.

## 5. Next job: Vlog 1

The brief is a **private Google Doc** in his Video Editing folder, the doc whose title starts "Vlog 1 brief". It names a client and a contract amount: never copy it here. Read it first, then the
vlog footage and images in his Drive, then tell him which pictures need generating and send a plan.
Skill `voiceover-edit` (his voice note over his footage), plus `reaction-clips`, `privacy-blur` (no
client name anywhere on screen), `sound-mix`. Bring what life video 1 taught: kinetic captions in bright
colours, full-screen inserts with whips, zooms at every cut, crossfaded joints, pauses at most 0.3 s.

## 6. Skills changed in this stretch

- New: `reaction-clips` (clip catalogue in `clips/CATALOGUE.md`, `pipeline/15_clip_scan.py`).
- New scripts: `pipeline/room/` (room replace, edit list, voice cut, assembly, kinetic captions, mix).
- Updated: `transcript-captions` (caption style from his samples).
- To do: fold the room pipeline into a skill once v4 is approved (a third use makes it a skill).
