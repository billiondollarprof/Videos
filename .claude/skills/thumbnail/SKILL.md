---
name: thumbnail
description: Make a YouTube thumbnail (1280 x 720) from Anthony's real photo - background removed only, face and body never changed - in the style of his channel. Use when he asks for a thumbnail, or when a long video is ready to upload.
---

# Thumbnail

## Rules (his, 2026-11-05)
- **Use his real photo.** Remove the background only. Never redraw, retouch, reshape or "enhance"
  his face or body. Image generators spoil faces: they never touch him.
- The thumbnail title is **different from the video title**: a short punchy hook.
- Canva: only by hand, never by sending it a prompt. Canva's tools here can only edit a design
  that already exists, and the only way to make one is an AI brief, so build it in code instead,
  and offer to import the finished image into Canva if he wants to tweak it there.
- Match his channel: bold words on the left (white and yellow, thick dark outline), his face large
  on the right, a bright blue background, a pill with the benefit ("100% FREE" style). His existing
  thumbnails: "STOP UPLOADING FILES TO CHATGPT!", "MORE CHATGPT 100% FREE".
- Only claim what the video shows. A number on the thumbnail must be a number from the video
  (video 1: "9,700", the count Claude gave on screen).
- Crop so no shirt logo shows.

## Steps
1. His photo comes from Drive ("My Brand Photo"). Never commit it.
2. `python3 ../../pipeline/14_cutout.py photo.jpg cutout.png` (rembg). Look at it on a blue
   background: ceiling, door and curtain must be gone and the outline smooth. If a loose line is
   left, the script already removes disconnected specks; never erase with a rectangle.
3. Build the `Thumb` composition (see `pipeline/endcard/Root.tsx`): cut-out bottom-aligned on the
   right, head about 60 px from the top, text on the left, pill at the bottom.
4. `npx remotion still src/Root.tsx Thumb thumb.png --frame=0`, export a JPG at quality 92
   (YouTube allows up to 2 MB; this comes to about 200 KB).
5. Zoom into the shoulder outline and the corners to check for specks and notches.
6. Send it with 2 or 3 title options for the video (different from the thumbnail words).

## Video 1 example
Thumbnail: "STOP DELETING EMAILS!" + envelope with a red "9,700" badge + "CLAUDE DOES IT FREE".
Video title options: "How to Clean Your Gmail with Claude (Free)"; "Clear 9,700 Emails Without
Deleting One by One"; "Let Claude Clean Your Gmail Inbox for You (Free Plan)".
