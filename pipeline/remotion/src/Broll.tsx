// ============================================================
// B-ROLL ANIMATIONS
// What : 1. DeleteMock: an inbox where emails are deleted one at a time, slowly.
//           Plays over "you don't have the time to ... delete emails one after the other".
//        2. ConnectCard: "Claude" and "Gmail" chips joining, then "Inbox clean".
//           Plays over "I'll show you how to connect Claude to your Gmail".
//        3. Notification: a phone notification sliding down.
//           Plays over "it will notify you once it's done".
// Why  : the opening had 30 s of face only. B-roll shows the problem while he describes it.
// Never: every mock-up says "Example". Never show a number he did not show in the video.
//        (9,700 is the real number Claude gave him on screen.)
// ============================================================
import React from 'react';
import {interpolate, spring, useCurrentFrame} from 'remotion';
import {C, FPS, fontFamily} from './theme';

// --- 1. Inbox with emails deleted one at a time ---
const SENDERS = [
  ['Flash Sale', 'Last chance: 70% off everything'],
  ['Weekly Digest', 'Your weekly newsletter is here'],
  ['Shop Updates', 'New arrivals you might like'],
  ['Deals Daily', 'Today only: free delivery'],
  ['Promo Team', 'You have a reward waiting'],
  ['News Roundup', 'Top stories this week'],
  ['Offers', 'Members get 2 for 1'],
  ['Events', 'Join our free webinar'],
  ['Flash Sale', 'Ends tonight'],
  ['Weekly Digest', 'Five things to read'],
  ['Shop Updates', 'Back in stock'],
  ['Deals Daily', 'Price drop alert'],
  ['Promo Team', 'Spin to win'],
  ['News Roundup', 'Morning briefing'],
];
const ROW_H = 150;
const EVERY = 24; // frames between deletes: slow on purpose, that is the point

export const DeleteMock: React.FC = () => {
  const f = useCurrentFrame();
  const deleted = Math.floor(f / EVERY);              // rows fully gone so far
  const inStep = (f % EVERY) / EVERY;                 // 0 to 1 within the current delete
  const swipe = interpolate(inStep, [0.35, 0.75], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const collapse = interpolate(inStep, [0.75, 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const tap = interpolate(inStep, [0.05, 0.2, 0.35], [0, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const count = 9700 - deleted;
  return (
    <div style={{position: 'absolute', inset: 0, background: '#131417', fontFamily, overflow: 'hidden'}}>
      {/* the count sits left, under the title: the face circle covers the top right corner */}
      <div style={{padding: '60px 44px 24px', display: 'flex', gap: 24, alignItems: 'baseline'}}>
        <div style={{fontSize: 52, fontWeight: 800, color: C.white}}>Promotions</div>
        <div style={{fontSize: 40, fontWeight: 800, color: C.yellow}}>{count.toLocaleString('en-GB')}</div>
      </div>
      <div style={{position: 'relative'}}>
        {SENDERS.slice(deleted, deleted + 9).map(([who, what], k) => {
          const first = k === 0;
          const y = (k - (first ? 0 : collapse)) * ROW_H;
          return (
            <div key={deleted + k} style={{position: 'absolute', left: 0, right: 0, top: y, height: ROW_H,
              padding: '26px 44px', boxSizing: 'border-box', display: 'flex', gap: 28, alignItems: 'center',
              transform: first ? `translateX(${-swipe * 110}%)` : 'none', opacity: first ? 1 - collapse : 1,
              background: first && tap > 0 ? `rgba(43,107,255,${0.35 * tap})` : 'transparent',
              borderBottom: '1px solid #26282e'}}>
              <div style={{width: 84, height: 84, borderRadius: 42, background: '#3a3d46', flex: 'none'}} />
              <div>
                <div style={{fontSize: 38, fontWeight: 700, color: C.white}}>{who}</div>
                <div style={{fontSize: 32, fontWeight: 600, color: '#9aa0ab', marginTop: 6}}>{what}</div>
              </div>
            </div>
          );
        })}
      </div>
      <div style={{position: 'absolute', left: 32, bottom: 36, fontSize: 30, fontWeight: 700, color: C.navyDeep,
        background: C.yellow, borderRadius: 999, padding: '8px 22px'}}>Example</div>
    </div>
  );
};

// --- 2. Claude and Gmail joining ---
const Chip: React.FC<{label: string; colour: string; x: number; show: number}> = ({label, colour, x, show}) => (
  <div style={{position: 'absolute', top: 0, left: x, transform: `translateY(${(1 - show) * 40}px) scale(${0.7 + 0.3 * show})`,
    opacity: show, fontFamily, fontWeight: 800, fontSize: 56, color: C.white, background: C.navyDeep,
    border: `4px solid ${colour}`, borderRadius: 30, padding: '22px 40px', boxShadow: '0 18px 50px rgba(0,0,0,0.5)'}}>
    {label}
  </div>
);

export const ConnectCard: React.FC<{connectAt: number; cleanAt: number}> = ({connectAt, cleanAt}) => {
  const f = useCurrentFrame();
  const a = spring({frame: f, fps: FPS, config: {damping: 14}});
  const line = interpolate(f, [connectAt, connectAt + 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const clean = spring({frame: f - cleanAt, fps: FPS, config: {damping: 12}});
  return (
    <div style={{position: 'absolute', left: 60, right: 60, top: 200, height: 360}}>
      <Chip label="Claude" colour={C.yellow} x={0} show={a} />
      <Chip label="Gmail" colour={C.blueSoft} x={560} show={a} />
      <div style={{position: 'absolute', top: 58, left: 300, height: 8, width: 255 * line, background: C.yellow,
        borderRadius: 4, boxShadow: `0 0 20px ${C.yellow}`}} />
      {f >= cleanAt && (
        <div style={{position: 'absolute', top: 190, left: 0, right: 0, display: 'flex', justifyContent: 'center',
          opacity: clean, transform: `scale(${0.6 + 0.4 * clean})`}}>
          <div style={{fontFamily, fontWeight: 800, fontSize: 52, color: C.navyDeep, background: C.yellow,
            borderRadius: 999, padding: '16px 40px', display: 'flex', alignItems: 'center', gap: 16}}>
            <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke={C.navyDeep} strokeWidth="3.2"
              strokeLinecap="round" strokeLinejoin="round"><path d="M4 12.5l5 5L20 6.5" /></svg>
            Inbox kept clean
          </div>
        </div>
      )}
    </div>
  );
};

// --- 3. Notification sliding down ---
export const Notification: React.FC<{width: number}> = ({width}) => {
  const f = useCurrentFrame();
  const inn = spring({frame: f, fps: FPS, config: {damping: 15}});
  const out = interpolate(f, [80, 95], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 18, width: width - 36, top: 18, opacity: out,
      transform: `translateY(${(inn - 1) * 180}px)`, fontFamily, background: '#24262c', borderRadius: 30,
      padding: '24px 28px', display: 'flex', gap: 22, alignItems: 'center', boxShadow: '0 16px 40px rgba(0,0,0,0.55)'}}>
      <div style={{width: 72, height: 72, borderRadius: 18, background: '#D97757', flex: 'none'}} />
      <div>
        <div style={{fontSize: 30, fontWeight: 800, color: C.white}}>Claude</div>
        <div style={{fontSize: 30, fontWeight: 600, color: '#c9ced8', marginTop: 4}}>Your task is finished</div>
      </div>
    </div>
  );
};
