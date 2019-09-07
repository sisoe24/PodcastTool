import platform
import subprocess
from tkinter import messagebox

from dotenv import load_dotenv, find_dotenv

from . import logger
from . import util
from . import podcasttools
from .podcasttools import PodcastFile, generate_html, upload_to_server


# search and load .env file
load_dotenv(find_dotenv())

if platform.system() == 'Darwin':
    OS_SYSTEM = 'Mac'
elif platform.system() == 'Linux':
    OS_SYSTEM = 'Linux'

CATALOG_NAMES = util.catalog_names()


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
