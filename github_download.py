"""
GitHub Actions: Random NCS Song Downloader
Yeh script cookies ke bina kaam karegi! 
Multiple tricks use karta hai download ke liye.
"""

import yt_dlp
import random
import os
import glob
import time
import json

# NCS songs list
SONGS = [
    "tobu infectious ncs", "tobu hope ncs", "tobu colors ncs",
    "tobu higher ncs", "different heaven ncs", "cartoon on on ncs",
    "warriyo mortals ncs", "electro light symbolism ncs",
    "jim yosef firefly ncs", "lost sky fearless ncs",
    "tobu candyland ncs", "tobu mesmerize ncs",
    "aeden what is love ncs", "egzod royalty ncs",
    "laszlo supernova ncs", "syn cole time ncs",
    "havsun big beat ncs", "kontinuum lost ncs",
    "tobu summer burst ncs", "rival lonely way ncs",
    "alex skrindo ncs", "diviners ncs", "k-391 ncs",
    "alan walker fade ncs", "it's different ncs",
]

def search_songs(query, max_results=5):
    """Search YouTube using android client to avoid bot detection"""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
                "skip": ["webpage", "dash", "hls"],
            }
        },
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            entries = [e for e in info.get("entries", []) if e and e.get("id")]
            return entries
    except Exception as e:
        print(f"  Search error: {str(e)[:80]}")
        return []

def try_download_with_android(url):
    """Download using android client with different formats"""
    formats_to_try = [
        "bestaudio[ext=m4a]/bestaudio/best",
        "worstaudio/worst",
        "bestaudio[protocol^=http]/bestaudio",
        "best[height<=360]/best",
    ]
    
    for fmt in formats_to_try:
        for client in ["android", "android_music", "web", "ios"]:
            print(f"  Trying {client} / {fmt[:30]}...")
            dl_opts = {
                "format": fmt,
                "outtmpl": "ncs_song.%(ext)s",
                "quiet": True,
                "no_warnings": True,
                "ignoreerrors": True,
                "extract_flat": False,
                "extractor_args": {
                    "youtube": {
                        "player_client": [client],
                        "skip": ["webpage", "dash", "hls"],
                        "player_skip": ["webpage", "dash", "hls"],
                    }
                },
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36",
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Origin": "https://www.youtube.com",
                    "Referer": "https://www.youtube.com/",
                },
            }
            try:
                with yt_dlp.YoutubeDL(dl_opts) as ydl:
                    ydl.download([url])
                    for f in glob.glob("ncs_song.*"):
                        sz = os.path.getsize(f)
                        if sz > 10000:
                            print(f"  ✅ Success with {client}! ({sz} bytes)")
                            return True
            except Exception as e:
                err = str(e)[:60]
                if "Sign in" not in err and "bot" not in err.lower():
                    print(f"    {err}")
    return False

def try_download_without_player(url):
    """Fallback: Download without player_client, just headers"""
    print("  Trying minimal download...")
    dl_opts = {
        "format": "bestaudio[protocol^=http]/bestaudio/best",
        "outtmpl": "ncs_song.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "extract_flat": False,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*",
        },
    }
    try:
        with yt_dlp.YoutubeDL(dl_opts) as ydl:
            ydl.download([url])
            for f in glob.glob("ncs_song.*"):
                sz = os.path.getsize(f)
                if sz > 10000:
                    print(f"  ✅ Success! ({sz} bytes)")
                    return True
    except Exception as e:
        print(f"    {str(e)[:60]}")
    return False


# -----------------------------------------
# Main script
# -----------------------------------------
query = random.choice(SONGS)
print(f"🎵 Selected: {query}")

# Search karo with android client
entries = search_songs(query)

if not entries:
    # Backup queries
    backups = ["tobu ncs", "cartoon ncs", "different heaven ncs", "egzod royalty ncs", "alan walker ncs"]
    for bq in backups:
        print(f"🔄 Backup: {bq}")
        entries = search_songs(bq, 3)
        if entries:
            break

if not entries:
    print("❌ No results found!")
    exit(1)

# Filter: songs under 10 minutes
valid = [e for e in entries if e.get("duration", 0) and int(e.get("duration", 0)) < 600]
if not valid:
    valid = entries

chosen = random.choice(valid)
video_id = chosen.get("id", "")
url = f"https://youtube.com/watch?v={video_id}"
title = chosen.get("title", "Unknown")
artist = chosen.get("channel", "NCS")
duration = int(chosen.get("duration", 0))
m, s = divmod(duration, 60)
dur_str = f"{m}:{s:02d}"

print(f"🎧 Title: {title}")
print(f"👤 Artist: {artist}")
print(f"⏱ Duration: {dur_str}")
print(f"🔗 URL: {url}")
print()

# Download with all methods
success = try_download_with_android(url)

if not success:
    success = try_download_without_player(url)

if not success:
    print("❌ All download attempts failed!")
    # Save whatever info we have
    with open("song_title.txt", "w") as f:
        f.write(f"Song: {title}\n")
        f.write(f"Artist: {artist}\n")
        f.write(f"Duration: {dur_str}\n")
        f.write(f"URL: {url}\n")
        f.write(f"Status: DOWNLOAD_FAILED\n")
    exit(1)

# Rename to ncs_song.*
song_file = None
for f in glob.glob("ncs_song.*"):
    sz = os.path.getsize(f)
    if sz > 10000:
        song_file = f
        break

if not song_file:
    for f in os.listdir("."):
        if any(f.endswith(e) for e in [".m4a", ".webm", ".mp3", ".mp4", ".mkv"]):
            sz = os.path.getsize(f)
            if sz > 10000:
                song_file = f
                break

if song_file:
    ext = os.path.splitext(song_file)[1]
    new_name = f"ncs_song{ext}"
    if song_file != new_name:
        os.rename(song_file, new_name)
        print(f"📁 Renamed: {new_name}")
    print(f"💾 Size: {os.path.getsize(new_name)} bytes")
else:
    print("⚠️ No song file found, but creating info file")
    with open("song_title.txt", "w") as f:
        f.write(f"Song: {title}\n")
        f.write(f"Artist: {artist}\n")
        f.write(f"Duration: {dur_str}\n")
        f.write(f"URL: {url}\n")
        f.write(f"Status: DOWNLOAD_FAILED\n")
    exit(1)

# Save song info
with open("song_title.txt", "w") as f:
    f.write(f"Song: {title}\n")
    f.write(f"Artist: {artist}\n")
    f.write(f"Duration: {dur_str}\n")
    f.write(f"URL: {url}\n")

print(f"\n✅ Done! Song ready from GitHub Actions artifacts!")