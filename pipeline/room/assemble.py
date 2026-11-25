# ============================================================
# ASSEMBLE life video 1: the finished picture, in one pass, from the room render and the edit list.
# What : for every output frame (1080 x 1920, 30 fps): his shot (wide or close, a slow push-in,
#        a jump at each new sentence), the picture cards and reaction clips on their exact words,
#        captions (his spelling, Whisper's timing, the spoken word in yellow), the hook title,
#        the camera flashes, darker corners. Writes work/picture.mp4 (no sound) and work/cues.json
#        (when each sound effect plays).
# Never: never change his face or body; never put a flash on the first frame; never show a clip's
#        burned-in titles, logos or handles (each clip is cropped to a clean area).
# ============================================================
import json, re, os, subprocess, difflib, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

OW, OH, FPS = 1080, 1920, 30
IW, IH = 1440, 2560
E = json.load(open('work/edl.json'))
TAIL = 1.2                                   # hold on the last picture after his last word
LENGTH = E['length'] + TAIL
N = int(round(LENGTH * FPS))
YELLOW = (255, 210, 63); WHITE = (255, 255, 255); NAVY = (14, 27, 61)

# ---------- 1. Caption words: his spelling, Whisper's timing ----------
norm = lambda s: re.sub(r"[^a-z0-9']", '', s.lower().replace('2', 'two').replace('3', 'three').replace('4', 'four'))
heard = E['words']
mine = open('transcript.txt').read().split()
A = [norm(w['w']) for w in heard]; B = [norm(w) for w in mine]
cap = []
for op, a0, a1, b0, b1 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
    if op == 'equal' or (op == 'replace' and a1 - a0 == b1 - b0):
        for k in range(a1 - a0): cap.append(dict(heard[a0 + k], w=mine[b0 + k]))
    elif op in ('delete', 'replace'):
        for k in range(a0, a1): cap.append(dict(heard[k]))
# words checked by listening (Whisper medium, 2026-11-25) where the word list and his transcript disagree
FIX = {245: 'You', 246: 'should', 302: 'you begin'}   # raw word numbers
for w in cap:
    if w.get('i') in FIX: w['w'] = FIX[w['i']]
# the clips' own words get captions too (times inside the clip, from Whisper medium)
CLIP_WORDS = {'clips/pawpaw_skit.mp4': [('Please,', .34, .66), ('please,', .8, 1.04), ('I', 1.1, 1.24), ("don't", 1.24, 1.42), ('have', 1.42, 1.54),
              ('any', 1.54, 1.76), ('time', 1.76, 1.86), ('for', 1.86, 2.02), ('any', 2.02, 2.18), ('gossip', 2.18, 2.42), ('now.', 2.42, 2.8)],
              'clips/aki_pawpaw_best_of.mp4': [('This', 1.28, 1.52), ('is', 1.52, 1.76), ('business!', 1.76, 2.36)]}
for it in E['items']:
    if it['type'] == 'clip':
        for w, a, b in CLIP_WORDS[it['file']]:
            cap.append({'w': w, 's': round(it['t0'] + a - it['s'], 3), 'e': round(it['t0'] + b - it['s'], 3), 'clip': True})
cap.sort(key=lambda w: w['s'])
# groups of 1 to 3 words, broken after punctuation
groups, g = [], []
for w in cap:
    g.append(w)
    nxt = cap[cap.index(w) + 1] if cap.index(w) + 1 < len(cap) else None
    if len(g) == 3 or w['w'][-1] in '.,?!' or len(' '.join(x['w'] for x in g)) > 16 or (nxt and nxt.get('clip') != w.get('clip')):
        groups.append(g); g = []
if g: groups.append(g)

# ---------- 2. Font ----------
def font(size, weight=800):
    f = ImageFont.truetype('work/PlusJakartaSans.ttf', size); f.set_variation_by_axes([weight]); return f
F_CAP = font(78); F_TITLE = font(74); F_TITLE2 = font(96)

def at_word(i):                       # finished-video time of the kept word with original index i
    for w in heard:
        if w['i'] == i: return w['s']
    raise KeyError(i)
def end_word(i):
    for w in heard:
        if w['i'] == i: return w['e']
    raise KeyError(i)

# ---------- 3. Inserts on exact words (approved plan) ----------
def wi(text_index): return heard[text_index]['i']        # index in the finished word list -> raw index
H = heard
def t_of(k): return H[k]['s']
def e_of(k): return H[k]['e']
# Pictures and clips fill the whole screen, a screen of their own; his voice carries on underneath
# (his note on version 1). Each: start, end (finished-video seconds).
CARDS = [  # picture, start, end
    ('pictures/scrolling_others_lives.png', t_of(41) - 0.05, e_of(46) + 0.05),
    ('pictures/student_reading_2h.png',     t_of(253) - 0.05, e_of(269) + 0.05),
    ('pictures/report_card_up_2.png',       t_of(277) - 0.05, e_of(291) + 0.02),
    ('pictures/market_sale.png',            t_of(323) - 0.05, e_of(341) + 0.02),
    ('pictures/sunrise_arms_open.png',      t_of(370) - 0.05, LENGTH),
]
SILENT_CLIPS = [  # file, clip start, clip end, crop (x, y, w, h) clean of burned-in text, video start
    ('clips/check_phone_one_person.mp4', 0.3, 2.6, (160, 300, 332, 590), e_of(46) + 0.05),   # crying girl on her phone, after "someone else's life"
    ('clips/mr_ibu_lawyer.mp4', 12.0, 14.0, (170, 180, 462, 820), e_of(291) + 0.02),          # lawyer laughing, "That's an improvement"
]
SOUND_CLIP_CROP = {'clips/pawpaw_skit.mp4': (130, 324, 360, 640),          # centred on Pawpaw, 9:16
                   'clips/aki_pawpaw_best_of.mp4': (300, 140, 316, 562)}   # centred on Aki, 9:16
# ---------- 4. Shots: a jump at each new sentence, wide and close in turn ----------
cands = [0.0] + [H[k]['s'] - 0.03 for k in range(1, len(H)) if H[k]['s'] - H[k - 1]['e'] > 0.04 or H[k - 1]['w'][-1] in '.,?!']
for it in E['items']:
    if it['type'] == 'room' and it['t0'] > 0: cands.append(it['t0'])
cands = sorted(set(round(c, 2) for c in cands))
starts = [0.0]
for c in cands:
    if (1.0 if c < 6 else 1.6) <= c - starts[-1]: starts.append(c)
    elif c - starts[-1] > 2.6: starts.append(c)
shots = [(s_, starts[k + 1] if k + 1 < len(starts) else LENGTH) for k, s_ in enumerate(starts)]
LEVELS = [1.0, 1.38, 1.15, 1.6, 1.25, 1.45]          # wide (iPad shows), close, mid, very close...
ZOOM = [LEVELS[k % len(LEVELS)] for k in range(len(shots))]
# ---------- 5. His face, for the close shots ----------
face = json.load(open('work/face_track.json'))            # raw frame -> (x, y) centre, 1440 x 2560
fx = np.array(face['x']); fy = np.array(face['y'])

def raw_frame_at(t):
    for it in E['items']:
        if it['t0'] <= t < it['t1']:
            return ('room', int(round((it['s'] + (t - it['t0']) * E.get('speed', 1.0)) * FPS))) if it['type'] == 'room' else ('clip', it)
    last = E['items'][-1]
    return ('room', int(round((last['e'] - 0.04) * FPS)))     # tail: hold his last frame (under the card)

# ---------- 6. Readers ----------
class Room:
    # the room was rendered in two halves side by side: room_A holds raw frames 0 to 2084,
    # room_B holds raw frame 2085 onwards (its 1 s warm-up was not written)
    PARTS = [('work/room_A.mkv', 0), ('work/room_B.mkv', 2085)]
    def __init__(s):
        s.part = -1; s.p = None; s.idx = -1; s.f = None
    def _open(s, k):
        s.part = k; s.idx = s.PARTS[k][1] - 1
        s.p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', s.PARTS[k][0], '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
    def get(s, n):
        k = 1 if n >= s.PARTS[1][1] else 0
        if k != s.part: s._open(k)
        while s.idx < n:
            b = s.p.stdout.read(IW * IH * 3)
            if len(b) < IW * IH * 3: break
            s.f = np.frombuffer(b, np.uint8).reshape(IH, IW, 3); s.idx += 1
        return s.f
room = Room()

def load_clip(path, t0, t1, crop):
    x, y, w, h = crop
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', str(t0), '-to', str(t1), '-i', path, '-vf',
                          f'fps={FPS},crop={w}:{h}:{x}:{y}', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
CLIPS = {}
for it in E['items']:
    if it['type'] == 'clip': CLIPS[it['file']] = load_clip(it['file'], it['s'], it['e'], SOUND_CLIP_CROP[it['file']])
SIL = [(load_clip(f, a, b, c), t0) for f, a, b, c, t0 in SILENT_CLIPS]
PICS = {p: cv2.imread(p) for p, _, _ in CARDS}

# ---------- 7. Drawing helpers ----------
def rounded_mask(w, h, r):
    m = np.zeros((h, w), np.uint8); cv2.rectangle(m, (r, 0), (w - r, h), 255, -1); cv2.rectangle(m, (0, r), (w, h - r), 255, -1)
    for cx, cy in ((r, r), (w - r, r), (r, h - r), (w - r, h - r)): cv2.circle(m, (cx, cy), r, 255, -1)
    return m.astype(np.float32) / 255
def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def paste_card(frame, img, cx, cy, width, alpha, lift):
    h = int(img.shape[0] * width / img.shape[1])
    if h > 1100: width = int(width * 1100 / h); h = 1100
    card = cv2.resize(img, (width, h), interpolation=cv2.INTER_LANCZOS4)
    m = rounded_mask(width, h, 34)
    x0 = int(cx - width / 2); y0 = int(cy - h / 2 + lift)
    # soft shadow
    sh = np.zeros(frame.shape[:2], np.float32)
    ys, xs = max(y0 + 18, 0), max(x0, 0)
    sh[ys:min(y0 + 18 + h, OH), xs:min(x0 + width, OW)] = 1
    sh = cv2.GaussianBlur(sh, (0, 0), 22) * 0.55 * alpha
    frame[:] = frame * (1 - sh[..., None])
    y1, x1 = min(y0 + h, OH), min(x0 + width, OW); cy0, cx0 = max(0, -y0), max(0, -x0)
    reg = frame[max(y0, 0):y1, max(x0, 0):x1]
    c = card[cy0:cy0 + reg.shape[0], cx0:cx0 + reg.shape[1]]; mm = (m[cy0:cy0 + reg.shape[0], cx0:cx0 + reg.shape[1]] * alpha)[..., None]
    reg[:] = reg * (1 - mm) + c * mm
def full(img, z=1.0):
    # fill the whole 1080 x 1920 screen (crop the overflow), zoomed by z about the centre, lightly sharpened
    s_ = max(OW / img.shape[1], OH / img.shape[0]) * z
    r = cv2.resize(img, (int(img.shape[1] * s_) + 1, int(img.shape[0] * s_) + 1), interpolation=cv2.INTER_LANCZOS4)
    y0 = (r.shape[0] - OH) // 2; x0 = (r.shape[1] - OW) // 2
    r = r[y0:y0 + OH, x0:x0 + OW].astype(np.float32)
    return cv2.addWeighted(r, 1.25, cv2.GaussianBlur(r, (0, 0), 2.0), -0.25, 0)
def cover(img, w=OW, h=OH):
    s = max(w / img.shape[1], h / img.shape[0]); r = cv2.resize(img, (int(img.shape[1] * s) + 1, int(img.shape[0] * s) + 1))
    y0 = (r.shape[0] - h) // 2; x0 = (r.shape[1] - w) // 2
    return r[y0:y0 + h, x0:x0 + w]

yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
rr = np.sqrt(((xx - OW * 0.5) / (OW * 0.62)) ** 2 + ((yy - OH * 0.42) / (OH * 0.62)) ** 2)
VIG = (1 - 0.55 * np.clip((rr - 0.50) / 0.55, 0, 1) ** 1.2)[..., None]   # darker edges (his note on v1)
# cinematic grade (his colour sample): softer light, highlights rolled off, warm highlights,
# slightly teal shadows, a touch less colour. Built once as a lookup table.
_x = np.arange(256) / 255.0
_tone = np.where(_x < 0.55, _x, 0.55 + (1 - np.exp(-(_x - 0.55) * 2.2)) / 2.2) * 0.94 + 0.02
def grade(f):
    f = f / 255.0
    L = (0.299 * f[..., 2] + 0.587 * f[..., 1] + 0.114 * f[..., 0])[..., None]
    f = L + (f - L) * 0.88                                   # a little less colour
    f = np.interp(f, _x, _tone)                              # soft shoulder, slightly darker
    sh = (1 - L) ** 2; hi = L ** 2
    f = f + sh * np.array([0.030, 0.012, -0.020]) + hi * np.array([-0.030, 0.0, 0.030])   # BGR: teal shadows, warm highlights
    return np.clip(f, 0, 1) * 255

CAP_Y = 1330
cap_cache = {}
def caption_layer(gi, active):
    key = (gi, active)
    if key in cap_cache: return cap_cache[key]
    words = groups[gi]
    img = Image.new('RGBA', (OW, 220), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    texts = [w['w'].upper() for w in words]
    sp = 22; widths = [d.textlength(t, font=F_CAP) for t in texts]
    total = sum(widths) + sp * (len(texts) - 1)
    if total > OW - 120:
        f = font(int(78 * (OW - 120) / total)); widths = [d.textlength(t, font=f) for t in texts]; total = sum(widths) + sp * (len(texts) - 1)
    else: f = F_CAP
    x = (OW - total) / 2
    for k, t in enumerate(texts):
        col = YELLOW if k == active else WHITE
        d.text((x, 60), t, font=f, fill=col + (255,), stroke_width=9, stroke_fill=(0, 0, 0, 235))
        x += widths[k] + sp
    a = np.array(img).astype(np.float32); cap_cache[key] = a
    return a
def draw_caption(frame, t):
    for gi, g in enumerate(groups):
        if g[0]['s'] - 0.02 <= t < min(groups[gi + 1][0]['s'] if gi + 1 < len(groups) else 1e9, g[-1]['e'] + 0.4):
            active = max([k for k, w in enumerate(g) if w['s'] - 0.02 <= t] or [0])
            L = caption_layer(gi, active); al = L[..., 3:4] / 255
            reg = frame[CAP_Y:CAP_Y + 220]; reg[:] = reg * (1 - al) + L[..., :3][..., ::-1] * al
            return

title = Image.new('RGBA', (OW, 360), (0, 0, 0, 0)); d = ImageDraw.Draw(title)
for txt, f, y, col in (('WHY LIFE IS', F_TITLE, 20, WHITE), ('BEAUTIFUL', F_TITLE2, 105, YELLOW)):
    w = d.textlength(txt, font=f); d.text(((OW - w) / 2, y), txt, font=f, fill=col + (255,), stroke_width=10, stroke_fill=(0, 0, 0, 230))
TITLE = np.array(title).astype(np.float32)

FLASHES = [0.20, t_of(186) - 0.05, t_of(203) - 0.05, CARDS[-1][1] + 0.05]   # opening, "Start looking inward", "For example", the ending
cues = [{'t': t, 's': 'camera-shutter'} for t in FLASHES]
for p, s_, e_ in CARDS: cues.append({'t': s_, 's': 'whoosh-air-short'})
for _, a_, b_, _, t0 in SILENT_CLIPS: cues.append({'t': t0, 's': 'whoosh-air-short'})
for it in E['items']:
    if it['type'] == 'clip': cues.append({'t': it['t0'], 's': 'whoosh-air-short'})

import sys; sys.path.insert(0, 'scripts'); from kinetic import Kinetic
KIN = Kinetic(cap)

# ---------- 8. Render ----------
enc = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', 'work/picture.mp4'], stdin=subprocess.PIPE)
STILLS = [float(v) for v in os.environ.get('STILLS', '').split(',') if v]   # check mode: only these times, as PNGs
todo = sorted(int(round(v * FPS)) for v in STILLS) if STILLS else range(N)
if STILLS: enc.stdin.close()
shot_i = 0
for n in todo:
    t = n / FPS
    while shot_i + 1 < len(shots) and t >= shots[shot_i + 1][0]: shot_i += 1
    kind, ref = raw_frame_at(t)
    if kind == 'room':
        rn = min(ref, len(fx) - 1)
        src = room.get(rn)
        s0, s1 = shots[shot_i]; prog = (t - s0) / max(s1 - s0, 0.1)
        prev_z = ZOOM[shot_i - 1] if shot_i else ZOOM[0]
        k_ = ease((t - s0) / 0.12)                               # a quick 0.12 s punch to the new level
        z = (prev_z + (ZOOM[shot_i] - prev_z) * k_) * (1 + 0.06 * prog)
        cw, ch = IW / z, IH / z
        w_ = min(max((z - 1.0) / 0.3, 0), 1)                      # wide: frame centre; closer: his face
        cx = IW / 2 * (1 - w_) + fx[rn] * w_
        cy = IH / 2 * (1 - w_) + (fy[rn] + ch * 0.12) * w_
        x0 = int(np.clip(cx - cw / 2, 0, IW - cw)); y0 = int(np.clip(cy - ch / 2, 0, IH - ch))
        fr = grade(cv2.resize(src[y0:y0 + int(ch), x0:x0 + int(cw)], (OW, OH), interpolation=cv2.INTER_AREA).astype(np.float32))
    else:
        it = ref; frames = CLIPS[it['file']]; k = min(int((t - it['t0']) * FPS), len(frames) - 1)
        c = frames[k]
        zz = 1.12 - 0.12 * ease((t - it['t0']) / 0.25) + 0.03 * (t - it['t0'])   # lands with a quick settle, then drifts in
        fr = full(c, zz)
    # pictures: a screen of their own, a quick settle then a slow push (Ken Burns)
    for p, s_, e_ in CARDS:
        if s_ <= t < e_:
            zz = 1.12 - 0.12 * ease((t - s_) / 0.25) + 0.035 * (t - s_)
            fr = full(PICS[p], zz)
    for frames, t0 in SIL:
        L = len(frames) / FPS
        if t0 <= t < t0 + L:
            k = min(int((t - t0) * FPS), len(frames) - 1)
            fr = full(frames[k], 1.12 - 0.12 * ease((t - t0) / 0.25) + 0.03 * (t - t0))
    fr *= VIG
    if False:
        a = (1 - ease((t - 2.9) / 0.5)) if t > 2.9 else ease(t / 0.3) if t > 0.05 else 0
        L_ = TITLE[..., 3:4] / 255 * a; reg = fr[60:420]; reg[:] = reg * (1 - L_) + TITLE[..., :3][..., ::-1] * L_
    KIN.draw(fr, t)
    for ft in FLASHES:
        if ft <= t < ft + 0.2:
            k = (t - ft) / 0.2; fr = fr + (255 - fr) * (0.55 * (1 - k) ** 2)
    if STILLS: cv2.imwrite(f'work/still_{t:.2f}.png', np.clip(fr, 0, 255).astype(np.uint8)); continue
    enc.stdin.write(np.clip(fr, 0, 255).astype(np.uint8).tobytes())
    if n % 300 == 0: print('frame', n, 'of', N, flush=True)
if not STILLS: enc.stdin.close(); enc.wait()
json.dump({'cues': sorted(cues, key=lambda c: c['t']), 'length': LENGTH}, open('work/cues.json', 'w'), indent=1)
print('done', N, 'frames')
