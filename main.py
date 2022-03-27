import subprocess
from re import sub
from gui import GUI
from uuid import uuid4
from pytube import YouTube
from os import path, remove
from threading import Thread
from tempfile import gettempdir
from string import ascii_letters, digits
from tkinter import messagebox, filedialog
from pytube.exceptions import VideoUnavailable, RegexMatchError

filename = None
streams = None
processing_video = False
downloaded_audio_file = None
downloaded_video_file = None
user_download_folder = path.join(path.expanduser("~"), "Downloads")
user_temp_folder = gettempdir()


def load_streams():
    global streams, filename
    try:
        yt = YouTube(gui.entry_url.get(), on_complete_callback=download_complete)
    except VideoUnavailable:
        messagebox.showinfo(master=gui, title="ERROR", message="This video is not available.")
    except RegexMatchError:
        messagebox.showinfo(master=gui, title="ERROR", message="Invalid YouTube URL.")
    else:
        streams = yt.streams
        filename = sanitize_filename(yt.title)
        change_download_buttons_state("active")
        update_status("")


# noinspection PyUnresolvedReferences
def download_video():
    global processing_video, downloaded_video_file, downloaded_audio_file
    processing_video = True
    downloaded_video_file = None
    downloaded_audio_file = None
    selected_video_stream = streams.filter(type="video").order_by("resolution").last()
    download_stream_thread(selected_video_stream)


# noinspection PyUnresolvedReferences
def download_audio():
    global processing_video, downloaded_audio_file
    processing_video = False
    downloaded_audio_file = None
    selected_audio_stream = streams.filter(type="audio").order_by("abr").last()
    download_stream_thread(selected_audio_stream)


def download_stream_thread(stream):
    update_status("Downloading...")

    def download_stream():
        stream.download(output_path=user_temp_folder, filename=str(uuid4()))

    thread = Thread(target=download_stream)
    thread.start()
    change_download_buttons_state("disabled")


def browse_button():
    folder = filedialog.askdirectory().replace("/", "\\")
    gui.entry_folder.delete(0, "end")
    gui.entry_folder.insert(0, folder)


def change_download_buttons_state(state):
    gui.video_button.config(state=state)
    gui.audio_button.config(state=state)


# noinspection PyUnresolvedReferences
def download_complete(*args):
    global downloaded_video_file, downloaded_audio_file
    if processing_video:
        if downloaded_video_file is None:
            downloaded_video_file = args[1]
            selected_stream = streams.filter(type="audio").order_by("abr").last()
            download_stream_thread(selected_stream)
        else:
            downloaded_audio_file = args[1]
            convert(input_video_file=downloaded_video_file, input_audio_file=downloaded_audio_file)
    else:
        downloaded_audio_file = args[1]
        convert(input_audio_file=downloaded_audio_file)


# noinspection PyUnresolvedReferences
def convert(**kwargs):
    update_status("Converting...")
    if processing_video:
        output_file = f"{gui.entry_folder.get()}\\{filename}.mp4"
        cmd = ["ffmpeg", "-n", "-i", kwargs.get("input_video_file"), "-i", kwargs.get("input_audio_file"), "-c:v",
               "copy", "-c:a", "aac", output_file]
    else:
        output_file = f"{gui.entry_folder.get()}\\{filename}.mp3"
        cmd = ["ffmpeg", "-n", "-i", kwargs.get("input_audio_file"), "-c:a", "libmp3lame", output_file]
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    if process.returncode != 0:
        error_message = process.stdout.split('\n')[-2].strip()
        update_status(f"Failed to convert. ERROR: {error_message}")
    else:
        update_status(f"Downloaded to: {output_file}")
    change_download_buttons_state("active")
    if processing_video:
        remove(kwargs.get("input_video_file"))
    remove(kwargs.get("input_audio_file"))


def sanitize_filename(file_name):
    valid_chars = f"-_.() {ascii_letters}{digits}"
    file_name = file_name.replace("|", "-")
    file_name = ''.join(c for c in file_name if c in valid_chars)
    return sub(' +', ' ', file_name)


def update_status(status_text):
    gui.status_text.config(text=status_text)


if __name__ == '__main__':
    gui = GUI()
    gui.entry_folder.insert(0, user_download_folder)
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except FileNotFoundError:
        messagebox.showerror(master=gui, title="ERROR", message="ffmpeg is required to run this application. Please "
                                                                "download and install it from https://github.com/BtbN"
                                                                "/FFmpeg-Builds/releases")
        gui.quit()
    else:
        gui.button_load.config(command=load_streams)
        gui.button_folder.config(command=browse_button)
        gui.video_button.config(command=download_video)
        gui.audio_button.config(command=download_audio)
        gui.mainloop()
