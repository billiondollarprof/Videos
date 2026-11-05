// ============================================================
// ROOT
// What : puts every layer together, in order from back to front, and registers
//        the video with Remotion. Sound is added afterwards by ffmpeg (see finish.sh).
// ============================================================
import React from 'react';
import {AbsoluteFill, Composition, registerRoot} from 'remotion';
import {Background} from './Background';
import {Captions} from './Captions';
import data from './data.json';
import {EndCard, FastBadge, Hook, Progress, Steps, Tips} from './Overlays';
import {People} from './People';
import {FPS, H, W} from './theme';

const END_CARD_FRAMES = 4 * FPS;
const TOTAL = data.frames + END_CARD_FRAMES;

const Video: React.FC = () => (
  <AbsoluteFill>
    <Background />
    <People />
    <FastBadge />
    <Steps />
    <Tips />
    <Captions />
    <Hook />
    <EndCard />
    <Progress total={TOTAL} />
  </AbsoluteFill>
);

const Root: React.FC = () => (
  <Composition id="Gmail" component={Video} durationInFrames={TOTAL} fps={FPS} width={W} height={H} />
);

registerRoot(Root);
