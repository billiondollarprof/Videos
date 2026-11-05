# ============================================================
# 14 CUT-OUT: remove the background from Anthony's photo, and nothing else
# What : cuts him out of a photo with rembg (a free, open-source background remover, model
#        isnet-general-use), then removes only loose specks that are not connected to his body.
# Why  : thumbnails use his REAL photo. His face and body are never redrawn, retouched or
#        reshaped (his rule, 2026-11-05: image tools "will go and spoil my image").
# Use  : python3 14_cutout.py photo.jpg cutout.png
# Never: never run a rectangle eraser over his outline: it nicked his shoulder once. Only
#        components that are not connected to the main body are removed.
# ============================================================
import sys

import numpy as np
from PIL import Image
from rembg import new_session, remove
from scipy import ndimage as ndi

SRC, OUT = sys.argv[1], sys.argv[2]
cut = np.array(remove(Image.open(SRC).convert("RGB"), session=new_session("isnet-general-use")).convert("RGBA"))
alpha = cut[..., 3]
lab, n = ndi.label(alpha > 60)
main = lab == (1 + int(np.argmax(ndi.sum(alpha > 60, lab, range(1, n + 1)))))
keep = ndi.binary_dilation(main, iterations=8)          # a few pixels of soft edge around him
cut[..., 3] = np.where(keep, alpha, 0)
Image.fromarray(cut).save(OUT)
print("cut-out saved:", OUT, "| loose specks removed:", int(((alpha > 0) & ~keep).sum()), "pixels")
