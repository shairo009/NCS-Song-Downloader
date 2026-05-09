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

# Random song select karo
query = random.choice(SONGS)
print(f"Selected: {query}")

# Search karo on YouTube - Android client se (bypasses bot detection)
ydl_opts = {
    "quiet": True,
    "no_warnings": True,
    "extract_flat": True,
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(f"ytsearch5:{query}", download=False)
    entries = [e for e in info.get("entries", []) if e and e.get("id")]

    if not entries:
        print("No results found!")
        exit(1)

    # Randomly choose from results
    chosen = random.choice(entries)
    url = f"https://youtube.com/watch?v={chosen.get('id', '')}"
    title = chosen.get("title", "Unknown")
    artist = chosen.get("channel", "NCS")
    print(f"Downloading: {title}")
    print(f"URL: {url}")

# Download karo - use Android client to bypass restrictions
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

with yt_dlp.YoutubeDL(dl_opts) as ydl_dl:
    try:
        ydl_dl.download([url])
    except Exception as e:
        print(f"First attempt failed: {e}")
        print("Trying with web client...")
        dl_opts["extractor_args"] = {"youtube": {"player_client": ["web"]}}
        with yt_dlp.YoutubeDL(dl_opts) as ydl_dl2:
            ydl_dl2.download([url])

# File rename karo
for f in os.listdir("."):
    if f.endswith(".m4a") or f.endswith(".webm"):
        base = os.path.splitext(f)[0]
        ext = os.path.splitext(f)[1]
        os.rename(f, f"ncs_song{ext}")
        print(f"Downloaded: {f} -> ncs_song{ext}")
        break
    elif "." in f and not f.endswith(".py") and not f.endswith(".txt") and not f.endswith(".yml"):
        size = os.path.getsize(f)
        if size > 100000:  # > 100KB = real audio file
            os.rename(f, f"ncs_song{os.path.splitext(f)[1]}")
            print(f"Downloaded: {f} -> ncs_song{os.path.splitext(f)[1]}")
            break

# Save info
with open("song_title.txt", "w") as f:
    f.write(f"Song: {title}\n")
    f.write(f"Artist: {artist}\n")

print(f"TITLE: {title}")
print(f"ARTIST: {artist}")
print("Done! Song ready to download from GitHub Actions artifacts!")