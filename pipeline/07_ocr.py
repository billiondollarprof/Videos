# ============================================================
# 07 OCR: read the text on the screen recording
# What : reads every word on the screen, twice a second, with tesseract (a free
#        text-reading tool), so 08_make_mask.py can find names and emails to blur.
# Why  : a few stills miss things. On video 1 an email showed on 23 different frames.
# Speed: only frames that changed are read (277 of 961 on video 1), at normal size.
#        Reading at double size was 100 times slower and found nothing more.
# Use  : python3 07_ocr.py
# Out  : ocr_out/f_NNNN.tsv (one per read frame), ocr_reuse.json (which read frame
#        stands for each half second)
# ============================================================
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

import numpy as np

P = json.load(open("project.json"))
os.makedirs("ocr", exist_ok=True)
os.makedirs("ocr_out", exist_ok=True)

# --- 1. Frames, twice a second, in grey ---
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", P["screen_video"], "-vf", "fps=2,format=gray",
                "ocr/f_%04d.png"], check=True)
frames = sorted(os.listdir("ocr"))

# --- 2. Which frames changed? Compare small copies ---
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", P["screen_video"], "-vf", "fps=2,scale=216:480,format=gray",
                "-f", "rawvideo", "small.raw"], check=True)
small = np.fromfile("small.raw", dtype=np.uint8).reshape(-1, 480, 216).astype(np.float32)
reuse, keep, last = {}, [], None
for k in range(1, min(len(frames), len(small)) + 1):
    f = small[k - 1]
    changed = last is None or np.abs(f - small[last - 1]).mean() > 0.6 \
        or (np.abs(f - small[last - 1]) > 40).mean() > 0.002
    if changed:
        keep.append(k)
        last = k
    reuse[k] = last
json.dump(reuse, open("ocr_reuse.json", "w"))
print(f"reading {len(keep)} of {len(reuse)} frames")


# --- 3. Read them, 4 at a time ---
def read(k):
    out = subprocess.run(["tesseract", f"ocr/f_{k:04d}.png", "-", "--psm", "11", "tsv"],
                         capture_output=True, text=True, env={**os.environ, "OMP_THREAD_LIMIT": "1"}).stdout
    rows = [r.split("\t") for r in out.splitlines()[1:]]
    with open(f"ocr_out/f_{k:04d}.tsv", "w") as fh:
        for r in rows:
            if len(r) >= 12 and r[11].strip():
                fh.write("\t".join([r[6], r[7], r[8], r[9], r[11]]) + "\n")


with ThreadPoolExecutor(4) as pool:
    list(pool.map(read, keep))
print("done")
