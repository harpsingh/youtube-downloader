import os
import sys
import webbrowser
from tkinter import *


# https://stackoverflow.com/questions/51060894/adding-a-data-file-in-pyinstaller-using-the-onefile-option
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class GUI(Tk):

    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader")
        self.config(padx=20, pady=10)
        icon = PhotoImage(file=resource_path("images/downloader-icon.png"))
        self.iconphoto(False, icon)

        self.label_url = Label(self, text="Paste YouTube link here and click \"Load\":", font=("Arial", 10))
        self.label_url.grid(column=0, row=0, columnspan=2, sticky="W", pady=5)
        self.entry_url = Entry(self, borderwidth=2, font=("Arial", 9))
        self.entry_url.grid(column=0, row=1, columnspan=2, sticky=W+E)
        self.button_load = Button(self, text="Load")
        self.button_load.grid(pady=5, column=0, row=2, columnspan=2, sticky="E")

        self.label_folder = Label(self, text="Download location:", font=("Arial", 10))
        self.label_folder.grid(column=0, row=3, columnspan=2, sticky="W", pady=5)
        self.entry_folder = Entry(self, borderwidth=2, font=("Arial", 9))
        self.entry_folder.grid(column=0, row=4, columnspan=2, sticky=W+E)
        self.button_folder = Button(self, text="Browse")
        self.button_folder.grid(column=0, row=5, columnspan=2, sticky="E")

        self.spacer1 = Label(self, text="", font=("Arial", 6))
        self.spacer1.grid(column=0, row=6, columnspan=2)

        self.video_icon = PhotoImage(file="images/video.png")
        self.video_button = Button(image=self.video_icon, borderwidth=1, bg="#D3DEDC", state="disabled")
        self.video_button.grid(column=0, row=7, padx=20, ipadx=10, pady=10)

        self.audio_icon = PhotoImage(file="images/audio.png")
        self.audio_button = Button(image=self.audio_icon, borderwidth=1, bg="#D3DEDC", state="disabled")
        self.audio_button.grid(column=1, row=7, padx=20, pady=10)

        self.label_video = Label(self, text="Download Video", font=("Arial", 9))
        self.label_video.grid(column=0, row=8)

        self.label_video = Label(self, text="Download Audio", font=("Arial", 9))
        self.label_video.grid(column=1, row=8)

        self.status_text = Label(self, text="", font=("Courier", 9), wraplength=350, justify="center")
        self.status_text.grid(column=0, row=9, columnspan=2, padx=5, pady=10)

        self.label_credit = Label(self, text="https://github.com/harpsingh/youtube-downloader",
                                  font=("Arial", 9, "underline"), fg="blue")
        self.label_credit.grid(column=0, row=11, columnspan=2)
        self.label_credit.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/harpsingh/youtube-downloader"))
