# ============================================================
# VO 03 RENDER: the picture for a voiceover video, drawn frame by frame (PIL) into x264
# What : shots anchored to spoken phrases (vo_shots.py in the project): the post (post/tall.png) with the line
#        being read highlighted and the page scrolling with him (readlines.json), photos as rounded cards over a blurred copy
#        of themselves, a map. Every shot moves: cards zoom in or out (alternating) and pan,
#        the backdrop drifts, a soft band of light crosses each card and each highlighted line,
#        kickers slide up. Grade: vignette and fine grain. A soft white flash (5 frames) at
#        each shot change, never on frame 0. Captions 1 to 3 words, spoken word yellow.
# Why  : no face video to cut around, so the pictures carry the eye. Remotion is not needed.
# In   : caps.json, readlines.json, post/tall.png, vo_timeline.json, vo_config.json (source line), vo_shots.py, pjs800/600.ttf
# Out  : video_silent.mp4, shots.json (for the sound cues)
# Use  : python3 vo_03_render.py           whole video
#        python3 vo_03_render.py 0 300 900  stills of frames 300 and 900 (look before rendering)
# Never: never put the editing on screen. A post shot marked top=True opens at the top and highlights nothing.
# ============================================================
# Voiceover video 1: frame renderer (PIL) -> silent video + cue list
import json,re,subprocess,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageOps,ImageEnhance
W_,H_,FPS=1080,1920,30
NAVY=(11,27,58);YEL=(255,204,0);BLUE=(30,136,255);WHITE=(255,255,255)
C=json.load(open('caps.json')); SOURCE=json.load(open('vo_config.json'))['source']; TOTAL=json.load(open('vo_timeline.json'))['total']; END=3.2; DUR=TOTAL+END
F8=lambda s:ImageFont.truetype('pjs800.ttf',s); F6=lambda s:ImageFont.truetype('pjs600.ttf',s)
DJ=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',s)
n=lambda t:re.sub(r'[^a-z0-9]','',t.lower())
def at(phrase,after=0.0):
    p=[n(x) for x in phrase.split()]; ws=[n(c['w']) for c in C]
    for i in range(len(ws)):
        if C[i]['s']>=after and ws[i:i+len(p)]==p: return C[i]['s']-0.12
    raise SystemExit('not found: '+phrase)
# ---- 1. shots ----
SH=[]; t=0.0
def add(ph,kind,src,**k):
    global t
    s=0.0 if ph is None else at(ph,t); t=s; SH.append(dict(s=s,kind=kind,src=src,**k))
exec(open('vo_shots.py').read())
SH.append(dict(s=TOTAL+0.05,kind='end',src=None))
for i,s in enumerate(SH): s['e']=SH[i+1]['s'] if i+1<len(SH) else DUR
json.dump([{k:v for k,v in s.items()} for s in SH],open('shots.json','w'),indent=0)
for s in SH: print(f"{s['s']:7.2f} {s['kind']:5} {s['src']} {s.get('kick','')}")
# ---- 2. prepared layers ----
def enhance(im):
    im=ImageOps.autocontrast(im.convert('RGB'),cutoff=0.5)
    im=ImageEnhance.Color(im).enhance(1.08)
    if im.width<1000: im=im.resize((1000,round(im.height*1000/im.width)),Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(2,80,2))
def rounded(im,r=36):
    m=Image.new('L',im.size,0); ImageDraw.Draw(m).rounded_rectangle([0,0,*im.size],r,fill=255); return m
cache={}
def layer(s):
    key=s['src']+s['kind']
    if key in cache: return cache[key]
    if s['kind'] in('photo','map'):
        im=enhance(Image.open(s['src'])) if s['kind']=='photo' else Image.open(s['src']).convert('RGB')
        bg=ImageOps.fit(im,(W_,H_)).filter(ImageFilter.GaussianBlur(40)); bg=ImageEnhance.Brightness(bg).enhance(0.45)
        cw=980; ch=min(1180,round(im.height*cw/im.width)); card=ImageOps.fit(im,(cw,ch),centering=(0.5,0.45))
        cache[key]=(bg,card)
    else:
        im=Image.open(s['src']).convert('RGB').crop((0,100,1080,2400)); cache[key]=im
    return cache[key]
vig=np.ones((H_,W_),np.float32); yy,xx=np.mgrid[0:H_,0:W_]; r=np.sqrt(((xx-W_/2)/(W_*0.75))**2+((yy-H_/2)/(H_*0.75))**2)
vig=np.clip(1-0.35*r**2,0.55,1)[...,None]
rng=np.random.default_rng(1); GR=[rng.normal(0,5,(H_,W_,1)).astype(np.float32) for _ in range(4)]
def text_w(d,txt,font,alt):
    return sum(d.textlength(ch,font=alt if ord(ch)>0x2000 and ch=='₦' else font) for ch in txt)
def draw_text(d,xy,txt,font,alt,fill,stroke=0,sf=(0,0,0)):
    x,y=xy
    for ch in txt:
        f=alt if ch=='₦' else font
        d.text((x,y),ch,font=f,fill=fill,stroke_width=stroke,stroke_fill=sf); x+=d.textlength(ch,font=f)
def pill(d,cy,txt,size=58,bg=YEL,fg=NAVY):
    f,a=F8(size),DJ(size); w=text_w(d,txt,f,a); x=(W_-w)/2
    d.rounded_rectangle([x-34,cy-size*0.75,x+w+34,cy+size*0.75],28,fill=bg); draw_text(d,(x,cy-size*0.62),txt,f,a,fg)
# captions: groups of up to 3 words, break at punctuation
groups=[];g=[]
for i,c in enumerate(C):
    g.append(i)
    if len(g)==3 or c['w'][-1] in '.,?!:' or (i+1<len(C) and C[i+1]['s']-c['e']>0.35): groups.append(g);g=[]
if g: groups.append(g)
def caption(d,tt):
    for g in groups:
        s,e=C[g[0]]['s'],C[g[-1]]['e']
        if s<=tt<e+0.15 or (s<=tt and groups.index(g)+1<len(groups) and tt<C[groups[groups.index(g)+1][0]]['s'] and tt-e<0.4):
            f,a=F8(84),DJ(84); words=[C[i]['w'] for i in g]; sp=d.textlength(' ',font=f)
            tw=sum(text_w(d,w,f,a) for w in words)+sp*(len(words)-1); x=(W_-tw)/2; y=1530
            for i,w in zip(g,words):
                col=YEL if C[i]['s']<=tt<C[i]['e']+0.05 or (C[i]['s']<=tt and i==g[-1]) else WHITE
                draw_text(d,(x,y),w,f,a,col,stroke=7); x+=text_w(d,w,f,a)+sp
            return
SW=Image.new('L',(400,2600),0)
for i in range(400): ImageDraw.Draw(SW).line([(i,0),(i,2600)],fill=int(120*np.sin(np.pi*i/400)**2))
SW=SW.rotate(-20,expand=True)
def sweep(im,x0,y0,w,h,p):
    # a soft band of light crosses the picture from left to right
    band=Image.new('L',im.size,0); band.paste(SW,(int(x0-500+(w+700)*p),y0-600))
    m=Image.new('L',im.size,0); m.paste(255,(x0,y0,x0+w,y0+h)); from PIL import ImageChops
    im.paste((255,250,235),(0,0),ImageChops.multiply(band,m))
_t=Image.open('post/tall.png').convert('RGB'); TALL=Image.new('RGB',(_t.width,_t.height+700),(0,0,0)); TALL.paste(_t,(0,0)); PTOP=170; VIEW=H_-PTOP
RL=json.load(open('readlines.json'))
NF_=round(DUR*FPS); READ=[None]*NF_; SCROLL=[0.0]*NF_
cur=None; ci=0; tgt=0.0; pos=0.0; prev_shot=None
for fi in range(NF_):
    tt=fi/FPS
    while ci<len(C) and C[ci]['s']<=tt:
        if RL[ci]: cur=(ci,RL[ci])
        ci+=1
    sh=next((x for x in SH if x['s']<=tt<x['e']),None)
    reading=cur is not None and tt<=C[cur[0]]['e']+1.2 and not (sh and sh.get('top'))
    if reading: tgt=max(0,(cur[1][0]+cur[1][1])/2-0.33*VIEW)
    if sh and sh.get('top'): tgt=0.0
    if sh is not prev_shot:
        if not reading: tgt=0.0
        pos=tgt; prev_shot=sh
    pos+= (tgt-pos)*0.10
    SCROLL[fi]=pos; READ[fi]=cur[1] if reading else None
def ease(u): return u*u*(3-2*u)
def frame(fi):
    tt=fi/FPS; s=next(x for x in SH if x['s']<=tt<x['e']) if tt<SH[-1]['e'] else SH[-1]
    u=(tt-s['s'])/max(0.1,s['e']-s['s'])
    if s['kind']=='end':
        im=Image.new('RGB',(W_,H_),NAVY); d=ImageDraw.Draw(im)
        pill(d,760,'WHAT DO YOU THINK?',76,YEL,NAVY)
        f=F6(56); t1='Tell me in the comments.'; d.text(((W_-d.textlength(t1,font=f))/2,860),t1,font=f,fill=WHITE)
        pill(d,1060,'FOLLOW FOR MORE',64,BLUE,WHITE)
    elif s['kind']=='post':
        top=SCROLL[fi]; im=Image.new('RGB',(W_,H_),(0,0,0))
        im.paste(TALL.crop((0,round(top),W_,round(top)+H_-PTOP)),(0,PTOP))
        li=READ[fi]
        if li is not None:
            y0,y1=li[0]-top+PTOP,li[1]-top+PTOP; ov=Image.new('RGBA',(W_,H_))
            ImageDraw.Draw(ov).rounded_rectangle([10,y0-10,W_-10,y1+10],14,fill=(255,204,0,60),outline=(255,204,0,230),width=4)
            im=Image.alpha_composite(im.convert('RGBA'),ov).convert('RGB')
        band=Image.new('RGBA',(W_,H_));ImageDraw.Draw(band).rectangle([0,1470,W_,1700],fill=(0,0,0,190));im=Image.alpha_composite(im.convert('RGBA'),band).convert('RGB');d=ImageDraw.Draw(im)
        d.rounded_rectangle([40,62,40+d.textlength(SOURCE,font=F6(30))+52,132],34,fill=(25,25,25)); d.text((66,76),SOURCE,font=F6(30),fill=(225,225,225))
        if s.get('hook'): pill(d,1300,s['hook'],62)
    else:
        bg,card=layer(s); k=SH.index(s); zin=k%2==0; z=1.0+0.09*(ease(u) if zin else 1-ease(u))
        bz=1.0+0.05*u; bg2=bg.resize((round(W_*bz),round(H_*bz))); im=bg2.crop(((bg2.width-W_)//2,(bg2.height-H_)//2,(bg2.width-W_)//2+W_,(bg2.height-H_)//2+H_))
        px=int(30*(u-0.5)*(1 if k%3 else -1))
        cw,ch=card.size; c2=card.resize((round(cw*z),round(ch*z)),Image.LANCZOS)
        ox=max(0,min(c2.width-cw,(c2.width-cw)//2+px)); c2=c2.crop((ox,(c2.height-ch)//2,ox+cw,(c2.height-ch)//2+ch))
        y=max(330,(1450-ch)//2+60); sh=Image.new('L',im.size,0); ImageDraw.Draw(sh).rounded_rectangle([50,y+20,50+cw,y+ch+20],40,fill=150)
        im.paste((0,0,0),(0,0),sh.filter(ImageFilter.GaussianBlur(24))); im.paste(c2,((W_-cw)//2,y),rounded(c2))
        dt=tt-s['s']
        if 0.15<dt<1.45: sweep(im,(W_-cw)//2,y,cw,ch,(dt-0.15)/1.3)
        d=ImageDraw.Draw(im)
        if s.get('kick') and tt-s['s']>0.12: pill(d,y-90+int(max(0,30*(1-(tt-s['s']-0.12)/0.25))),s['kick'])
    if s['kind']!='end': caption(ImageDraw.Draw(im),tt)
    a=np.asarray(im).astype(np.float32)*vig+GR[fi%4]
    # flash at each shot change after the first: 4 frames
    for x in SH[1:]:
        k=fi-round(x['s']*FPS)
        if 0<=k<5: a=a+(255-a)*(0.55*(1-k/5))
    return np.clip(a,0,255).astype(np.uint8).tobytes()
if __name__=='__main__':
    import sys
    NF=round(DUR*FPS); lim=int(sys.argv[1]) if len(sys.argv)>1 else NF
    if len(sys.argv)>2:
        for fi in map(int,sys.argv[2:]): Image.frombytes('RGB',(W_,H_),frame(fi)).save(f'still_{fi}.jpg')
        raise SystemExit
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','video_silent.mp4'],stdin=subprocess.PIPE)
    for fi in range(min(lim,NF)): p.stdin.write(frame(fi))
    p.stdin.close(); p.wait()
