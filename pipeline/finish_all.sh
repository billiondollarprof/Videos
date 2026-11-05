#!/bin/bash
# ============================================================
# FINISH ALL: render, add sound, check the finished video
# Run from the project folder, after the stills have been looked at and look right.
# Order: Remotion render (about 35 minutes for 4 minutes of video: run it in the background) ->
# sound effects, mix, loudness, end card flash (11) -> listen to the final video (12).
# Use  : bash ../../pipeline/finish_all.sh final_name.mp4
# ============================================================
set -e
P="$(cd "$(dirname "$0")" && pwd)"; OUT="${1:-final.mp4}"
(cd remotion && npx remotion render src/Root.tsx Gmail ../video_silent.mp4 --concurrency=4 --codec=h264 --crf=18 --muted --jpeg-quality=92 --timeout=120000)
python3 "$P/11_finish.py" video_silent.mp4 voice_cut_raw.wav "$OUT" remotion/src/data.json
python3 "$P/12_check_final.py" "$OUT" kept_text.txt
echo "Zero tics and silences is the goal. Fix anything listed with a time cut, rebuild, then send."
