"""
GitHub Actions: Random NCS Song Downloader
Directly from NCS website AWS S3 - NO YouTube needed!
"""

import urllib.request
import re
import random
import os

# Known NCS track IDs (latest tracks from the website)
# These are fetched dynamically from NCS site
# Fallback direct links if site scrape fails
FALLBACK_TRACKS = [
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/095/ascend-1778112066-nZIUxvdw4b.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/094/anesthesia-1777986065-3JLflZOAtD.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/091/be-there-with-u-1777507266-8IFhcw6MJC.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/090/back2u-1777474865-KiepxHUuGa.wav",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/089/shotgun-1776988869-Edp70qsLNl.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/088/voyage-1776902473-ayHnu2narR.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/087/whenyoufindout-1776384070-hsvQOv0c3w.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/086/cerberus-1776297674-Rclxs9JEZO.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/085/devaste-1776124870-yRL6Tb0bhg.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/080/colors-1775088076-j9QxNfMR1j.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/078/1774950915_QZCgZJgVdk_Money-Mouth-NCS-Release.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/076/raindrops-1774573266-aRJwywY8I1.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/075/1774616894_j4U1Z0pRWE_Slip-Thru-NCS-Release.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/074/pull-me-down-1773968470-0WG1VhGXTH.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/073/shut-em-down-1773876069-M0r3MfNvFU.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/072/all-i-want-1773792068-1bp5v3O5hA.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/071/cosmos-1773523266-ArY5GxOCMh.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/070/undefeated-1773364865-LwSW7h77HS.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/069/daydream-1773206465-k6AWBj5Q1j.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/003/favela-1762477273-EdjAqE9a7B.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/001/848/harinezumi-1739530854-Dz5HzYsUJ1.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/001/908/stuck-in-my-head-1749772863-rPqCNSW3oe.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/002/020/alex-hagen-superhero-1765328465-LA31zzAZNoU.mp3",
    "https://ncsmusic.s3.eu-west-1.amazonaws.com/tracks/000/001/952/fearless-funk-1755597664-wxNklTHR1R.mp3",
]

def scrape_ncs_page():
    """Scrape NCS music page for download links"""
    try:
        url = 'https://ncs.io/music?genre=All&sort=latest'
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='replace')
        
        # Extract S3 URLs
        links = re.findall(r'https://ncsmusic\.s3\.eu-west-1\.amazonaws\.com/[^"\'<>]+\.(?:mp3|wav|flac|m4a)', html)
        unique = list(set(links))
        print(f"  Scraped {len(unique)} tracks from NCS site")
        return unique
    except Exception as e:
        print(f"  Scrape failed: {str(e)[:60]}, using fallback")
        return []

def get_track_name_from_url(url):
    """Extract track name from URL"""
    # URL format: .../tracks/000/001/908/stuck-in-my-head-1749772863-rPqCNSW3oe.mp3
    filename = url.rstrip('/').split('/')[-1]
    # Remove extension
    name = re.sub(r'\.\w+$', '', filename)
    # Remove timestamp hash at end (e.g., -1749772863-rPqCNSW3oe)
    name = re.sub(r'-\d{10}-[A-Za-z0-9]+$', '', name)
    # Replace dashes/underscores with spaces
    name = name.replace('-', ' ').replace('_', ' ')
    # Clean up
    name = ' '.join(word for word in name.split() if not word.isdigit() or len(word) < 8)
    return name if name.strip() else "NCS Song"

def download_file(url):
    """Download a file from URL"""
    name = get_track_name_from_url(url)
    ext = url.rstrip('/').split('.')[-1].split('?')[0]
    if ext not in ['mp3', 'wav', 'm4a', 'flac']:
        ext = 'mp3'
    
    output = f"ncs_song.{ext}"
    
    print(f"  🎧 {name[:50]}")
    print(f"  ⬇️ Downloading...")
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
        resp = urllib.request.urlopen(req, timeout=120)
        
        total = 0
        with open(output, 'wb') as f:
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                f.write(chunk)
                total += len(chunk)
        
        if total > 50000:
            print(f"  ✅ Success! {total:,} bytes ({total/1024/1024:.1f} MB)")
            return True, name, total
        else:
            print(f"  ⚠️ Too small: {total} bytes")
            if os.path.exists(output):
                os.remove(output)
            return False, name, 0
    except Exception as e:
        print(f"  ❌ {str(e)[:70]}")
        if os.path.exists(output):
            os.remove(output)
        return False, name, 0

# ============ MAIN ============
print("🎵 NCS Song Downloader (from NCS S3)")
print()

# Get tracks
all_tracks = scrape_ncs_page()
if len(all_tracks) < 5:
    all_tracks = FALLBACK_TRACKS

random.shuffle(all_tracks)
print(f"  Total tracks: {len(all_tracks)}")

# Try tracks until one works
for i, track_url in enumerate(all_tracks, 1):
    print(f"\n[{i}/{len(all_tracks)}]")
    success, name, size = download_file(track_url)
    if success:
        # Save info
        with open("song_title.txt", "w") as f:
            f.write(f"Song: {name}\n")
            f.write(f"URL: {track_url}\n")
            f.write(f"Size: {size} bytes\n")
        print(f"\n✅ Done! Song ready in artifacts!")
        exit(0)

print("\n❌ All downloads failed!")
with open("song_title.txt", "w") as f:
    f.write("Song: all_downloads_failed\nStatus: FAILED\n")
exit(1)