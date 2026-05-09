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

# Find and rename the downloaded song file
song_file = None
for f in os.listdir("."):
    if f.startswith("song."):
        song_file = f
        break

if not song_file:
    # Try to find by file size
    for f in os.listdir("."):
        if f == "ncs_song.m4a" or f == "ncs_song.webm":
            song_file = f
            break
        fp = os.path.join(".", f)
        if os.path.isfile(fp) and not f.endswith(".py") and not f.endswith(".txt") and not f.endswith(".yml"):
            size = os.path.getsize(fp)
            if size > 50000:
                song_file = f
                break

if song_file and song_file != "ncs_song.m4a":
    ext = os.path.splitext(song_file)[1]
    os.rename(song_file, f"ncs_song{ext}")
    print(f"Renamed: {song_file} -> ncs_song{ext}")
elif song_file:
    print(f"File already named: {song_file}")

# List final files
print("Files in directory:")
for f in os.listdir("."):
    fp = os.path.join(".", f)
    if os.path.isfile(fp):
        sz = os.path.getsize(fp)
        print(f"  {f} ({sz} bytes)")

# Save info
with open("song_title.txt", "w") as f:
    f.write(f"Song: {title}\n")
    f.write(f"Artist: {artist}\n")

print(f"TITLE: {title}")
print(f"ARTIST: {artist}")
print("Done! Song ready to download from GitHub Actions artifacts!")