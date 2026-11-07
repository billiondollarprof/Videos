# ============================================================
# VO 03 RENDER: the picture for a voiceover video, drawn frame by frame (PIL) into x264
# What : shots anchored to spoken phrases (vo_shots.py in the project): photos and the map as
#        floating cards over a blurred copy of themselves, and the post as a floating sheet whose
#        line being read is highlighted while the page scrolls with him (readlines.json).
#        Motion (his notes, 2026-11-07: "float out from the bottom up", "swag", "fluid"):
#        - every shot change: the new card rises from the bottom with a soft overshoot while the
#          old one leaves upward; the backdrops cross-fade; a faint flash (3 frames)
#        - while on screen: cards bob and tilt a little, the picture inside zooms slowly, a band
#          of light crosses each card, the backdrop drifts; the post sheet floats and pushes in
#        - kickers pop in with a bounce; the spoken caption word pops a little bigger
#        Grade: vignette and fine grain.
# Why  : no face video, so the pictures carry the eye. Remotion is not needed.
# In   : caps.json, readlines.json, post/tall.png, vo_timeline.json, vo_config.json (source line),
#        vo_shots.py, pjs800.ttf / pjs600.ttf
# Out  : video_silent.mp4, shots.json (for the sound cues)
# Use  : python3 vo_03_render.py            whole video
#        python3 vo_03_render.py 0 300 900   stills of frames 300 and 900 (look before rendering)
# Never: never open on the post: open on a moving picture with the hook. Never put the editing
#        on screen. A post shot marked top=True opens at the top and highlights nothing.
# ============================================================
import json, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance, ImageChops

# --- 1. Size, colours, inputs ---
W_, H_, FPS = 1080, 1920, 30
NAVY = (11, 27, 58); YEL = (255, 204, 0); BLUE = (30, 136, 255); WHITE = (255, 255, 255)
C = json.load(open("caps.json")); P = json.load(open("vo_config.json")); SOURCE = P.get("source", "")
TOTAL = json.load(open("vo_timeline.json"))["total"]; END = 3.2; DUR = TOTAL + END
F8 = lambda s: ImageFont.truetype("pjs800.ttf", s); F6 = lambda s: ImageFont.truetype("pjs600.ttf", s)
DJ = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s)  # for ₦
n = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())
TR = 0.55                                                  # seconds a shot change takes

# --- 2. Shots, anchored to the first time a phrase is said after the previous shot ---
def at(phrase, after=0.0):
    p = [n(x) for x in phrase.split()]; ws = [n(c["w"]) for c in C]
    for i in range(len(ws)):
        if C[i]["s"] >= after and ws[i:i + len(p)] == p: return max(0.0, C[i]["s"] - 0.15)
    raise SystemExit("not found: " + phrase)
SH = []; _t = 0.0
def add(ph, kind, src, **k):
    global _t
    s = 0.0 if ph is None else at(ph, _t); _t = s; SH.append(dict(s=s, kind=kind, src=src, **k))
exec(open("vo_shots.py").read())                           # the shot list lives in the project
SH.append(dict(s=TOTAL + 0.05, kind="end", src=None))
for i, s in enumerate(SH): s["e"] = SH[i + 1]["s"] if i + 1 < len(SH) else DUR; s["i"] = i
json.dump(SH, open("shots.json", "w"), indent=0)

# --- 3. Easing ---
def smooth(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)
def out_back(u, k=1.4): u = min(1, max(0, u)) - 1; return 1 + (k + 1) * u ** 3 + k * u ** 2
def in_cubic(u): u = min(1, max(0, u)); return u ** 3

# --- 4. Pictures: enhanced once, cached ---
def enhance(im):
    im = ImageOps.autocontrast(im.convert("RGB"), cutoff=0.5); im = ImageEnhance.Color(im).enhance(1.08)
    if im.width < 1100: im = im.resize((1100, round(im.height * 1100 / im.width)), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(2, 80, 2))
_c = {}
def assets(s):
    if s["i"] in _c: return _c[s["i"]]
    if s["kind"] in ("photo", "map"):
        im = enhance(Image.open(s["src"])) if s["kind"] == "photo" else Image.open(s["src"]).convert("RGB")
        bg = ImageOps.fit(im, (W_, H_)).filter(ImageFilter.GaussianBlur(40)); bg = ImageEnhance.Brightness(bg).enhance(0.42)
        cw = 960; ch = min(1150, round(im.height * cw / im.width)); big = ImageOps.fit(im, (round(cw * 1.12), round(ch * 1.12)))
        _c[s["i"]] = (bg, big, (cw, ch))
    elif s["kind"] == "post":
        bg = Image.new("RGB", (W_, H_), (8, 14, 30)); g = ImageDraw.Draw(bg)
        for y in range(H_): g.line([(0, y), (W_, y)], fill=(8 + y * 10 // H_, 16 + y * 14 // H_, 34 + y * 30 // H_))
        _c[s["i"]] = (bg, None, None)
    else:
        _c[s["i"]] = (Image.new("RGB", (W_, H_), NAVY), None, None)
    return _c[s["i"]]

# light band that crosses a card
SW = Image.new("L", (420, 2600), 0)
for i in range(420): ImageDraw.Draw(SW).line([(i, 0), (i, 2600)], fill=int(120 * np.sin(np.pi * i / 420) ** 2))
SW = SW.rotate(-20, expand=True)
def sweep(card, p):
    band = Image.new("L", card.size, 0); band.paste(SW, (int(-560 + (card.width + 760) * p), -600))
    card.paste((255, 250, 235), (0, 0), band)

def rounded_mask(size, r):
    m = Image.new("L", size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], r, fill=255); return m

# --- 5. The post: one tall page, the reading line and the scroll for every frame ---
_t = Image.open("post/tall.png").convert("RGB"); TALL = Image.new("RGB", (_t.width, _t.height + 900), (0, 0, 0)); TALL.paste(_t, (0, 0))
SHEET_W, SHEET_Y, WIN_H = 1020, 180, 1580                   # sheet on screen, window of the page (source px)
SCALE = SHEET_W / 1080; SHEET_H = round(WIN_H * SCALE)
RL = json.load(open("readlines.json"))
NF = round(DUR * FPS); READ = [None] * NF; SCROLL = [0.0] * NF
cur = None; ci = 0; tgt = 0.0; pos = 0.0; prev = None
for fi in range(NF):
    tt = fi / FPS
    while ci < len(C) and C[ci]["s"] <= tt:
        if RL[ci]: cur = (ci, RL[ci])
        ci += 1
    sh = next((x for x in SH if x["s"] <= tt < x["e"]), None)
    reading = cur is not None and tt <= C[cur[0]]["e"] + 1.2 and not (sh and sh.get("top"))
    if reading: tgt = max(0, (cur[1][0] + cur[1][1]) / 2 - 0.33 * WIN_H)
    if sh and sh.get("top"): tgt = 0.0
    if sh is not prev: pos = tgt; prev = sh
    pos += (tgt - pos) * 0.10
    SCROLL[fi] = pos; READ[fi] = cur[1] if reading else None

# --- 6. Text helpers ---
def tw(d, txt, f, a): return sum(d.textlength(ch, font=a if ch == "₦" else f) for ch in txt)
def text(d, xy, txt, f, a, fill, stroke=0):
    x, y = xy
    for ch in txt:
        ff = a if ch == "₦" else f; d.text((x, y), ch, font=ff, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0)); x += d.textlength(ch, font=ff)
def pill(im, cy, txt, size=58, bg=YEL, fg=NAVY, pop=1.0):
    """A rounded label; pop 0..1 makes it grow in with a bounce."""
    if pop <= 0: return
    k = out_back(pop, 2.0); sz = max(8, int(size * k)); f, a = F8(sz), DJ(sz); d = ImageDraw.Draw(im)
    w = tw(d, txt, f, a); x = (W_ - w) / 2
    d.rounded_rectangle([x - 34 * k, cy - sz * 0.75, x + w + 34 * k, cy + sz * 0.75], int(28 * k), fill=bg)
    text(d, (x, cy - sz * 0.62), txt, f, a, fg)

# --- 7. Captions: 1 to 3 words, the spoken word yellow and popped ---
groups = []; g = []
for i, c in enumerate(C):
    g.append(i)
    if len(g) == 3 or c["w"][-1] in ".,?!:" or (i + 1 < len(C) and C[i + 1]["s"] - c["e"] > 0.35): groups.append(g); g = []
if g: groups.append(g)
def caption(im, tt):
    d = ImageDraw.Draw(im)
    for gi, g in enumerate(groups):
        s, e = C[g[0]]["s"], C[g[-1]]["e"]; nxt = C[groups[gi + 1][0]]["s"] if gi + 1 < len(groups) else 1e9
        if not (s <= tt < min(nxt, e + 0.5)): continue
        size = 84; words = [C[i]["w"] for i in g]
        while True:
            f, a = F8(size), DJ(size); sp = d.textlength(" ", font=f)
            total = sum(tw(d, w, f, a) for w in words) + sp * (len(words) - 1)
            if total <= 980 or size <= 50: break
            size -= 4                                     # a long group shrinks to fit the screen
        x = (W_ - total) / 2; y = 1540
        for i, w in zip(g, words):
            on = C[i]["s"] <= tt < (C[i + 1]["s"] if i + 1 < len(C) else 1e9)
            if on:
                k = 1 + 0.06 * (1 - smooth((tt - C[i]["s"]) / 0.12))   # pop, then settle
                fk, ak = F8(int(size * k)), DJ(int(size * k)); dy = (size * k - size) * 0.6
                text(d, (x - (tw(d, w, fk, ak) - tw(d, w, f, a)) / 2, y - dy), w, fk, ak, YEL, stroke=7)
            else:
                text(d, (x, y), w, f, a, WHITE, stroke=7)
            x += tw(d, w, f, a) + sp
        return

# --- 8. One shot's moving element (card or sheet), and where it sits ---
def element(s, tt, fi):
    """Return (RGBA image, x, y) for the shot at time tt, with its idle motion."""
    u = (tt - s["s"]); D = max(0.1, s["e"] - s["s"]); k = s["i"]
    bob = 9 * np.sin(2 * np.pi * u / 4.2 + k); tilt = 0.5 * np.sin(2 * np.pi * u / 6.0 + k)
    if s["kind"] in ("photo", "map"):
        _, big, (cw, ch) = assets(s)
        z = 1.0 + 0.10 * (smooth(u / D) if k % 2 else 1 - smooth(u / D))          # inside zoom, in or out
        px = 0.5 + 0.35 * (smooth(u / D) - 0.5) * (1 if k % 3 else -1)               # slow pan
        bw, bh = big.size; vw, vh = cw / (1.12 / z) * (1 / z) * z, 0
        vw, vh = bw / z, bh / z; x0 = (bw - vw) * px; y0 = (bh - vh) / 2
        card = big.crop((round(x0), round(y0), round(x0 + vw), round(y0 + vh))).resize((cw, ch), Image.LANCZOS)
        if 0.35 < u < 1.75: sweep(card, (u - 0.35) / 1.4)
        if 6.0 < u < 7.4: sweep(card, (u - 6.0) / 1.4)
        rgba = card.convert("RGBA"); rgba.putalpha(rounded_mask(card.size, 38))
        y = max(360, (1460 - ch) // 2 + 70)
    elif s["kind"] == "post":
        top = SCROLL[fi]; push = 1.0 + 0.025 * smooth(u / D)
        win = TALL.crop((0, round(top), 1080, round(top) + WIN_H)).resize((round(SHEET_W * push), round(SHEET_H * push)), Image.LANCZOS)
        win = win.crop(((win.width - SHEET_W) // 2, 0, (win.width - SHEET_W) // 2 + SHEET_W, SHEET_H))
        li = READ[fi]
        if li is not None:
            y0 = (li[0] - top) * SCALE * push; y1 = (li[1] - top) * SCALE * push
            ov = Image.new("RGBA", win.size); ImageDraw.Draw(ov).rounded_rectangle([6, y0 - 9, SHEET_W - 6, y1 + 9], 14, fill=(255, 204, 0, 60), outline=(255, 204, 0, 235), width=4)
            win = Image.alpha_composite(win.convert("RGBA"), ov).convert("RGB")
        rgba = win.convert("RGBA"); rgba.putalpha(rounded_mask(win.size, 34)); y = SHEET_Y
        tilt *= 0.5; bob *= 0.7
    else:
        return None
    if abs(tilt) > 0.02: rgba = rgba.rotate(tilt, resample=Image.BICUBIC, expand=True)
    return rgba, (W_ - rgba.width) // 2, int(y + bob - (rgba.height - (rgba.height if abs(tilt) <= 0.02 else rgba.height)) / 2)

def shadow(im, el, x, y, a=1.0):
    m = Image.new("L", im.size, 0); m.paste(el.split()[3].point(lambda v: int(v * 0.6 * a)), (x, y + 26))
    im.paste((0, 0, 0), (0, 0), m.filter(ImageFilter.GaussianBlur(26)))

def backdrop(s, tt):
    bg = assets(s)[0]; u = tt - s["s"]; z = 1.0 + 0.06 * smooth(u / max(0.1, s["e"] - s["s"]))
    if s["kind"] != "photo" and s["kind"] != "map": return bg.copy()
    b = bg.resize((round(W_ * z), round(H_ * z))); ox = (b.width - W_) // 2; oy = (b.height - H_) // 2
    return b.crop((ox, oy, ox + W_, oy + H_))

# --- 9. End card ---
def endcard(tt):
    im = Image.new("RGB", (W_, H_), NAVY); u = tt - SH[-1]["s"]
    pill(im, 760, "WHAT DO YOU THINK?", 76, YEL, NAVY, pop=u / 0.35)
    if u > 0.35:
        d = ImageDraw.Draw(im); f = F6(56); t1 = "Tell me in the comments."
        d.text(((W_ - d.textlength(t1, font=f)) / 2, 862 + 30 * (1 - smooth((u - 0.35) / 0.3))), t1, font=f, fill=WHITE)
    pill(im, 1060, "FOLLOW FOR MORE", 64, BLUE, WHITE, pop=(u - 0.7) / 0.35)
    return im

# --- 10. Grade ---
yy, xx = np.mgrid[0:H_, 0:W_]; r = np.sqrt(((xx - W_ / 2) / (W_ * 0.75)) ** 2 + ((yy - H_ / 2) / (H_ * 0.75)) ** 2)
VIG = np.clip(1 - 0.35 * r ** 2, 0.55, 1)[..., None].astype(np.float32)
rng = np.random.default_rng(1); GR = [rng.normal(0, 4.5, (H_, W_, 1)).astype(np.float32) for _ in range(4)]

# --- 11. One frame ---
def frame(fi):
    tt = fi / FPS
    s = next((x for x in SH if x["s"] <= tt < x["e"]), SH[-1])
    if s["kind"] == "end" and tt - s["s"] >= TR:
        im = endcard(tt)
    else:
        p = (tt - s["s"]) / TR if s["i"] > 0 else 1.0      # 0..1 through the change into this shot
        old = SH[s["i"] - 1] if s["i"] > 0 else None
        im = backdrop(s, tt) if s["kind"] != "end" else endcard(tt)
        if p < 1 and old is not None and old["kind"] != "end":
            im = Image.blend(backdrop(old, tt), im, smooth(p))
            e = element(old, tt, fi)
            if e:                                            # the old card leaves upward
                el, x, y = e; y -= int(1500 * in_cubic(p)); el.putalpha(el.split()[3].point(lambda v: int(v * (1 - smooth(p)))))
                shadow(im, el, x, y, 1 - p); im.paste(el, (x, y), el)
        if s["kind"] != "end":
            e = element(s, tt, fi)
            if e:                                            # the new card rises from the bottom
                el, x, y = e; y += int(1300 * (1 - out_back(p, 1.2)))
                shadow(im, el, x, y); im.paste(el, (x, y), el)
            if s["kind"] == "post":
                d = ImageDraw.Draw(im); f = F6(30); w = d.textlength(SOURCE, font=f)
                d.rounded_rectangle([(W_ - w) / 2 - 26, 78, (W_ + w) / 2 + 26, 140], 31, fill=(0, 0, 0)); d.text(((W_ - w) / 2, 92), SOURCE, font=f, fill=(225, 225, 225))
                band = Image.new("RGBA", (W_, H_)); ImageDraw.Draw(band).rectangle([0, 1490, W_, 1720], fill=(0, 0, 0, 170))
                im = Image.alpha_composite(im.convert("RGBA"), band).convert("RGB")
            if s.get("kick"):
                ch = assets(s)[2][1] if s["kind"] in ("photo", "map") else 0
                pill(im, max(360, (1460 - ch) // 2 + 70) - 92, s["kick"], pop=(tt - s["s"] - 0.35) / 0.35)
            if s.get("hook"):
                pill(im, 250, s["hook"], 64, pop=(tt - s["s"] - 0.25) / 0.4)
            caption(im, tt)
    a = np.asarray(im).astype(np.float32) * VIG + GR[fi % 4]
    for x in SH[1:]:                                        # a faint flash on each change
        k = fi - round(x["s"] * FPS)
        if 0 <= k < 3: a = a + (255 - a) * (0.28 * (1 - k / 3))
    return np.clip(a, 0, 255).astype(np.uint8).tobytes()

# --- 12. Run: stills to look at, or the whole video ---
if __name__ == "__main__":
    if len(sys.argv) > 2:
        for fi in map(int, sys.argv[2:]): Image.frombytes("RGB", (W_, H_), frame(fi)).save(f"still_{fi}.jpg")
        raise SystemExit
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", "30", "-i", "-",
                          "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "video_silent.mp4"], stdin=subprocess.PIPE)
    for fi in range(NF): p.stdin.write(frame(fi))
    p.stdin.close(); p.wait()
