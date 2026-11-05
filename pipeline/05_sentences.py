# ============================================================
# 05 SENTENCES: the talk, one sentence per line, with word numbers
# What : prints every sentence with its time and its word numbers, for planning cuts.
# Why  : cuts are chosen by sentence, between phrases, then listed for Anthony's yes.
#        The word numbers go into project.json "cuts", "steps" and "tips".
# Use  : python3 05_sentences.py > sentences.txt
# ============================================================
import json
import re

W = json.load(open("aligned_words.json"))
sentence = []
k = 0
for i, w in enumerate(W):
    sentence.append(i)
    if re.search(r"[.?!]$", w["w"]) or i == len(W) - 1:
        a, b = W[sentence[0]], W[sentence[-1]]
        text = " ".join(W[j]["w"] for j in sentence)
        print(f"S{k:03d} {a['s']:6.1f}-{b['e']:6.1f} [{sentence[0]}-{sentence[-1]}] {text}")
        sentence = []
        k += 1
