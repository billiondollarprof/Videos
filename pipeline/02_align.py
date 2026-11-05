import json, re, difflib
# ============================================================
# 02 ALIGN: his words, Whisper's timing
# What : gives every word of Anthony's own transcript a start and end time, by lining
#        it up with Whisper's words. Words Whisper missed get times spread between
#        their neighbours.
# Use  : python3 02_align.py   (reads face_words_fillers.json and project.json "transcript")
# Out  : aligned_words.json
# ============================================================
P = json.load(open("project.json"))
W = json.load(open("face_words_fillers.json"))["words"]
T = open(P["transcript"]).read().split()
norm = lambda x: re.sub(r"[^a-z0-9']", "", x.lower())
wn = [norm(w["w"]) for w in W]; tn = [norm(t) for t in T]
sm = difflib.SequenceMatcher(None, tn, wn, autojunk=False)
tm = [None]*len(T)   # (start,end) per transcript word
matched = 0
for a,b,n in sm.get_matching_blocks():
    for k in range(n):
        tm[a+k] = (W[b+k]["s"], W[b+k]["e"]); matched += 1
# fill gaps by spreading evenly between neighbours
i=0
while i < len(tm):
    if tm[i] is None:
        j=i
        while j < len(tm) and tm[j] is None: j+=1
        left = tm[i-1][1] if i>0 else 0.0
        right = tm[j][0] if j < len(tm) else W[-1]["e"]
        step = (right-left)/(j-i)
        for k in range(i,j):
            tm[k]=(round(left+step*(k-i),3), round(left+step*(k-i+1),3))
        i=j
    else: i+=1
out=[{"w":T[i],"s":tm[i][0],"e":tm[i][1]} for i in range(len(T))]
json.dump(out, open("aligned_words.json","w"))
print("transcript words", len(T), "whisper words", len(W), "matched exactly", matched, "(%.0f%%)"%(100*matched/len(T)))
# where does "So you open your Claude account" start?
for i in range(len(T)-5):
    if [norm(x) for x in T[i:i+5]]==["so","you","open","your","claude"]:
        print("'So you open your Claude' at", out[i]["s"], "s")
print("first words:", [(o["w"],o["s"]) for o in out[:6]])
print("last words:", [(o["w"],o["s"],o["e"]) for o in out[-4:]])
