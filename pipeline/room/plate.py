# Build the clean plate (empty room) from frames where he does not cover each pixel.
import os, sys, subprocess, numpy as np, cv2, mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
SRC='raw/why_life_is_beautiful.mp4'; W,H=1080,1920
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=mpt.BaseOptions(model_asset_path='/home/user/Videos/models/selfie_segmenter.tflite'), output_confidence_masks=True))
times=np.arange(0.5,137,0.75)
frames=[];masks=[]
for t in times:
    raw=subprocess.run(['ffmpeg','-loglevel','error','-ss',str(t),'-i',SRC,'-frames:v','1','-vf',f'scale={W}:{H}','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    f=np.frombuffer(raw,np.uint8).reshape(H,W,3)
    small=cv2.resize(f,(270,480))
    r=seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB,data=np.ascontiguousarray(small)))
    m=cv2.resize(r.confidence_masks[0].numpy_view(),(W,H))
    m=cv2.dilate((m>0.2).astype(np.uint8),np.ones((41,41),np.uint8))
    frames.append(f);masks.append(m)
F=np.stack(frames); M=np.stack(masks).astype(bool); del frames,masks
# camera motion check: correlation of the top-right corner between first and later frames
g=[cv2.cvtColor(x[0:400,700:1080],cv2.COLOR_RGB2GRAY).astype(np.float32) for x in F[::20]]
print('shift vs first:',[tuple(np.round(cv2.phaseCorrelate(g[0],x)[0],1)) for x in g[1:]])
plate=np.zeros((H,W,3),np.float32)
for y in range(0,H,64):
    blk=F[:,y:y+64].astype(np.float16); mk=M[:,y:y+64]
    blk[mk]=np.nan
    plate[y:y+64]=np.nanmedian(blk.astype(np.float32),axis=0)
cover=np.isnan(plate[...,0]); print('never seen pixels:',cover.mean())
plate=np.nan_to_num(plate).astype(np.uint8)
plate=cv2.inpaint(cv2.cvtColor(plate,cv2.COLOR_RGB2BGR),cover.astype(np.uint8)*255,9,cv2.INPAINT_TELEA)
cv2.imwrite('work/plate_raw.png',plate); np.save('work/cover.npy',cover)
