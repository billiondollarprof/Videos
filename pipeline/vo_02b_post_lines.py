# ============================================================
# VO 02b POST LINES: one tall, clean picture of the post, and which line he reads at each word
# What : 1. stitches two stills of the scrolled post (top and bottom) by matching rows, from
#           just under the phone's top bar (status bar and app header cut off) to the date line
#        2. reads the text with tesseract and matches it to his caption words (difflib), so every
#           word he reads knows its line on the post. Lone matches inside his commentary are dropped.
# Why  : when the post is on screen, the line he is reading is highlighted and the page scrolls
#        with him (his note, 2026-11-07: "show where exactly I am reading").
# In   : top.png, bottom.png (stills), caps.json, and in vo_config.json: post_top_px (first row
#        to keep, under the app header), post_bottom_px (last row of the bottom still), and
#        post_blank (boxes to paint black, e.g. the screen recorder's floating button)
# Out  : post/tall.png, readlines.json
# Use  : python3 vo_02b_post_lines.py post/f0.3.png post/f12.9.png
# Never: never keep the status bar (time, signal, battery). Check tall.png by eye.
# ============================================================
import json, re, subprocess, sys, difflib
import numpy as np
from PIL import Image, ImageDraw

P = json.load(open("vo_config.json"))
TOP, BOT = P.get("post_top_px", 280), P.get("post_bottom_px", 1790)

# --- 1. Stitch: find how far the page scrolled between the two stills ---
a = np.asarray(Image.open(sys.argv[1]).convert("RGB")); b = np.asarray(Image.open(sys.argv[2]).convert("RGB"))
ga, gb = a.mean(2), b.mean(2)
cut = 2100                                                  # rows of the top still we keep
off = min(range(300, cut - 100), key=lambda o: np.abs(ga[cut - 400:cut - 200] - gb[cut - 400 - o:cut - 200 - o]).mean())
tall = Image.fromarray(np.vstack([a[TOP:cut], b[cut - off:BOT]]))
for box in P.get("post_blank", []): ImageDraw.Draw(tall).rectangle(box, fill=(0, 0, 0))
tall.save("post/tall.png"); print("scroll offset", off, "tall", tall.size)

# --- 2. Read the lines and match them to the spoken words ---
subprocess.run(["tesseract", "post/tall.png", "post/tall", "--psm", "4", "tsv"], capture_output=True)
rows = [l.split("\t") for l in open("post/tall.tsv").read().splitlines()[1:]]
words = [r for r in rows if r[0] == "5" and r[11].strip()]
lines = {}
for r in words:
    k = (r[2], r[3], r[4]); t, h = int(r[7]), int(r[9]); lo, hi = lines.get(k, (9e9, 0))
    lines[k] = (min(lo, t), max(hi, t + h))
n = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())
C = json.load(open("caps.json"))
m = difflib.SequenceMatcher(None, [n(c["w"]) for c in C], [n(r[11]) for r in words], autojunk=False)
L = [None] * len(C)
for bl in m.get_matching_blocks():
    for d in range(bl.size):
        r = words[bl.b + d]; L[bl.a + d] = lines[(r[2], r[3], r[4])]
for i in range(len(L)):                                     # a word needs 3 mapped neighbours to count
    if L[i] and sum(1 for j in range(i - 3, i + 4) if 0 <= j < len(L) and L[j]) < 4: L[i] = None
json.dump(L, open("readlines.json", "w"))
print("words on the post:", sum(x is not None for x in L), "of", len(C))
