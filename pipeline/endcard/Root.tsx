// ============================================================
// CONTINUE-ON-YOUTUBE END CARD (for the short version)
// What : a 6 second end card for a short that stops at a hook: a big red YouTube-style play
//        button that gets pressed, "Watch the full video on YouTube", a search bar that types his
//        name, and his channel header (photo, name, handle) as the result.
// Why  : the short (Instagram Reels, Shorts, TikTok) ends at a hook and sends people to the
//        full video. No video inside, so it renders in about a minute, not 35.
// Never: never show subscriber counts or any number about the channel, and never say "link in
//        bio" (his notes, 2026-11-05). The tagline is the one on his own channel page.
// ============================================================
import React from 'react';
import {AbsoluteFill, Composition, Img, interpolate, registerRoot, spring, staticFile, useCurrentFrame} from 'remotion';
import {Background} from './Background';
import {C, FPS, fontFamily} from './theme';

const W = 1088;
const H = 1920;
const CARD = {w: 700, h: 1010, x: (W - 700) / 2, y: 520};

// --- 1. The YouTube-style play button: pops in, then gets pressed (with a click sound) ---
const RED = '#FF0000';
const Play: React.FC<{press: number; pop: number}> = ({press, pop}) => (
  <div style={{position: 'relative', width: 380, height: 266, transform: `scale(${(0.4 + 0.6 * pop) * (1 - 0.07 * press)})`, opacity: pop}}>
    {/* a ring that spreads out from the button when it is pressed */}
    <div style={{position: 'absolute', inset: -10, borderRadius: 86, border: `6px solid ${RED}`,
      opacity: press > 0 ? 0.7 * (1 - press) : 0, transform: `scale(${1 + 0.5 * press})`}} />
    <div style={{width: 380, height: 266, borderRadius: 78, background: RED, display: 'flex', alignItems: 'center',
      justifyContent: 'center', boxShadow: `0 24px 70px rgba(255,0,0,0.45), 0 10px 30px rgba(0,0,0,0.6)`}}>
      <div style={{width: 0, height: 0, borderTop: '64px solid transparent', borderBottom: '64px solid transparent',
        borderLeft: '108px solid #fff', marginLeft: 26}} />
    </div>
  </div>
);

const NAME = 'Anthony Nwobosi';

// --- 2. The card: play button, headline, a search bar that types his name, his channel header ---
const Card: React.FC = () => {
  const f = useCurrentFrame();
  const sp = (n: number, damping = 14) => spring({frame: f - n, fps: FPS, config: {damping, mass: 0.8}});
  const pop = sp(2, 11);
  const press = interpolate(f, [20, 26, 38], [0, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const head = sp(10), bar = sp(44, 16), result = sp(112, 13);
  const typed = Math.max(0, Math.min(NAME.length, Math.floor(interpolate(f, [58, 100], [0, NAME.length + 1]))));
  const caret = Math.floor(f / 8) % 2 === 0 || typed < NAME.length;
  const glow = 0.55 + 0.15 * Math.sin(f / 9);
  return (
    <AbsoluteFill style={{background: '#0A0A0A', fontFamily}}>
      <div style={{position: 'absolute', left: -200, top: -150, width: 1500, height: 1000, borderRadius: '50%',
        background: `radial-gradient(circle, rgba(255,0,0,${glow * 0.55}) 0%, transparent 62%)`}} />
      <div style={{position: 'absolute', left: 0, width: W, top: 290, display: 'flex', justifyContent: 'center'}}><Play press={press} pop={pop} /></div>
      <div style={{position: 'absolute', left: 0, width: W, top: 660, textAlign: 'center', opacity: head,
        transform: `translateY(${(1 - head) * 40}px)`}}>
        <div style={{fontWeight: 800, fontSize: 98, lineHeight: 1.05, color: '#fff'}}>Watch the full video</div>
        <div style={{fontWeight: 800, fontSize: 98, lineHeight: 1.05, color: RED}}>on YouTube</div>
      </div>
      {/* a search bar that types his name */}
      <div style={{position: 'absolute', left: 90, width: W - 180, top: 1040, height: 128, borderRadius: 64, background: '#121212',
        border: '3px solid #3F3F3F', display: 'flex', alignItems: 'center', opacity: bar, transform: `translateY(${(1 - bar) * 60}px)`}}>
        <div style={{flex: 1, paddingLeft: 52, fontWeight: 600, fontSize: 56, color: '#fff'}}>
          {NAME.slice(0, typed)}<span style={{opacity: caret ? 1 : 0, color: '#aaa'}}>|</span>
        </div>
        <div style={{width: 150, height: '100%', borderLeft: '3px solid #3F3F3F', background: '#222', borderRadius: '0 64px 64px 0',
          display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
          <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.2" strokeLinecap="round">
            <circle cx="10.5" cy="10.5" r="6.5" /><path d="M16 16l5 5" />
          </svg>
        </div>
      </div>
      {/* his channel header, as the search result: photo, name, handle. No numbers. */}
      <div style={{position: 'absolute', left: 90, width: W - 180, top: 1250, height: 330, borderRadius: 48, background: '#181818',
        border: `3px solid ${RED}`, display: 'flex', alignItems: 'center', gap: 36, padding: '0 44px', opacity: result,
        transform: `translateY(${(1 - result) * 120}px) scale(${0.94 + 0.06 * result})`,
        boxShadow: '0 0 0 10px rgba(255,0,0,0.16), 0 30px 80px rgba(0,0,0,0.6)'}}>
        <Img src={staticFile('avatar.jpg')} style={{width: 190, height: 190, borderRadius: '50%', objectFit: 'cover', border: '6px solid #fff', flex: 'none'}} />
        <div>
          <div style={{fontWeight: 800, fontSize: 60, lineHeight: 1.05, color: '#fff', whiteSpace: 'nowrap'}}>{NAME}</div>
          <div style={{fontWeight: 700, fontSize: 42, color: '#AAAAAA', marginTop: 8}}>@anthony_nwobosi</div>
          <div style={{fontWeight: 600, fontSize: 34, color: '#E8E8E8', marginTop: 14, lineHeight: 1.2}}>Welcome to a smarter way to use AI!</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ============================================================
// YOUTUBE THUMBNAIL (1280 x 720)
// Anthony's real photo, cut out (background removed only, never redrawn), on a brand blue
// background. Bold words on the left in his channel's style, a notification badge with the
// real number from the video (Claude said about 9,700), and a "DO THIS INSTEAD" pill. The hook
// copies the shape of his own thumbnails ("STOP X! USE THIS INSTEAD"): it makes people curious
// about what "this" is, and the video title says it is Claude.
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
    <div style={{position: 'absolute', left: 58, top: 566, background: C.yellow, color: C.navyDeep, fontWeight: 800, fontSize: 48,
      borderRadius: 999, padding: '12px 40px 12px 40px', boxShadow: '0 12px 30px rgba(0,0,0,0.45)', display: 'flex', alignItems: 'center', gap: 16}}>
      DO THIS INSTEAD
      <svg width="52" height="40" viewBox="0 0 52 40" fill="none"><path d="M4 20 H42 M28 6 L44 20 L28 34" stroke={C.navyDeep} strokeWidth="7" strokeLinecap="round" strokeLinejoin="round" /></svg>
    </div>
  </AbsoluteFill>
);

registerRoot(() => (
  <>
    <Composition id="Continue" component={Card} durationInFrames={180} fps={FPS} width={W} height={H} />
    <Composition id="Thumb" component={Thumb} durationInFrames={1} fps={FPS} width={1280} height={720} />
  </>
));
