// ============================================================
// BACKGROUND
// What : the navy backdrop with two soft glows that drift very slowly.
// Why  : the phone screen does not fill the width, so the sides need to look designed.
// Never: never make the glows bright enough to pull the eye from the screen.
// ============================================================
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C} from './theme';

export const Background: React.FC = () => {
  const f = useCurrentFrame();
  const drift = Math.sin(f / 240) * 60; // slow, about one sway every 25 s
  return (
    <AbsoluteFill style={{background: `linear-gradient(180deg, ${C.navyDeep} 0%, ${C.navy} 55%, ${C.navyDeep} 100%)`}}>
      <div style={{position: 'absolute', left: -300 + drift, top: -200, width: 1100, height: 1100, borderRadius: '50%',
        background: `radial-gradient(circle, ${C.blue}55 0%, transparent 65%)`}} />
      <div style={{position: 'absolute', right: -350 - drift, bottom: -300, width: 1000, height: 1000, borderRadius: '50%',
        background: `radial-gradient(circle, ${C.yellow}22 0%, transparent 65%)`}} />
    </AbsoluteFill>
  );
};
