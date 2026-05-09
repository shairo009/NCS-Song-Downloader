"""
Random NCS Song Downloader
Click once → downloads a random NCS song each time!
Har baar naya song! 🎵
"""

import os
import subprocess
import sys
import random
from pathlib import Path

# Ensure yt-dlp
try:
    import yt_dlp
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp", "--quiet"])
    import yt_dlp

DOWNLOAD_DIR = Path.home() / "Desktop" / "NCS_Songs"
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Popular NCS songs to randomly pick from
NCS_PLAYLIST = [
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
    "Alan Walker fade ncs",
    "tobu candyland ncs",
    "tobu mesmerize ncs",
    "aeden what is love ncs",
    "egzod royalty ncs",
    "level up ncs song",
    "ship warshape ncs",
    "unknown brain ncs",
    "laszlo supernova ncs",
    "syn cole time ncs",
    "havsun big beat ncs",
    "kontinuum lost ncs",
    "tobu summer burst ncs",
    "uphill battle ncs",
    "rival lonely way ncs",
    "ncs melodic dubstep",
    "ncs house music",
    "ncs trap song",
    "ncs progressive house",
]

# NCS artists to pick from
NCS_ARTISTS = [
    "tobu ncs",
    "cartoon ncs",
    "different heaven ncs",
    "warriyo ncs",
    "itero ncs",
    "jim yosef ncs",
    "lost sky ncs",
    "electro light ncs",
    "kontinuum ncs",
    "laszlo ncs",
    "egzod ncs",
    "aeden ncs",
    "rival ncs",
    "syn cole ncs",
    "havsun ncs",
]

def get_random_query():
    """Pick a random NCS song/artist to search"""
    if random.random() < 0.6:
        return random.choice(NCS_PLAYLIST)
    else:
        artist = random.choice(NCS_ARTISTS)
        if random.random() < 0.3:
            return f"{artist} -latest"
        return artist

def download_random():
    """Download a random NCS song"""
    query = get_random_query()
    
    print(f"\n{'='*50}")
    print(f"🎲 Today's luck: Searching '{query}'...")
    print(f"{'='*50}\n")
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch30:{query}", download=False)
            
            if not info or 'entries' not in info or not info['entries']:
                print("❌ No results. Trying again...")
                return False
            
            # Filter: only pick songs with reasonable duration (30s-15min)
            valid = []
            for entry in info['entries']:
                if entry and entry.get('id'):
                    dur = entry.get('duration', 0)
                    if dur and 30 < dur < 900:
                        valid.append(entry)
            
            if not valid:
                valid = [e for e in info['entries'] if e and e.get('id')]
            
            if not valid:
                print("❌ No valid songs found.")
                return False
            
            # Pick a random one from the results
            chosen = random.choice(valid)
            title = chosen.get('title', 'Unknown')
            url = f"https://youtube.com/watch?v={chosen.get('id', '')}"
            duration = chosen.get('duration', 0)
            
            # Format duration
            m, s = divmod(int(duration), 60)
            h, m = divmod(m, 60)
            dur_str = f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"
            
            print(f"🎵 Selected: {title}")
            print(f"⏱ Duration: {dur_str}")
            print(f"⬇️ Downloading...\n")
            
            # Check ffmpeg
            ffmpeg_ok = False
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
                ffmpeg_ok = True
            except:
                pass
            
            fmt = 'bestaudio[ext=m4a]/bestaudio' if ffmpeg_ok else 'bestaudio[ext=webm]/bestaudio'
            post = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'm4a'}] if ffmpeg_ok else []
            
            dl_opts = {
                'format': fmt,
                'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'postprocessors': post,
                'embedthumbnail': True,
            }
            
            with yt_dlp.YoutubeDL(dl_opts) as ydl_dl:
                dl_info = ydl_dl.extract_info(url, download=True)
                actual_title = dl_info.get('title', title)
                
                # Get file size
                files = list(DOWNLOAD_DIR.glob(f"{actual_title[:20]}*"))
                if not files:
                    files = list(DOWNLOAD_DIR.iterdir())
                    if files:
                        latest = max(files, key=os.path.getmtime)
                        size_mb = latest.stat().st_size / (1024 * 1024)
                    else:
                        size_mb = 0
                else:
                    size_mb = max(f.stat().st_size for f in files) / (1024 * 1024)
            
            print(f"\n{'='*50}")
            print(f"✅ DOWNLOADED!")
            print(f"🎵 {actual_title}")
            print(f"💾 {size_mb:.1f} MB")
            print(f"📁 Desktop/NCS_Songs/")
            print(f"{'='*50}\n")
            
            return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print()
    print("🎵 NCS RANDOM DOWNLOADER 🎵")
    print("   Har baar naya song!")
    print()
    
    success = download_random()
    
    if not success:
        print("\n🔄 Trying one more time with different query...")
        success = download_random()
    
    print("\n✅ Done! Double-click again for another random song!")
    input("\nPress Enter to exit...")