# ============================================================
# FACE TRACK
# What : finds Anthony's face in face_cut.mp4, 10 times a second, and writes where its
#        centre is (0 to 1 across, 0 to 1 down) to faceTrack.json, smoothed over 1 second.
# Why  : in the circle his face drifted right when he moved (his note on version 1).
#        People.tsx uses this to keep the face centred.
# Use  : python3 09b_face_track.py face_cut.mp4 remotion/src/faceTrack.json [yunet.onnx]
# How  : YuNet (a small, free face detector built into OpenCV; model file models/yunet.onnx,
#        from huggingface.co/opencv/face_detection_yunet).
#        A frame where no face is found keeps the last known position.
# ============================================================
import json
import subprocess
import sys

import cv2
import numpy as np

VIDEO, OUT = sys.argv[1], sys.argv[2]
W, H, RATE = 360, 640, 10            # read a small copy, 10 frames a second

# --- 1. Small frames ---
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", VIDEO, "-vf", f"fps={RATE},scale={W}:{H},format=gray",
                      "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
frames = np.frombuffer(raw, dtype=np.uint8).reshape(-1, H, W)

# --- 2. Find the biggest face in each frame ---
finder = cv2.FaceDetectorYN.create(sys.argv[3] if len(sys.argv) > 3 else "models/yunet.onnx", "", (W, H), 0.6)
centres, last, found = [], (0.5, 0.55), 0
for f in frames:
    _, faces = finder.detect(cv2.cvtColor(f, cv2.COLOR_GRAY2BGR))
    if faces is not None and len(faces):
        x, y, w, h = max(faces, key=lambda r: r[2] * r[3])[:4]
        last = ((x + w / 2) / W, (y + h / 2) / H)
        found += 1
    centres.append(last)

# --- 3. Smooth it, so the circle glides instead of jittering ---
c = np.array(centres)
k = 10                                # 1 second either side
pad = np.pad(c, ((k, k), (0, 0)), mode="edge")
smooth = np.array([pad[i:i + 2 * k + 1].mean(axis=0) for i in range(len(c))])
json.dump([[round(float(a), 4), round(float(b), 4)] for a, b in smooth], open(OUT, "w"))
print(f"{len(c)} readings, face found in {found} ({100 * found / len(c):.0f}%), "
      f"across {smooth[:, 0].min():.2f} to {smooth[:, 0].max():.2f}")
