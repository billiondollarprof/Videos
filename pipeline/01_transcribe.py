# ============================================================
# 01 TRANSCRIBE
# What : word-by-word timings of the speech, with Whisper (free speech-to-text).
# Use  : python3 01_transcribe.py voice16k.wav words.json small
#        (make voice16k.wav with: ffmpeg -i raw/face.mov -vn -ac 1 -ar 16000 voice16k.wav)
# Why  : Whisper mishears Anthony's accent sometimes. That is fine: only its TIMING is
#        used. The words come from his own transcript (02_align.py).
# ============================================================
import json, sys, wave
import numpy as np
from faster_whisper import WhisperModel
wav, out, size = sys.argv[1], sys.argv[2], sys.argv[3]
m = WhisperModel(size, device="cpu", compute_type="int8", cpu_threads=4)
prompt = "Claude, Gmail, ChatGPT, Claude Code, connectors, promotions, newsletters, OKRs, Himalayas."
w_=wave.open(wav); audio=np.frombuffer(w_.readframes(w_.getnframes()),dtype=np.int16).astype(np.float32)/32768
segs, info = m.transcribe(audio, language="en", word_timestamps=True, vad_filter=False,
                          initial_prompt=prompt, condition_on_previous_text=False)
words = []
for s in segs:
    for w in s.words:
        words.append({"w": w.word.strip(), "s": round(w.start,3), "e": round(w.end,3), "p": round(w.probability,3)})
    print(round(s.end), "s done", flush=True)
json.dump({"duration": info.duration, "words": words}, open(out, "w"))
print("FINISHED", len(words), "words", flush=True)
