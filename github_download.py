"""
GitHub Actions: Random NCS Song Downloader
Ye script GitHub pe chalti hai, tumhare PC pe nahi!
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

# Search karo on YouTube
ydl_opts = {"quiet": True, "no_warnings": True, "extract_flat": True}
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

# Download karo
dl_opts = {
    "format": "bestaudio[ext=m4a]/bestaudio",
    "outtmpl": "song.%(ext)s",
    "quiet": True,
    "no_warnings": True,
    "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}],
    "embedthumbnail": False,
}

with yt_dlp.YoutubeDL(dl_opts) as ydl_dl:
    ydl_dl.download([url])

# File rename karo
for f in os.listdir("."):
    if f.endswith(".m4a"):
        os.rename(f, "ncs_song.m4a")
        print(f"Downloaded: {f} -> ncs_song.m4a")

# Save info
with open("song_title.txt", "w") as f:
    f.write(f"Song: {title}\n")
    f.write(f"Artist: {artist}\n")

print(f"TITLE: {title}")
print(f"ARTIST: {artist}")
print("Done!")