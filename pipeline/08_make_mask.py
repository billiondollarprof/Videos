# ============================================================
# BLUR MASK
# What : builds mask.mkv, a black and white video the same size and length as the raw
#        screen recording. White = blur this spot. build_tracks.py applies it.
# Rules (Anthony, 2026-11-05, also in CLAUDE.md section 5):
#   1. Every email address: blur the part before "@". "@gmail.com" stays readable.
#   2. Names on the Google account chooser: blur the second half (the surname).
#   3. A name that is not his, in a greeting or a list: blurred fully (privacy.always_blur).
#   4. A business account he names as public: left readable (privacy.keep).
#   5. Security codes and account numbers (5 or more digits): always blurred.
# How  : 07_ocr.py read the text on every changed frame into ocr_out/ (tesseract, a free
#        text-reading tool). The names to blur come from project.json, never from this file.
# Never: never leave a gap. Each box is held 0.4 s either side of where it was seen.
# ============================================================
import difflib, glob, json, os, re, subprocess
import numpy as np

P = json.load(open("project.json"))
probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
    "stream=width,height,r_frame_rate:format=duration", "-of", "json", P["screen_video"]],
    capture_output=True, text=True).stdout)
W, H = probe["streams"][0]["width"], probe["streams"][0]["height"]
num, den = probe["streams"][0]["r_frame_rate"].split("/"); FPS = round(int(num) / int(den))
DUR = float(probe["format"]["duration"])
N = int(DUR * FPS) + 1

PAD_PX = 8            # extra pixels around each box
SURNAMES = set(P["privacy"]["surnames"])        # blurred (the second half of a name)
ALWAYS = set(P["privacy"]["always_blur"])       # blurred in full
KEEP = tuple(P["privacy"]["keep"])               # left readable
OWN_EMAIL_PARTS = tuple(P["privacy"].get("email_parts", []))  # bits of an address the reader may split off
OCR_FPS = P.get("ocr_fps", 2)                    # must match 07_ocr.py
STEP = 1 / OCR_FPS                               # seconds between readings
PAD_T = 0.4 if OCR_FPS <= 2 else STEP            # hold a box this long either side of where it was seen


def close_to(word, targets):
    """True when the word is one of the targets, a cut-off start of one ("OKECHUK..."),
    or a near misreading of one (a mangled spelling of a real name)."""
    letters = re.sub(r"[^a-z]", "", word)
    if len(letters) < 4:
        return False
    for t in targets:
        if t in letters or (len(letters) >= 5 and t.startswith(letters)):
            return True
        if difflib.SequenceMatcher(None, letters[:len(t)], t).ratio() > 0.75:
            return True
    return False

# --- 1. Boxes from the text reading ---
reuse = {int(k): v for k, v in json.load(open("ocr_reuse.json")).items()}
boxes = []  # (t, x0, y0, x1, y1)
seen = {}
for k, src in reuse.items():
    path = f"ocr_out/f_{src:04d}.tsv"
    if not os.path.exists(path):
        continue
    if src not in seen:
        found = []
        for line in open(path):
            p = line.rstrip("\n").split("\t")
            if len(p) < 5 or not p[0].isdigit(): continue   # skip the header row
            x, y, w, h = (int(v) for v in p[:4])
            word = p[4]; low = word.lower()
            if any(s in low for s in KEEP):
                continue
            if re.search(r"[a-z0-9._-]{3,}@[a-z0-9-]+\.[a-z]{2,}", low):   # a real email address
                frac = word.index("@") / len(word)          # blur up to the "@"
                found.append((x, y, x + w * frac, y + h))
            elif "gmail.com" in low or close_to(low, OWN_EMAIL_PARTS):
                cut = low.find("gmail.com")                  # "@" misread: blur up to "gmail"
                frac = (cut / len(word)) if cut > 0 else 1.0
                found.append((x, y, x + w * frac, y + h))
            elif re.fullmatch(r"[\d\s-]{5,12}", word) and sum(ch.isdigit() for ch in word) >= 5:
                found.append((x, y, x + w, y + h))           # a code or account number (rule 5)
            elif close_to(low, SURNAMES | ALWAYS):
                found.append((x, y, x + w, y + h))
        seen[src] = found
    t = (k - 1) * STEP
    for b in seen[src]:
        boxes.append((t, *b))

# --- 2. Extra boxes a text reader cannot find (a list sliding in, a moving greeting) ---
# Each is [start s, end s, x0, y0, x1, y1] in screen-recording time and pixels.
spans = [tuple(x) for x in P["privacy"].get("extra_spans", [])]
for t, x0, y0, x1, y1 in boxes:
    spans.append((t - PAD_T, t + STEP + PAD_T, x0 - PAD_PX, y0 - PAD_PX, x1 + PAD_PX, y1 + PAD_PX))
json.dump(spans, open("mask_spans.json", "w"))

# --- 3. Write the mask video, one frame at a time ---
by_frame = [[] for _ in range(N)]
for t0, t1, x0, y0, x1, y1 in spans:
    for n in range(max(0, int(t0 * FPS)), min(N, int(t1 * FPS) + 1)):
        by_frame[n].append((int(max(0, x0)), int(max(0, y0)), int(min(W, x1)), int(min(H, y1))))
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}",
                       "-r", str(FPS), "-i", "-", "-c:v", "ffv1", "mask.mkv"], stdin=subprocess.PIPE)
blank = np.zeros((H, W), np.uint8)
for n in range(N):
    if not by_frame[n]:
        ff.stdin.write(blank.tobytes()); continue
    m = blank.copy()
    for x0, y0, x1, y1 in by_frame[n]:
        m[y0:y1, x0:x1] = 255
    ff.stdin.write(m.tobytes())
ff.stdin.close(); ff.wait()
print("text boxes:", len(boxes), "| spans:", len(spans), "| frames with blur:", sum(1 for f in by_frame if f))
