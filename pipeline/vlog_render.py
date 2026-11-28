# ============================================================
# VLOG RENDER: the picture for a voiceover vlog (photos, clips, phone screens, a TV) with kinetic captions
# What : draws the vertical video 1080 x 1920 at 30 fps from a shot list (vlog_shots.py in the project
#        folder) and his caption words (caps.json). Shot kinds:
#          photo     a photo with a slow push (Ken Burns), optional soft blurs on names or faces
#          clip      a video clip, optional soft blurs that follow the thing they hide
#          phone     one or more screenshots inside a phone; the next screen slides in, with a tap ring
#          phonevid  a screen recording inside a phone
#          tv        a landscape screen (a hotel TV page) inside a TV frame
#        Any shot can carry a kicker (a few words in capitals at the top).
# Why  : voiceover video 1 redrew EVERY frame in one process, so one caption fix cost about an hour
#        (his note, 2026-11-26: "managing time is very necessary"). This script:
#          1. cuts the video into 3 second pieces and fingerprints each (shots + captions + files)
#          2. draws the pieces on ALL cores at once (multiprocessing)
#          3. keeps every finished piece in cache/, so a change redraws only the pieces it touches
#          4. joins the pieces with no re-encoding (the picture is encoded once, ever)
#          5. DRAFT=1 draws every second frame at half size, to look at before the real render
# Use  : python3 vlog_render.py                 full render -> video_silent.mp4
#        DRAFT=1 python3 vlog_render.py         quick look  -> draft_silent.mp4
#        python3 vlog_render.py still 12.5 40   stills of those seconds -> still_<t>.jpg
# In   : vlog_shots.py (SHOTS, LENGTH), caps.json, the files the shots name
# Never: never show a hospital name, a phone number or a looking-at-the-camera face unblurred.
#        Blurs are SOFT (his note, 2026-11-26): feathered edges, never a hard block.
#        Never put a sound on a caption. The cache key includes a fingerprint of this file, so a stale piece is never reused.
# ============================================================
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from multiprocessing import Pool

import cv2
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "room"))         # the caption drawing lives with the room pipeline
VERSION = hashlib.sha1(open(__file__, "rb").read()).hexdigest()[:10]       # the fingerprint of THIS file: any change to the drawing code redraws every piece, so a stale piece can never be reused
W, H, FPS, CH = 1080, 1920, 30, 90                      # size, frames per second, frames per cached piece
XF = 0.18                                               # seconds a new shot takes to fade in over the old one
DRAFT = os.environ.get("DRAFT") == "1"
CORES = int(os.environ.get("CORES", os.cpu_count() or 4))

# ---------- 1. Small helpers ----------
def ease(k):                                            # smooth start and end, k from 0 to 1
    k = min(1.0, max(0.0, k)); return k * k * (3 - 2 * k)

def ease_out(k):
    k = min(1.0, max(0.0, k)); return 1 - (1 - k) ** 3

def paste(dst, src, x, y, alpha=1.0):                   # src is BGRA uint8; dst is BGR uint8
    h, w = src.shape[:2]
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, dst.shape[1]), min(y + h, dst.shape[0])
    if x1 <= x0 or y1 <= y0 or alpha <= 0: return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x]
    a = (s[..., 3:4].astype(np.float32) / 255.0) * alpha
    d = dst[y0:y1, x0:x1].astype(np.float32)
    if dst.shape[2] == 4:                                # a layer with its own transparency: the "over" rule
        da = d[..., 3:4] / 255.0; oa = a + da * (1 - a)
        rgb = (s[..., :3].astype(np.float32) * a + d[..., :3] * da * (1 - a)) / np.maximum(oa, 1e-4)
        dst[y0:y1, x0:x1] = np.concatenate([rgb, oa * 255.0], axis=2).astype(np.uint8)
        return
    dst[y0:y1, x0:x1] = (d * (1 - a) + s[..., :3].astype(np.float32) * a).astype(np.uint8)

def soft_blur(img, rect, strength=1.0):
    # a SOFT blur: the rectangle (normalised x0,y0,x1,y1) is blurred and its edges fade out, never a hard block
    h, w = img.shape[:2]
    x0, y0, x1, y1 = int(rect[0] * w), int(rect[1] * h), int(rect[2] * w), int(rect[3] * h)
    pad = int(max(x1 - x0, y1 - y0) * 0.35) + 4
    X0, Y0, X1, Y1 = max(x0 - pad, 0), max(y0 - pad, 0), min(x1 + pad, w), min(y1 + pad, h)
    sub = img[Y0:Y1, X0:X1]
    sig = max(6.0, max(x1 - x0, y1 - y0) / 5.0) * strength
    blur = cv2.GaussianBlur(sub, (0, 0), sig)
    yy, xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float32)
    f = max(8.0, pad * 0.8)                              # feather width in pixels
    m = np.minimum(np.minimum(xx - x0, x1 - xx), np.minimum(yy - y0, y1 - yy)) / f + 1.0   # 1 inside the box, fading to 0 one feather outside it
    m = np.clip(m, 0, 1)[..., None]
    img[Y0:Y1, X0:X1] = (sub * (1 - m) + blur * m).astype(np.uint8)
    return img

def erase_text(img, poly, light=True):
    # CLEAN removal of the writing on a name board (his notes of 2026-11-27: it must not cover the parapet or the wall, and nobody should notice).
    # poly = the board's own four corners (normalised x, y), so ONLY the board is touched. The board is repainted in its own dark colour with the
    # sideways lighting it had (the dark end of what is on it, left third to right third), plus the photo's grain. Edges are a pixel soft.
    h, w = img.shape[:2]
    pts = np.array([[x * w, y * h] for x, y in poly], np.float32)
    x0, y0 = int(pts[:, 0].min()) - 4, int(pts[:, 1].min()) - 4; x1, y1 = int(pts[:, 0].max()) + 5, int(pts[:, 1].max()) + 5
    sub = img[y0:y1, x0:x1].astype(np.float32)
    S = 4                                                  # draw the board's shape at 4x and shrink it: a smooth edge
    big = np.zeros(((y1 - y0) * S, (x1 - x0) * S), np.uint8)
    cv2.fillPoly(big, [np.round((pts - [x0, y0]) * S).astype(np.int32)], 255)
    inside = cv2.resize(big, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    core = cv2.erode((inside > 0.99).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)      # pixels surely on the board, edge excluded
    xs = np.arange(x1 - x0)[None, :].repeat(y1 - y0, 0)
    lo, hi = np.percentile(xs[core], 33), np.percentile(xs[core], 67)
    def dark(sel):
        px = sub[sel]; g = px.mean(1); return px[g <= np.percentile(g, 10)].mean(0)       # the board's dark end: the white lettering cannot reach it
    cl, cr = dark(core & (xs <= lo)), dark(core & (xs >= hi))
    t = np.clip((xs - (x1 - x0) * 0.1) / ((x1 - x0) * 0.8), 0, 1)[..., None]
    plain = cl[None, None, :] * (1 - t) + cr[None, None, :] * t
    rng = np.random.default_rng(3)
    grain = cv2.GaussianBlur(rng.normal(0, 3.0, sub.shape[:2]).astype(np.float32), (0, 0), 0.7)[..., None]
    m = cv2.GaussianBlur(inside, (0, 0), 0.7)[..., None] * (inside[..., None] > 0.02)
    img[y0:y1, x0:x1] = np.clip(sub * (1 - m) + (plain + grain) * m, 0, 255).astype(np.uint8)
    return img

def rounded_mask(w, h, r):
    m = Image.new("L", (w * 2, h * 2), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * 2 - 1, h * 2 - 1], radius=r * 2, fill=255)
    return np.asarray(m.resize((w, h), Image.LANCZOS), np.float32)[..., None] / 255.0

def interp_rect(keys, t):                               # keys: [(t, (x0,y0,x1,y1)), ...] -> rect at t, or None outside
    if t < keys[0][0] - 1e-6 or t > keys[-1][0] + 1e-6: return None
    for (ta, ra), (tb, rb) in zip(keys, keys[1:]):
        if ta <= t <= tb:
            k = 0 if tb == ta else (t - ta) / (tb - ta)
            return tuple(a + (b - a) * k for a, b in zip(ra, rb))
    return keys[-1][1]

# ---------- 2. Backgrounds, phone and TV frames (built once per worker) ----------
_BG = {}
def background():
    if "bg" not in _BG:
        y = np.linspace(0, 1, H, dtype=np.float32)[:, None]; x = np.linspace(-1, 1, W, dtype=np.float32)[None, :]
        glow = np.exp(-((x * 0.9) ** 2 + ((y - 0.38) * 1.6) ** 2) * 2.2)
        top, bot = np.array([42, 22, 12], np.float32), np.array([20, 10, 6], np.float32)     # navy (BGR), brand colour
        base = top * (1 - y)[..., None] + bot * y[..., None]
        glow_c = np.array([120, 66, 28], np.float32)                                           # brighter blue in the middle
        _BG["bg"] = np.clip(base + glow[..., None] * glow_c * 0.55, 0, 255).astype(np.uint8)
    return _BG["bg"].copy()

def build_phone(pw, ph, bez=16, r=64):
    ow, oh = pw + 2 * bez, ph + 2 * bez
    S = 2
    body = Image.new("RGBA", (ow * S, oh * S), (0, 0, 0, 0)); d = ImageDraw.Draw(body)
    d.rounded_rectangle([0, 0, ow * S - 1, oh * S - 1], radius=(r + bez) * S, fill=(26, 28, 34, 255), outline=(88, 92, 104, 255), width=4)
    hole = Image.new("L", (ow * S, oh * S), 255); ImageDraw.Draw(hole).rounded_rectangle([bez * S, bez * S, (bez + pw) * S - 1, (bez + ph) * S - 1], radius=r * S, fill=0)
    a = np.minimum(np.asarray(body.split()[3]), np.asarray(hole))
    body.putalpha(Image.fromarray(a))
    ImageDraw.Draw(body).rounded_rectangle([(ow // 2 - int(pw * 0.14)) * S, (bez + 14) * S, (ow // 2 + int(pw * 0.14)) * S, (bez + 14 + 30) * S], radius=15 * S, fill=(0, 0, 0, 255))
    body = np.asarray(body.resize((ow, oh), Image.LANCZOS))
    bgra = cv2.cvtColor(body, cv2.COLOR_RGBA2BGRA)
    pad = 70
    sh = np.zeros((oh + 2 * pad, ow + 2 * pad), np.uint8); sh[pad + 30:pad + 30 + oh, pad:pad + ow] = 150
    sh = cv2.GaussianBlur(sh, (0, 0), 28)                               # the soft shadow, made once
    mask = rounded_mask(pw, ph, r)
    body_a = bgra[..., 3:4].astype(np.float32) / 255.0
    return {"body": bgra, "body_a": body_a, "body_rgb": bgra[..., :3].astype(np.float32) * body_a, "mask": mask, "pw": pw, "ph": ph, "bez": bez, "shadow": sh, "pad": pad}

def phone_inner(ph_, screen):
    # the phone with a screen in it (BGRA, no shadow): the screen first, the body over it
    bez, pw, ph = ph_["bez"], ph_["pw"], ph_["ph"]
    ow, oh = pw + 2 * bez, ph + 2 * bez
    scr = np.zeros((oh, ow, 3), np.float32); scr[bez:bez + ph, bez:bez + pw] = screen.astype(np.float32) * ph_["mask"]
    sa = np.zeros((oh, ow, 1), np.float32); sa[bez:bez + ph, bez:bez + pw] = ph_["mask"]
    ba = ph_["body_a"]
    rgb = scr * (1 - ba) + ph_["body_rgb"]; alpha = np.maximum(sa, ba)
    straight = np.clip(rgb / np.maximum(alpha, 1e-4), 0, 255)            # the colours above were multiplied by the coverage: undo that
    return np.concatenate([straight, alpha * 255], axis=2).clip(0, 255).astype(np.uint8)

def draw_phone(frame, ph_, inner, cx, cy, scale=1.0):
    # the shadow, then the phone, centred on (cx, cy)
    pad = ph_["pad"]; sh = ph_["shadow"]
    if abs(scale - 1) > 1e-3:
        sh = cv2.resize(sh, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR); inner = cv2.resize(inner, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    h, w = sh.shape[:2]
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    X0, Y0, X1, Y1 = max(x0, 0), max(y0, 0), min(x0 + w, frame.shape[1]), min(y0 + h, frame.shape[0])
    if X1 > X0 and Y1 > Y0:
        a = sh[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0].astype(np.float32)[..., None] / 255.0
        frame[Y0:Y1, X0:X1] = (frame[Y0:Y1, X0:X1] * (1 - a)).astype(np.uint8)
    ih, iw = inner.shape[:2]
    paste(frame, inner, int(cx - iw / 2), int(cy - ih / 2))

def draw_layer(frame, lay, cx, cy, scale=1.0, alpha=1.0):
    h, w = lay.shape[:2]
    if abs(scale - 1) > 1e-3: lay = cv2.resize(lay, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR); h, w = lay.shape[:2]
    paste(frame, lay, int(cx - w / 2), int(cy - h / 2), alpha)

# ---------- 3. Loading pictures and clips ----------
_IMG = {}
def load_image(path):
    if path not in _IMG:
        im = cv2.imread(path, cv2.IMREAD_COLOR)
        if im is None: sys.exit("STOP: cannot read " + path)
        _IMG[path] = im
    return _IMG[path]

def fit_cover(im, w, h):                                # scale to cover w x h, centre crop
    s = max(w / im.shape[1], h / im.shape[0])
    r = cv2.resize(im, (max(w, int(im.shape[1] * s + 0.5)), max(h, int(im.shape[0] * s + 0.5))), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR)
    y0, x0 = (r.shape[0] - h) // 2, (r.shape[1] - w) // 2
    return r[y0:y0 + h, x0:x0 + w]

def crop_image(im, crop):
    h, w = im.shape[:2]
    return im[int(crop[1] * h):int(crop[3] * h), int(crop[0] * w):int(crop[2] * w)]

def screen_image(path, pw, ph, crop=None):
    im = load_image(path)
    if crop:
        h, w = im.shape[:2]; im = im[int(crop[1] * h):int(crop[3] * h), int(crop[0] * w):int(crop[2] * w)]
    return fit_cover(im, pw, ph)

class Video:                                            # frames of a clip, read through ffmpeg, in order; asked for by frame number
    def __init__(s, path, ss, dur, speed, w, h, crop=None):
        vf = []
        if crop: vf.append(f"crop=iw*{crop[2]-crop[0]}:ih*{crop[3]-crop[1]}:iw*{crop[0]}:ih*{crop[1]}")
        vf += [f"setpts=PTS/{speed}", f"fps={FPS}", f"scale={w}:{h}:force_original_aspect_ratio=increase", f"crop={w}:{h}"]
        s.w, s.h, s.n, s.last, s.t_start = w, h, -1, None, None
        s.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{ss:.3f}", "-i", path, "-t", f"{dur * speed + 0.3:.3f}", "-vf", ",".join(vf),
                                "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    def at(s, k):                                       # frame number k since the start (reads and drops frames in between)
        while s.n < k:
            b = s.p.stdout.read(s.w * s.h * 3)
            if len(b) != s.w * s.h * 3: break           # the clip ended: hold its last frame
            s.last = np.frombuffer(b, np.uint8).reshape(s.h, s.w, 3); s.n += 1
        return s.last if s.last is not None else np.zeros((s.h, s.w, 3), np.uint8)
    def close(s):
        try: s.p.stdout.close(); s.p.kill()
        except Exception: pass

def cam(sp, lt, dur, z0=1.0, z1=1.14, drift=True):
    # where the camera is, lt seconds into a shot: (zoom, centre x, centre y). A "path" [(fraction, zoom, x, y), ...] is followed with smooth moves
    # (a zoom in and out); otherwise a straight push z0 -> z1. A little hand-held drift keeps a photo alive (his note: not still).
    k = min(1.0, max(0.0, lt / max(dur, 0.1)))
    if "path" in sp:
        P = sp["path"]
        if k <= P[0][0]: z, fx, fy = P[0][1:]
        elif k >= P[-1][0]: z, fx, fy = P[-1][1:]
        else:
            for a, b in zip(P, P[1:]):
                if a[0] <= k <= b[0]:
                    e = ease((k - a[0]) / max(b[0] - a[0], 1e-6))
                    z, fx, fy = (a[i] + (b[i] - a[i]) * e for i in (1, 2, 3)); break
    else:
        e = ease(k); z0, z1 = sp.get("z0", z0), sp.get("z1", z1)
        fx0, fy0 = sp.get("fx0", sp.get("fx", 0.5)), sp.get("fy0", sp.get("fy", 0.5))
        z = z0 + (z1 - z0) * e
        fx = fx0 + (sp.get("fx1", sp.get("fx", 0.5)) - fx0) * e; fy = fy0 + (sp.get("fy1", sp.get("fy", 0.5)) - fy0) * e
    if drift and sp.get("drift", True):
        fx += 0.005 * np.sin(2 * np.pi * 0.31 * lt + 1.3); fy += 0.004 * np.sin(2 * np.pi * 0.23 * lt)
    return z, fx, fy

# ---------- 4. One shot = one object with frame(t) ----------
class Shot:
    def __init__(s, spec, t_end):
        s.spec, s.t0, s.t1 = spec, spec["t0"], t_end
        s.kind = spec["kind"]
        s.vid = None; s.vid_t = None
        k = s.kind
        if k == "photo":
            im = load_image(spec["file"]).copy()
            for r in spec.get("erase", []): erase_text(im, r)                  # a name board: painted out cleanly
            for r in spec.get("blur", []): soft_blur(im, r, spec.get("blur_strength", 1.0))   # small things (a number plate): a soft blur
            s.base = fit_cover_keep(im, 1.3)
        elif k in ("phone", "phonevid"):
            s.pw = spec.get("pw", 620); s.ph = int(s.pw * spec.get("aspect", 844 / 390))
            s.phone = build_phone(s.pw, s.ph)
            if k == "phone": s.screens = [(screen_image(f, s.pw, s.ph, spec.get("crop")), ti, tap) for f, ti, tap in spec["screens"]]
        elif k == "screen":
            s.screens = [(fit_cover(load_image(f) if not spec.get("crop") else crop_image(load_image(f), spec["crop"]), int(W * 1.5), int(H * 1.5)), ti, tap) for f, ti, tap in spec["screens"]]
        elif k == "wide":
            im = load_image(spec["file"]); s.wide_img = cv2.resize(im, (W, int(W * im.shape[0] / im.shape[1])), interpolation=cv2.INTER_AREA)
            bg = fit_cover(im, W // 8, H // 8); bg = cv2.GaussianBlur(bg, (0, 0), 5); s.bg = (cv2.resize(bg, (W, H), interpolation=cv2.INTER_CUBIC) * 0.45).astype(np.uint8)
        elif k == "tv":
            s.tw = spec.get("tw", 960); s.th = int(s.tw * 9 / 16)
            s.img = screen_image(spec["file"], s.tw, s.th)
        s.kick = None; s.static = {}

    # -- the moving content of the shot at time t --
    def frame(s, t):
        k, sp = s.kind, s.spec
        lt = t - s.t0; dur = max(s.t1 - s.t0, 0.1)
        if k == "photo": return s.photo(t, lt, dur)
        if k == "clip": return s.clip(t, lt, dur)
        if k == "screen": return s.screen(t, lt, dur)
        if k == "wide": return s.wide(t, lt, dur)
        if k in ("phone", "phonevid", "tv"):
            f = background(); s.device(f, t, lt, dur); return f
        raise SystemExit("unknown shot kind " + k)

    def photo(s, t, lt, dur):
        z, fx, fy = cam(s.spec, lt, dur, 1.0, 1.22)
        return window(s.base, z, fx, fy)

    def clip(s, t, lt, dur):
        sp = s.spec
        if s.vid is None:
            start = sp.get("ss", 0.0) + max(0.0, (t - s.t0)) * sp.get("speed", 1.0)
            s.vid = Video(sp["file"], start, s.t1 - t + 0.1, sp.get("speed", 1.0), W, H, sp.get("crop")); s.vid_t = t
        fr = s.vid.at(int(round((t - s.vid_t) * FPS))).copy()
        src_t = sp.get("ss", 0.0) + lt * sp.get("speed", 1.0)
        for b in sp.get("blur", []):                    # {"keys": [(source_t, rect), ...], "strength": 1.0}
            r = interp_rect(b["keys"], src_t)
            if r: soft_blur(fr, r, b.get("strength", 1.0))
        z, fx, fy = cam(sp, lt, dur, 1.0, 1.1)
        return window(fr, z, fx, fy, base_scale=1.0)

    def screen(s, t, lt, dur):
        # a screenshot or app screen shown FULL SCREEN; the next screen pushes it out; a ring shows each tap
        sp = s.spec
        cur = 0
        for i, (_, ti, _) in enumerate(s.screens):
            if t >= ti: cur = i
        z, fx, fy = cam(sp, lt, dur, 1.0, 1.04, drift=False)
        out = window(s.screens[cur][0], z, fx, fy, base_scale=1.5)
        if cur > 0:
            p = (t - s.screens[cur][1]) / 0.30
            if p < 1:
                off = int((1 - ease_out(p)) * W); prev = window(s.screens[cur - 1][0], z, fx, fy, base_scale=1.5)
                comp = np.empty_like(out); comp[:, :W - off] = prev[:, off:]; comp[:, W - off:] = out[:, :off]; out = comp
        for _, ti, tap in s.screens:
            if tap and ti - 0.45 <= t < ti:
                p = (t - (ti - 0.45)) / 0.45; cx_, cy_ = int(tap[0] * W), int(tap[1] * H)
                ring = out.copy(); cv2.circle(ring, (cx_, cy_), int(40 + 70 * ease_out(p)), (255, 255, 255), 8, cv2.LINE_AA)
                cv2.circle(ring, (cx_, cy_), int(22 * (1 - p) + 8), (255, 220, 120), -1, cv2.LINE_AA)
                a_ = 0.85 * (1 - p * 0.6); out = cv2.addWeighted(ring, a_, out, 1 - a_, 0)
        return out

    def wide(s, t, lt, dur):
        # a landscape page (the TV display) as wide as the screen, on a soft blurred copy of itself, zooming in and out
        sp = s.spec; z, _, _ = cam(sp, lt, dur, 1.0, 1.0, drift=False)
        out = s.bg.copy(); fg = s.wide_img
        if abs(z - 1) > 1e-3: fg = cv2.resize(fg, None, fx=z, fy=z, interpolation=cv2.INTER_LINEAR)
        h_, w_ = fg.shape[:2]; cy = int(H * sp.get("cyf", 0.42))
        x0, y0 = (W - w_) // 2, cy - h_ // 2
        X0, Y0, X1, Y1 = max(x0, 0), max(y0, 0), min(x0 + w_, W), min(y0 + h_, H)
        out[Y0:Y1, X0:X1] = fg[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
        return out

    def device(s, f, t, lt, dur):
        k, sp = s.kind, s.spec
        enter = ease_out(lt / 0.45); drift = 1.0 + 0.035 * (lt / dur)
        sc = (0.88 + 0.12 * enter) * drift
        cy = sp.get("cy", 900) + int(70 * (1 - enter))
        if k == "tv":
            cy = sp.get("cy", 760) + int(70 * (1 - enter))
            z = 1.0 + 0.06 * (lt / dur)
            bez = 26; tv = np.zeros((s.th + 2 * bez + 70, s.tw + 2 * bez, 4), np.uint8)
            tv[..., 3] = 0
            body = np.zeros((s.th + 2 * bez, s.tw + 2 * bez, 3), np.uint8); body[:] = (28, 24, 22)
            body[bez:bez + s.th, bez:bez + s.tw] = s.img
            m = (rounded_mask(s.tw + 2 * bez, s.th + 2 * bez, 22)[..., 0] * 255).astype(np.uint8)
            tv[:s.th + 2 * bez, :, :3] = body; tv[:s.th + 2 * bez, :, 3] = m
            tv[s.th + 2 * bez:, s.tw // 2 - 60:s.tw // 2 + 120, :3] = (40, 36, 34); tv[s.th + 2 * bez:, s.tw // 2 - 60:s.tw // 2 + 120, 3] = 255
            lay = np.zeros((tv.shape[0] + 140, tv.shape[1] + 140, 4), np.uint8)
            sh = np.zeros(lay.shape[:2], np.uint8); sh[100:100 + s.th + 2 * bez, 70:70 + tv.shape[1]] = 160; lay[..., 3] = cv2.GaussianBlur(sh, (0, 0), 30)
            paste(lay, tv, 70, 70)
            draw_layer(f, lay, W / 2, cy, sc * z)
            return
        if k == "phone":
            cur = 0
            for i, (_, ti, _) in enumerate(s.screens):
                if t >= ti: cur = i
            img = s.screens[cur][0].copy()
            if cur > 0:
                p = (t - s.screens[cur][1]) / 0.30
                if p < 1:                                    # the new screen pushes the old one out to the left
                    off = int((1 - ease_out(p)) * s.pw)
                    prev = s.screens[cur - 1][0]; comp = np.empty_like(img)
                    comp[:, :s.pw - off] = prev[:, off:]; comp[:, s.pw - off:] = img[:, :off]
                    img = comp
            nxt = [(ti, tap) for (_, ti, tap) in s.screens if tap and ti - 0.45 <= t < ti]
            for ti, tap in nxt:
                p = (t - (ti - 0.45)) / 0.55; cx_, cy_ = int(tap[0] * s.pw), int(tap[1] * s.ph)
                ring = img.copy(); cv2.circle(ring, (cx_, cy_), int(26 + 40 * ease_out(p)), (255, 255, 255), 5, cv2.LINE_AA)
                cv2.circle(ring, (cx_, cy_), int(14 * (1 - p) + 6), (255, 220, 120), -1, cv2.LINE_AA)
                img = cv2.addWeighted(ring, 0.8 * (1 - p * 0.6), img, 1 - 0.8 * (1 - p * 0.6), 0)
            moving = (cur > 0 and (t - s.screens[cur][1]) / 0.30 < 1) or bool(nxt)
            if moving: inner = phone_inner(s.phone, img)
            else:
                if cur not in s.static: s.static[cur] = phone_inner(s.phone, img)
                inner = s.static[cur]
            draw_phone(f, s.phone, inner, W / 2, cy, sc)
            return
        if k == "phonevid":
            if s.vid is None:
                start = sp.get("ss", 0.0) + max(0.0, (t - s.t0)) * sp.get("speed", 1.0)
                s.vid = Video(sp["file"], start, s.t1 - t + 0.1, sp.get("speed", 1.0), s.pw, s.ph, sp.get("crop")); s.vid_t = t
            scr = s.vid.at(int(round((t - s.vid_t) * FPS))).copy(); src_t = sp.get("ss", 0.0) + lt * sp.get("speed", 1.0)
            for b in sp.get("blur", []):
                r = interp_rect(b["keys"], src_t)
                if r: soft_blur(scr, r, b.get("strength", 1.0))
            draw_phone(f, s.phone, phone_inner(s.phone, scr), W / 2, cy, sc)

def fit_cover_keep(im, over):                           # the whole picture, scaled so it covers over x (1080 x 1920); NOT cropped
    s = max(W * over / im.shape[1], H * over / im.shape[0])
    return cv2.resize(im, (int(im.shape[1] * s + 0.5), int(im.shape[0] * s + 0.5)), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)

def window(base, z, fx, fy, base_scale=1.3):
    # the part of base that fills 1080 x 1920 at zoom z. base was made base_scale times bigger than the screen (1.3 for photos, 1.0 for clips)
    h, w = base.shape[:2]
    ww, hh = W * base_scale / z, H * base_scale / z
    cx = min(max(fx * w, ww / 2), w - ww / 2); cy = min(max(fy * h, hh / 2), h - hh / 2)
    x0, y0 = int(cx - ww / 2), int(cy - hh / 2)
    crop = base[y0:y0 + int(hh), x0:x0 + int(ww)]
    return cv2.resize(crop, (W, H), interpolation=cv2.INTER_AREA if crop.shape[1] > W else cv2.INTER_LINEAR)

# ---------- 5. Kickers (a few capital words at the top) ----------
_KICK = {}
def kicker_layer(text):
    if text not in _KICK:
        from kinetic import word_image, F_KEY2, YELLOW
        img, th, pad = word_image(text.upper(), F_KEY2, YELLOW, key=True)
        s = min(1.0, (W - 120) / (img.shape[1] - 2 * pad))
        if s < 1: img = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        bgra = np.concatenate([img[..., :3][..., ::-1], img[..., 3:4] * 255], axis=2).astype(np.uint8)
        _KICK[text] = bgra
    return _KICK[text]

# ---------- 6. One frame ----------
class Renderer:
    def __init__(s, shots_spec, caps):
        order = sorted(shots_spec, key=lambda x: x["t0"])
        s.order = order; s.cache = {}
        s.ends = [order[i + 1]["t0"] + XF if i + 1 < len(order) else LENGTH for i in range(len(order))]
        s.n = len(order)
        from kinetic import Kinetic
        s.kin = Kinetic(caps, personality=True, karaoke=True)
    def shot(s, i):                                       # built the first time a frame needs it
        if i not in s.cache: s.cache[i] = Shot(s.order[i], s.ends[i])
        return s.cache[i]
    def frame(s, t):
        idx = max(i for i in range(s.n) if s.order[i]["t0"] <= t + 1e-9)
        cur = s.shot(idx)
        fr = cur.frame(t)
        if idx > 0 and t - cur.t0 < XF:
            prev = s.shot(idx - 1).frame(t)
            a = ease((t - cur.t0) / XF)
            fr = cv2.addWeighted(prev, 1 - a, fr, a, 0)
        for sh in (cur,):
            kt = sh.spec.get("kicker")
            if kt:
                st = sh.t0 + sh.spec.get("kt", 0.3)
                en = sh.t0 + sh.spec.get("kend", sh.t1 - XF - sh.t0)
                if st <= t <= en:
                    a = min(1.0, (t - st) / 0.25) * min(1.0, (en - t) / 0.2)
                    lay = kicker_layer(kt)
                    paste(fr, lay, (W - lay.shape[1]) // 2, sh.spec.get("ky", 40 if sh.kind == "screen" else 150 if sh.kind in ("phone", "phonevid", "tv", "wide") else 250) + int(24 * (1 - ease_out((t - st) / 0.3))), a)
        f = fr.astype(np.float32)
        s.kin.draw(f, t)
        out = np.clip(f, 0, 255).astype(np.uint8)
        # a short soft light flash on the shots that ask for it
        fl = cur.spec.get("flash")
        if fl and 0 <= t - cur.t0 < 0.22:
            out = cv2.addWeighted(out, 1 - 0.35 * (1 - (t - cur.t0) / 0.22), np.full_like(out, 255), 0.35 * (1 - (t - cur.t0) / 0.22), 0)
        return out
    def close(s):                                         # after a piece: stop the clip readers; pictures and phones stay for the next piece
        for sh in s.cache.values():
            if sh.vid: sh.vid.close(); sh.vid = None

# ---------- 7. Cached pieces on all cores ----------
def load_project():
    spec = importlib.util.spec_from_file_location("vlog_shots", "vlog_shots.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.SHOTS, m.LENGTH

def file_stamp(p):
    try: st = os.stat(p); return f"{p}:{st.st_size}:{int(st.st_mtime)}"
    except OSError: return p

def spec_files(sp):
    out = []
    for k in ("file",):
        if k in sp: out.append(sp[k])
    for sc in sp.get("screens", []): out.append(sc[0])
    return out

def piece_key(c, shots_spec, caps):
    a, b = c * CH / FPS - 0.6, (c + 1) * CH / FPS + 0.6
    order = sorted(shots_spec, key=lambda x: x["t0"])
    rel = []
    for i, sp in enumerate(order):
        t_end = order[i + 1]["t0"] + XF if i + 1 < len(order) else LENGTH
        if t_end >= a and sp["t0"] <= b: rel.append((sp, [file_stamp(f) for f in spec_files(sp)], t_end))
    cw = [w for w in caps if w["e"] >= a - 1 and w["s"] <= b + 1]
    # the caption phrases that reach this piece can start earlier: include a margin
    blob = json.dumps([VERSION, DRAFT, rel, cw], sort_keys=True, default=str)
    return hashlib.sha1(blob.encode()).hexdigest()[:16]

def render_piece(args):
    c, key, n_frames = args
    out = f"cache/{key}.mp4"
    if os.path.exists(out): return c, out, 0
    if "R" not in _DATA:                                  # one Renderer for the whole life of this worker
        shots_spec, caps = load_project_data(); _DATA["R"] = Renderer(shots_spec, caps)
    R = _DATA["R"]
    step = 2 if DRAFT else 1
    ow, oh = (W // 2, H // 2) if DRAFT else (W, H)
    tmp = out + ".part.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{ow}x{oh}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "ultrafast" if DRAFT else "fast", "-crf", "30" if DRAFT else "16", "-g", str(CH), "-keyint_min", str(CH),
                            "-sc_threshold", "0", "-pix_fmt", "yuv420p", "-bf", "0", "-f", "mp4", tmp], stdin=subprocess.PIPE)
    last = None
    for i in range(n_frames):
        fi = c * CH + i
        if step == 1 or i % step == 0 or last is None:
            fr = R.frame(fi / FPS)
            if DRAFT: fr = cv2.resize(fr, (ow, oh), interpolation=cv2.INTER_AREA)
            last = fr
        enc.stdin.write(last.tobytes())
    enc.stdin.close(); enc.wait(); R.close()
    os.replace(tmp, out)
    return c, out, n_frames

_DATA = {}
def load_project_data():
    if "d" not in _DATA:
        shots, _ = load_project(); caps = json.load(open("caps.json"))
        if os.path.exists("caps_extra.json"): caps = sorted(caps + json.load(open("caps_extra.json")), key=lambda w: w["s"])
        _DATA["d"] = (shots, caps)
    return _DATA["d"]

if __name__ == "__main__":
    shots_spec, LENGTH = load_project()
    caps = load_project_data()[1]
    os.makedirs("cache", exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "still":
        R = Renderer(shots_spec, caps)
        for t in map(float, sys.argv[2:]):
            Image.fromarray(R.frame(t)[..., ::-1]).save(f"still_{t:g}.jpg", quality=90); print("still", t)
        R.close(); sys.exit(0)
    N = int(LENGTH * FPS)
    jobs = []
    for c in range((N + CH - 1) // CH):
        n = min(CH, N - c * CH); jobs.append((c, piece_key(c, shots_spec, caps), n))
    todo = [j for j in jobs if not os.path.exists(f"cache/{j[1]}.mp4")]
    print(f"{len(jobs)} pieces, {len(todo)} to draw, {CORES} cores" + (" (draft)" if DRAFT else ""))
    if todo:
        with Pool(CORES) as p:
            for c, out, n in p.imap_unordered(render_piece, todo): print("piece", c, "done", flush=True)
    name = "draft_silent.mp4" if DRAFT else "video_silent.mp4"
    with open("pieces.txt", "w") as f:
        for _, key, _ in jobs: f.write(f"file 'cache/{key}.mp4'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "pieces.txt", "-c", "copy", name], check=True)
    print("wrote", name)
