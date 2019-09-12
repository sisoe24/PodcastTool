import platform
import subprocess
from tkinter import messagebox, TkVersion

from . import logger
from . import util
from . import podcasttools
from .podcasttools import PodcastFile, generate_html, upload_to_server

if TkVersion <= 8.5:
    messagebox.showinfo(message=f"your tcl-tk version {TkVersion} has some serious bugs!"
                        "please update to the last version: 8.6")
    exit("tk version is old")

try:
    subprocess.check_output(["which", "ffmpeg"])
except Exception as error:
    messagebox.showinfo(message="ffmpeg doesnt appear to be installed?")
    exit("ffmpeg is not installed")


if platform.system() == 'Darwin':
    OS_SYSTEM = 'Mac'
elif platform.system() == 'Linux':
    OS_SYSTEM = 'Linux'

CATALOG_NAMES = util.catalog_names()
podcasttools.COURSES_NAMES = CATALOG_NAMES['corsi']
podcasttools.TEACHERS_NAMES = CATALOG_NAMES['docenti']


def open_link(link):
    """Open a file path or a website link."""
    if OS_SYSTEM == 'Mac':
        subprocess.run(['open', link])
    elif OS_SYSTEM == 'Linux':
        subprocess.run(['xdg-open', link])


def open_log(msg, title="Error", icon="warning"):
    """If fatal error ask user if wants to open log file."""
    user = messagebox.askyesno(title=title, message=msg, icon=icon)
    if user:
        log_path = util.get_path("log") / "errors.log"
        open_link(log_path)
