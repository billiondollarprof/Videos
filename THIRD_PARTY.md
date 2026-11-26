# Borrowed things and their licences

| What | From | Licence | Where it is used |
|---|---|---|---|
| Editing ideas: the note-becomes-a-rule loop, cut between phrases, sound effects on visible actions, soft sound palette, -14 LUFS measured on the delivery, the checks before delivery | Nate Herk, `nateherkai/herk-edit-kit`, `docs/EDITING-PLAYBOOK.md` | MIT | `CLAUDE.md`, the skills. Ideas only, no code copied. |
| Mouse click sound (`sfx/mouse-click-cc0.ogg`) | Wikimedia Commons, "Computer mouse single click.ogg", by Darklanlan | CC0 (free for any use) | "Speeding up" badge |
| Plus Jakarta Sans font (`pipeline/remotion/public/`) | Google Fonts, Tokotype | SIL Open Font Licence 1.1 | Captions and titles |
| RNNoise model `sh.rnnn` (downloaded at edit time, not stored) | `GregorR/rnnoise-models` | BSD-style | Voice noise removal |
| Remotion | remotion.dev | Free for individuals and companies of up to 3 people | Layout and render |

Our own sounds in `sfx/` (whooshes, taps, tick, paper, camera shutter) are made in code by
`sfx/make_sfx.py` and belong to this repo.

## Robust Video Matting (tested 2026-11-25, life video 1)
- What: a video model that separates a person from the background, steady from frame to frame.
- From: github.com/PeterL1n/RobustVideoMatting, release v1.0.0, `rvm_mobilenetv3_fp32.torchscript`.
- Licence: GPL-3.0. We run it as a tool on our machine; its code and weights are not in this repo.

## Instrument Serif Italic (life video 1, 2026-11-25)
- What: the italic serif for feeling words in the captions.
- From: github.com/google/fonts, `ofl/instrumentserif/InstrumentSerif-Italic.ttf`.
- Licence: SIL Open Font License 1.1. Downloaded at edit time, not stored in this repo.

## Anton (life video 1 v4, 2026-11-26)
- What: the tall condensed display face for some key words in the captions.
- From: github.com/google/fonts, `ofl/anton/Anton-Regular.ttf`. Licence: SIL Open Font License 1.1. Not stored here.
