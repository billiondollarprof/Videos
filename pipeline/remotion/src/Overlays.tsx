// ============================================================
// OVERLAYS
// What : 1. Hook title in the first 3.5 s.
//        2. Step label at the top left (Step 1 to 4).
//        3. Tip cards that pop over the screen.
//        4. "Speeding up" badge while the screen is fast-forwarded.
//        5. Progress bar at the very top.
//        6. End card.
// Why  : the hook stops people scrolling. The steps tell them where they are.
// Never: never claim anything you did not say in the video.
// The words come from project.json "text" (via data.json), so this file fits any video.
// ============================================================
import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame} from 'remotion';
import data from './data.json';
import {BUBBLE, C, FPS, fontFamily, SCREEN, W} from './theme';

const sec = (s: number) => Math.round(s * FPS);
const TALK_END = sec(data.moments.end);

// --- 1. Hook title ---
export const Hook: React.FC = () => {
  const f = useCurrentFrame();
  if (f > sec(3.8)) return null;
  const inn = spring({frame: f - 3, fps: FPS, config: {damping: 14}});
  const out = interpolate(f, [sec(3.3), sec(3.8)], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 60, right: 60, top: 170, opacity: out,
      transform: `translateY(${(1 - inn) * -60}px)`}}>
      <div style={{background: `${C.navyDeep}D9`, border: `3px solid ${C.blue}`, borderRadius: 36, padding: '34px 40px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.45)'}}>
        <div style={{fontFamily, fontWeight: 800, fontSize: 92, lineHeight: 1.02, color: C.white}}>{data.text.hook_line_1}</div>
        <div style={{fontFamily, fontWeight: 800, fontSize: 92, lineHeight: 1.02, color: C.yellow}}>{data.text.hook_line_2}</div>
        <div style={{marginTop: 22, display: 'inline-block', fontFamily, fontWeight: 700, fontSize: 38, color: C.white,
          background: C.blue, borderRadius: 999, padding: '10px 26px'}}>{data.text.hook_pill}</div>
      </div>
    </div>
  );
};

// --- 2. Step label ---
export const Steps: React.FC = () => {
  const f = useCurrentFrame();
  if (f >= TALK_END) return null;
  const steps = data.moments.steps;
  const cur = [...steps].reverse().find((s) => f >= sec(s.t));
  if (!cur) return null;
  const inn = spring({frame: f - sec(cur.t) - 6, fps: FPS, config: {damping: 15}});
  return (
    <div style={{position: 'absolute', left: 48, top: 62, width: BUBBLE.x - 48 - 30, opacity: inn,
      transform: `translateX(${(1 - inn) * -80}px)`}}>
      <div style={{display: 'inline-block', fontFamily, fontWeight: 800, fontSize: 30, letterSpacing: 2,
        color: C.navyDeep, background: C.yellow, borderRadius: 999, padding: '8px 22px'}}>STEP {cur.n} OF 4</div>
      <div style={{fontFamily, fontWeight: 800, fontSize: 46, lineHeight: 1.1, color: C.white, marginTop: 12}}>{cur.label}</div>
    </div>
  );
};

// --- 3. Tip cards ---
const Bulb: React.FC = () => (
  <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke={C.navyDeep} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z" />
  </svg>
);
export const Tips: React.FC = () => {
  const f = useCurrentFrame();
  const tip = data.moments.tips.find((t) => f >= sec(t.t) && f < sec(t.t + t.d));
  if (!tip) return null;
  const inn = spring({frame: f - sec(tip.t), fps: FPS, config: {damping: 12, mass: 0.7}});
  const out = interpolate(f, [sec(tip.t + tip.d) - 8, sec(tip.t + tip.d)], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 70, width: W - 140, top: 860, opacity: out,
      transform: `scale(${0.6 + 0.4 * inn})`}}>
      <div style={{display: 'flex', gap: 26, alignItems: 'center', background: C.navyDeep, border: `4px solid ${C.yellow}`,
        borderRadius: 34, padding: '30px 34px', boxShadow: `0 24px 70px rgba(0,0,0,0.6), 0 0 80px ${C.yellow}33`}}>
        <div style={{flex: 'none', width: 96, height: 96, borderRadius: 26, background: C.yellow,
          display: 'flex', alignItems: 'center', justifyContent: 'center'}}><Bulb /></div>
        <div>
          <div style={{fontFamily, fontWeight: 800, fontSize: 30, letterSpacing: 2, color: C.yellow}}>{tip.title.toUpperCase()}</div>
          <div style={{fontFamily, fontWeight: 800, fontSize: 48, lineHeight: 1.15, color: C.white, marginTop: 6}}>{tip.text}</div>
        </div>
      </div>
    </div>
  );
};

// --- 4. Speeding-up badge ---
const FAST = data.pieces.filter((p) => p.type === 'fast').map((p) => [sec(p.out), sec(p.out + p.len)]);
export const FastBadge: React.FC = () => {
  const f = useCurrentFrame();
  if (!FAST.some(([a, b]) => f >= a && f < b)) return null;
  return (
    <div style={{position: 'absolute', left: 0, width: W, top: SCREEN.y + 120, display: 'flex', justifyContent: 'center'}}>
      <div style={{fontFamily, fontWeight: 800, fontSize: 34, color: C.navyDeep, background: C.yellow, borderRadius: 999,
        padding: '10px 26px', boxShadow: '0 10px 30px rgba(0,0,0,0.4)'}}>▶▶ Speeding up</div>
    </div>
  );
};

// --- 5. Progress bar ---
export const Progress: React.FC<{total: number}> = ({total}) => {
  const f = useCurrentFrame();
  return (
    <div style={{position: 'absolute', left: 0, top: 0, height: 10, width: (f / total) * W, background: C.yellow,
      boxShadow: `0 0 18px ${C.yellow}`}} />
  );
};

// --- 6. End card ---
export const EndCard: React.FC = () => {
  const f = useCurrentFrame() - TALK_END;
  if (f < 0) return null;
  const inn = spring({frame: f, fps: FPS, config: {damping: 16}});
  return (
    <AbsoluteFill style={{opacity: Math.min(1, f / 8), background: `linear-gradient(180deg, ${C.navyDeep}, ${C.navy})`,
      alignItems: 'center', justifyContent: 'center', textAlign: 'center'}}>
      <div style={{transform: `translateY(${(1 - inn) * 60}px)`, padding: '0 70px'}}>
        <div style={{fontFamily, fontWeight: 800, fontSize: 96, lineHeight: 1.05, color: C.white}}>{data.text.end_line_1}</div>
        <div style={{fontFamily, fontWeight: 800, fontSize: 96, lineHeight: 1.05, color: C.yellow}}>{data.text.end_line_2}</div>
        <div style={{marginTop: 60, fontFamily, fontWeight: 700, fontSize: 46, color: C.white}}>{data.text.end_name}</div>
        <div style={{marginTop: 10, fontFamily, fontWeight: 600, fontSize: 36, color: C.textDim}}>{data.text.end_sub}</div>
      </div>
    </AbsoluteFill>
  );
};
