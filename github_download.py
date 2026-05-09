"""
GitHub Actions: Random NCS Song Downloader
Ye script GitHub pe chalti hai, tumhare PC pe nahi!
Android client use karta hai to avoid YouTube bot detection
"""

import yt_dlp
import random
import os

# NCS songs list - har baar naya song milega!
SONGS = [
    "tobu infectious ncs",
    "tobu hope ncs",
    "tobu colors ncs",
    "tobu higher ncs",
    "different heaven ncs",
    "cartoon on on ncs",
    "warriyo mortals ncs",
    "electro light symbolism ncs",
    "jim yosef firefly ncs",
    "itero apocalypse ncs",
    "lost sky fearless ncs",
    "tobu candyland ncs",
    "tobu mesmerize ncs",
    "aeden what is love ncs",
    "egzod royalty ncs",
    "laszlo supernova ncs",
    "syn cole time ncs",
    "havsun big beat ncs",
    "kontinuum lost ncs",
    "tobu summer burst ncs",
    "rival lonely way ncs",
]

# Search config with Android client to bypass bot detection
YDL_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "extract_flat": True,
    "extractor_args": {"youtube": {"player_client": ["android"]}},
    "ignoreerrors": True,
}

def search_youtube(query):
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)
            return [e for e in info.get("entries", []) if e and e.get("id")]
    except Exception as e:
        print(f"Search error: {e}")
        return []

# Random song select karo
query = random.choice(SONGS)
print(f"Selected: {query}")

# Search karo
entries = search_youtube(query)

# Retry with simpler query if no results
if not entries:
    parts = query.split()
    if len(parts) > 1:
        simpler = parts[0]
        print(f"No results, trying: {simpler}")
        entries = search_youtube(simpler)

# Retry with backup queries
if not entries:
    backups = ["tobu ncs", "cartoon ncs", "different heaven ncs"]
    for bq in backups:
        print(f"Trying backup: {bq}")
        entries = search_youtube(bq)
        if entries:
            break

if not entries:
    print("No results found after all retries!")
    exit(1)

# Randomly choose from results
chosen = random.choice(entries)
url = f"https://youtube.com/watch?v={chosen.get('id', '')}"
title = chosen.get("title", "Unknown")
artist = chosen.get("channel", "NCS")
print(f"Downloading: {title}")
print(f"URL: {url}")

# Download karo - use Android client
dl_opts = {
    "format": "bestaudio/best",
    "outtmpl": "song.%(ext)s",
    "quiet": True,
    "no_warnings": True,
    "extractor_args": {"youtube": {"player_client": ["android"]}},
    "extractor_retries": 3,
    "fragment_retries": 3,
    "ignoreerrors": True,
}

try:
    with yt_dlp.YoutubeDL(dl_opts) as ydl:
        ydl.download([url])
except Exception as e:
    print(f"Android client failed: {e}")
    print("Trying web client...")
    dl_opts["extractor_args"] = {"youtube": {"player_client": ["web"]}}
    with yt_dlp.YoutubeDL(dl_opts) as ydl:
        ydl.download([url])

# File rename karo
for f in os.listdir("."):
    if f.endswith(".m4a") or f.endswith(".webm"):
        ext = os.path.splitext(f)[1]
        os.rename(f, f"ncs_song{ext}")
        print(f"Downloaded: {f} -> ncs_song{ext}")
        break
    elif "." in f and not f.endswith(".py") and not f.endswith(".txt") and not f.endswith(".yml"):
        size = os.path.getsize(f)
        if size > 100000:
            ext = os.path.splitext(f)[1]
            os.rename(f, f"ncs_song{ext}")
            print(f"Downloaded: {f} -> ncs_song{ext}")
            break

# Save info
with open("song_title.txt", "w") as f:
    f.write(f"Song: {title}\n")
    f.write(f"Artist: {artist}\n")

print(f"TITLE: {title}")
print(f"ARTIST: {artist}")
print("Done! Song ready to download from GitHub Actions artifacts!")