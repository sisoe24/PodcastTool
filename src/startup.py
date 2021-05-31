import os
import re
import sys
import logging
import platform
import subprocess

from tkinter import messagebox, TkVersion

from pydub import AudioSegment

import logger

from app.geometry import AppGeometry
from app.colors import Colors

LOGGER = logging.getLogger('podcasttool.startup')
LOGGER.debug('\nSTART APPLICATION')

PLATFORM = platform.system()


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


# TODO: work on windows version
if PLATFORM == 'Windows':
    LOGGER.critical('Currently not Windows supported')
    sys.exit()

if TkVersion <= 8.5:
    LOGGER.critical('tk Version is <=8.6')
    messagebox.showinfo(
        message=f"Your Tcl-Tk version {TkVersion} has some bugs!"
        "Please update to +8.6")
    sys.exit("tk version is old")

APP_GEOMETRY = AppGeometry()
COLORS = Colors()

LOGGER.debug('CWD: %s', os.getcwd())

PWD = os.path.dirname(__file__)
LOGGER.debug('Startup file directory: %s', PWD)

# TODO: find better solution.
# HACK: when launching app on linux, app will assume the home directory as working directory
# thus will not find the resources
if PLATFORM == 'Linux' and os.getcwd() == os.getenv('HOME'):
    os.chdir(PWD)

# PACKAGE_PATH = os.path.dirname(PWD)
# LOGGER.debug('Package path: %s', PACKAGE_PATH)

LOG_PATH = logger.LOG_PATH
LOGGER.debug('Log path: %s', LOG_PATH)


RESOURCES_PATH = os.path.join(os.getcwd(), 'resources')
LOGGER.debug('Resources path: %s', RESOURCES_PATH)

if not os.path.exists(RESOURCES_PATH):
    LOGGER.critical('could not find resourcers in path', exc_info=True)
    critical(title='PodcastTool',
             msg='Could not find resources directory')


try:
    subprocess.check_output(["which", 'ffmpeg'])
except Exception as error:
    LOGGER.warning(error)

    included_bin = os.path.join(
        os.getcwd(), 'resources', 'bin', PLATFORM, 'ffmpeg')
    if not os.path.exists(included_bin):
        LOGGER.critical('no ffmppeg binary found', exc_info=True)
        critical('no ffmpeg binary found')

    AudioSegment.converter = included_bin
    LOGGER.warning(
        "System ffmpeg not found! Falling back on: %s", included_bin)
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
