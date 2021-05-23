import os
import sys
import platform
import subprocess

from datetime import datetime

from tkinter import messagebox, TkVersion

if TkVersion <= 8.5:
    messagebox.showinfo(
        message=f"Your Tcl-Tk version {TkVersion} has some bugs!"
        "Please update to +8.6")
    sys.exit("tk version is old")

if platform.system() == 'Darwin':
    OS_SYSTEM = 'Mac'
elif platform.system() == 'Linux':
    OS_SYSTEM = 'Linux'


PATH_PACKAGE = os.path.dirname(os.path.dirname(__file__))

PATH_RESOURCES = os.path.join(PATH_PACKAGE, 'resources')
PATH_AUDIO = os.path.join(PATH_RESOURCES,  'audio')

SYS_CONFIG_PATH = os.path.join(os.getenv('HOME'), '.podcasttool')

USER_CATALOG = os.path.join(SYS_CONFIG_PATH, 'catalog.json')
USER_AUDIO = os.path.join(SYS_CONFIG_PATH, 'audio')
USER_CONFIG = os.path.join(SYS_CONFIG_PATH, '.config')

os.makedirs(SYS_CONFIG_PATH, exist_ok=True)
os.makedirs(USER_AUDIO, exist_ok=True)

if not os.path.exists(USER_CONFIG):
    with open(USER_CONFIG, 'wb') as _:
        pass


def write_report():
    """Write and open log with missing dependencies info status."""
    log_path = os.path.join(PATH_PACKAGE, 'log')
    report_file = os.path.join(log_path, "dependecies_missing.log")

    with open(report_file, "w") as report:
        for app in MISSING_DEPENDECIES:
            now = datetime.today().strftime("%x_%X")
            msg = f"{now} - The following packages are required: {app}\n"
            report.write(msg)

            if OS_SYSTEM == "Linux":
                report.write(
                    f"type in the terminal:\nsudo apt install {app}\n")

    messagebox.showerror(
        title='PodcastTool',
        message=f'Missing packages!\nCheck log folder for more details:\n{log_path}')


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
