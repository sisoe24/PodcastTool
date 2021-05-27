import os
import sys
import platform
import subprocess

from datetime import datetime

from tkinter import messagebox, TkVersion

from app.geometry import AppGeometry

if TkVersion <= 8.5:
    messagebox.showinfo(
        message=f"Your Tcl-Tk version {TkVersion} has some bugs!"
        "Please update to +8.6")
    sys.exit("tk version is old")

APP_GEOMETRY = AppGeometry()

PWD = os.path.dirname(__file__)
PACKAGE_PATH = os.path.dirname(PWD)

LOG_PATH = os.path.join(PACKAGE_PATH, 'log')
os.makedirs(LOG_PATH, exist_ok=True)

# RESOURCES_PATH = os.path.join(PACKAGE_PATH, 'resources')

SYS_CONFIG_PATH = os.path.join(os.getenv('HOME'), '.podcasttool')
USER_ARCHIVE = os.path.join(SYS_CONFIG_PATH, 'archive')
USER_AUDIO = os.path.join(SYS_CONFIG_PATH, 'audio')

os.makedirs(SYS_CONFIG_PATH, exist_ok=True)
os.makedirs(USER_ARCHIVE, exist_ok=True)
os.makedirs(USER_AUDIO, exist_ok=True)

USER_CATALOG = os.path.join(SYS_CONFIG_PATH, 'catalog.json')
USER_CONFIG = os.path.join(SYS_CONFIG_PATH, '.config')
if not os.path.exists(USER_CONFIG):
    with open(USER_CONFIG, 'wb') as _:
        pass


def write_report():
    """Write and open log with missing dependencies info status."""
    log_path = os.path.join(PACKAGE_PATH, 'log')
    report_file = os.path.join(log_path, "dependecies_missing.log")

    with open(report_file, "w") as report:
        for app in MISSING_DEPENDECIES:
            now = datetime.today().strftime("%x_%X")
            msg = f"{now} - The following packages are required: {app}\n"
            report.write(msg)

            if platform.system() == "Linux":
                report.write(
                    f"type in the terminal:\nsudo apt install {app}\n")

    messagebox.showerror(
        title='PodcastTool',
        message=f'Missing packages!\nCheck log folder for more details:\n{log_path}')


DEPENDECIES = ["ffmpeg"]
MISSING_DEPENDECIES = []

for package in DEPENDECIES:
    try:
        subprocess.check_output(["which", package])
    except Exception as error:
        MISSING_DEPENDECIES.append(package)

if MISSING_DEPENDECIES:
    write_report()
    sys.exit("some dependecies are required")
