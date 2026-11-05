---
name: study-reference
description: Learn editing ideas from somebody else's video cheaply - pace, hook, structure, cut rate, captions, sound - and write what is worth copying into LESSONS.md. Use when Anthony shares a video he likes.
---

# Study a reference video

Cheap means: never watch it whole. Measure it, and look at a few grids of stills.

## What works today
1. **Captions only** (works for most YouTube links):
   `yt-dlp --skip-download --write-auto-subs --sub-langs en --sub-format vtt -o ref <link>`
   From them: words per minute, the first 30 seconds (the hook), how it turns to the
   viewer, and how it ends.
2. **YouTube refuses video downloads from this machine** (a bot check). Never try to get
   round it. If the pictures matter, Anthony either:
   - downloads it on his phone where he is allowed to and uploads it to Drive, or
   - screen-records the 1 or 2 minutes he likes and uploads that.

## With the video file
1. Cuts: `ffmpeg -i ref.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null -` gives the
   time of every cut. Shots per minute = the pace.
2. One still per shot, in grids of 20: `tile=5x4`. 10 to 20 grids cover a long video.
   Look at those, not the video.
3. Sound effects: loud short peaks in the sound away from the voice (a spectrogram
   picture of 30 seconds shows them).
4. Write what to copy into `LESSONS.md` as rules, with the reference named. Copy ideas
   and techniques, never their footage, music or graphics.

## Video 1 reference (Patrick Dang, "The New Way to Make Money with AI at Night")
209 words a minute with no dead air. A bold claim as the first sentence. Within 30 s:
"this video isn't about me... a roadmap for you". Music under the voice from the start.
Ends by pointing to another video.
