---
name: publish-copy
description: Write the words for posting a finished video - YouTube title options, the description with chapters, a short caption for Reels, Shorts and TikTok, hashtags, and the thumbnail words. Use when Anthony asks for the description, the title, the caption, or says the video is ready to post.
---

# Publish copy

He posts the full video on YouTube and a short on Instagram, YouTube Shorts and TikTok. Write
everything so he can copy it from his phone: each block in its own code block.

## Inputs
- The finished video's word timings (`12_check_final.py` writes `_final_words.json`, or transcribe
  the final video with `01b_transcribe_fillers.py`).
- His own words from the video. Only claim what the video says or shows.

## 1. Chapters (YouTube description)
1. Find the time of each key moment from the word timings: the problem, connecting the tool, the
   prompt, each main step, the result, the extra tip, the end. Print the sentences with times.
2. YouTube needs at least 3 chapters, the first at 0:00, each at least 10 seconds long.
3. Write plain chapter names, an action each: "Connect Gmail to Claude", "Let it work".
4. The times belong to the finished cut. If he trims it later, they shift. Say so in one line.

## 2. The description
In this order:
1. Two or three sentences: the problem, what the video shows, who it is for. Say "free" only if
   he shows the free plan (video 1: he did).
2. CHAPTERS.
3. THE PROMPT HE USED, in his own words, so people can copy it.
4. GOOD TO KNOW: three short, true points that stop wrong expectations. Video 1: Claude moves
   emails to Trash (not deleted for good), Gmail keeps Trash 30 days, Claude trashes one
   conversation at a time and gives the quick Gmail steps for big batches.
5. One line about him and a subscribe line. No "link in bio". No promises he did not make.
6. Hashtags, 3 to 5 (video 1: #Claude #Gmail #AI #Productivity #InboxZero).

## 3. Titles (give 3, each different)
Pair with the thumbnail (skill `thumbnail`): the thumbnail asks the question, the title answers it.
- "Stop Deleting Emails by Hand: Use Claude Instead (Free)"
- "How to Clean Your Gmail with Claude"
- "Let Claude Clean Your Gmail Inbox for You (Free Plan)"

## 4. The short's caption
One line: the hook, the benefit, where to find the full video, 3 or 4 hashtags. Tell people to
search his name on YouTube. Do not write "link in bio" (his note, 2026-11-05).
Example: "Stop deleting emails by hand. Watch Claude clean a full Gmail inbox, free. Full video on
YouTube: search Anthony Nwobosi. #Claude #Gmail #AI #Productivity"

## 5. Check
No em dashes, British English, no number or claim that is not in the video, chapters in order.
