// ============================================================
// FACE, CARD AND B-ROLL
// What : the video is a list of SEGMENTS (data.moments.segments, worked out from his words
//        in captions.py). Each says where the face is (full frame or the circle) and what
//        the phone card shows (B-roll clip, animation, screen recording, or nothing).
//        At every change the face moves with a spring and the card slides in, swaps or fades.
// Face : in the circle, the face is kept centred using faceTrack.json (where his face is,
//        10 times a second, smoothed). Without it the face drifted right when he moved.
// Never: never shift the timing of a video file here. They are cut in step already.
// ============================================================
import React from 'react';
import {AbsoluteFill, interpolate, OffthreadVideo, Sequence, spring, staticFile, useCurrentFrame} from 'remotion';
import {ConnectCard, DeleteMock, Notification} from './Broll';
import data from './data.json';
import track from './faceTrack.json';
import {BUBBLE, C, FPS, fontFamily, H, SCREEN, W} from './theme';

const fr = (s: number) => Math.round(s * FPS);
const M = data.moments as any;
const SCREEN_START = fr(M.screenStart);

// --- 1. The segments ---
type Seg = {t: number; face: 'full' | 'bubble'; card?: 'broll' | 'mock' | 'screen'};
const SEGS: Seg[] = M.segments;
const segAt = (f: number) => {
  let i = 0;
  SEGS.forEach((s, k) => { if (f >= fr(s.t)) i = k; });
  return i;
};

// --- 2. Small zoom changes at real cuts while the face fills the frame ---
const zoomSteps: number[] = [];
{
  const p = data.pieces;
  for (let i = 1; i < p.length; i++) {
    const prevEnd = p[i - 1].src + p[i - 1].len * (p[i - 1].type === 'fast' ? 4 : 1) * (data as any).speed;
    if (p[i].src - prevEnd > 0.8) zoomSteps.push(fr(p[i].out));
  }
}
const zoomAt = (f: number) => (zoomSteps.filter((z) => z <= f).length % 2 === 0 ? 1.0 : 1.09);

// --- 3. Where his face is (0 to 1 across and down the face video), 10 times a second ---
const faceAt = (f: number): [number, number] => {
  const k = Math.min(track.length - 1, Math.max(0, Math.round((f / FPS) * 10)));
  return track[k] as [number, number];
};
// In the circle the face video is shown this wide, so his face fills about two thirds of it.
const BUBBLE_VIDEO_W = 400;
const BUBBLE_VIDEO_H = BUBBLE_VIDEO_W * (1280 / 720);

// --- 4. What goes inside the card ---
const CardContent: React.FC<{kind: Seg['card']; from: number}> = ({kind, from}) => {
  if (kind === 'broll')
    return (
      <>
        <OffthreadVideo src={staticFile('broll_cut.mp4')} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        {/* the real number Claude gave him later in the video */}
        <Sequence from={fr(M.junkAt) - from} layout="none">
          <PromoLabel />
        </Sequence>
      </>
    );
  if (kind === 'mock') return <DeleteMock />;
  return (
    <>
      <OffthreadVideo src={staticFile('screen_cut.mp4')} startFrom={from} muted
        style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      <Sequence from={fr(M.notifyAt) - from} durationInFrames={100} layout="none">
        <Notification width={SCREEN.w} />
      </Sequence>
    </>
  );
};

const PromoLabel: React.FC = () => {
  const f = useCurrentFrame();
  const inn = spring({frame: f, fps: FPS, config: {damping: 13}});
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: '38%', display: 'flex', justifyContent: 'center',
      opacity: inn, transform: `scale(${0.6 + 0.4 * inn})`}}>
      <div style={{fontFamily, fontWeight: 800, fontSize: 54, lineHeight: 1.1, textAlign: 'center', color: C.white,
        background: `${C.navyDeep}EE`, border: `4px solid ${C.yellow}`, borderRadius: 30, padding: '24px 34px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.6)'}}>
        About <span style={{color: C.yellow}}>9,700</span><br />promotions
      </div>
    </div>
  );
};

// --- 5. The layout ---
export const People: React.FC = () => {
  const f = useCurrentFrame();
  const i = segAt(f);
  const seg = SEGS[i];
  const prev = SEGS[Math.max(0, i - 1)];
  const start = fr(seg.t);
  const t = spring({frame: f - start, fps: FPS, config: {damping: 18, mass: 0.9}});

  // 5a. the face frame: full screen or the circle, moving between them
  const place = (m: Seg['face']) => (m === 'full' ? [0, 0, W, H, 0] : [BUBBLE.x, BUBBLE.y, BUBBLE.size, BUBBLE.size, BUBBLE.size / 2]);
  const a = place(i === 0 ? seg.face : prev.face);
  const b = place(seg.face);
  const [left, top, width, height, radius] = a.map((v, k) => interpolate(t, [0, 1], [v, b[k]]));
  const bub = i === 0 ? 0 : (seg.face === 'bubble' ? t : (prev.face === 'bubble' ? 1 - t : 0));

  // 5b. the face video inside the frame: full size, or sized and moved so his face is centred
  const [cx, cy] = faceAt(f);
  const s = BUBBLE.size;
  const bx = Math.min(0, Math.max(s - BUBBLE_VIDEO_W, s / 2 - cx * BUBBLE_VIDEO_W));
  const by = Math.min(0, Math.max(s - BUBBLE_VIDEO_H, s / 2 - cy * BUBBLE_VIDEO_H));
  const vw = interpolate(bub, [0, 1], [W, BUBBLE_VIDEO_W]);
  const vh = interpolate(bub, [0, 1], [H, BUBBLE_VIDEO_H]);
  const vx = interpolate(bub, [0, 1], [0, bx]);
  const vy = interpolate(bub, [0, 1], [0, by]);
  const zoom = seg.face === 'full' ? zoomAt(f) : 1;

  // 5c. the card: slides in when it appears, swaps content, fades out when the face goes full
  const cardKind = seg.card ?? (prev.card && f - start < 10 ? prev.card : undefined);
  const cardFrom = seg.card ? start : fr(prev.t);
  const cardIn = seg.card && !prev.card ? spring({frame: f - start - 4, fps: FPS, config: {damping: 16}})
    : seg.card ? 1 : interpolate(f - start, [0, 10], [1, 0], {extrapolateRight: 'clamp'});
  const swap = seg.card && prev.card && prev.card !== seg.card ? interpolate(f - start, [0, 8], [0, 1], {extrapolateRight: 'clamp'}) : 1;
  const connectFrom = fr(SEGS[3].t);

  return (
    <AbsoluteFill>
      {cardKind && (
        <div style={{position: 'absolute', left: SCREEN.x, top: SCREEN.y, width: SCREEN.w, height: SCREEN.h,
          borderRadius: SCREEN.radius, overflow: 'hidden', border: `3px solid ${C.blueSoft}`, background: '#111',
          boxShadow: `0 0 0 10px ${C.blue}22, 0 30px 90px rgba(0,0,0,0.55), 0 0 120px ${C.blue}44`,
          opacity: cardIn, transform: `translateY(${(1 - cardIn) * 120}px) scale(${0.9 + 0.1 * cardIn})`}}>
          <Sequence from={cardFrom} layout="none">
            <div style={{position: 'absolute', inset: 0, opacity: swap, transform: `translateX(${(1 - swap) * 60}px)`}}>
              <CardContent kind={cardKind} from={cardFrom} />
            </div>
          </Sequence>
        </div>
      )}

      {/* his face */}
      <div style={{position: 'absolute', left, top, width, height, borderRadius: radius, overflow: 'hidden',
        boxShadow: bub > 0.01 ? `0 0 0 ${6 * bub}px ${C.yellow}, 0 18px 50px rgba(0,0,0,0.5)` : 'none'}}>
        <div style={{position: 'absolute', left: vx, top: vy, width: vw, height: vh,
          transform: `scale(${zoom})`, transformOrigin: '50% 45%'}}>
          <OffthreadVideo src={staticFile('face_cut.mp4')} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        </div>
      </div>
      {/* drawn after the face, so it sits on top of it.  "I'll show you how to connect Claude to your Gmail" */}
      <Sequence from={connectFrom} durationInFrames={SCREEN_START - connectFrom} layout="none">
        <ConnectCard connectAt={fr(M.connectAt) - connectFrom} cleanAt={fr(M.cleanAt) - connectFrom} />
      </Sequence>

    </AbsoluteFill>
  );
};
