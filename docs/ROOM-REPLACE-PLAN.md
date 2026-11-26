# Plan: a clean cutout when he puts a studio background behind a talking head

Recorded 2026-11-26, from Anthony's note. **Not started.** We try it on his next talking-head video.

## What he wants

He films a bright, well-lit talking head. He wants to put any studio picture behind him and have it blend, with
**no outline, halo, blur or shadow around his body**, especially when he moves his neck or body. He has bought lights.

## Why an outline shows (four causes)

1. **Old-room colour leaks into the edge** (hair, shoulders, ears). The old wall is still mixed into the edge pixels.
2. **The cutout (the "matte") is rough or jitters** between frames when he moves.
3. **The light does not match.** A bright face on a dim picture looks pasted on.
4. **Nothing grounds him.** No soft shadow, no light from the new picture on his edge.

## What we do about each

| Cause | Fix | Where |
|---|---|---|
| 1. Colour leak | Edge un-mix with a clean plate (already in `pipeline/room/plate.py`). Check it on the new background. | `room/` |
| 2. Rough matte | Run a side-by-side test on his hardest frames: Robust Video Matting (what we use now) against MatAnyone and BiRefNet. Same frames, same new background, he picks. **Not tested yet: do not promise any of them.** | test script, then `room/` |
| 3. Light mismatch | Match the new picture's brightness and colour to his face (a simple grade), and add a thin "light wrap": a little of the new picture's colour spilled onto his edge. | `room/assemble.py` |
| 4. No grounding | A very soft shadow under and behind him; a 1 to 2 pixel soft edge on the matte (never a hard edge). | `room/assemble.py` |

Also smooth the matte over time (a small blend with the frame before and after), so it does not shimmer.

## How he films (this helps more than any software)

1. One light in front of him, slightly to one side. A second, softer light on the plain wall behind if he can.
2. Sit about 1 metre or more away from the wall, so his shadow does not fall on it.
3. A plain wall, not a patterned curtain.
4. One colour of light, not mixed.
5. Lock the camera's focus and exposure.
6. Record about 3 seconds of the empty room first (the clean plate).
7. Ask for a 20 second test under the new lights before the real video.

## Steps when we start

1. He sends a 20 second test clip under the new lights, and tells us which studio picture he wants.
2. Run the matte test (RVM, MatAnyone, BiRefNet) on 5 hard frames. Show him side by side. He picks.
3. Build the light match, light wrap, soft edge and shadow into `pipeline/room/`.
4. Render with the cached, parallel renderer (`pipeline/vlog_render.py` shows the method) so a change costs minutes, not an hour.
5. Turn it into a skill, `room-replace`, once he approves the look.

## Never

Never change his face, body or voice. Only the background. Never promise a tool before it has run on his footage.
