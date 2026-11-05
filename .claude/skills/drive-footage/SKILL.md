---
name: drive-footage
description: Get Anthony's raw video files from Google Drive into the project folder. Use at the start of every edit, or when he says he has uploaded footage.
---

# Footage from Google Drive

The Drive connector passes files through the chat as text, which is far too small for
video. So the connector only **finds** the files, and `curl` downloads them.

1. Find the files with the Drive connector (`search_files`). Look in **shared with me**
   too (`sharedWithMe = true`): he sometimes uploads from another Google account and
   shares the folder. Note each file's id and size.
2. The file must be shared as **"Anyone with the link can view"**, or the download
   returns a web page instead of the video. If it is not, give him the steps:
   1. Open the Google Drive app.
   2. Tap the three dots next to the file, then **Share**, then **General access**.
   3. Choose **Anyone with the link**.
3. Download each file:
   `curl -sSL -o raw/<name> "https://drive.usercontent.google.com/download?id=<id>&export=download&confirm=t"`
4. Check the size matches Drive, and that `ffprobe` reads it. A file of a few KB is a
   web page, not a video: go back to step 2.
5. If `drive.usercontent.google.com` is refused, the environment's network access is
   too narrow. He changes it in the Claude app: the environment name in the title bar,
   **Edit**, **Network access**, **Full** (or add the Google Drive hosts).

## Sending the finished video back
A file sent in the chat (SendUserFile) reaches his phone. Keep it under about 150 MB.
