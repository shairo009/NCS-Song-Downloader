"""
GitHub Actions: Random NCS Song Downloader
Using yt-dlp nightly + format fallback - no cookies
"""

import yt_dlp
import random
import os
import glob
import subprocess
import sys
import urllib.request
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
]

def search_songs(query):
    """Search with extract_flat only"""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "ignoreerrors": True,
        "extractor_args": {"youtube": {"player_client": ["android"]}},
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)
            return [e for e in info.get("entries", []) if e and e.get("id")]
    except:
        return []

def download_audio(video_id):
    """Download using multiple format approaches"""
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_template = "song.%(ext)s"
    
    # Try different combinations
    attempts = [
        # 1. Android client, default format
        {
            "format": "bestaudio[protocol^=http]/bestaudio/best",
            "extractor_args": {"youtube": {"player_client": ["android"]}},
            "http_headers": {"User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36"},
        },
        # 2. Android Music client
        {
            "format": "bestaudio[protocol^=http]/bestaudio/best",
            "extractor_args": {"youtube": {"player_client": ["android_music"]}},
        },
        # 3. Web client with skip
        {
            "format": "best[height<=360]/best",
            "extractor_args": {"youtube": {"player_client": ["web"], "skip": ["webpage", "dash"]}},
        },
        # 4. No extractor_args, simple format
        {
            "format": "worstaudio/worst",
            "extractor_args": {},
        },
        # 5. iOS client
        {
            "format": "bestaudio/best",
            "extractor_args": {"youtube": {"player_client": ["ios"]}},
        },
        # 6. No client restriction, minimal
        {
            "format": "worst",
            "extractor_args": {},
            "http_headers": {"User-Agent": "curl/8.0"},
        },
    ]
    
    for i, opts in enumerate(attempts, 1):
        dl_opts = {
            "quiet": True,
            "no_warnings": True,
            "ignoreerrors": True,
            "outtmpl": output_template,
            "restrictfilenames": True,
            "extract_flat": False,
            "geo_bypass": True,
            "geo_bypass_country": "US",
            "extractor_retries": 2,
            "fragment_retries": 2,
            "overwrites": True,
        }
        dl_opts.update(opts)
        
        # Remove empty extractor_args
        if not dl_opts.get("extractor_args"):
            del dl_opts["extractor_args"]
        
        print(f"  Attempt {i}...", end=" ")
        try:
            with yt_dlp.YoutubeDL(dl_opts) as ydl:
                ydl.download([url])
                for f in glob.glob("song.*"):
                    sz = os.path.getsize(f)
                    if sz > 3000:
                        print(f"✅ ({sz} bytes)")
                        return f
                print("no file")
        except Exception as e:
            err = str(e)[:60]
            print(f"✗ {err}")
    
    return None

# ===== MAIN =====
query = random.choice(SONGS)
print(f"🎵 {query}")

entries = search_songs(query)

if not entries:
    for bq in ["tobu ncs", "cartoon ncs", "different heaven ncs"]:
        entries = search_songs(bq)
        if entries:
            break

if not entries:
    print("❌ No results!")
    exit(1)

valid = [e for e in entries if e.get("duration", 0) and int(e.get("duration", 0)) < 600]
if not valid:
    valid = entries

chosen = random.choice(valid)
video_id = chosen.get("id", "")
title = chosen.get("title", "Unknown")
artist = chosen.get("channel", "NCS")
dur = int(chosen.get("duration", 0))

print(f"🎧 {title} - {artist} ({dur//60}:{dur%60:02d})")

song_file = download_audio(video_id)

if not song_file:
    print("❌ Failed! Make sure the song is in repo artifacts.")
    with open("song_title.txt", "w") as f:
        f.write(f"Song: {title}\nArtist: {artist}\nStatus: FAILED\n")
    exit(1)

ext = os.path.splitext(song_file)[1]
os.rename(song_file, f"ncs_song{ext}")
size = os.path.getsize(f"ncs_song{ext}")

with open("song_title.txt", "w") as f:
    f.write(f"Song: {title}\nArtist: {artist}\nDuration: {dur//60}:{dur%60:02d}\n")

print(f"✅ Done! {size} bytes")