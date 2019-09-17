import sys
import platform
import subprocess

from textwrap import dedent
from datetime import datetime
from tkinter import messagebox, TkVersion

from . import logger
from . import util
from . import podcasttools
from .podcasttools import (
    PodcastFile,
    generate_html,
    upload_to_server,
    check_server_path
)

if TkVersion <= 8.5:
    messagebox.showinfo(message=f"your tcl-tk version {TkVersion} has some serious bugs!"
                        "please update to the last version: 8.6")
    sys.exit("tk version is old")


if platform.system() == 'Darwin':
    OS_SYSTEM = 'Mac'
elif platform.system() == 'Linux':
    OS_SYSTEM = 'Linux'


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


def write_report():
    """Write and open log with missing dependencies info status."""
    report_file = "log/dependecies_missing.log"
    with open(report_file, "w") as report:
        for app in MISSING_DEPENDECIES:
            now = datetime.today().strftime("%x_%X")
            msg = f"{now} - the following packages are required: {app}\n"
            report.write(msg)
            if OS_SYSTEM == "Linux":
                report.write(f"type in the terminal:\nsudo apt install {app}\n")
            else:
                report.write(dedent("""
                                    ffmpeg and ffprobe are required if you
                                    install ffmpeg manually from their website,
                                    or you could install it with brew."""))
    open_link(report_file)


# Check if dependecies are installed. Launching from GUI may not show if
# they are missing so custom msg is needed.
DEPENDECIES = ["ffmpeg"]
MISSING_DEPENDECIES = []

if OS_SYSTEM == "Linux":
    DEPENDECIES.append("xsel")
for package in DEPENDECIES:
    try:
        subprocess.check_output(["which", package])
    except Exception as error:
        MISSING_DEPENDECIES.append(package)

if MISSING_DEPENDECIES:
    write_report()
    sys.exit("some dependecies are required")
