// ============================================================
// THEME
// What : the colours, sizes and layout numbers for the whole video.
// Why  : colours come from anthony.stellaxafe.com (navy, bright blue, yellow, white),
//        so the video looks like the same brand as the website.
// Change one look here and it changes everywhere.
// ============================================================
import {continueRender, delayRender, staticFile} from 'remotion';

// --- 0. Font ---
// Plus Jakarta Sans, the font on the website. The file is kept in public/ and loaded
// from there, so rendering never needs the internet. It is one "variable" font file
// (one file that holds every thickness, 200 to 800).
export const fontFamily = 'Plus Jakarta Sans';
if (typeof document !== 'undefined') {
  const handle = delayRender('Loading Plus Jakarta Sans');
  const face = new FontFace(fontFamily, `url(${staticFile('PlusJakartaSans-latin.woff2')}) format('woff2')`, {weight: '200 800'});
  face.load().then((f) => { document.fonts.add(f); continueRender(handle); });
}

// --- 1. Colours ---
export const C = {
  navyDeep: '#050B24',
  navy: '#0A1A4D',
  blue: '#2B6BFF',
  blueSoft: '#5B8CFF',
  yellow: '#FFD23F',
  white: '#FFFFFF',
  textDim: '#B9C6F2',
};

// --- 2. Canvas ---
export const W = 1080;
export const H = 1920;
export const FPS = 30;

// --- 3. Layout once the phone screen is showing ---
// The screen recording is 864 x 1840 once the phone's status bar is cropped off.
// Shown 1380 tall, it is 648 wide.
export const SCREEN = {w: 648, h: 1380, x: (1080 - 648) / 2, y: 230, radius: 40};
// Your face, in a circle at the top right, overlapping the phone's status bar.
export const BUBBLE = {size: 300, x: 1080 - 300 - 36, y: 40};
// Captions sit below the phone screen, so they never cover it.
export const CAPTION_Y_FACE = 1430; // while your face fills the frame
export const CAPTION_Y_SCREEN = 1760; // once the screen is showing
