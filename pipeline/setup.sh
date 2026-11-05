#!/bin/bash
# ============================================================
# SETUP: get a fresh session ready for a video edit (about 3 minutes)
# What : installs every tool the pipeline uses, downloads the three small models, and
#        installs the Remotion layout's packages. Safe to run twice.
# Why  : each cloud session starts empty. On video 1 this took many separate steps and
#        several dead ends (a missing graphics library, a face finder OpenCV 5 dropped,
#        a browser Remotion cannot download). Now it is one command.
# Use  : bash pipeline/setup.sh        (from the repo root)
# Needs: network access set to Full, or these hosts allowed: pypi.org, files.pythonhosted.org,
#        registry.npmjs.org, github.com, huggingface.co, storage.googleapis.com,
#        raw.githubusercontent.com, fonts.gstatic.com, drive.usercontent.google.com
# ============================================================
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MODELS="$ROOT/models"; mkdir -p "$MODELS"

echo "1. Python tools"
pip3 install -q faster-whisper scipy numpy pillow opencv-python-headless mediapipe "rembg[cpu]" yt-dlp 2>&1 | grep -v WARNING || true

echo "2. System tools (text reader for the privacy scan, graphics libraries for the background model)"
if ! command -v tesseract >/dev/null || ! ldconfig -p | grep -q libEGL.so.1; then
  (apt-get install -y -qq tesseract-ocr libegl1 libgles2 libgl1 >/dev/null 2>&1 || (apt-get update -qq >/dev/null 2>&1 && apt-get install -y -qq tesseract-ocr libegl1 libgles2 libgl1 >/dev/null 2>&1)) || echo "   (apt failed: install tesseract-ocr, libegl1, libgles2, libgl1 by hand)"
fi

echo "3. Models (each is small: 0.2 MB, 0.2 MB, 0.3 MB)"
get() { [ -s "$MODELS/$2" ] || curl -sSL -o "$MODELS/$2" "$1"; [ -s "$MODELS/$2" ] && echo "   $2 ok" || echo "   $2 FAILED"; }
get "https://huggingface.co/opencv/face_detection_yunet/resolve/main/face_detection_yunet_2023mar.onnx" yunet.onnx                        # finds his face (09b)
get "https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_segmenter/float16/latest/selfie_segmenter.tflite" selfie_segmenter.tflite   # finds him against the background (09c)
get "https://raw.githubusercontent.com/GregorR/rnnoise-models/master/somnolent-hogwash-2018-09-01/sh.rnnn" sh.rnnn                      # removes room noise from his voice (04b)

echo "4. Remotion layout (the browser is the one already on this machine, see remotion.config.ts)"
if [ -d "$ROOT/pipeline/remotion" ]; then (cd "$ROOT/pipeline/remotion" && npm install --silent 2>&1 | tail -1); fi

echo "Ready. Next: read CLAUDE.md, LESSONS.md and IMPROVEMENTS.md, then skill vertical-edit."
