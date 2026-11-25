# ROOM FULL (from OPTION B v2): whole video, no zoom and no corner darkening (those come at assembly).
# OPTION B v2: his ChatGPT room behind him, calmer: darker, softer, less green, warm; light on him.
# Matting runs inline (RVM), and its cleaned foreground colours are used at the edge, so no light
# rim of the old room shows against the darker new one.
import sys, subprocess, numpy as np, cv2, torch
T0,DUR,OUT,SKIP=float(sys.argv[1]),float(sys.argv[2]),sys.argv[3],float(sys.argv[4])   # SKIP: warm-up seconds not written
IW,IH=1440,2560; OW,OH=1080,1920; FPS=30
# --- 1. The look of the room ---
BG_LIGHT=0.55     # room brightness (1 = as the picture is)
BG_SAT=0.62       # colour strength of the room (the green was too loud)
BG_BLUR=3.5       # a little soft focus, like a camera focused on him
WARM=(1.06,1.00,0.90)   # B,G,R gains... applied as R up, B down (warm, like his references)
# --- 2. The room picture, lined up and matched to the real room ---
H=np.load('work/H_ai.npy'); Sc=np.diag([IW/1080,IH/1920,1.0])
ai=cv2.warpPerspective(cv2.imread('pictures/room_ai.png'),Sc@H,(IW,IH),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
real=cv2.resize(cv2.imread('work/plate_raw.png'),(IW,IH)).astype(np.float32)
seen=cv2.resize((~np.load('work/cover.npy')).astype(np.uint8),(IW,IH),interpolation=cv2.INTER_NEAREST)>0
for c in range(3):
    a_,r_=ai[...,c][seen],real[...,c][seen]
    ai[...,c]=(ai[...,c]-a_.mean())/(a_.std()+1e-6)*r_.std()+r_.mean()
ai=np.clip(ai,0,255).astype(np.uint8)
hsv=cv2.cvtColor(ai,cv2.COLOR_BGR2HSV).astype(np.float32); hsv[...,1]*=BG_SAT; hsv[...,2]*=BG_LIGHT
bg=cv2.cvtColor(np.clip(hsv,0,255).astype(np.uint8),cv2.COLOR_HSV2BGR).astype(np.float32)
bg[...,2]*=1.05; bg[...,0]*=0.92                     # warm: a touch more red, less blue
bg=cv2.GaussianBlur(bg,(0,0),BG_BLUR)
# light falls off away from him: a soft pool of light behind his head, darker towards the edges
yy,xx=np.mgrid[0:IH,0:IW].astype(np.float32)
pool=np.exp(-(((xx-IW*0.42)/(IW*0.55))**2+((yy-IH*0.30)/(IH*0.42))**2))
bg*= (0.70+0.30*pool)[...,None]
bg=np.clip(bg,0,255)
OLD=cv2.resize(cv2.imread('work/plate_raw.png'),(IW,IH)).astype(np.float32)
SEEN=cv2.GaussianBlur(seen.astype(np.float32),(0,0),3)
BGW=cv2.GaussianBlur(bg,(0,0),12)
KEEP=np.clip((np.linspace(0,1,IH)[:,None]-0.63)/0.06,0,1)*np.ones((1,IW),np.float32)
# --- 3. Polish for the whole picture (after the flip) ---
r=np.sqrt(((xx-IW*0.5)/(IW*0.62))**2+((yy-IH*0.42)/(IH*0.62))**2)
cw=np.clip((r-0.60)/0.50,0,1)**1.3; VIG=(1-0.40*cw)[...,None]
x=np.arange(256)/255.0
curve=np.clip(255*(x+0.03*np.sin(np.pi*x)*(1-x)*2+0.05*(x-0.5)*np.sin(np.pi*x)),0,255).astype(np.uint8)
torch.set_num_threads(2); cv2.setNumThreads(2)
m=torch.jit.load('/home/user/Videos/models/rvm_mobilenetv3.torchscript').eval(); rec=[None]*4
dec=subprocess.Popen(['ffmpeg','-loglevel','error','-ss',str(T0),'-t',str(DUR),'-i','raw/why_life_is_beautiful.mp4','-vf',f'fps={FPS},scale={IW}:{IH}:flags=lanczos','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{IW}x{IH}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','14','-preset','fast','-pix_fmt','yuv420p',OUT],stdin=subprocess.PIPE)
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
        f=fgc*al+bg*(1-al)
        # 2. light wrap: a little of the new room's light spills onto his outer edge, as in a real room
        soft_a=cv2.GaussianBlur(al[...,0],(0,0),6)[...,None]
        wrap=np.clip(al-soft_a,0,1)*0.7                   # only a thin band just inside his edge
        f=f*(1-wrap)+BGW*wrap
        f=np.clip(f,0,255).astype(np.uint8)
        f=cv2.flip(f,1); f=cv2.LUT(f,curve)
        bl=cv2.GaussianBlur(f,(0,0),1.6); f=cv2.addWeighted(f,1.3,bl,-0.3,0)
        out=f
        if i>=int(round(SKIP*FPS)): enc.stdin.write(out.tobytes())
        i+=1
        if i%300==0: print('frame',i,flush=True)
enc.stdin.close(); enc.wait(); print('frames',i)
