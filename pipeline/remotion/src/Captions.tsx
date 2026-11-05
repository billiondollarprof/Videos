// ============================================================
// CAPTIONS
// What : one to three words at a time. The word being said turns yellow.
// Why  : most people watch Shorts with the sound off. Big, short captions keep them.
//        The words are from your own transcript. Only the timing is from the speech tool.
// Never: never show a word before it is said.
// ============================================================
import React from 'react';
import {spring, useCurrentFrame} from 'remotion';
import data from './data.json';
import {C, CAPTION_Y_FACE, CAPTION_Y_SCREEN, FPS, fontFamily, W} from './theme';

type Cap = {s: number; e: number; words: {t: string; s: number; e: number}[]};
const CAPS = data.captions as Cap[];

export const Captions: React.FC = () => {
  const f = useCurrentFrame();
  const now = f / FPS;
  const cap = CAPS.find((c) => now >= c.s && now < c.e);
  if (!cap) return null;
  // captions sit below the card whenever a card is showing (B-roll in the opening, then the screen)
  // captions sit below the card whenever a card is showing (cardWindows, from captions.py)
  const onScreen = (data.moments as any).cardWindows.some(([a, b]: number[]) => now >= a && now < b);
  const pop = spring({frame: f - Math.round(cap.s * FPS), fps: FPS, config: {damping: 14, mass: 0.5}, durationInFrames: 8});
  const size = onScreen ? 66 : 80;
  return (
    <div style={{position: 'absolute', left: 40, width: W - 80, top: (onScreen ? CAPTION_Y_SCREEN : CAPTION_Y_FACE) - size,
      display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: '0 18px',
      transform: `scale(${0.82 + 0.18 * pop})`, opacity: pop}}>
      {cap.words.map((w, i) => {
        const active = now >= w.s && now < Math.max(w.e, w.s + 0.12);
        return (
          <span key={i} style={{fontFamily, fontWeight: 800, fontSize: size, lineHeight: 1.15,
            color: active ? C.yellow : C.white,
            WebkitTextStroke: `12px ${C.navyDeep}`, paintOrder: 'stroke fill',
            textShadow: '0 6px 18px rgba(0,0,0,0.45)',
            transform: active ? 'scale(1.08)' : 'none', display: 'inline-block'}}>
            {w.t}
          </span>
        );
      })}
    </div>
  );
};
