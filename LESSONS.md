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
| End card: never show the subscriber count, never the whole channel. Only the header (photo, name, handle), in YouTube's red with a big play button and a sound. Do not tell people to find a "link in bio". | `short-cut` step 2, `pipeline/endcard/Root.tsx` |
| Thumbnail hook: "Stop deleting emails. Do this instead." beats "Claude does it for you" (that gives the answer away). Keep the verbs exact: Claude trashes, one conversation per call. | `thumbnail` |

## Notes for later, from Anthony (2026-11-06)

| Note | Now lives in |
|---|---|
| His voice must never be changed: it is unique. Only clean, balance and even it out. A little low warmth only if he has heard it A/B and approved. | CLAUDE.md 5 (Sound 0), `IMPROVEMENTS.md` plan 3 |
| He is getting a mic: make the sound feel like a strong mic, still his own voice. A voice profile he picks by ear. | `IMPROVEMENTS.md` plan 3 |
| He is getting a light: a darker room, white light on his face. | `IMPROVEMENTS.md` plan 2 |
| Prefer his own room, improved (cut him out, clean the empty background, sharpen, brighten, remove stains, put him back), over a replacement. One or several backgrounds depending on whether he moved. | CLAUDE.md 5 (Look 5a), `IMPROVEMENTS.md` plan 1 |

## Voiceover video 1 (2026-11-07)

| Note | Now lives in |
|---|---|
| Under 3 minutes. Do it once and do it well. Make it clean. | `voiceover-edit` step 3 |
| "Our papa" means the President: put it in quotes in the captions. | `voiceover-edit` step 6 |
| Follow the post's wording where he reads it. He said 33 states. Fix mishearings from what is on screen. | `voiceover-edit` step 6 |
| Repetitions: the first take is usually the mistake. Keep the later one. | `voiceover-edit` step 5, `cut-plan` |
| Do not fast-forward. Cut pauses but keep short breaths. | `vo_01_cut.py` |
| Animate the pictures: light flowing across, light zoom, movement on every shot. | `vo_03_render.py`, `voiceover-edit` |
| Record every step, and turn new work into a skill. | `voiceover-edit`, this file |
| No faces of people in pictures. | `voiceover-edit` step 7 |
| The screen share must read properly, with the phone top cut off. Show exactly the line I am reading at that moment. | `vo_02b_post_lines.py`, `vo_03_render.py`, `voiceover-edit` step 7 |

## Found while editing voiceover video 1

- A claim in his commentary (Benue) did not match his own research (Plateau). Cut it and told him.
- A false start (a restarted phrase) hid inside one
  2-second "word" in the raw times. Found with a loudness plot. Now `voiceover-edit` step 5.
- The filler prompt made Whisper invent "Obi," before each sentence of the cut voice, and call
  the first 28 s laughter. Check the cut voice without the prompt.
- Zooming a phone post cuts text at the sides. Posts get only a 4% zoom; the highlight carries the eye.

## Voiceover video 1, notes on version 1 (2026-11-07)

| Note | Now lives in |
|---|---|
| The opening showed the post. Open on a moving picture instead. | `vo_03_render.py` header, `voiceover-edit` step 7 |
| "Obi, Obi" at every joint. Cause: the room tone was one second taken from one spot, and that spot was his voice. Room tone is now built from the 200 quietest slices, and checked. | `vo_01_cut.py` section 3 |
| Gaps still a little too long. Pauses now 0.06 s inside a sentence, 0.16 s between, 0.22 s at a cut. | `vo_config.example.json`, `voiceover-edit` |
| Repeats were still in. Two were hidden inside words Whisper stretched over 2 to 4 s. Every raw word longer than 0.9 s is now re-listened to on its own. | `voiceover-edit` step 5 |
| Add music: without it the video does not flow. Our own music, made in code. | `music/make_music.py`, `vo_04_mix.py` |
| Motion was not top notch. Pictures rise from the bottom with a soft bounce while the old one leaves upward. Cards float and tilt. The post is a floating sheet that moves while he reads. Labels and caption words pop. | `vo_03_render.py` |
| A picture must arrive with the words it shows: the candle came in on the power line, before kidnapping was mentioned. Anchor each picture to the exact phrase it illustrates, not to the start of the sentence before. | `voiceover-edit` step 7 |
| "M" sounds and a repeat at the end. A cut had left half of "making" and an "um". Cuts are now set on the loudness plot, at the silence between words, never inside a word. | `voiceover-edit` step 5 |

## Voiceover video 1, notes on version 2 (2026-11-07)

| Note | Now lives in |
|---|---|
| While he reads the post, a picture is a short insert (2 to 3 s) on the exact words it shows, then the video goes back to the post, on the line he is reading, before the next picture. Pictures only stay long while he comments. | `vo_03_render.py` (`add(..., dur=, back=True)`), `voiceover-edit` step 7 |
| Pictures stayed too long. Make 2 to 4 AI pictures for his commentary (prompts in the skill). | `voiceover-edit` step 7 |
| Pops, not whooshes, for pictures in a voiceover (no camera, the pictures are graphics): a soft pop with a tiny air swipe when a picture arrives, a lower pop when it goes back to the post. One camera shutter on the hook and one on the end card. | `sfx/make_sfx.py`, `vo_04_mix.py` |
| The food came too early. Food on "delicious cuisine", the map on "Akwa Ibom", each short, with the post between. | `voiceover-edit` step 7 |
| The last word ("accountable") was cut off. The end mark was set on the loudness plot at the end of the last word, not after it. Keep 0.4 s after his last word, then a 0.3 s breath before the end card. | `voiceover-edit` step 4 |

## Voiceover video 1, notes on version 3 (2026-11-07)

| Note | Now lives in |
|---|---|
| I can only hear whoosh, no pop. Cause: the pops sat 18 dB under the voice, and a small air swipe under each one sounded like a whoosh. Pops now mix about as loud as the voice, with no swipe and no whoosh. After mixing, measure the pop level against the voice. | `vo_04_mix.py`, `sfx/make_sfx.py` |
| The music was not nice: "ting ting ting", fake. If no soft tone can be found, no music. Music is off by default. The code-made bed (plucks, hi-hats) is not good enough: for music, use TikTok's library or YouTube's Audio Library. | `vo_04_mix.py` (`--music`), `music/make_music.py` header |
| Pop, pop, pop on every transition, please. | `vo_04_mix.py` |

## Voiceover video 1, notes on version 4 (2026-11-08)

| Note | Now lives in |
|---|---|
| "This part cracked me up": show someone laughing, or his own laughing photo, not clapping hands. | `voiceover-edit/prompts.md` |
| Kidnapping line: show people being taken away by force (illustrated, invented characters, no blood), not a candle vigil. | `voiceover-edit/prompts.md` |
| "Playing opposition": one more picture, invented Nigerian politicians against the government, as a semi-realistic cartoon (his usual style for this). Invented characters are fine; real people are not. Inserts are quick. | `voiceover-edit/prompts.md` |
| Match each picture to the words, not the topic around them. | `voiceover-edit` step 7 |
| Remove the clapping hands and the candle vigil: they make no sense for the words. Laughter line: a picture of young Nigerians laughing, one laughing hardest, shown briefly. Kidnapping line: the illustrated picture of people being taken away. Opposition lines: ballot boxes, the chamber and the politicians facing the government, each a quick insert. | `voiceover-edit` step 7 |
| He names files by hand and not always in order: look at each picture and match it by what it shows, then say the mapping back. | `voiceover-edit` step 1 |

## Voiceover video 1, notes on version 5 (2026-11-08)

| Note | Now lives in |
|---|---|
| An underlying background sound and small cracks are still there. Voice cleaner, purer, without changing it. Even with no music it must sound nice. | `04c_polish_voice.py`, `vo_01_cut.py` |
| Cause 1: low rumble (120 to 250 Hz) in the pauses, lifted by the loudness step. Fixed by a gentle second clean-up: pauses went from -64 dB to -83 dB, voice level and tone unchanged. | `04c_polish_voice.py` |
| Cause 2: the "cracks". 67 of 91 pieces began with the voice already loud, because the lead-in was only 0.03 s, so the fade-in clipped the start of a word. Lead-in is now 0.07 s, tail 0.09 s, fades 12 and 15 ms. Now 5 of 91. | `vo_01_cut.py` |
| The polish step delays the sound by 25 ms. It is measured and removed in the script, so cuts do not move. | `04c_polish_voice.py` |

## Voiceover video 1, notes on version 6 (2026-11-08)

| Note | Now lives in |
|---|---|
| Opening picture: a semi-realistic AI picture of Peter Obi cooking a cap in a pot, as satire. He checked that satire is allowed. | `vo_shots.py` (his project), `voiceover-edit` |
| An AI picture of a real person carries a small "AI-GENERATED SATIRE" tag on screen, and he switches on the platform's AI label when posting. A tall picture is shown whole (`full=True`), never cropped through the joke. | `vo_03_render.py` (`tag=`, `full=`, `focus=`) |
| Two files can have the same name in his Drive ("ai 9"): check the creation time and say which one is used. | `voiceover-edit` step 1 |
| Dead air: the polished pauses rounded to exact zero (315 slices, 3 s). The cleaned source also has a few exact-zero stretches, and the "quietest slices" picker chose them. A faint continuous room bed (-76 dB) now runs under the whole voice, built from slices that are never dead-silent. Check: zero slices of dead silence in the cut voice. | `vo_01_cut.py` |
| A "pause floor" measured on the finished file is not comparable to one measured on the cleaned voice (pauses are mostly word tails). Compare the same metric on the previous version. | `voiceover-edit` step 11 |

## Life video 1, "Why Life is Beautiful" (2026-11-25)

| Note | Now lives in |
|---|---|
| A new series: talking-head videos about life, raw files in the Drive folder "Video Editing / Life". | `vertical-edit` (start from it) |
| He trims a little himself first. Still cut the awkward bits, and tighten the joins at the places he already cut. | `cut-plan` |
| He likes the camera shutter with the light flash: keep it for this series. | `sound-mix` |
| He has a mic now: the sound is good. Enhance it and remove any distraction, still his own voice. | `sound-mix` |
| Zoom in and out on his face through the talk (he uses it in his own videos): a punch-in or pull-out every few seconds, at phrase joins. | `vertical-edit` step 4 |
| Short reaction clips that land on certain words (the "surprise" clips in Nigerian videos) make it lively. He brings the clips; we never take them from someone else's video. Check the licence of each, and tell him plainly when a clip is someone else's copyright. | `vertical-edit` step 4 |
| Write him AI picture prompts for moments in what he says. | `voiceover-edit/prompts.md` |
| The video must feel lively and flow. Speed never above 1.1. | `speed-change` |
| His own background, cleaned up and made top notch, still real. Not a replacement. | `IMPROVEMENTS.md` clean-plate plan |
| His first 30 s came 21 dB louder than the rest (his editing app boosted one clip): measure loudness along the whole raw file and level each clip before anything else. | `sound-mix` |

## Reference videos (2026-11-25): three talking-head shorts he likes

- Two from one creator (podcast mic, bookshelf, warm light, shallow depth of field): a cut or zoom
  jump every 1.4 s on average. The frame jumps between wide and close at phrase joins.
  On certain words a 1 to 2 s clip lands: a film or Nollywood reaction, an icon card popping over his
  blurred picture, or a book cover on a grey gradient with a bold title. Then straight back to him.
  Captions: small bold white capitals low in the frame, the spoken word in grey-to-white.
- The third (a creator in front of purple lights and warm lamps): one take, no cuts, no inserts; it
  works on his energy and a lit, colourful room.
- Copy the ideas (pace, punch-ins, quick inserts on exact words, icon cards over a blurred him), never
  their footage.

## Life video 1, answers to the plan (2026-11-25)

| Note | Now lives in |
|---|---|
| Cut list approved: keep "a better life today", the second "you should be", the first and last "little things" (the saying is "little things that matter"). | his project `cut list` |
| Level the loud clip down to the quiet one, never the quiet one up. | `sound-mix` |
| Speed: 1.1 at most, and check first whether it needs any speed-up at all. Try 1.0 and 1.05 before 1.1. | `speed-change` |
| The iPad he holds should show some of the time, clean, with its logo visible. Close zooms may hide it. | `vertical-edit` step 4 |
| His room should look as if he sits further from the wall: more depth behind him. Still his own room, never a fake backdrop. The bookshelf sample was only to show how clean a room can look. | `09c_soft_background.py`, clean-plate plan |

## Life video 1, notes on the room test (2026-11-25)

| Note | Now lives in |
|---|---|
| The cut-out showed: a light fringe round his head, ear and shoulder, and the edge changed as he moved. Anyone could tell it was a cut-out. Nothing may show an edge, ever. Cause: the selfie model's edge is coarse, and the darker, blurred room no longer matched the light edge pixels. | `IMPROVEMENTS.md` clean-plate plan |
| The cleaned door looked smeared and blotchy (my fill-in of the poster and the noise removal). An area I fill in myself must look like the real thing, or it stays as filmed. | `IMPROVEMENTS.md` clean-plate plan |
| His idea: he makes the clean empty room himself from a screenshot in ChatGPT, we put it behind him, but it must never shake or look like a cut-out. | `IMPROVEMENTS.md` clean-plate plan |

## Life video 1, reaction clips and the flip (2026-11-25)

| Note | Now lives in |
|---|---|
| Clips he downloads (Nollywood and skit reactions) are a library for every video: catalogue each clip once, by time: the 1 to 2.5 s moments worth using, the expression, the words, and what kind of line each suits. Any agent reuses the catalogue instead of watching the clips again. | skill `reaction-clips`, `clips/CATALOGUE.md` |
| A picture made as a collage (several in one image) is cut into its single pictures. | skill `reaction-clips` |
| Flip a front-camera video so writing reads the right way, when it costs nothing else. | `vertical-edit` step 1 |
| A new Drive folder is private by default: ask him to share the folder itself ("Anyone with the link"), so every file in it can be downloaded. | skill `drive-footage` |

## Life video 1, notes on tests A2 and B (2026-11-25)

| Note | Now lives in |
|---|---|
| Option B chosen: his ChatGPT room behind him, with the video matting edge. | `IMPROVEMENTS.md` |
| A2: the patch over the poster shimmered and blinked. Cause: the blend was worked out again on every frame, so it changed with the noise. A patch must be computed once and held still (or tracked), never re-blended per frame. | `IMPROVEMENTS.md` (option A notes) |
| B: the room is too bright. Calmer atmosphere: the background darker and softer, less bright green, the light focused on him, a nicer, richer quality. Take the look from his reference shorts (warm, dark room, shallow focus, bright subject). | `IMPROVEMENTS.md` clean-plate plan |
| B v2 room approved, clip plan approved (wide eyes on "gap 2 people", "This is business!" on "sales", Pawpaw "no time for gossip" on "someone else's life"). | his project |
| The edge round his head, neck and shoulders still showed a light rim against the darker room. Blend it: take the old room's light out of the edge pixels (un-mix with the clean plate), then let a little of the new room's light wrap onto his edge. | `IMPROVEMENTS.md` clean-plate plan |

## Life video 1, notes on version 1 (2026-11-25)

| Note | Now lives in |
|---|---|
| Speed 1.1. | `speed-change`, his project |
| Pictures and clips fill the whole screen, as a screen of their own, his voice carrying on underneath. Never a card over his blurred picture. (His reference shorts do this.) | `reaction-clips` B.4, `vertical-edit` |
| Captions too plain: he has put caption samples in Drive to study. | `transcript-captions` |
| Still too bright: stronger corner darkening, softer light overall. | `pipeline/room/room_full.py`, `assemble.py` |
| Zooms too small and too slow: zoom in further and move faster, like his reference shorts (a jump every 1 to 2 s). | `vertical-edit` step 4 |
| Pauses at most about 0.3 s. | `cut-plan` |
| He will regenerate the 3 narrow pictures from the collage. | his project |
| Study the cinematic colour sample he put in Drive and take what enriches the look. | `study-reference` |
| The phone clip (crying girl) after "someone else's life" is the one he meant. | his project |
| The opening is too calm: the captions and things on screen must carry energy from the first second. If 1.1 still feels calm, try 1.2 or 1.3. | `vertical-edit` step 4, `speed-change` |

## His caption and colour samples (2026-11-25)

- **Caption 1** (a creator talking in a warm room): words build up one by one into a stacked phrase
  beside his head. Three voices: small lowercase, a big bold word, a glowing orange italic serif for
  the feeling word ("crazy text", "follow"). Key words in colour (yellow "LOOKS", red "BIG", glowing "LONG").
- **Caption 2** (a creator in a white room): one or two words at a time, large lowercase, soft shadow,
  above her head; emphasis in a small italic serif ("to deliver", "gatekeeping") or bold red ("not").
- **Cinematic colour sample**: warm rich skin, slightly teal shadows, muted colour elsewhere, soft
  contrast with highlights rolled off, dark edges; small captions with one peach accent word.
- Now in `pipeline/room/kinetic.py` (captions) and `grade()` in `pipeline/room/assemble.py` (colour).
  Built in our own code: no outside caption tool was needed. Fonts: Plus Jakarta Sans and Instrument Serif
  Italic (free, SIL Open Font Licence).
