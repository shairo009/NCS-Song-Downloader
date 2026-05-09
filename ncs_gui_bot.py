"""
NCS GUI Downloader - Click & Download NCS Songs
Just click on any song to download instantly!
"""

import os
import re
import subprocess
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# Ensure yt-dlp is available
try:
    import yt_dlp
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp

# Colors
BG_DARK = "#1a1a2e"
BG_CARD = "#16213e"
BG_INPUT = "#0f3460"
ACCENT = "#e94560"
ACCENT_HOVER = "#ff6b81"
TEXT_WHITE = "#ffffff"
TEXT_GRAY = "#a0a0b0"
TEXT_GREEN = "#2ecc71"
PROGRESS_BG = "#0f3460"
PROGRESS_FILL = "#e94560"

# Download folder
DOWNLOAD_DIR = Path.home() / "Desktop" / "NCS_Songs"
DOWNLOAD_DIR.mkdir(exist_ok=True)

class NCSDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NCS Song Downloader")
        self.root.geometry("800x650")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(True, True)
        
        # Set icon if possible
        try:
            self.root.iconbitmap(default='')
        except:
            pass
        
        # Style configuration
        self.setup_styles()
        
        # Data
        self.search_results = []
        self.current_download = None
        self.download_queue = []
        self.is_downloading = False
        
        # Build UI
        self.build_ui()
        
        # Load initial results
        self.root.after(500, self.load_initial)
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", 
                       background=BG_CARD, 
                       foreground=TEXT_WHITE, 
                       fieldbackground=BG_CARD,
                       rowheight=40,
                       font=("Segoe UI", 11))
        style.configure("Treeview.Heading", 
                       background=BG_INPUT, 
                       foreground=TEXT_WHITE, 
                       font=("Segoe UI", 11, "bold"))
        style.map('Treeview', background=[('selected', ACCENT)])
        style.map('Treeview.Heading', background=[('active', BG_INPUT)])
    
    def build_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg=BG_DARK, pady=15)
        header_frame.pack(fill=tk.X)
        
        title = tk.Label(header_frame, text="🎵 NCS SONG DOWNLOADER", 
                        font=("Segoe UI", 22, "bold"), 
                        fg=ACCENT, bg=BG_DARK)
        title.pack()
        
        subtitle = tk.Label(header_frame, text="Click any song to download instantly!", 
                           font=("Segoe UI", 10), 
                           fg=TEXT_GRAY, bg=BG_DARK)
        subtitle.pack()
        
        # Search Frame
        search_frame = tk.Frame(self.root, bg=BG_DARK, pady=10, padx=20)
        search_frame.pack(fill=tk.X)
        
        # Search input with rounded look
        input_frame = tk.Frame(search_frame, bg=BG_INPUT, bd=0, highlightthickness=0)
        input_frame.pack(fill=tk.X)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_type)
        
        self.search_entry = tk.Entry(input_frame, textvariable=self.search_var,
                                     font=("Segoe UI", 14),
                                     bg=BG_INPUT, fg=TEXT_WHITE,
                                     insertbackground=TEXT_WHITE,
                                     bd=0, highlightthickness=0,
                                     relief=tk.FLAT)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=12, padx=(15, 5))
        self.search_entry.insert(0, "🔍  Search NCS songs...")
        self.search_entry.bind("<FocusIn>", self.on_search_focus)
        self.search_entry.bind("<FocusOut>", self.on_search_blur)
        self.search_entry.bind("<Return>", lambda e: self.search_songs())
        
        # Search button
        self.search_btn = tk.Button(input_frame, text="🔍 Search", 
                                    font=("Segoe UI", 11, "bold"),
                                    bg=ACCENT, fg=TEXT_WHITE,
                                    activebackground=ACCENT_HOVER,
                                    activeforeground=TEXT_WHITE,
                                    bd=0, padx=20, pady=8,
                                    cursor="hand2",
                                    command=self.search_songs)
        self.search_btn.pack(side=tk.RIGHT, padx=(5, 15))
        
        # Quick buttons frame
        quick_frame = tk.Frame(self.root, bg=BG_DARK, pady=5, padx=20)
        quick_frame.pack(fill=tk.X)
        
        self.latest_btn = tk.Button(quick_frame, text="🔥 Latest NCS", 
                                    font=("Segoe UI", 10),
                                    bg=BG_INPUT, fg=TEXT_WHITE,
                                    activebackground=ACCENT,
                                    activeforeground=TEXT_WHITE,
                                    bd=0, padx=15, pady=6,
                                    cursor="hand2",
                                    command=lambda: self.load_latest())
        self.latest_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.paste_btn = tk.Button(quick_frame, text="📋 Paste URL", 
                                   font=("Segoe UI", 10),
                                   bg=BG_INPUT, fg=TEXT_WHITE,
                                   activebackground=ACCENT,
                                   activeforeground=TEXT_WHITE,
                                   bd=0, padx=15, pady=6,
                                   cursor="hand2",
                                   command=self.paste_url_download)
        self.paste_btn.pack(side=tk.LEFT)
        
        self.downloads_btn = tk.Button(quick_frame, text="📂 Open Downloads", 
                                       font=("Segoe UI", 10),
                                       bg=BG_INPUT, fg=TEXT_WHITE,
                                       activebackground=ACCENT,
                                       activeforeground=TEXT_WHITE,
                                       bd=0, padx=15, pady=6,
                                       cursor="hand2",
                                       command=self.open_downloads)
        self.downloads_btn.pack(side=tk.RIGHT)
        
        # Results - Treeview Table
        list_frame = tk.Frame(self.root, bg=BG_DARK)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 0))
        
        # Create treeview
        columns = ('#', 'Title', 'Duration', 'Views')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', 
                                 height=10, selectmode='browse')
        
        self.tree.heading('#', text='#')
        self.tree.heading('Title', text='Song Title')
        self.tree.heading('Duration', text='Duration')
        self.tree.heading('Views', text='Views')
        
        self.tree.column('#', width=50, minwidth=40, anchor='center')
        self.tree.column('Title', width=450, minwidth=300)
        self.tree.column('Duration', width=100, minwidth=80, anchor='center')
        self.tree.column('Views', width=120, minwidth=80, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind click event
        self.tree.bind("<ButtonRelease-1>", self.on_song_click)
        self.tree.bind("<Double-1>", self.on_song_click)
        
        # Status/Progress bar
        status_frame = tk.Frame(self.root, bg=BG_DARK, padx=20, pady=(5, 10))
        status_frame.pack(fill=tk.X)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='determinate', 
                                        length=760, style='')
        self.progress.pack(fill=tk.X, pady=(0, 5))
        self.progress.pack_forget()  # Hidden initially
        
        # Status label
        self.status_label = tk.Label(status_frame, text="Ready ✓", 
                                     font=("Segoe UI", 10),
                                     fg=TEXT_GREEN, bg=BG_DARK, anchor='w')
        self.status_label.pack(fill=tk.X)
        
        # Result label (shows download complete)
        self.result_label = tk.Label(status_frame, text="", 
                                     font=("Segoe UI", 10),
                                     fg=ACCENT, bg=BG_DARK, anchor='w')
        self.result_label.pack(fill=tk.X)
        
        # Bind hover effects for buttons
        for btn in [self.search_btn, self.latest_btn, self.paste_btn, self.downloads_btn]:
            orig_bg = btn.cget('bg')
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=ACCENT_HOVER))
            btn.bind("<Leave>", lambda e, b=btn, obg=orig_bg: b.configure(bg=obg))
    
    def on_search_focus(self, event):
        if self.search_entry.get() == "🔍  Search NCS songs...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.configure(fg=TEXT_WHITE)
    
    def on_search_blur(self, event):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "🔍  Search NCS songs...")
            self.search_entry.configure(fg=TEXT_GRAY)
    
    def on_search_type(self, *args):
        pass  # We'll search on button click or Enter
    
    def set_status(self, text, color=TEXT_GREEN):
        self.status_label.configure(text=text, fg=color)
        self.root.update_idletasks()
    
    def set_result(self, text):
        self.result_label.configure(text=text)
        self.root.after(5000, lambda: self.result_label.configure(text=""))
    
    def show_progress(self):
        self.progress.pack(fill=tk.X, pady=(0, 5))
        self.progress['value'] = 0
    
    def hide_progress(self):
        self.progress.pack_forget()
        self.progress['value'] = 0
    
    def load_initial(self):
        self.set_status("⏳ Loading latest NCS releases...", TEXT_GRAY)
        self.root.after(100, self.load_latest)
    
    def load_latest(self):
        self.search_var.set("")
        self.search_songs_custom("ncs release", limit=20)
    
    def search_songs(self):
        query = self.search_entry.get().strip()
        if not query or query == "🔍  Search NCS songs...":
            messagebox.showinfo("Search", "Please enter a song name to search!")
            return
        self.search_songs_custom(query)
    
    def search_songs_custom(self, query, limit=20):
        self.set_status(f"🔍 Searching for '{query}'...", TEXT_GRAY)
        self.clear_results()
        
        # Auto-add NCS if not in query
        if not any(kw in query.lower() for kw in ['ncs', 'nocopyright']):
            query = query + " ncs"
        
        # Run search in thread
        thread = threading.Thread(target=self._do_search, args=(query, limit), daemon=True)
        thread.start()
    
    def _do_search(self, query, limit):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            search_query = f"ytsearch{limit}:{query}"
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_query, download=False)
                
                results = []
                if 'entries' in info:
                    for i, entry in enumerate(info['entries'], 1):
                        if entry and entry.get('id'):
                            views = entry.get('view_count', 0)
                            duration = entry.get('duration', 0)
                            
                            # Format views
                            if views >= 1000000:
                                views_str = f"{views/1000000:.1f}M"
                            elif views >= 1000:
                                views_str = f"{views/1000:.1f}K"
                            else:
                                views_str = str(views)
                            
                            # Format duration
                            if duration:
                                m, s = divmod(int(duration), 60)
                                h, m = divmod(m, 60)
                                if h > 0:
                                    dur_str = f"{h}:{m:02d}:{s:02d}"
                                else:
                                    dur_str = f"{m}:{s:02d}"
                            else:
                                dur_str = "??:??"
                            
                            results.append({
                                'id': entry.get('id', ''),
                                'title': entry.get('title', 'Unknown'),
                                'url': f"https://youtube.com/watch?v={entry.get('id', '')}",
                                'duration': dur_str,
                                'views': views_str,
                                'channel': entry.get('channel', ''),
                                'duration_sec': duration,
                            })
                
                self.root.after(0, self._display_results, results)
        
        except Exception as e:
            self.root.after(0, lambda: self.set_status(f"❌ Search error: {e}", ACCENT))
    
    def _display_results(self, results):
        self.clear_results()
        
        if not results:
            self.set_status("❌ No results found! Try a different search.", ACCENT)
            return
        
        self.search_results = results
        
        for i, r in enumerate(results, 1):
            title = r['title'][:55] + '...' if len(r['title']) > 55 else r['title']
            self.tree.insert('', tk.END, values=(i, title, r['duration'], r['views']))
        
        self.set_status(f"✅ Found {len(results)} songs - Click any to download!")
    
    def clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.search_results = []
    
    def on_song_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = selected[0]
        values = self.tree.item(item, 'values')
        
        if not values:
            return
        
        idx = int(values[0]) - 1
        if 0 <= idx < len(self.search_results):
            self.download_song(self.search_results[idx])
    
    def download_song(self, song_info):
        if self.is_downloading:
            self.download_queue.append(song_info)
            self.set_status(f"⏳ Queued: {song_info['title'][:30]}...", TEXT_GRAY)
            return
        
        self.is_downloading = True
        self.set_status(f"⬇️ Downloading: {song_info['title'][:40]}...", ACCENT)
        self.show_progress()
        
        thread = threading.Thread(target=self._do_download, args=(song_info,), daemon=True)
        thread.start()
    
    def _do_download(self, song_info):
        url = song_info['url']
        title = song_info['title']
        
        def progress_hook(d):
            if d['status'] == 'downloading':
                try:
                    total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                    downloaded = d.get('downloaded_bytes', 0)
                    if total > 0:
                        percent = int(downloaded * 100 / total)
                        self.root.after(0, lambda p=percent: self.progress.configure(value=p))
                except:
                    pass
            elif d['status'] == 'finished':
                self.root.after(0, lambda: self.progress.configure(value=100))
        
        # Check ffmpeg
        ffmpeg_available = False
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            ffmpeg_available = True
        except:
            pass
        
        if ffmpeg_available:
            fmt = 'bestaudio[ext=m4a]/bestaudio'
            post = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'm4a'}]
        else:
            fmt = 'bestaudio[ext=webm]/bestaudio'
            post = []
        
        ydl_opts = {
            'format': fmt,
            'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook],
            'postprocessors': post,
            'embedthumbnail': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                actual_title = info.get('title', title)
                
                # Find the downloaded file
                files = list(DOWNLOAD_DIR.glob(f"{actual_title[:30]}*"))
                if not files:
                    files = list(DOWNLOAD_DIR.glob("*"))
                    files = [f for f in files if f.stat().st_size > 100000]  # >100KB
                
                file_size = "unknown"
                if files:
                    latest = max(files, key=os.path.getmtime)
                    size_mb = latest.stat().st_size / (1024 * 1024)
                    file_size = f"{size_mb:.1f} MB"
            
            self.root.after(0, lambda t=actual_title, s=file_size: self._download_complete(t, s))
        
        except Exception as e:
            self.root.after(0, lambda e=e: self._download_failed(str(e)))
    
    def _download_complete(self, title, file_size):
        self.is_downloading = False
        self.hide_progress()
        self.set_status(f"✅ Downloaded: {title}", TEXT_GREEN)
        self.set_result(f"✅ Complete! '{title}' saved to Desktop/NCS_Songs ({file_size})")
        self.check_queue()
    
    def _download_failed(self, error):
        self.is_downloading = False
        self.hide_progress()
        self.set_status(f"❌ Download failed", ACCENT)
        self.set_result(f"❌ Error: {error}")
        self.check_queue()
    
    def check_queue(self):
        if self.download_queue:
            next_song = self.download_queue.pop(0)
            self.root.after(500, lambda: self.download_song(next_song))
    
    def paste_url_download(self):
        """Download from URL"""
        url = self.root.clipboard_get()
        if not url or not (url.startswith('http://') or url.startswith('https://')):
            # Ask user to paste manually
            dialog = tk.Toplevel(self.root)
            dialog.title("Download from URL")
            dialog.geometry("500x150")
            dialog.configure(bg=BG_DARK)
            dialog.transient(self.root)
            dialog.grab_set()
            
            tk.Label(dialog, text="Paste YouTube URL:", 
                    font=("Segoe UI", 12), fg=TEXT_WHITE, bg=BG_DARK).pack(pady=(20, 10))
            
            url_var = tk.StringVar()
            url_entry = tk.Entry(dialog, textvariable=url_var, 
                               font=("Segoe UI", 12),
                               bg=BG_INPUT, fg=TEXT_WHITE,
                               insertbackground=TEXT_WHITE,
                               bd=0, highlightthickness=0)
            url_entry.pack(fill=tk.X, padx=20, ipady=8)
            url_entry.focus()
            
            def download_from_entry():
                url = url_var.get().strip()
                dialog.destroy()
                if url and ('youtube.com' in url or 'youtu.be' in url):
                    song_info = {
                        'id': url.split('v=')[-1] if 'v=' in url else url.split('/')[-1],
                        'title': f"URL: {url[:40]}...",
                        'url': url,
                        'duration': '??:??',
                        'views': 'N/A',
                        'channel': 'YouTube',
                    }
                    self.download_song(song_info)
                else:
                    messagebox.showerror("Error", "Please paste a valid YouTube URL!")
            
            tk.Button(dialog, text="⬇️ Download", 
                     font=("Segoe UI", 11, "bold"),
                     bg=ACCENT, fg=TEXT_WHITE,
                     activebackground=ACCENT_HOVER,
                     activeforeground=TEXT_WHITE,
                     bd=0, padx=20, pady=8,
                     cursor="hand2",
                     command=download_from_entry).pack(pady=15)
            
            url_entry.bind("<Return>", lambda e: download_from_entry())
            return
        
        # If clipboard has URL
        if 'youtube.com' in url or 'youtu.be' in url:
            song_info = {
                'id': url.split('v=')[-1] if 'v=' in url else url.split('/')[-1],
                'title': f"URL: {url[:40]}...",
                'url': url,
                'duration': '??:??',
                'views': 'N/A',
                'channel': 'YouTube',
            }
            self.download_song(song_info)
        else:
            messagebox.showerror("Error", "Clipboard doesn't contain a valid YouTube URL!")
    
    def open_downloads(self):
        os.startfile(str(DOWNLOAD_DIR))


def main():
    root = tk.Tk()
    app = NCSDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()