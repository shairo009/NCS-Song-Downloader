"""
GitHub Actions: Random NCS Song Downloader
Updated: Using latest yt-dlp bypass tricks - no cookies needed!
"""

import yt_dlp
import random
import os
import glob
import subprocess
import sys

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
    """Search YouTube - use extract_flat only, no cookies needed"""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "ignoreerrors": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android"],
                "skip": ["webpage", "dash", "hls", "player_requests"],
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

def download_audio(video_id):
    """Download using yt-dlp with all possible bypass tricks"""
    
    base_opts = {
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "extract_flat": False,
        "outtmpl": "song.%(ext)s",
        "restrictfilenames": True,
        "overwrites": True,
        "no_overwrites": False,
        "continuedl": False,
        "age_limit": 99,
        "geo_bypass": True,
        "geo_bypass_country": "US",
        "sleep_interval_requests": 1,
        "throttled_rate": "100K",
        "extractor_retries": 3,
        "fragment_retries": 3,
        # Skip everything that triggers bot detection
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "android_music", "android_creator", "web"],
                "skip": ["webpage", "dash", "hls", "player_requests", "js", "player"],
                "player_skip": ["webpage", "dash", "hls", "js", "player"],
                "innertube_host": "android",
            }
        },
        # Headers to look like Android app
        "http_headers": {
            "User-Agent": "com.google.android.youtube/19.09.36 (Linux; U; Android 14; GB) gzip",
            "Accept": "*/*",
            "Accept-Language": "en-GB,en;q=0.9",
            "X-YouTube-Client-Name": "3",
            "X-YouTube-Client-Version": "19.09.36",
            "Origin": "https://www.youtube.com",
            "Referer": "https://www.youtube.com/",
        },
        # Prefer HTTP streaming (not DASH) - less bot detection
        "format": "bestaudio[protocol!=m3u8][protocol!=dash]/bestaudio/best",
        # Don't post-process (just raw audio)
        "postprocessors": [],
    }
    
    # Try 1: Normal android download
    url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"  Method 1: Android client...")
    try:
        with yt_dlp.YoutubeDL(base_opts) as ydl:
            ydl.download([url])
            for f in glob.glob("song.*"):
                sz = os.path.getsize(f)
                if sz > 5000:
                    print(f"  ✅ Success! ({sz} bytes)")
                    return f
    except Exception as e:
        err = str(e)[:80]
        if "Sign in" in err:
            print(f"    Blocked (Sign in required)")
        else:
            print(f"    {err}")
    
    # Try 2: Just best audio, no client constraint
    print(f"  Method 2: Simple bestaudio...")
    opts2 = base_opts.copy()
    opts2["format"] = "worstaudio/worst"
    opts2["extractor_args"] = {}
    del opts2["extractor_args"]
    try:
        with yt_dlp.YoutubeDL(opts2) as ydl:
            ydl.download([url])
            for f in glob.glob("song.*"):
                sz = os.path.getsize(f)
                if sz > 5000:
                    print(f"  ✅ Success! ({sz} bytes)")
                    return f
    except Exception as e:
        print(f"    {str(e)[:60]}")
    
    # Try 3: Format sort by size (get smallest)
    print(f"  Method 3: Smallest audio only...")
    opts3 = base_opts.copy()
    opts3["format_sort"] = ["size", "br"]
    opts3["format"] = "worstaudio/worst"
    del opts3["extractor_args"]
    try:
        with yt_dlp.YoutubeDL(opts3) as ydl:
            ydl.download([url])
            for f in glob.glob("song.*"):
                sz = os.path.getsize(f)
                if sz > 5000:
                    print(f"  ✅ Success! ({sz} bytes)")
                    return f
    except Exception as e:
        print(f"    {str(e)[:60]}")
    
    return None


# ==========================================
# MAIN
# ==========================================
print(f"🎵 Query: {random.choice(SONGS)}")
query = random.choice(SONGS)

entries = search_songs(query)

if not entries:
    backups = ["tobu ncs", "cartoon ncs", "different heaven ncs", "egzod ncs"]
    for bq in backups:
        print(f"🔄 Backup: {bq}")
        entries = search_songs(bq, 3)
        if entries:
            break

if not entries:
    print("❌ No results!")
    exit(1)

# Filter: under 10 min
valid = [e for e in entries if e.get("duration", 0) and int(e.get("duration", 0)) < 600]
if not valid:
    valid = entries

chosen = random.choice(valid)
video_id = chosen.get("id", "")
title = chosen.get("title", "Unknown")
artist = chosen.get("channel", "NCS")
duration = int(chosen.get("duration", 0))
m, s = divmod(duration, 60)

print(f"🎧 {title}")
print(f"👤 {artist}")
print(f"⏱ {m}:{s:02d}")
print()

# DOWNLOAD
song_file = download_audio(video_id)

if not song_file:
    print("❌ Download failed!")
    with open("song_title.txt", "w") as f:
        f.write(f"Song: {title}\nArtist: {artist}\nStatus: FAILED\n")
    exit(1)

# Rename
ext = os.path.splitext(song_file)[1]
os.rename(song_file, f"ncs_song{ext}")
size = os.path.getsize(f"ncs_song{ext}")
print(f"💾 Size: {size} bytes")

with open("song_title.txt", "w") as f:
    f.write(f"Song: {title}\nArtist: {artist}\nDuration: {m}:{s:02d}\n")

print("✅ Done!")