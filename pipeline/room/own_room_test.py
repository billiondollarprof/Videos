# OPTION C (v4 plan): HIS OWN ROOM, softly blurred, same colours, poster blurred; RVM edge.
# (based on OPTION B v2) his ChatGPT room behind him, calmer: darker, softer, less green, warm; light on him.
# Matting runs inline (RVM), and its cleaned foreground colours are used at the edge, so no light
# rim of the old room shows against the darker new one.
import sys, subprocess, numpy as np, cv2, torch
T0,DUR,OUT,JOIN=float(sys.argv[1]),float(sys.argv[2]),sys.argv[3],float(sys.argv[4])
IW,IH=1440,2560; OW,OH=1080,1920; FPS=30
# --- 1. The look of the room ---
BG_LIGHT=0.55     # room brightness (1 = as the picture is)
BG_SAT=0.62       # colour strength of the room (the green was too loud)
BG_BLUR=3.5       # a little soft focus, like a camera focused on him
WARM=(1.06,1.00,0.90)   # B,G,R gains... applied as R up, B down (warm, like his references)
OLD=cv2.resize(cv2.imread('work/plate_raw.png'),(IW,IH)).astype(np.float32)
seen=cv2.resize((~np.load('work/cover.npy')).astype(np.uint8),(IW,IH),interpolation=cv2.INTER_NEAREST)>0
SEEN=cv2.GaussianBlur(seen.astype(np.float32),(0,0),3)
yy,xx=np.mgrid[0:IH,0:IW].astype(np.float32)
# the poster (as filmed, before the flip): blurred hard so its writing cannot be read; a fixed soft mask
PM=np.zeros((IH,IW),np.float32); cv2.fillPoly(PM,[np.array([(1080,110),(1434,28),(1439,172),(1082,270)],np.int32)],1.0)
PM=cv2.GaussianBlur(cv2.dilate(PM,np.ones((25,25),np.uint8)),(0,0),12)[...,None]
BLUR=4.0
KEEP=np.clip((np.linspace(0,1,IH)[:,None]-0.63)/0.06,0,1)*np.ones((1,IW),np.float32)
# --- 3. Polish for the whole picture (after the flip) ---
r=np.sqrt(((xx-IW*0.5)/(IW*0.62))**2+((yy-IH*0.42)/(IH*0.62))**2)
cw=np.clip((r-0.60)/0.50,0,1)**1.3; VIG=(1-0.40*cw)[...,None]
x=np.arange(256)/255.0
curve=np.clip(255*(x+0.03*np.sin(np.pi*x)*(1-x)*2+0.05*(x-0.5)*np.sin(np.pi*x)),0,255).astype(np.uint8)
torch.set_num_threads(4)
m=torch.jit.load('/home/user/Videos/models/rvm_mobilenetv3.torchscript').eval(); rec=[None]*4
dec=subprocess.Popen(['ffmpeg','-loglevel','error','-ss',str(T0),'-t',str(DUR),'-i','raw/why_life_is_beautiful.mp4','-vf',f'fps={FPS},scale={IW}:{IH}:flags=lanczos','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{OW}x{OH}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p',OUT],stdin=subprocess.PIPE)
i=0
with torch.no_grad():
    while True:
        b=dec.stdout.read(IW*IH*3)
        if len(b)<IW*IH*3: break
        rgb=np.frombuffer(b,np.uint8).reshape(IH,IW,3)
        t_=torch.from_numpy(rgb.copy()).permute(2,0,1)[None].float()/255
        fgr,pha,*rec=m(t_,*rec,downsample_ratio=0.2)
        a=pha[0,0].numpy()
        fg=(fgr[0].permute(1,2,0).numpy()*255)[...,::-1]          # RVM's clean colours of him (BGR)
        raw=rgb[...,::-1].astype(np.float32)
        # inside him use the real pixels; only at the soft edge use RVM's cleaned colours
        # --- edge blending (his note: a light rim showed round his head and shoulders) ---
        # 1. choke: the outermost, half-transparent edge pixels carry the old, brighter room. Pull
        #    the edge in to where he is solid, then soften it by about one pixel.
        a=np.clip((a-0.30)/0.55,0,1); a=a*a*(3-2*a)
        a=cv2.GaussianBlur(a,(0,0),1.1)
        # on the thin band left, gently take out the old room's light (un-mix, limited and smoothed)
        a3=a[...,None]
        unmix=np.clip((raw-(1-a3)*OLD)/np.maximum(a3,0.5),0,255)
        band=((a>0.02)&(a<0.98)).astype(np.float32)
        w=(cv2.GaussianBlur(band,(0,0),1.5)*SEEN*(1-KEEP)*0.6)[...,None]
        fgc=raw*(1-w)+cv2.GaussianBlur(unmix,(0,0),1.0)*w
        al=np.maximum(a,KEEP)[...,None]
        # his own room behind him: where he stands, the clean plate fills in; then a soft blur, poster blurred hard
        room=raw*(1-a3)+OLD*a3
        bg=cv2.GaussianBlur(room,(0,0),BLUR)
        bg=bg*(1-PM)+cv2.GaussianBlur(room,(0,0),28)*PM
        f=fgc*al+bg*(1-al)
        # 2. light wrap: a little of the new room's light spills onto his outer edge, as in a real room
        soft_a=cv2.GaussianBlur(al[...,0],(0,0),6)[...,None]
        wrap=np.clip(al-soft_a,0,1)*0.7                   # only a thin band just inside his edge
        f=f*(1-wrap)+cv2.GaussianBlur(bg,(0,0),12)*wrap
        f=np.clip(f,0,255).astype(np.uint8)
        f=cv2.flip(f,1); f=cv2.LUT(f,curve)
        bl=cv2.GaussianBlur(f,(0,0),1.6); f=cv2.addWeighted(f,1.3,bl,-0.3,0)
        o=f.astype(np.float32)*VIG
        t=i/FPS; z=1.0+0.02*t/DUR+(0.14 if t>=JOIN else 0.0)
        cw_,ch_=IW/z,IH/z; cy=IH*0.40 if z>1.1 else IH/2
        x0=int(IW/2-cw_/2); y0=int(np.clip(cy-ch_/2,0,IH-ch_))
        out=cv2.resize(np.clip(o[y0:y0+int(ch_),x0:x0+int(cw_)],0,255).astype(np.uint8),(OW,OH),interpolation=cv2.INTER_AREA)
        enc.stdin.write(out.tobytes()); i+=1
enc.stdin.close(); enc.wait(); print('frames',i)
