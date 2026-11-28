# ============================================================
# KINETIC CAPTIONS (his caption samples, 2026-11-25)
# What : captions that build word by word into a short phrase, stacked, in three voices:
#        small lowercase for little words, one big bold word in an accent colour per phrase (the key
#        word), and a soft italic serif for feeling words. Each word lands on its spoken time with a
#        quick rise and fade (the key word pops); the phrase clears together.
#        v5 (his note on v4): the captions sit LOW, over the chest and stomach, never over the face;
#        a soft dark scrim under them keeps them readable; key words get a gradient, a crisp outline,
#        a coloured glow and a growing underline; words settle with a small overshoot. No sound.
#        v6 (his note on the hospital vlog, 2026-11-27: a voiceover needs captions with more personality): Kinetic(..., personality=True) adds a marker
#        highlight on some key words, key words tilted a few degrees, a light sweep across each key word, a small pulse as it ends, brand colours
#        for product names (Amara, StellaXafe), and phrases that enter from alternate sides. Off by default: the Life video is unchanged.
#        karaoke=True (idea taken from a reference, 2026-11-28): ordinary words turn yellow while they are being said, then back to white.
#        Each video uses a different mix of these ideas on purpose (docs/CAPTION-IDEAS.md): the same look every time gets boring.
# Fonts: Plus Jakarta Sans (brand), Instrument Serif Italic (SIL Open Font Licence, google/fonts).
# ============================================================
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

STOP = set('a an the to of in on at for and or but so is are was be been it its i you your we our they their them that this these those who what when how as by from with if can no not do just even get up out about there then than all some any my me he she his her us one'.split())
FEEL = set('life beautiful inward little things improvement improvements appreciate thankful god yourself today yesterday past better living worth heart grateful gossip business'.split())
NEG = set('distress depression spiraling last difficult cannot couldnt cant stop stopped struggle'.split())
# v4 colours (his note on v3): bright white, bright yellow, bright red, silver for small words. No peach, no dim red.
YELLOW = (255, 222, 0); RED = (255, 45, 45); WHITE = (255, 255, 255); SILVER = (205, 211, 220); PEACH = YELLOW

def _font(path, size, w=None):
    f = ImageFont.truetype(path, size)
    if w: f.set_variation_by_axes([w])
    return f
SANS = 'work/PlusJakartaSans.ttf'; SERIF = 'work/InstrumentSerif-Italic.ttf'
DISPLAY = 'work/Anton-Regular.ttf'   # a tall condensed display face (SIL OFL, google/fonts): the stylish key words
F_SMALL = _font(SANS, 58, 700); F_MID = _font(SANS, 72, 800); F_KEY = _font(SANS, 118, 800)
F_KEY2 = _font(DISPLAY, 150); F_FEEL = _font(SERIF, 112)

def clean(w): return ''.join(c for c in w.lower() if c.isalnum())

def phrases(cap):
    out, cur = [], []
    for k, w in enumerate(cap):
        if cur and (w['s'] - cur[-1]['e'] > 0.35 or w.get('clip') != cur[-1].get('clip')):
            out.append(cur); cur = []
        cur.append(w)
        end = w['w'][-1] in '.?!,' and len(cur) >= 2
        if end or len(cur) >= 6: out.append(cur); cur = []
    if cur: out.append(cur)
    return out

def word_image(text, font, colour, glow=False, key=False):
    # one word: a crisp dark outline, a soft two-layer shadow (readable on any background), a light
    # gradient on key words, and a warm glow on key and feeling words
    pad = 48
    d0 = ImageDraw.Draw(Image.new('L', (1, 1)))
    bb = d0.textbbox((0, 0), text, font=font)
    w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    txt = Image.new('L', (w, h), 0); ImageDraw.Draw(txt).text((pad - bb[0], pad - bb[1]), text, font=font, fill=255)
    a = np.array(txt).astype(np.float32) / 255
    outline = np.clip(cv2.dilate(a, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9 if key else 7,) * 2)), 0, 1)
    sh = np.clip(cv2.GaussianBlur(outline, (0, 0), 6) * 1.15 + cv2.GaussianBlur(a, (0, 0), 18) * 0.6, 0, 0.95)
    img = np.zeros((h, w, 4), np.float32)
    col = np.array(colour, np.float32)
    fill = np.ones((h, w, 3), np.float32) * col
    if key:                                                  # a light top edge fading to the full colour
        ramp = np.clip(np.linspace(0.55, 0.0, h), 0, 1)[:, None, None]
        fill = fill * (1 - ramp) + np.array([255, 255, 255], np.float32) * ramp * 0.55 + fill * ramp * 0.45
    if glow or key:
        g = cv2.GaussianBlur(a, (0, 0), 16 if key else 14) * (0.85 if key else 0.9)
        img[..., :3] = col * g[..., None] * 0.55; img[..., 3] = np.maximum(sh, g * 0.45)
    else:
        img[..., 3] = sh
    img[..., :3] = img[..., :3] * (1 - outline[..., None]) + np.array([12, 12, 16], np.float32) * outline[..., None] * (1 - 0)
    img[..., 3] = np.maximum(img[..., 3], outline)
    img[..., :3] = img[..., :3] * (1 - a[..., None]) + fill * a[..., None]
    img[..., 3] = np.maximum(img[..., 3], a)
    return img, bb[3] - bb[1], pad

BRAND = {'amara': (236, 198, 104), 'stellaxafe': (150, 166, 255)}      # product names get their own colour (personality mode)

def brand_of(word):
    c = clean(word)
    for b, col in BRAND.items():
        if c.startswith(b): return col
    return None

def tilt_image(img, th, pad, deg):
    # the same word turned a few degrees: the canvas grows so nothing is cut, and the layout keeps the word's own width
    h, w = img.shape[:2]; m = int(0.14 * max(h, w))
    big = np.zeros((h + 2 * m, w + 2 * m, 4), np.float32); big[m:m + h, m:m + w] = img
    M = cv2.getRotationMatrix2D((big.shape[1] / 2, big.shape[0] / 2), deg, 1.0)
    return cv2.warpAffine(big, M, (big.shape[1], big.shape[0]), flags=cv2.INTER_LINEAR), th, pad + m

def marker_image(text, font, bg=(255, 222, 0), ink=(14, 18, 40)):
    # a highlighter swipe behind the word, the word in dark ink on it: the "marker" look
    pad = 48; px, py = 34, 14
    d0 = ImageDraw.Draw(Image.new('L', (1, 1))); bb = d0.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    w, h = tw + 2 * px + 2 * pad, th + 2 * py + 2 * pad
    rect = Image.new('L', (w * 2, h * 2), 0)
    ImageDraw.Draw(rect).rounded_rectangle([pad * 2, pad * 2, (w - pad) * 2, (h - pad) * 2], radius=20, fill=255)
    rect = np.array(rect.resize((w, h), Image.LANCZOS)).astype(np.float32) / 255
    txt = Image.new('L', (w, h), 0); ImageDraw.Draw(txt).text((pad + px - bb[0], pad + py - bb[1]), text, font=font, fill=255)
    a = np.array(txt).astype(np.float32) / 255
    sh = cv2.GaussianBlur(rect, (0, 0), 9) * 0.55
    img = np.zeros((h, w, 4), np.float32)
    img[..., :3] = np.array(bg, np.float32) * rect[..., None] * (1 - a[..., None]) + np.array(ink, np.float32) * a[..., None]
    img[..., 3] = np.maximum(np.maximum(rect, sh), a)
    return img, th + 2 * py, pad

def ease_out_k(k):
    k = min(max(k, 0), 1); return 1 - (1 - k) ** 3

def _ease_back(k, o=1.5):
    k = min(max(k, 0), 1) - 1
    return 1 + (o + 1) * k ** 3 + o * k ** 2

class Kinetic:
    def __init__(s, cap, OW=1080, bottom=1560, width=900, OH=1920, personality=False, karaoke=False):   # low on the screen, above TikTok's bottom buttons
        s.OW, s.bottom, s.width, s.OH = OW, bottom, width, OH
        s.personality = personality; s.karaoke = karaoke; s.ph = []; kc = 0
        for k, p in enumerate(phrases(cap)):
            words = [w['w'] for w in p]
            cands = [i for i, w in enumerate(words) if clean(w) not in STOP]
            key = max(cands, key=lambda i: (len(clean(words[i])), i)) if cands else len(words) - 1
            if personality:
                br = [i for i, w in enumerate(words) if brand_of(w)]
                if br: key = br[0]
            items = []
            for i, w in enumerate(p):
                c = clean(w['w']); t = w['w'].strip(',.!?')
                if i == key:
                    col = RED if c in NEG else YELLOW if k % 3 != 2 else WHITE
                    style = 'pop'
                    if personality:
                        brand = brand_of(w['w'])
                        if brand: col = brand
                        else: style = ('tilt', 'marker', 'pop', 'tilt2')[kc % 4]
                        kc += 1
                    fnt = F_KEY2 if k % 2 else F_KEY
                    if style == 'marker': img = marker_image(t.upper(), fnt)
                    else:
                        img = word_image(t.upper(), fnt, col, key=True)
                        if style in ('tilt', 'tilt2'): img = tilt_image(*img, 3.5 if style == 'tilt' else -3.5)
                    kind = 'key'
                elif c in FEEL:
                    img = word_image(t.lower(), F_FEEL, YELLOW if k % 2 == 0 else WHITE, glow=True); kind = 'feel'
                elif c in STOP:
                    img = word_image(t.lower(), F_SMALL, SILVER); kind = 'small'
                else:
                    img = word_image(t.lower(), F_MID, WHITE); kind = 'mid'
                items.append({'img': img, 's': w['s'], 'e': w['e'], 'kind': kind})
                if karaoke and kind in ('small', 'mid'):                     # the same word in yellow, for the moment it is being said
                    items[-1]['act'] = word_image(t.lower(), F_SMALL if kind == 'small' else F_MID, YELLOW)[0]
                if kind == 'key': items[-1]['ucol'] = col; items[-1]['style'] = style if personality else 'pop'
            s._layout(items)
            s.ph.append({'items': items, 's': p[0]['s'] - 0.05, 'e': p[-1]['e'] + 0.35, 'top': items[0]['y'], 'dir': (0, -1, 1)[k % 3] if personality else 0})
        for k in range(len(s.ph) - 1):                      # a phrase clears when the next one starts
            s.ph[k]['e'] = min(s.ph[k]['e'], s.ph[k + 1]['s'])

    def _layout(s, items):
        # flow words into lines (the key word sits on a line of its own), centred
        lines, cur, cw = [], [], 0
        for it in items:
            img, th, pad = it['img']; w = img.shape[1] - 2 * pad
            if it['kind'] == 'key':
                if cur: lines.append(cur)
                lines.append([it]); cur, cw = [], 0; continue
            if cur and cw + w + 18 > s.width: lines.append(cur); cur, cw = [], 0
            cur.append(it); cw += w + 18
        if cur: lines.append(cur)
        total_h = sum(max(it['img'][1] for it in line) for line in lines) + 22 * (len(lines) - 1)
        y = s.bottom - total_h
        for line in lines:
            hmax = max(it['img'][1] for it in line)
            total = sum(it['img'][0].shape[1] - 2 * it['img'][2] for it in line) + 18 * (len(line) - 1)
            x = (s.OW - total) / 2
            for it in line:
                img, th, pad = it['img']
                it['x'] = int(x - pad); it['y'] = int(y + (hmax - th) - pad)
                x += img.shape[1] - 2 * pad + 18
            y += hmax + 22

    def _scrim(s):
        # a soft dark gradient behind the caption area (nothing over the face): clear at the top, up to 38% at the bottom
        y = np.arange(s.OH, dtype=np.float32)
        top = s.bottom - 560
        a = np.clip((y - top) / 380, 0, 1) ** 1.4 * 0.38
        return a[:, None, None]

    def draw(s, frame, t):
        if not hasattr(s, '_sc'): s._sc = s._scrim()
        for p in s.ph:
            if not (p['s'] <= t < p['e']): continue
            fade_in = min(1.0, max(0.0, (t - p['s']) / 0.15))
            fade_out = min(1.0, max(0.0, (p['e'] - t) / 0.14))
            frame *= 1 - s._sc * fade_in * fade_out                   # the scrim
            lift = int(10 * (1 - fade_out))
            for it in p['items']:
                dt = t - it['s'] + 0.04
                if dt < 0: continue
                k = min(dt / 0.16, 1.0); e = _ease_back(k, 1.2) if it['kind'] != 'key' else _ease_back(k, 1.7)
                img = it['img'][0]
                if s.karaoke and 'act' in it:                          # the walking highlight: white, yellow while it is said, white again (idea from a reference, 2026-11-28)
                    wa = min(1.0, max(0.0, (t - it['s']) / 0.05)) * (1.0 - min(1.0, max(0.0, (t - it['e'] - 0.02) / 0.08)))
                    if wa > 0: img = img * (1 - wa) + it['act'] * wa
                pulse = 0.0
                if s.personality and it['kind'] == 'key' and k >= 1:           # a small pulse as the key word ends
                    de = t - it['e']
                    if 0 <= de < 0.20: pulse = 0.07 * np.sin(np.pi * de / 0.20)
                if it['kind'] == 'key' and (k < 1 or pulse > 0):               # the key word pops in with a small overshoot (and pulses as it ends)
                    sc = 1.0 + 0.30 * (1 - e) + pulse
                    img = cv2.resize(img, None, fx=sc, fy=sc, interpolation=cv2.INTER_LINEAR)
                    ox = it['x'] - (img.shape[1] - it['img'][0].shape[1]) // 2; oy = it['y'] - (img.shape[0] - it['img'][0].shape[0]) // 2
                else:
                    ox, oy = it['x'] + int(p['dir'] * 46 * (1 - e)), it['y'] + int(18 * (1 - e))
                if s.personality and it.get('style') == 'marker' and k < 1:    # the highlighter swipes across, left to right
                    wipe = ease_out_k(min(1.0, dt / 0.20)); img = img.copy(); cut = int(img.shape[1] * wipe); img[:, cut:, 3] = 0
                oy -= lift
                al = min(1.0, k * 1.6) * fade_out
                a = img[..., 3:4] * al
                h, w = img.shape[:2]
                y0, x0 = max(oy, 0), max(ox, 0); y1, x1 = min(oy + h, frame.shape[0]), min(ox + w, frame.shape[1])
                if y1 <= y0 or x1 <= x0: continue
                sub = img[y0 - oy:y1 - oy, x0 - ox:x1 - ox]; aa = a[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
                reg = frame[y0:y1, x0:x1]
                reg[:] = reg * (1 - aa) + sub[..., :3][..., ::-1] * aa
                if s.personality and it['kind'] == 'key' and it.get('style') != 'marker':      # a light sweeps across the word once, just after it lands
                    u = (dt - 0.14) / 0.55
                    if 0 < u < 1:
                        hh, ww = sub.shape[:2]; xx = np.arange(ww, dtype=np.float32)[None, :] - np.arange(hh, dtype=np.float32)[:, None] * 0.45
                        band = np.exp(-((xx - (u * (ww + 160) - 80)) / 34.0) ** 2)[..., None]
                        reg[:] = reg + 150.0 * band * aa * (sub[..., 3:4] > 0.5)
                if it['kind'] == 'key' and it.get('style') != 'marker':       # a thin underline grows out from the middle (not on a marker)
                    th, pad = it['img'][1], it['img'][2]; wid = it['img'][0].shape[1] - 2 * pad
                    grow = min(1.0, max(0.0, (dt - 0.10) / 0.22)); grow = 1 - (1 - grow) ** 3
                    ux = it['x'] + pad + wid // 2; half = int(wid * 0.5 * grow * 0.92); uy = it['y'] + pad + th + 16 - lift
                    if half > 2 and 0 <= uy < frame.shape[0] - 8:
                        col = np.array(it.get('ucol', (255, 222, 0)), np.float32)[::-1]
                        band = frame[uy:uy + 7, max(ux - half, 0):ux + half]
                        band[:] = band * (1 - 0.9 * fade_out) + col * 0.9 * fade_out
            return
