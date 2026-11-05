// ============================================================
// CONTINUE-ON-YOUTUBE END CARD (for the short version)
// What : a 5 second end card for a short that stops at a hook: "Watch the full video on
//        YouTube", his YouTube page in a framed card that slowly scrolls to show his videos,
//        his name and handle.
// Why  : the short (Instagram Reels, Shorts, TikTok) ends at a hook and sends people to the
//        full video. No video inside, so it renders in about a minute, not 35.
// Never: never claim anything about the channel that the screenshot does not show.
// ============================================================
import React from 'react';
import {AbsoluteFill, Composition, Img, interpolate, registerRoot, spring, staticFile, useCurrentFrame} from 'remotion';
import {Background} from './Background';
import {C, FPS, fontFamily} from './theme';

const W = 1088;
const H = 1920;
const CARD = {w: 700, h: 1010, x: (W - 700) / 2, y: 520};

const Play: React.FC = () => (
  // a plain red play badge: "video", without copying any logo
  <div style={{width: 120, height: 84, borderRadius: 24, background: '#E62117', display: 'flex',
    alignItems: 'center', justifyContent: 'center', boxShadow: '0 12px 34px rgba(0,0,0,0.45)'}}>
    <div style={{width: 0, height: 0, borderTop: '20px solid transparent', borderBottom: '20px solid transparent',
      borderLeft: '34px solid #fff', marginLeft: 8}} />
  </div>
);

const Card: React.FC = () => {
  const f = useCurrentFrame();
  const t = (n: number, damping = 14) => spring({frame: f - n, fps: FPS, config: {damping, mass: 0.8}});
  const head = t(2), card = t(12, 16), name = t(34), badge = t(6, 11);
  // the page scrolls slowly up by about 150 px, so his videos come into view
  const scroll = interpolate(f, [30, 140], [0, 150], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const imgW = CARD.w, imgH = CARD.w * (2078 / 1080);
  return (
    <AbsoluteFill>
      <Background />
      <div style={{position: 'absolute', left: 0, width: W, top: 150, textAlign: 'center', fontFamily,
        opacity: head, transform: `translateY(${(1 - head) * -50}px)`}}>
        <div style={{display: 'flex', justifyContent: 'center', transform: `scale(${0.5 + 0.5 * badge})`, opacity: badge}}><Play /></div>
        <div style={{fontWeight: 800, fontSize: 92, lineHeight: 1.05, color: C.white, marginTop: 34}}>Watch the full video</div>
        <div style={{fontWeight: 800, fontSize: 92, lineHeight: 1.05, color: C.yellow}}>on YouTube</div>
      </div>
      <div style={{position: 'absolute', left: CARD.x, top: CARD.y, width: CARD.w, height: CARD.h, borderRadius: 46,
        overflow: 'hidden', border: `3px solid ${C.blueSoft}`, background: '#0f0f0f',
        boxShadow: `0 0 0 10px ${C.blue}22, 0 30px 90px rgba(0,0,0,0.55), 0 0 120px ${C.blue}44`,
        opacity: card, transform: `translateY(${(1 - card) * 140}px) scale(${0.92 + 0.08 * card})`}}>
        <Img src={staticFile('youtube_page.jpg')} style={{position: 'absolute', left: 0, top: -scroll - 40, width: imgW, height: imgH}} />
      </div>
      <div style={{position: 'absolute', left: 0, width: W, top: CARD.y + CARD.h + 56, textAlign: 'center', fontFamily,
        opacity: name, transform: `translateY(${(1 - name) * 40}px)`}}>
        <div style={{fontWeight: 800, fontSize: 60, color: C.white}}>Anthony Nwobosi</div>
        <div style={{fontWeight: 700, fontSize: 40, color: C.blueSoft, marginTop: 6}}>@anthony_nwobosi</div>
      </div>
    </AbsoluteFill>
  );
};

// ============================================================
// YOUTUBE THUMBNAIL (1280 x 720)
// Anthony's real photo, cut out (background removed only, never redrawn), on a brand blue
// background. Bold words on the left in his channel's style, a notification badge with the
// real number from the video (Claude said about 9,700), and a "free" pill.
// Never: never change his face or body. Only crop, scale and place the cut-out.
// ============================================================
const Thumb: React.FC = () => (
  <AbsoluteFill style={{background: `radial-gradient(circle at 78% 42%, ${C.blue} 0%, #1243B8 32%, ${C.navy} 62%, ${C.navyDeep} 100%)`, fontFamily}}>
    <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(115deg, transparent 52%, rgba(255,255,255,0.07) 52.4%, transparent 66%)'}} />
    <Img src={staticFile('anthony_cutout.png')}
      style={{position: 'absolute', left: 584, top: -171, width: 756, height: 1243,
        filter: `drop-shadow(0 0 5px ${C.yellow}) drop-shadow(0 26px 40px rgba(0,0,0,0.55))`}} />
    <div style={{position: 'absolute', left: 58, top: 52, width: 620}}>
      <div style={{fontWeight: 800, fontSize: 150, lineHeight: 0.98, color: C.white, WebkitTextStroke: `10px ${C.navyDeep}`, paintOrder: 'stroke fill'}}>STOP</div>
      <div style={{fontWeight: 800, fontSize: 112, lineHeight: 1.0, color: C.white, WebkitTextStroke: `9px ${C.navyDeep}`, paintOrder: 'stroke fill'}}>DELETING</div>
      <div style={{fontWeight: 800, fontSize: 158, lineHeight: 1.0, color: C.yellow, WebkitTextStroke: `10px ${C.navyDeep}`, paintOrder: 'stroke fill'}}>EMAILS!</div>
    </div>
    <svg style={{position: 'absolute', left: 470, top: 54}} width="160" height="120" viewBox="0 0 160 120" fill="none">
      <rect x="6" y="14" width="140" height="96" rx="14" fill={C.white} stroke={C.navyDeep} strokeWidth="6" />
      <path d="M12 26 L76 72 L140 26" stroke={C.navyDeep} strokeWidth="7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
    <div style={{position: 'absolute', left: 560, top: 20, background: '#E62117', color: C.white, fontWeight: 800, fontSize: 40,
      borderRadius: 999, padding: '4px 20px', border: `5px solid ${C.white}`, transform: 'rotate(-6deg)', boxShadow: '0 8px 20px rgba(0,0,0,0.45)'}}>9,700</div>
    <div style={{position: 'absolute', left: 58, top: 566, background: C.yellow, color: C.navyDeep, fontWeight: 800, fontSize: 46,
      borderRadius: 999, padding: '12px 36px', boxShadow: '0 12px 30px rgba(0,0,0,0.45)'}}>CLAUDE DOES IT FREE</div>
  </AbsoluteFill>
);

registerRoot(() => (
  <>
    <Composition id="Continue" component={Card} durationInFrames={150} fps={FPS} width={W} height={H} />
    <Composition id="Thumb" component={Thumb} durationInFrames={1} fps={FPS} width={1280} height={720} />
  </>
));
