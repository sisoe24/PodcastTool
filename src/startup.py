import os
import re
import sys
import logging
import platform
import subprocess
from datetime import datetime
from tkinter import messagebox, TkVersion

from pydub import AudioSegment

import logger
from app.geometry import AppGeometry
from app.colors import Colors

LOGGER = logging.getLogger('podcasttool.startup')

PLATFORM = platform.system()

# TODO: work on windows version
if PLATFORM == 'Windows':
    LOGGER.critical('current not Windows supported')
    sys.exit()

if TkVersion <= 8.5:
    LOGGER.critical('tk Version is <=8.6')
    messagebox.showinfo(
        message=f"Your Tcl-Tk version {TkVersion} has some bugs!"
        "Please update to +8.6")
    sys.exit("tk version is old")

APP_GEOMETRY = AppGeometry()
COLORS = Colors()

PWD = os.path.dirname(__file__)
PACKAGE_PATH = os.path.dirname(PWD)
LOGGER.debug('Package path: %s', PACKAGE_PATH)

LOG_PATH = os.path.join(PACKAGE_PATH, 'log')
os.makedirs(LOG_PATH, exist_ok=True)

RESOURCES_PATH = os.path.join(PACKAGE_PATH, 'resources')

try:
    subprocess.check_output(["which", 'ffmpeg'])
except Exception as error:
    LOGGER.warning(error)
    # TODO: add linux binary
    included_bin = os.path.join(RESOURCES_PATH, 'bin', PLATFORM, 'ffmpeg')
    AudioSegment.converter = included_bin
    LOGGER.warning("Falling back on: %s", included_bin)
else:
    LOGGER.debug('Using system ffmpeg')

finally:
    output = subprocess.check_output([AudioSegment.converter, '-version'])
    ffmpeg_version = re.search(r'ffmpeg\sversion\s.+?\s', str(output)).group()
    LOGGER.debug(ffmpeg_version)


SYS_CONFIG_PATH = os.path.join(os.getenv('HOME'), '.podcasttool')
USER_ARCHIVE = os.path.join(SYS_CONFIG_PATH, 'archive')
USER_AUDIO = os.path.join(SYS_CONFIG_PATH, 'audio')

os.makedirs(SYS_CONFIG_PATH, exist_ok=True)
os.makedirs(USER_ARCHIVE, exist_ok=True)
os.makedirs(USER_AUDIO, exist_ok=True)

USER_CATALOG = os.path.join(SYS_CONFIG_PATH, 'catalog.json')
USER_CONFIG = os.path.join(SYS_CONFIG_PATH, '.config')

if not os.path.exists(USER_CONFIG):
    LOGGER.debug('user config file didnt exists. creating one')
    with open(USER_CONFIG, 'wb') as _:
        pass


def open_path(link):
    """Open a file path or a website link."""

    if PLATFORM == 'Darwin':
        open_cmd = 'open'
    elif PLATFORM == 'Linux':
        open_cmd = 'xdg-open'
    else:
        return
    subprocess.Popen([open_cmd, link])


def critical(msg, title="Error", icon="warning", _exit=True):
    """If fatal error ask user if wants to open log file."""
    msg += '\nOpen log file?'
    user = messagebox.askyesno(title=title, message=msg, icon=icon)
    if user:
        log_path = os.path.join(LOG_PATH, "errors.log")
        open_path(log_path)
    if _exit:
        sys.exit()
