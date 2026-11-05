---
name: privacy-blur
description: Find and blur email addresses and other people's names on a screen recording, by Anthony's rules, and prove none was missed. Use for every screen recording that will be published.
---

# Privacy blur

Rules (CLAUDE.md section 5): email start blurred, "@gmail.com" kept; other people's
surnames blurred; a name in a greeting that is not his blurred fully; a public business
account may stay.

1. Look at stills from the whole recording first, and **list every private detail** you
   see: names, emails, phone numbers, addresses. Tell Anthony what you found and which
   rule covers each. Ask about anything the rules do not cover.
2. Fill `project.json` `privacy`: `surnames`, `always_blur`, `keep`, `email_parts`
   (pieces of his own address the reader may split off). These stay out of git.
3. `python3 ../../pipeline/07_ocr.py` (reads the text on every changed frame; about a
   minute).
4. `python3 ../../pipeline/08_make_mask.py` builds `mask.mkv`.
5. Anything that moves or slides in faster than the reader can catch (a list sliding
   up, a greeting moving while he types): add a box to `extra_spans` covering both
   positions for that moment.
6. After `09_build_tracks.py`: check stills at every moment a detail appeared, then
   **scan the whole cut screen** for the unblurred text (template match or a second
   text read). A readable name scores about 1.0; a blurred one about 0.5.
7. Tell Anthony which details were blurred and which were left, and why.

## A clip that scrolls (B-roll of an inbox or a feed)
Text reading misses words on moving lists, and scroll tracking (`08b_track_mask.py`) can lock
onto the wrong row because rows look alike. The safe way: lightly blur the whole list
(`boxblur=9:3`) so it still reads as a busy inbox, keep only bars with nothing private sharp,
and check the bottom strip of every sampled frame. Say on screen what the viewer should take
from it (on video 1: "About 9,700 promotions", the real number Claude gave him).
