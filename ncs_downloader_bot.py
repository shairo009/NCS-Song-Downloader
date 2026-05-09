"""
NCS (No Copyright Sounds) Song Downloader Bot
Downloads NCS songs from YouTube in best quality
"""

import os
import re
import subprocess
import sys
from pathlib import Path

# Try to import yt-dlp, install if not available
try:
    import yt_dlp
except ImportError:
    print("yt-dlp not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp

# Colors for terminal
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
RESET = "\033[0m"

# Download folder - creates "NCS_Songs" on Desktop
DOWNLOAD_DIR = Path.home() / "Desktop" / "NCS_Songs"
DOWNLOAD_DIR.mkdir(exist_ok=True)

# NCS channel URL
NCS_CHANNEL_URL = "https://www.youtube.com/@NoCopyrightSounds"

# Common NCS keywords for search
NCS_KEYWORDS = [
    "ncs", "nocopyrightsounds", "no copyright sounds",
    "ncs release", "ncs music"
]

def print_banner():
    """Print a cool banner"""
    banner = f"""
{CYAN}╔══════════════════════════════════════╗
║     🎵 NCS SONG DOWNLOADER BOT 🎵    ║
║     No Copyright Sounds Downloader    ║
╚══════════════════════════════════════╝{RESET}
    """
    print(banner)

def clean_filename(title):
    """Remove invalid characters from filename"""
    return re.sub(r'[<>:"/\\|?*]', '', title).strip()[:100]

def search_ncs(query, limit=10):
    """Search for NCS songs on YouTube"""
    print(f"{YELLOW}🔍 Searching for: '{query}'...{RESET}")
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'force_generic_extractor': False,
    }
    
    search_query = f"ytsearch{limit}:{query}"
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            results = []
            
            if 'entries' in info:
                for i, entry in enumerate(info['entries'], 1):
                    if entry:
                        results.append({
                            'id': entry.get('id', ''),
                            'title': entry.get('title', 'Unknown Title'),
                            'url': f"https://youtube.com/watch?v={entry.get('id', '')}",
                            'duration': entry.get('duration', 0),
                            'channel': entry.get('channel', 'Unknown'),
                            'views': entry.get('view_count', 0),
                        })
            
            return results
    except Exception as e:
        print(f"{RED}❌ Search error: {e}{RESET}")
        return []

def format_duration(seconds):
    """Convert seconds to mm:ss format"""
    if not seconds:
        return "??:??"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{m:02d}:{s:02d}"

def display_results(results):
    """Display search results nicely"""
    if not results:
        print(f"{RED}❌ No results found!{RESET}")
        return
    
    print(f"\n{CYAN}📋 Search Results:{RESET}")
    print(f"{'─' * 70}")
    
    for i, r in enumerate(results, 1):
        title_short = r['title'][:50] + '...' if len(r['title']) > 50 else r['title']
        duration = format_duration(r['duration'])
        print(f"{GREEN}{i:2d}.{RESET} {title_short}")
        print(f"     ⏱ {duration}  |  📺 {r['channel'][:25]:25s}  |  👁 {r['views']:,}")
    
    print(f"{'─' * 70}")

def get_best_thumbnail(video_id):
    """Get best quality thumbnail URL"""
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

def download_song(url, quality='best'):
    """Download song in best quality"""
    print(f"\n{YELLOW}⬇️  Downloading...{RESET}")
    
    # Progress hook
    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', '').strip()
            eta = d.get('_eta_str', '').strip()
            print(f"\r{YELLOW}📥 {percent} at {speed} ETA: {eta}{RESET}", end='', flush=True)
        elif d['status'] == 'finished':
            print(f"\n{GREEN}✅ Download complete! Processing...{RESET}")
    
    # Check for ffmpeg
    ffmpeg_available = False
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        ffmpeg_available = True
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # Best audio format
    if ffmpeg_available:
        # Best quality audio (opus) converted to m4a
        format_spec = 'bestaudio[ext=m4a]/bestaudio'
        postprocessors = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }]
        print(f"{CYAN}ℹ️  ffmpeg detected - downloading highest quality audio{RESET}")
    else:
        # Without ffmpeg, download best compatible audio
        format_spec = 'bestaudio[ext=webm]/bestaudio'
        postprocessors = []
        print(f"{YELLOW}⚠️  ffmpeg not found - downloading webm audio (still high quality){RESET}")
    
    ydl_opts = {
        'format': format_spec,
        'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [progress_hook],
        'postprocessors': postprocessors,
        'embedthumbnail': True,
        'embedsubtitles': True,
        'writethumbnail': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Unknown')
            filename = ydl.prepare_filename(info)
            
            # Get actual filename after processing
            if ffmpeg_available:
                base = Path(filename).stem
                actual_file = DOWNLOAD_DIR / f"{base}.m4a"
            else:
                actual_file = Path(filename)
            
            # If m4a doesn't exist, find the actual file
            if not actual_file.exists():
                # Find any recent file in download dir
                files = list(DOWNLOAD_DIR.glob("*"))
                if files:
                    actual_file = max(files, key=os.path.getmtime)
            
            file_size = actual_file.stat().st_size / (1024 * 1024)  # MB
            
            print(f"\n{GREEN}✅ SUCCESS!{RESET}")
            print(f"📁 File:     {actual_file.name}")
            print(f"📂 Location: {DOWNLOAD_DIR}")
            print(f"💾 Size:     {file_size:.2f} MB")
            print(f"🎵 Title:    {title}")
            
            return actual_file
    
    except Exception as e:
        print(f"\n{RED}❌ Download failed: {e}{RESET}")
        return None

def get_latest_ncs_songs(limit=10):
    """Get latest NCS releases"""
    print(f"{YELLOW}🔍 Fetching latest NCS releases...{RESET}")
    return search_ncs("ncs release", limit)

def interactive_mode():
    """Run the bot in interactive mode"""
    print_banner()
    
    while True:
        print(f"\n{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"{GREEN}🎵 NCS Song Downloader Bot 🎵{RESET}")
        print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"📁 Saving to: {DOWNLOAD_DIR}")
        print(f"\nOptions:")
        print(f"  {GREEN}1{RESET}. 🔍 Search NCS song")
        print(f"  {GREEN}2{RESET}. 📥 Download from YouTube URL")
        print(f"  {GREEN}3{RESET}. 🔥 Latest NCS releases")
        print(f"  {GREEN}4{RESET}. ℹ️  About")
        print(f"  {GREEN}5{RESET}. ❌ Exit")
        
        choice = input(f"\n{YELLOW}👉 Choose option (1-5): {RESET}").strip()
        
        if choice == '1':
            query = input(f"{YELLOW}🔍 Search for: {RESET}").strip()
            if not query:
                print(f"{RED}Please enter a search term!{RESET}")
                continue
            
            # Auto-add NCS if not already in query
            if not any(kw in query.lower() for kw in ['ncs', 'nocopyright']):
                query = query + " ncs"
            
            results = search_ncs(query)
            display_results(results)
            
            if results:
                try:
                    choice = input(f"\n{YELLOW}👉 Select song number to download (1-{len(results)}), or 0 to skip: {RESET}").strip()
                    idx = int(choice) - 1
                    if 0 <= idx < len(results):
                        download_song(results[idx]['url'])
                except (ValueError, IndexError):
                    print(f"{RED}Invalid choice!{RESET}")
        
        elif choice == '2':
            url = input(f"{YELLOW}🔗 Enter YouTube URL: {RESET}").strip()
            if url:
                download_song(url)
            else:
                print(f"{RED}Please enter a URL!{RESET}")
        
        elif choice == '3':
            results = get_latest_ncs_songs(15)
            display_results(results)
            
            if results:
                try:
                    choice = input(f"\n{YELLOW}👉 Select song number to download (1-{len(results)}), or 0 to skip: {RESET}").strip()
                    idx = int(choice) - 1
                    if 0 <= idx < len(results):
                        download_song(results[idx]['url'])
                except (ValueError, IndexError):
                    print(f"{RED}Invalid choice!{RESET}")
        
        elif choice == '4':
            print(f"\n{CYAN}ℹ️  About NCS Downloader Bot{RESET}")
            print(f"{'─' * 40}")
            print(f"NCS (No Copyright Sounds) is a label that releases")
            print(f"copyright-free music. This bot downloads their songs")
            print(f"from YouTube in the highest available quality.")
            print(f"\n📁 Downloads saved to: {DOWNLOAD_DIR}")
            print(f"\n{GREEN}✅ All downloads are for personal use only!{RESET}")
        
        elif choice == '5':
            print(f"\n{GREEN}👋 Thanks for using NCS Downloader Bot! Bye!{RESET}")
            break
        
        else:
            print(f"{RED}❌ Invalid option! Please choose 1-5.{RESET}")

def quick_download(query):
    """Quick download without interactive mode"""
    print_banner()
    
    # Check if it's a URL
    if query.startswith('http://') or query.startswith('https://'):
        if 'youtube.com' in query or 'youtu.be' in query:
            download_song(query)
        else:
            print(f"{RED}❌ Please provide a YouTube URL{RESET}")
    else:
        results = search_ncs(query)
        display_results(results)
        if results:
            download_song(results[0]['url'])

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Command line mode: python ncs_downloader_bot.py "song name"
        quick_download(' '.join(sys.argv[1:]))
    else:
        # Interactive mode
        try:
            interactive_mode()
        except KeyboardInterrupt:
            print(f"\n\n{GREEN}👋 Goodbye!{RESET}")
        except Exception as e:
            print(f"\n{RED}❌ Error: {e}{RESET}")
