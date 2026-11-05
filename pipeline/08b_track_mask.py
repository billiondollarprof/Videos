# ============================================================
# 08b TRACK MASK: blur that follows a scrolling list
# What : for a clip that scrolls (an inbox, a feed), measures how far the list moves
#        between frames, then carries every box 08_make_mask.py found onto EVERY frame
#        where that spot of the list is visible. One good reading covers the whole clip.
# Why  : the text reader misses words on some frames of a moving list (video 1: it read
#        "Copy code: 852029" as "coe )" for the first second). Tracking fixes that.
# Use  : after 07_ocr.py with "ocr_fps" set to the clip's frame rate, and after
#        08_make_mask.py (which writes mask_spans.json). Writes mask.mkv again.
# Never: a box is never dropped. If the scroll cannot be measured (a cut to another
#        screen), the tracking starts a new "scene" and boxes stay within their scene.
# ============================================================
import json
import subprocess

import numpy as np

P = json.load(open("project.json"))
OCR_FPS = P["ocr_fps"]
probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
    "stream=width,height,r_frame_rate:format=duration", "-of", "json", P["screen_video"]],
    capture_output=True, text=True).stdout)
W, H = probe["streams"][0]["width"], probe["streams"][0]["height"]
SW, SH = 216, int(round(216 * H / W))        # small copy used to measure the scroll
SCALE = H / SH

# --- 1. Small grey frames, one per reading ---
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", P["screen_video"], "-vf",
                f"fps={OCR_FPS},scale={SW}:{SH},format=gray", "-f", "rawvideo", "track.raw"], check=True)
F = np.fromfile("track.raw", dtype=np.uint8).reshape(-1, SH, SW).astype(np.float32)
N = len(F)

# --- 2. Scroll between neighbouring frames, measured in the middle band of the screen ---
# The top bar (search) and bottom bar (tabs) do not scroll, so they are left out.
top, bot = int(SH * 0.12), int(SH * 0.88)
offset = np.zeros(N)                         # how far the list has scrolled, in small pixels
scene = np.zeros(N, dtype=int)
for i in range(1, N):
    a, b = F[i - 1][top:bot], F[i][top:bot]
    best = (1e9, 0)
    for dy in range(-60, 61):                # positive: content moved up (scrolled down)
        if dy >= 0:
            d = np.abs(a[dy:] - b[:len(b) - dy]).mean() if dy else np.abs(a - b).mean()
        else:
            d = np.abs(a[:dy] - b[-dy:]).mean()
        if d < best[0]:
            best = (d, dy)
    if best[0] > 18:                         # nothing lines up: a new screen
        scene[i] = scene[i - 1] + 1
        offset[i] = 0
    else:
        scene[i] = scene[i - 1]
        offset[i] = offset[i - 1] + best[1]
print("scenes:", scene.max() + 1, "| largest scroll:", int(abs(offset).max() * SCALE), "px")

# --- 3. Every box, in list coordinates, copied to every frame of its scene ---
spans = json.load(open("mask_spans.json"))
step = 1 / OCR_FPS
boxes_by_frame = [[] for _ in range(N)]
for t0, t1, x0, y0, x1, y1 in spans:
    k = min(N - 1, max(0, int(round(((t0 + t1) / 2) * OCR_FPS))))   # the frame it was seen on
    in_list = top * SCALE <= (y0 + y1) / 2 <= bot * SCALE
    for j in range(N):
        if scene[j] != scene[k]:
            continue
        shift = (offset[j] - offset[k]) * SCALE if in_list else 0
        if not in_list and abs(j - k) * step > 0.6:
            continue                         # fixed bar items: only near where they were seen
        boxes_by_frame[j].append((x0, y0 - shift, x1, y1 - shift))

# --- 4. Write the mask at the clip's own frame rate ---
num, den = probe["streams"][0]["r_frame_rate"].split("/")
CLIP_FPS = int(num) / int(den)
total = int(float(probe["format"]["duration"]) * CLIP_FPS) + 1
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}",
                       "-r", f"{CLIP_FPS}", "-i", "-", "-c:v", "ffv1", "mask.mkv"], stdin=subprocess.PIPE)
for n in range(total):
    j = min(N - 1, int(n / CLIP_FPS * OCR_FPS))
    m = np.zeros((H, W), np.uint8)
    for x0, y0, x1, y1 in boxes_by_frame[j]:
        m[max(0, int(y0)):max(0, int(y1)), max(0, int(x0)):min(W, int(x1))] = 255
    ff.stdin.write(m.tobytes())
ff.stdin.close()
ff.wait()
print("tracked mask written:", total, "frames")
