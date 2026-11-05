---
name: short-cut
description: Turn a finished long video into a short for Instagram Reels, YouTube Shorts and TikTok that stops at a hook and sends people to the full video on YouTube. Use when Anthony says "cut it into two", "make the short", "a version for Reels", or wants people dragged to his YouTube. No long re-render.
---

# Short cut

Platforms limit shorts to 3 minutes, and he wants the shorts to pull people to his YouTube
channel. The full video goes on YouTube as it is. The short is the finished video **trimmed at a
hook**, plus a 5 second end card. Nothing is re-rendered except the end card (about 50 seconds).

## 1. Pick the hook (the cut point)
1. Transcribe the finished video with the medium model (`01b_transcribe_fillers.py`), print the
   sentences with times, and read from about 1:00 to 2:30.
2. A good hook is a moment where a viewer needs the next sentence: a question just asked with the
   choice on screen, a number about to be revealed, "step 3" about to start, a result about to
   show. Video 1: "How do you want to approve the deletion?" at 1:53, with both options on screen.
3. Aim for 1:30 to 2:30. Never cut mid-sentence, and never right before the payoff is spoken.
4. **Cut inside a silence**: print the sound level every 30 ms around the end of the last word,
   pick the quietest moment (video 1: 113.83 s, -58 dB, 70 ms before the next word). Tell him the
   cut point and the words either side. He can move it.

## 2. The end card
1. Needs his YouTube page screenshot (he uploads it to Drive; it stays out of git) and the handle.
2. Copy `pipeline/endcard/` into a Remotion project (`Root.tsx`, `Background.tsx`, `theme.ts`,
   `remotion.config.ts`, the font, `public/youtube_page.jpg`). Size must match the video.
3. `npx remotion render src/Root.tsx Continue endcard.mp4 --muted` (5 s, about 50 s to render).
4. Look at 3 stills: headline in, page scrolling, name and handle in.
5. Only say what the screenshot shows. No "link in bio", no promise, unless he says so.

## 3. Cut and join
`python3 ../../pipeline/13_short_cut.py full.mp4 <cut seconds> endcard.mp4 short.mp4`
It trims at the cut, adds the card with a whoosh, a tap and a tick, sets -14 LUFS with peaks
below -1.5 dB (measured on the encoded file), and prints the result.

## 4. Check, then send
1. Stills at the last second of the video part and each part of the end card.
2. Transcribe the last 8 seconds of the short: the last word must be whole and the next word
   must not leak in.
3. Send it to him. He posts the same short on all three platforms.

## Not done yet (asked for later)
- A "subscribe and ring the bell" animation on the end card. He said skip it for now.
