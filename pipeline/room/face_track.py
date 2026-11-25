# His face centre in every raw frame (YuNet face finder), mirrored to match the flipped room render,
# smoothed so the close shots glide instead of shake. Writes work/face_track.json (1440 x 2560 units).
import json, subprocess, numpy as np, cv2
W,H=360,640; S=1440/W
det=cv2.FaceDetectorYN.create('/home/user/Videos/models/yunet.onnx','',(W,H),0.6)
p=subprocess.Popen(['ffmpeg','-loglevel','error','-i','raw/why_life_is_beautiful.mp4','-vf',f'fps=30,scale={W}:{H}','-f','rawvideo','-pix_fmt','bgr24','-'],stdout=subprocess.PIPE)
xs=[];ys=[]
while True:
    b=p.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    f=np.frombuffer(b,np.uint8).reshape(H,W,3)
    _,faces=det.detect(f)
    if faces is not None and len(faces):
        x,y,w,h=faces[0][:4]; xs.append(x+w/2); ys.append(y+h/2)
    else: xs.append(np.nan); ys.append(np.nan)
xs=np.array(xs); ys=np.array(ys); ok=~np.isnan(xs); idx=np.arange(len(xs))
xs=np.interp(idx,idx[ok],xs[ok]); ys=np.interp(idx,idx[ok],ys[ok])
k=np.ones(31)/31
sm=lambda a: np.convolve(np.pad(a,15,mode='edge'),k,'valid')
X=1440-sm(xs)*S; Y=sm(ys)*S                     # mirrored: the room render is flipped
json.dump({'x':X.round(1).tolist(),'y':Y.round(1).tolist()},open('work/face_track.json','w'))
print('frames',len(X),'found',int(ok.sum()),'x range',int(X.min()),int(X.max()),'y range',int(Y.min()),int(Y.max()))
