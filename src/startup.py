import os
import re
import sys
import pathlib
import logging
import platform
import subprocess

from datetime import datetime

from tkinter import messagebox, TkVersion


from src import logger

from src.app.geometry import AppGeometry
from src.app.colors import Colors


LOGGER = logging.getLogger('podcasttool.startup')
LOGGER.debug('\n\nSTART APPLICATION %s', datetime.now())

PLATFORM = platform.system()


def open_path(link):
    """Open a file path or a website link."""
    if PLATFORM == 'Darwin':
        open_cmd = 'open'
    elif PLATFORM == 'Linux':
        open_cmd = 'xdg-open'
    else:
        return

    subprocess.run([open_cmd, link])


def critical(msg,  _exit=True):
    """If fatal error ask user if wants to open log file."""
    msg = str(msg)
    LOGGER.critical(msg, exc_info=True)

    msg += '\nOpen log file?'
    user = messagebox.askyesno(title='PodcastTool', message=msg, icon='error')

    if user:
        open_path(os.path.join(LOG_PATH, "errors.log"))
    if _exit:
        sys.exit()


def get_resources(find_path='resources', start_dir=__file__):

    def verify_path(_dir, path):
        path = os.path.join(_dir, path)
        if os.path.exists(path):
            return path
        return False

    current_path = pathlib.Path(os.path.dirname(start_dir))
    check_path = verify_path(current_path, find_path)

    if check_path:
        return check_path

    for parent in current_path.parents:
        check_path = verify_path(parent, find_path)
        if check_path:
            return check_path

    critical(msg='Could not find resources directory')


LOG_PATH = logger.LOG_PATH
LOGGER.debug('Log path: %s', LOG_PATH)

if PLATFORM == 'Windows':
    critical(msg='Currently not Windows supported')

# if TkVersion <= 8.5:
#     critical(msg=f"Tk {TkVersion}! Please update Tk to +8.6")

RESOURCES_PATH = get_resources()
LOGGER.debug('Resources path: %s', RESOURCES_PATH)

APP_GEOMETRY = AppGeometry()
COLORS = Colors()

LOGGER.debug('CWD: %s', os.getcwd())
LOGGER.debug('Startup file directory: %s', os.path.dirname(__file__))


for ff_bin in ['ffmpeg', 'ffprobe']:
    try:
        subprocess.check_output(["which", ff_bin])
    except Exception as error:
        LOGGER.warning(error)

        included_bin = os.path.join(RESOURCES_PATH, 'bin', PLATFORM)
        os.environ['PATH'] += os.pathsep + included_bin

        LOGGER.warning(f"System {ff_bin} not found! Falling back on: %s",
                       included_bin)

    else:
        LOGGER.debug(f'Using system: {ff_bin}')

    finally:
        output = subprocess.check_output([ff_bin, '-version'])
        ff_version = re.search(r'ff(probe|mpeg)\sversion\s.+?\s', str(output))
        LOGGER.debug(ff_version.group())

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
