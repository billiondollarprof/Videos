// ============================================================
// FACE AND SCREEN
// What : 1. Before the screen share: your face fills the frame, with a small zoom
//           change at each real cut (this hides the jump in the picture).
//        2. At the screen share: your face shrinks into a circle at the top right,
//           and the phone screen rises into a rounded card in the middle.
// Why  : the two cut videos are already in step (see build_tracks.py), so this
//        file only places them. It never shifts their timing.
// ============================================================
import React from 'react';
import {AbsoluteFill, interpolate, OffthreadVideo, Sequence, spring, staticFile, useCurrentFrame} from 'remotion';
import data from './data.json';
import {BUBBLE, C, FPS, H, SCREEN, W} from './theme';

const SCREEN_START = Math.round(data.moments.screenStart * FPS);

// --- 1. Zoom level for each moment before the screen share ---
// A "real cut" is one where more than 0.8 s of the recording was removed.
const zoomSteps: number[] = []; // output frame where the zoom flips
{
  const p = data.pieces;
  for (let i = 1; i < p.length; i++) {
    const prevEnd = p[i - 1].src + p[i - 1].len * (p[i - 1].type === 'fast' ? 4 : 1);
    if (p[i].src - prevEnd > 0.8) zoomSteps.push(Math.round(p[i].out * FPS));
  }
}
const zoomAt = (f: number) => (zoomSteps.filter((z) => z <= f).length % 2 === 0 ? 1.0 : 1.09);

// --- 2. The layout ---
export const People: React.FC = () => {
  const f = useCurrentFrame();
  // 0 = face fills the frame, 1 = face is the small circle
  const t = spring({frame: f - SCREEN_START, fps: FPS, config: {damping: 18, mass: 0.9}});

  const left = interpolate(t, [0, 1], [0, BUBBLE.x]);
  const top = interpolate(t, [0, 1], [0, BUBBLE.y]);
  const width = interpolate(t, [0, 1], [W, BUBBLE.size]);
  const height = interpolate(t, [0, 1], [H, BUBBLE.size]);
  const radius = interpolate(t, [0, 1], [0, BUBBLE.size / 2]);
  const ring = interpolate(t, [0, 1], [0, 6]);
  const zoom = f < SCREEN_START ? zoomAt(f) : 1;

  const cardIn = spring({frame: f - SCREEN_START - 4, fps: FPS, config: {damping: 16}});

  return (
    <AbsoluteFill>
      {/* the phone screen */}
      <Sequence from={SCREEN_START} layout="none">
        <div style={{position: 'absolute', left: SCREEN.x, top: SCREEN.y, width: SCREEN.w, height: SCREEN.h,
          borderRadius: SCREEN.radius, overflow: 'hidden', border: `3px solid ${C.blueSoft}`,
          boxShadow: `0 0 0 10px ${C.blue}22, 0 30px 90px rgba(0,0,0,0.55), 0 0 120px ${C.blue}44`,
          opacity: cardIn, transform: `translateY(${(1 - cardIn) * 120}px) scale(${0.9 + 0.1 * cardIn})`}}>
          <OffthreadVideo src={staticFile('screen_cut.mp4')} startFrom={SCREEN_START} muted
            style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        </div>
      </Sequence>

      {/* your face: full frame, then the circle */}
      <div style={{position: 'absolute', left, top, width, height, borderRadius: radius, overflow: 'hidden',
        boxShadow: t > 0.01 ? `0 0 0 ${ring}px ${C.yellow}, 0 18px 50px rgba(0,0,0,0.5)` : 'none'}}>
        <OffthreadVideo src={staticFile('face_cut.mp4')} muted
          // In the circle, the frame is cropped to a square. Your face sits in the lower
          // middle of the recording, so the square is taken from 70% of the way down.
          style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: '50% 70%',
            transform: `scale(${zoom * interpolate(t, [0, 1], [1, 1.15])})`,
            transformOrigin: '50% 50%'}} />
      </div>
    </AbsoluteFill>
  );
};
