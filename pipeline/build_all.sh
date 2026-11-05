#!/bin/bash
# ============================================================
# BUILD ALL: from the approved cuts to a layout ready for stills
# Run from the project folder, after: footage downloaded, sync, word timing (01b, 02), cuts
# approved and written to project.json, 04_vad, 06_edl, privacy mask (07, 08).
# Order: tracks (cut, speed, status bar crop) -> face track -> soft background -> captions and
# moments -> B-roll fitted and assets copied. About 25 minutes for a 9 minute recording, most of
# it the tracks (6) and the background (10). Stops at the first failing step.
# Use  : bash ../../pipeline/build_all.sh
# ============================================================
set -e
P="$(cd "$(dirname "$0")" && pwd)"
echo "== 1/5 cut tracks";           python3 "$P/09_build_tracks.py"
echo "== 2/5 face track";           python3 "$P/09b_face_track.py" face_cut.mp4 remotion/src/faceTrack.json
echo "== 3/5 soft background";      python3 "$P/09c_soft_background.py" face_cut.mp4 face_soft.mp4
echo "== 4/5 captions and moments"; python3 "$P/10_captions.py"
echo "== 5/5 B-roll and assets";    python3 "$P/10b_assets.py"
for f in face_cut.mp4 face_soft.mp4 screen_cut.mp4 voice_cut_raw.wav; do echo "   $f $(ffprobe -v error -show_entries format=duration -of csv=p=0 $f) s"; done
echo "All four must be the same length. Next: stills (npx remotion still), then finish_all.sh."
