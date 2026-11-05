# CLAUDE.md

How to edit Anthony's videos. **These rules are for every agent**: Claude, Codex,
Gemini and whatever comes next. Read this file first, then `LESSONS.md`.

This repo is **public**. Never commit a raw video, a transcript, a name, an email,
a phone number or anything from a client. Media and project data stay in `projects/`,
which git ignores. Finished videos go to Google Drive, never here.

---

## 1. Start and end of every video job

1. Read this file, then `LESSONS.md` (every note Anthony has given) and `IMPROVEMENTS.md`
   (what made each video better than the last). Start from the best so far.
2. Pick the skill for the job (section 8). Run it. Do not work it out again.
3. **Write every note Anthony gives into `LESSONS.md`** the moment he gives it, with
   the date, then into the skill or script it belongs to. He never gives the same
   note twice. This is how the skills get better with every video.
4. At the end, add the video's wins to `IMPROVEMENTS.md`, and say which skills changed and why.

## 2. Anthony is in charge

- **A specific request gets carried out**, at full size. Do it, then say it is done.
- **Opinions only when asked.** If something still looks wrong after, say it in one line, after.
- **His footage is his.** Cutting a line he did not approve, or changing his face, voice or
  body in any way, is never done without asking.
- **New or big work: say it back in a few plain lines and wait for his yes.**
- **The one exception:** anything that would put a false claim, a private detail or
  someone else's copyright in front of the public. Say so plainly and wait.

## 3. His hardware

Anthony has a **phone and an iPad, no laptop**. He cannot run anything. He watches
every draft on his phone. So:
- Raw footage arrives through **Google Drive**. Finished videos go back the same way,
  or as a file sent in the chat.
- Never end a job with "run it locally".

## 4. How to talk to Anthony

- Plain, direct **British English**. **No em dashes, ever.** Numbers as numbers.
- **The answer first**, then what he has to do. Short sentences, one idea each.
- **Every technical term gets its plain meaning in brackets the first time** it comes up
  in a conversation. Example: LUFS (the loudness unit the platforms use).
- **Anything he does himself is a numbered list**: where he is, then each tap.
- **Say what is already done before what is left.**
- **Name the model tier on the first line**: Opus for the first full edit of a video
  (cut choices, layout, pace). Sonnet for changes after he has watched a draft.

## 5. The rules of an edit

Vertical first: **1080 x 1920, 30 fps**, for TikTok, Shorts and Reels.

**Cutting**
1. Cut **between phrases, never inside one**. A phrase is what is said in one breath.
2. **His speech plays at 1.1 times speed** (his choice, 2026-11-05), with the pitch kept.
2a. **No silence anywhere.** Every phrase runs straight into the next (0.03 s of air before,
   0.06 s after). Silent screen action is cut, not fast-forwarded.
3. Keep the last clean take of a repeated line, unless Anthony picks the other.
3a. **Cut fillers by exact time**, not only by word number: his voice runs on from one word
   into the next, and a word cut can leave the tic's sound in (video 1, version 3).
3a. **Cut his fillers everywhere**: "uh", "um", "eh", "so now", "alright", "so so", repeated
   starts. Transcribe with a filler-friendly prompt so Whisper writes them down.
3b. The opening is where viewers leave. Give the first 15 seconds its own careful pass.
4. Cut lists go to Anthony **before** cutting, as numbered lines with times and words.
5. Select exact frames in **one pass** (no joining separately encoded pieces). Joining
   pieces drifts lip sync.
6. Two recordings of one session are lined up by their **sound**, and drift is measured
   along the whole length, not only at the start.

**Captions**
1. **His words, our timing.** Use his own transcript for the spelling. Use Whisper (a
   free speech-to-text tool) only for the timing of each word.
2. 1 to 3 words at a time. The word being said is highlighted.
3. Never over his mouth. Never white on a light background.

**Privacy (decided 2026-11-05)**
1. Every email address: blur the part before "@". Keep "@gmail.com" readable.
2. Other people's names: blur the second half (the surname).
3. A name in a greeting that is not his: blur it fully.
4. A business account he names as public may stay readable.
5. Security codes, bank statements and account numbers: always blurred, even his own.
6. Scan **every frame** with text reading (skill `privacy-blur`). Never trust a few stills.

**Sound**
1. His voice is always the loudest thing.
2. Clean the room noise. Master near **-14 LUFS**, peaks at or below **-1.5 dB**.
   Measure the final file, not the parts.
3. **Sound effects follow a visible action**, not every cut. Soft palette: air
   whooshes, soft taps, dry clicks, paper, one warm tick for a tip, a camera shutter
   for a camera-style moment. No laser zaps, no pitch-drop plops.
4. Background music is added by Anthony inside TikTok (its own licensed library) unless
   he asks for it in the file. YouTube Studio has a free Audio Library for long form.

**Look**
0. Crop the phone's status bar (time, signal, battery) off every screen recording.
1. Brand colours from anthony.stellaxafe.com: navy, bright blue, yellow, white.
   Font: Plus Jakarta Sans.
2. Every shot moves a little (a slow push-in, a zoom at a cut). No frozen frames.
3. A hook in the first 3 seconds. A clear ending. Never claim a result he did not show.
4. **Never put the editing itself on screen** ("Speeding up", "Cut here", "Zooming"). On screen
   is only his message, the B-roll, and what concerns the video.
5. Track his face. In the circle it stays centred, however he moves.
6. His background gets a light blur and is made a tiny bit brighter (`09c_soft_background.py`).
   **No coloured lights**: they looked fake in a lit room (his note, 2026-11-05). Coloured light
   only suits a really dark room. He is never changed, only the background.
7. Nothing white or washed out on the first frame: it is what people see before pressing play.

## 6. Nothing is done until it has been checked

Before he sees a draft:
1. **Stills** at every key moment, looked at, not just rendered.
2. **Sync**: the screen and the face match the voice from start to end.
3. **Every word whole, and no fillers left**: `12_check_final.py` listens to the final video
   with the bigger Whisper model. It lists tics still in it, silences inside the talk, and the
   match with the kept words. Never say "no fillers" without running it.
4. **Privacy**: the text scan finds no unblurred email or name.
5. **Loudness and peaks** measured on the delivered file.
6. Say exactly what was checked, and what was not.

His watch on his phone is the final check. Nothing is "done" before he says so.

## 7. Files

- `pipeline/`: the scripts, one job each, numbered in the order they run.
- `pipeline/remotion/`: the layout, captions and overlays (Remotion, which builds video
  from code).
- `sfx/`: the sound palette. `make_sfx.py` builds our own sounds.
- `LESSONS.md`: every note, newest at the bottom.
- `IMPROVEMENTS.md`: what made each video better than the last.
- `THIRD_PARTY.md`: where anything borrowed came from, and its licence.
- `projects/<name>/`: raw footage and working files for one video. Git ignores it.

Every script opens with a header: what it is, why it exists, what it must never do.
Labelled, numbered sections inside. Written for the slowest engineer in the room.

## 8. Skills

Skills live in `.claude/skills/`. **Anything done more than twice becomes a skill.**
When a skill fails, it stops at the failing step and says which. Fix the cause, or fix
the skill in the same change and say so. Never skip a step.

| Job | Skill |
|---|---|
| The whole edit of a talking video with a phone screen | `vertical-edit` |
| Get footage from Google Drive | `drive-footage` |
| Line up two recordings, find the drift | `sync-recordings` |
| Captions from his transcript | `transcript-captions` |
| Cut it tight: opening, repeats, fillers, tics, silences | `cut-plan` |
| Speed his speech up or down ("speed it up a bit" = 1.1) | `speed-change` |
| Blur names and emails | `privacy-blur` |
| Sound effects and the final mix | `sound-mix` |
| Learn from somebody else's video | `study-reference` |
| Turn a note from Anthony into a rule | `lesson` |
