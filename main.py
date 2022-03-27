import os
import subprocess
from re import sub
from gui import GUI
from uuid import uuid4
from threading import Thread
from tempfile import gettempdir
from string import ascii_letters, digits
from pytube_wrapper import YouTubeClient
from tkinter import messagebox, filedialog
from pytube.exceptions import VideoUnavailable, RegexMatchError

yt = None
user_download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
user_temp_folder = gettempdir()


def load_streams():
    try:
        global yt
        yt = YouTubeClient(gui.entry_url.get(), on_complete_callback=download_complete)
    except VideoUnavailable:
        messagebox.showerror(master=gui, title="ERROR", message="This video is not available.")
    except RegexMatchError:
        messagebox.showerror(master=gui, title="ERROR", message="Invalid YouTube URL.")
    else:
        yt.stream_list = yt.streams
        yt.get_best_streams()
        yt.filename = sanitize_filename(yt.title)
        change_download_buttons_state("active")
        update_status("")


# noinspection PyUnresolvedReferences
def download_video():
    yt.video_processing = True
    download_stream_thread(yt.best_video_stream)


# noinspection PyUnresolvedReferences
def download_audio():
    yt.video_processing = False
    download_stream_thread(yt.best_audio_stream)


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
    if yt.video_processing:
        if yt.video_file is None:
            yt.video_file = args[1]
            download_stream_thread(yt.best_audio_stream)
        else:
            yt.audio_file = args[1]
            convert(input_video_file=yt.video_file, input_audio_file=yt.audio_file)
    else:
        yt.audio_file = args[1]
        convert(input_audio_file=yt.audio_file)


# noinspection PyUnresolvedReferences
def convert(**kwargs):
    update_status("Converting...")
    output_file = f"{gui.entry_folder.get()}\\{yt.filename}"
    if yt.video_processing:
        output_file = f"{output_file}.mp4"
        cmd = ["ffmpeg", "-n", "-i", kwargs.get("input_video_file"), "-i", kwargs.get("input_audio_file"), "-c:v",
               "copy", "-c:a", "aac", output_file]
    else:
        output_file = f"{output_file}.mp3"
        cmd = ["ffmpeg", "-n", "-i", kwargs.get("input_audio_file"), "-c:a", "libmp3lame", output_file]
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    if process.returncode != 0:
        error_message = process.stdout.split('\n')[-2].strip()
        update_status(f"Failed to convert. ERROR: {error_message}")
    else:
        update_status(f"Downloaded to: {output_file}")
    change_download_buttons_state("active")
    if yt.video_processing:
        os.remove(kwargs.get("input_video_file"))
        yt.video_file = None
    os.remove(kwargs.get("input_audio_file"))
    yt.audio_file = None


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

    # Check if ffmpeg is detected
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
