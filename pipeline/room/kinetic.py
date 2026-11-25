# ============================================================
# KINETIC CAPTIONS (his caption samples, 2026-11-25)
# What : captions that build word by word into a short phrase, stacked, in three voices:
#        small lowercase for little words, one big bold word in an accent colour per phrase (the key
#        word), and a soft italic serif for feeling words. Each word lands on its spoken time with a
#        quick rise and fade (the key word pops); the phrase clears together. Upper third of the
#        screen, never over his mouth.
# Fonts: Plus Jakarta Sans (brand), Instrument Serif Italic (SIL Open Font Licence, google/fonts).
# ============================================================
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

STOP = set('a an the to of in on at for and or but so is are was be been it its i you your we our they their them that this these those who what when how as by from with if can no not do just even get up out about there then than all some any my me he she his her us one'.split())
FEEL = set('life beautiful inward little things improvement improvements appreciate thankful god yourself today yesterday past better living worth heart grateful gossip business'.split())
NEG = set('distress depression spiraling last difficult cannot couldnt cant stop stopped struggle'.split())
YELLOW = (255, 210, 63); PEACH = (240, 160, 122); RED = (232, 69, 60); WHITE = (255, 255, 255)

def _font(path, size, w=None):
    f = ImageFont.truetype(path, size)
    if w: f.set_variation_by_axes([w])
    return f
SANS = 'work/PlusJakartaSans.ttf'; SERIF = 'work/InstrumentSerif-Italic.ttf'
F_SMALL = _font(SANS, 58, 600); F_MID = _font(SANS, 70, 800); F_KEY = _font(SANS, 118, 800); F_FEEL = _font(SERIF, 104)

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

def word_image(text, font, colour, glow=False):
    # one word with a soft dark shadow (readable on any background); feeling words get a warm glow
    pad = 40
    d0 = ImageDraw.Draw(Image.new('L', (1, 1)))
    bb = d0.textbbox((0, 0), text, font=font)
    w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    txt = Image.new('L', (w, h), 0); ImageDraw.Draw(txt).text((pad - bb[0], pad - bb[1]), text, font=font, fill=255)
    a = np.array(txt).astype(np.float32) / 255
    # v3: a stronger, two-layer shadow: readable on the bright curtain too (never light text on light)
    sh = np.clip(cv2.GaussianBlur(cv2.dilate(a, np.ones((5, 5), np.uint8)), (0, 0), 5) * 1.1 + cv2.GaussianBlur(a, (0, 0), 16) * 0.6, 0, 0.92)
    img = np.zeros((h, w, 4), np.float32)
    col = np.array(colour, np.float32)
    if glow:
        g = cv2.GaussianBlur(a, (0, 0), 14) * 0.9
        img[..., :3] = col * g[..., None] * 0.5; img[..., 3] = np.maximum(sh, g * 0.5)
    else:
        img[..., 3] = sh                                      # shadow is black
    img[..., :3] = img[..., :3] * (1 - a[..., None]) + col * a[..., None]
    img[..., 3] = np.maximum(img[..., 3], a)
    return img, bb[3] - bb[1], pad

class Kinetic:
    def __init__(s, cap, OW=1080, top=320, width=900):   # below TikTok's top buttons
        s.OW, s.top, s.width = OW, top, width
        s.ph = []
        for k, p in enumerate(phrases(cap)):
            words = [w['w'] for w in p]
            cands = [i for i, w in enumerate(words) if clean(w) not in STOP]
            key = max(cands, key=lambda i: (len(clean(words[i])), i)) if cands else len(words) - 1
            items = []
            for i, w in enumerate(p):
                c = clean(w['w']); t = w['w'].strip(',.!?')
                if i == key:
                    col = RED if c in NEG else PEACH if c in FEEL else YELLOW
                    img = word_image(t.upper(), F_KEY, col); kind = 'key'
                elif c in FEEL:
                    img = word_image(t.lower(), F_FEEL, PEACH, glow=True); kind = 'feel'
                elif c in STOP:
                    img = word_image(t.lower(), F_SMALL, WHITE); kind = 'small'
                else:
                    img = word_image(t.lower(), F_MID, WHITE); kind = 'mid'
                items.append({'img': img, 's': w['s'], 'kind': kind})
            s._layout(items)
            s.ph.append({'items': items, 's': p[0]['s'] - 0.05, 'e': p[-1]['e'] + 0.35})
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
        y = s.top
        for line in lines:
            hmax = max(it['img'][1] for it in line)
            total = sum(it['img'][0].shape[1] - 2 * it['img'][2] for it in line) + 18 * (len(line) - 1)
            x = (s.OW - total) / 2
            for it in line:
                img, th, pad = it['img']
                it['x'] = int(x - pad); it['y'] = int(y + (hmax - th) - pad)
                x += img.shape[1] - 2 * pad + 18
            y += hmax + 22

    def draw(s, frame, t):
        for p in s.ph:
            if not (p['s'] <= t < p['e']): continue
            fade_out = min(1.0, max(0.0, (p['e'] - t) / 0.12))
            for it in p['items']:
                dt = t - it['s'] + 0.04
                if dt < 0: continue
                k = min(dt / 0.12, 1.0); e = 1 - (1 - k) ** 3
                img = it['img'][0]
                if it['kind'] == 'key' and k < 1:               # the key word pops in
                    sc = 1.25 - 0.25 * e
                    img = cv2.resize(img, None, fx=sc, fy=sc, interpolation=cv2.INTER_LINEAR)
                    ox = it['x'] - (img.shape[1] - it['img'][0].shape[1]) // 2; oy = it['y'] - (img.shape[0] - it['img'][0].shape[0]) // 2
                else:
                    ox, oy = it['x'], it['y'] + int(16 * (1 - e))
                a = img[..., 3:4] * e * fade_out
                h, w = img.shape[:2]
                y0, x0 = max(oy, 0), max(ox, 0); y1, x1 = min(oy + h, frame.shape[0]), min(ox + w, frame.shape[1])
                if y1 <= y0 or x1 <= x0: continue
                sub = img[y0 - oy:y1 - oy, x0 - ox:x1 - ox]; aa = a[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
                reg = frame[y0:y1, x0:x1]
                reg[:] = reg * (1 - aa) + sub[..., :3][..., ::-1] * aa
            return
