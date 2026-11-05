# ============================================================
# 09c SOFT BACKGROUND: a little blur and a soft light behind him
# What : separates Anthony from his background in every frame of the face video, then
#        1. blurs the background a little (not a heavy "portrait mode" blur),
#        2. dims it a little and adds two coloured lights (blue left, red right),
#        3. darkens the edges of the background a little more,
#        and puts him back on top, untouched.
# Why  : his note (2026-11-05): "a little blurring of my background... more focus on my own
#        body... a very little soft lighting... while still keeping everything okay".
# How  : MediaPipe's selfie segmenter (a small free model that marks which pixels are a
#        person; models/selfie_segmenter.tflite). The mask is smoothed over time so the
#        edge never flickers, and feathered so the edge is soft.
# Use  : python3 09c_soft_background.py face_cut.mp4 face_soft.mp4 [--still SECONDS out.png]
# Never: never change his face or body. Only pixels the model marks as background change.
# ============================================================
import subprocess
import sys

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision

SRC, OUT = sys.argv[1], sys.argv[2]
STILL = float(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[3] == "--still" else None
W, H, FPS = 720, 1280, 30

# --- 1. The look (change these to taste) ---
# v3 (his note on version 2): less blur, a darker background so the light shows, and a
# coloured light: blue from one side, red from the other.
BLUR_SIGMA = 2.5            # background blur: small = "a little"
DARKEN = 0.62               # the whole background is dimmed to this, so the lights show
LIGHTS = [                  # (across, down, size, strength, colour R G B)
    (0.00, 0.28, 0.36, 0.30, (60, 110, 255)),    # blue, from the left
    (1.00, 0.36, 0.36, 0.26, (255, 60, 90)),     # red, from the right
]
EDGE_DARKEN = 0.25          # how much the background edges darken further
MASK_SMOOTH = 0.55          # 0 = no smoothing over time, closer to 1 = smoother

# --- 2. The light and edge-darkening maps, made once ---
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
light_maps = []
for lx, ly, size, strength, colour in LIGHTS:
    d = np.sqrt(((xx / W - lx) * W / H) ** 2 + (yy / H - ly) ** 2)
    light_maps.append((np.exp(-(d / size) ** 2)[..., None] * strength, np.array(colour, np.float32)))
dv = np.sqrt(((xx / W - 0.5) * 1.2) ** 2 + ((yy / H - 0.45) * 1.0) ** 2)
vignette = (1 - EDGE_DARKEN * np.clip((dv - 0.25) / 0.45, 0, 1) ** 1.5)[..., None]

seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=mpt.BaseOptions(model_asset_path="models/selfie_segmenter.tflite"), output_confidence_masks=True))


def process(rgb, prev_mask):
    # 3a. where he is, smoothed over time and feathered at the edge
    m = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)).confidence_masks[0].numpy_view()
    m = np.clip(m.reshape(H, W), 0, 1).astype(np.float32)
    if prev_mask is not None:
        m = MASK_SMOOTH * prev_mask + (1 - MASK_SMOOTH) * m
    soft = cv2.GaussianBlur(m, (0, 0), 3)[..., None]
    # 3b. the background: a little blur, the warm light, the darker edges
    f = rgb.astype(np.float32)
    bg = cv2.GaussianBlur(f, (0, 0), BLUR_SIGMA)
    bg = bg * DARKEN * vignette
    for amount, colour in light_maps:             # each light adds its colour, like a gel
        bg = bg + colour * amount * (1 - bg / 255) # "screen" blend: brightens, never clips hard
    # 3c. him on top, untouched
    out = soft * f + (1 - soft) * bg
    return np.clip(out, 0, 255).astype(np.uint8), m


# --- 4. One test frame, or the whole video ---
if STILL is not None:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(STILL), "-i", SRC, "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    img, _ = process(np.frombuffer(raw, np.uint8).reshape(H, W, 3), None)
    cv2.imwrite(sys.argv[5], cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    sys.exit(0)

dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "fast", "-crf", "16",
                        "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
prev, n = None, 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    img, prev = process(np.frombuffer(buf, np.uint8).reshape(H, W, 3), prev)
    enc.stdin.write(img.tobytes())
    n += 1
enc.stdin.close()
enc.wait()
print("frames:", n)
