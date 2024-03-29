import tkinter as tk
from tkinter import messagebox, ttk
import sv_ttk
from yt_dlp import YoutubeDL
import threading
import os
import subprocess
import platform

class VideoDownloaderApp:
    quality_options = ["Default (1080p)", "High (1440p)", "4K (2160p)"]

    def __init__(self, root):
        self.root = root
        sv_ttk.set_theme("dark")
        self.failed_videos = []
        self.setup_ui()

    # ----------------- UI Setup Methods ----------------- #
    def setup_ui(self):
        self.setup_style()
        self.root.title("ADL | by dgside")
        self.create_frames()
        self.create_url_entry()
        self.create_options()
        self.create_control_buttons()
        self.create_progress_bar()
        self.create_status_label()

    def setup_style(self):
        style = ttk.Style()
        style.configure('Border.TFrame', borderwidth=2, relief="solid")
        style.configure('Border.TFrame', background='#333333')

    def create_frames(self):
        self.url_frame = ttk.Labelframe(self.root, text=" Video URL ")
        self.url_frame.pack(pady=(5, 5), padx=(5, 5), fill='x')
    
        self.options_frame = ttk.Labelframe(self.root, text=" Options ")
        self.options_frame.pack(pady=(5, 5), padx=(5, 5), fill='x')

        self.control_frame = ttk.Labelframe(self.root, text=" Actions ")
        self.control_frame.pack(pady=(5, 5), padx=(5, 5), fill='x')

    def create_url_entry(self):
        self.url_entry = ttk.Entry(self.url_frame, width=50)
        self.url_entry.pack(padx=10, pady=10)
        self.url_entry_var = tk.StringVar()
        self.url_entry["textvariable"] = self.url_entry_var
        self.url_entry_var.trace("w", lambda name, index, mode, sv=self.url_entry_var: self.fetch_video_info())
        self.create_right_click_menu(self.url_entry)
        self.url_entry.bind("<Button-3>", self.show_right_click_menu)

        self.video_title_label = ttk.Label(self.url_frame, text="", foreground="white")
        self.video_title_label.pack(pady=(5, 5))

    def create_options(self):
        self.audio_only_var = tk.IntVar()
        audio_only_checkbox = ttk.Checkbutton(self.options_frame, text="Audio Only", variable=self.audio_only_var)
        audio_only_checkbox.pack(side='left', padx=(10, 20))
        self.quality_var = tk.StringVar(value=self.quality_options[0])
        style = ttk.Style(self.root)
        style.configure('Default.TButton', foreground='#baffc9')
        style.configure('High.TButton', foreground='#ffdfba')
        style.configure('Ultra.TButton', foreground='#ffb3ba')

        # Create a frame within the options frame to hold the quality buttons
        self.quality_buttons_frame = ttk.Frame(self.options_frame)
        self.quality_buttons_frame.pack(side='right', padx=(10, 20), pady=(10, 10))

        # Create buttons for each quality option
        self.default_quality_button = ttk.Button(self.quality_buttons_frame, text="Default (1080p)", style='Default.TButton', command=lambda: self.set_quality("Default (1080p)"))
        self.default_quality_button.pack(side='left', padx=(0, 5))

        self.high_quality_button = ttk.Button(self.quality_buttons_frame, text="High (1440p)", style='High.TButton', command=lambda: self.set_quality("High (1440p)"))
        self.high_quality_button.pack(side='left', padx=5)

        self.ultra_quality_button = ttk.Button(self.quality_buttons_frame, text="4K (2160p)", style='Ultra.TButton', command=lambda: self.set_quality("4K (2160p)"))
        self.ultra_quality_button.pack(side='left', padx=(5, 0))


        # Initially set default quality button as selected
        self.set_quality("Default (1080p)")

    def set_quality(self, quality):
        self.quality_var.set(quality)
        # Update button states to reflect current selection
        for button in [self.default_quality_button, self.high_quality_button, self.ultra_quality_button]:
            button.state(['!alternate'])  # Reset the state
        if quality == "Default (1080p)":
            self.default_quality_button.state(['alternate'])
        elif quality == "High (1440p)":
            self.high_quality_button.state(['alternate'])
        elif quality == "4K (2160p)":
            self.ultra_quality_button.state(['alternate'])   

    def create_control_buttons(self):
        self.download_button = ttk.Button(self.control_frame, text="Download", command=self.start_download)
        self.download_button.pack(side='left', padx=(10, 5), pady=(10, 10), expand=False)

    def create_progress_bar(self):
        self.progress = ttk.Progressbar(self.control_frame, length=200, mode='determinate', maximum=100)
        self.progress.pack(padx=10, pady=10, fill='x', expand=True)

    def create_status_label(self):
        self.status_label = ttk.Label(self.control_frame, text="")
        self.status_label.pack(pady=(5, 5))

    # ----------------- Right Click Menu Methods ----------------- #
    def create_right_click_menu(self, widget):
        self.right_click_menu = tk.Menu(widget, tearoff=0)
        self.right_click_menu.add_command(label="Paste", command=lambda: widget.event_generate('<<Paste>>'))
        widget.bind("<Button-3>", self.show_right_click_menu)

    def show_right_click_menu(self, event):
        try:
            self.right_click_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.right_click_menu.grab_release()

    # ----------------- Video Fetching Methods ----------------- #
    def fetch_video_info(self):
        url = self.url_entry_var.get()
        if not url.strip():
            self.video_title_label.config(text="")
            return
        threading.Thread(target=self.retrieve_video_title, args=(url,), daemon=True).start()

    def retrieve_video_title(self, url):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'skip_download': True,
            'extract_flat': 'in_playlist',
            'force_generic_extractor': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(url, download=False)
                title = info_dict.get('title', 'Video title not found')
                self.root.after(0, lambda: self.video_title_label.config(text=title))
            except Exception as e:
                self.root.after(0, lambda: self.video_title_label.config(text=f"Error retrieving video info: {str(e)}"))

    # ----------------- Download Methods ----------------- #
    def start_download(self):
        if "playlist" in self.url_entry.get() and not self.confirm_playlist_download():
            return
        self.download_button["state"] = "disabled"
        self.progress["value"] = 0
        self.status_label["text"] = "Starting download..."
        threading.Thread(target=self.download_video, daemon=True).start()

    def confirm_playlist_download(self):
        return messagebox.askyesno("Download Playlist", "You're about to download an entire playlist. This may include a large number of videos. Do you want to continue?")

    def download_video(self):
        url = self.url_entry.get()
        audio_only = self.audio_only_var.get()
        quality = self.quality_var.get()
        ydl_opts = self.get_download_options(audio_only, quality)
        ydl_opts['progress_hooks'] = [self.progress_hook]

        with YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text=f"Download failed: {str(e)}"))
                return

        self.root.after(0, self.finalize_download)

    def progress_hook(self, d):
        if d['status'] == 'finished':
            self.root.after(0, lambda: self.status_label.config(text="Download finished"))
        elif d['status'] == 'downloading':
            bytes_downloaded = d['downloaded_bytes']
            bytes_total = d.get('total_bytes') or d.get('total_bytes_estimate')
            if bytes_total:
                percentage = int(bytes_downloaded / bytes_total * 100)
                self.root.after(0, lambda: (self.progress.config(value=percentage), self.status_label.config(text=f"Downloading... {percentage}%")))

    def finalize_download(self):
        self.progress['value'] = 100
        self.download_button["state"] = "normal"
        self.url_entry.delete(0, tk.END)

    # ----------------- Download Options Methods ----------------- #
    def get_download_options(self, audio_only, quality):
        format_option = self.format_by_quality(quality, audio_only)
        download_options = {
            'format': format_option,
            'outtmpl': self.output_template(audio_only),
            'ignoreerrors': True,
            'no_warnings': True,
            'quiet': True
        }
        if audio_only:
            download_options['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }]
        return download_options

    def format_by_quality(self, quality, audio_only):
        if audio_only:
            return 'bestaudio/best'
        return {
            "Default (1080p)": 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            "High (1440p)": 'bestvideo[height<=1440]+bestaudio/best[height<=1440]',
            "4K (2160p)": 'bestvideo[height<=2160]+bestaudio/best[height<=2160]'
        }[quality]

    def output_template(self, audio_only):
        return 'audio/%(title)s.%(ext)s' if audio_only else 'videos/%(title)s.%(ext)s'
    
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()
