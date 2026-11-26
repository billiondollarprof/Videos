#!/bin/bash
# finish life video 1 v4 once the own-room render halves are done
cd /home/user/Videos/projects/life_01
until [ "$(grep -h '^frames' work/room_A.log work/room_B.log 2>/dev/null | wc -l)" -ge 2 ] || [ "$(pgrep -f room_own_full.py | wc -l)" -eq 0 ]; do sleep 30; done
grep -h '^frames' work/room_A.log work/room_B.log
python3 scripts/assemble.py > work/assemble.log 2>&1; tail -1 work/assemble.log
python3 scripts/mix.py | tail -1
ffmpeg -hide_banner -loglevel error -y -i work/picture.mp4 -i work/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart why_life_is_beautiful_v4.mp4
ls -l why_life_is_beautiful_v4.mp4
ffmpeg -hide_banner -i why_life_is_beautiful_v4.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
python3 - <<'PY'
src=open('scripts/assemble.py').read(); cut=src.index('# ---------- 2. Font')
exec(src[:cut]); open('work/kept_text.txt','w').write(' '.join(w['w'] for w in cap))
PY
HF_HUB_DISABLE_XET=1 python3 ../../pipeline/12_check_final.py why_life_is_beautiful_v4.mp4 work/kept_text.txt 2>&1 | grep -v -i warn | tail -3
echo FINISHED
