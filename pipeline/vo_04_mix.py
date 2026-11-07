# ============================================================
# VO 04 MIX: voice + camera shutter at each shot change + whoosh and tick on the end card,
#        then two-pass loudnorm to -14 LUFS, true peak under -1.5 dB, measured on the AAC file.
# In   : voice_cut.wav, video_silent.mp4, shots.json   Out: vo1_final.mp4 (rename after)
# Never: never change the voice itself. Sound effects sit 14 to 17 dB under.
# ============================================================
import json,subprocess,re
SH=json.load(open('shots.json')); S='/home/user/videos/sfx/'
cues=[(s['s'],S+('whoosh-air.wav' if s['kind']=='end' else 'camera-shutter.wav'),-17 if s['kind']!='end' else -14) for s in SH[1:]]
cues.append((SH[-1]['s']+0.5,S+'tick-warm.wav',-16))
inp=['-i','voice_cut.wav']; f=[]
for i,(t,p,g) in enumerate(cues):
    inp+=['-i',p]; f.append(f'[{i+1}]aresample=48000,aformat=channel_layouts=stereo,volume={g}dB,adelay={int(t*1000)}:all=1[c{i}]')
f.append('[0]aresample=48000,aformat=channel_layouts=stereo[v]')
f.append('[v]'+''.join(f'[c{i}]' for i in range(len(cues)))+f'amix=inputs={len(cues)+1}:normalize=0:duration=first,apad=pad_dur=3.4[m]')
subprocess.run(['ffmpeg','-v','error','-y',*inp,'-filter_complex',';'.join(f),'-map','[m]','mix.wav'],check=True)
r=subprocess.run(['ffmpeg','-i','mix.wav','-af','loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
j=json.loads(r[r.rindex('{'):r.rindex('}')+1])
af=f"loudnorm=I=-14:TP=-2.0:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample=48000"
subprocess.run(['ffmpeg','-v','error','-y','-i','video_silent.mp4','-i','mix.wav','-af',af,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart','vo1_final.mp4'],check=True)
r=subprocess.run(['ffmpeg','-i','vo1_final.mp4','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True).stderr
print(r[r.rindex('Summary'):])
