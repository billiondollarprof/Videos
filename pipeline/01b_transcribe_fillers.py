# ============================================================
# 01b TRANSCRIBE WITH FILLERS
# What : Whisper (free speech-to-text) with a prompt full of fillers, so it writes down
#        "um", "uh", "eh", "so now", "alright" instead of quietly dropping them.
# Why  : version 1 of video 1 kept fillers and a repeated opening, because the normal
#        transcription skipped them and its timings at the very start were guesses.
# Use  : python3 01b_transcribe_fillers.py voice16k.wav face_words_fillers.json medium
#        (medium is slower than small but much better at fillers and timings: ~8 min for 9 min)
# ============================================================
import json, sys, wave
import numpy as np
from faster_whisper import WhisperModel
wav, out, size = sys.argv[1], sys.argv[2], sys.argv[3]
w_ = wave.open(wav); audio = np.frombuffer(w_.readframes(w_.getnframes()), dtype=np.int16).astype(np.float32) / 32768
m = WhisperModel(size, device="cpu", compute_type="int8", cpu_threads=4)
prompt = "Umm, so, uh, so now, eh, alright, alright. Okay so, uh, okay so, um, you know, like, eh. Claude, Gmail, ChatGPT."
segs, info = m.transcribe(audio, language="en", word_timestamps=True, vad_filter=False,
                          initial_prompt=prompt, condition_on_previous_text=False, suppress_tokens=[])
words = []
for s in segs:
    for x in s.words:
        words.append({"w": x.word.strip(), "s": round(x.start, 3), "e": round(x.end, 3), "p": round(x.probability, 3)})
    print(round(s.end), flush=True)
json.dump({"words": words}, open(out, "w"))
print("FINISHED", len(words), flush=True)
