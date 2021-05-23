"""Reusable utility functions."""
import os
import re
import sys
import time
import pickle
import pathlib
import logging
import datetime
import subprocess

from tkinter import messagebox

import gtts

from startup import OS_SYSTEM, USER_CONFIG

LOGGER = logging.getLogger('podcasttool.util')


class UserConfig:
    def __init__(self, mode='rb'):
        self._mode = mode
        self._file = USER_CONFIG

    def __enter__(self):
        self._open = open(self._file, self._mode)
        return self._open

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._open.close()

    @property
    def file(self):
        return self._file

    @property
    def data(self):
        if self.get_size() > 0:
            with open(self._file, 'rb') as file:
                return pickle.load(file)

    def value(self, key, default=''):
        try:
            value = self.data[key]
        except (KeyError, TypeError):
            return default
        else:
            if value:
                return value
            return default

    def is_empty(self):
        if self.get_size() <= 0:
            return True
        for key, value in self.data.items():
            if key in ['host', 'user', 'pass', 'web']:
                if not value:
                    return True
        return False

    def get_size(self):
        return os.path.getsize(self._file)


def profile(func):
    """Write to log the profiling of a function."""
    # SortKey class is not present on the linux version
    # need to upgrade python to 3.7.4
    try:
        import io
        import pstats
        import cProfile
        from pstats import SortKey

        def inner(*args, **kwargs):
            pr = cProfile.Profile()
            pr.enable()
            value = func(*args, **kwargs)
            pr.disable()
            s = io.StringIO()
            sortby = SortKey.CUMULATIVE
            ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            ps.print_stats()
            with open(f'{get_path("log")}/profile.log', 'w') as file:
                file.write(s.getvalue())
            return value
        return inner
    except ModuleNotFoundError:
        return lambda: ()


def total_time(func):
    """Write to log total time of function completition."""
    def wrapper(*args, **kwarg):
        start = time.time()
        value = func(*args, **kwarg)
        end = time.time()
        total = datetime.timedelta(seconds=end - start)
        print_str = f"total time: {str(total)}\n"
        print(print_str)
        with open(f'{get_path("log")}/profile.log', 'a') as file:
            file.write(print_str)
        return value
    return wrapper


def generate_audio(text, path, filename="", lang='it'):
    """Generate the audio cues.

    Arguments:
        text {str} - what is going to be spoke in the audio cue.
        file_name {str} - the name of the saved file.
        path {str} - relative path of where to save the file.

    Keyword Arguments:
        lang {str} - the language for the audio(default: 'it')
    """
    name = str(text).replace("_", " ")

    if not filename:
        filename = name.replace(" ", "_")
    else:
        filename = filename.replace(" ", "_")

    path = get_path(path)
    try:
        speak = gtts.gTTS(text=name, lang=lang)
        speak.save(f'{path}/{filename}.mp3')
    except Exception as error:
        msg = 'gTTS had some problems creating audio! check log file.'
        LOGGER.critical('%s', msg, exc_info=True)
        return False
    return True


def get_path(directory: str) -> str:
    """Search for the path in main working directory.

    Get path of the argument string directory if is in root PodcastTool folder.
    """
    file_path = pathlib.Path(os.path.dirname(__file__))
    main_directories = ["PodcastTool", "Resources"]
    for path in file_path.parents:
        if path.parts[-1] in main_directories:
            new_path = path.joinpath(directory)
            if os.path.exists(new_path):
                return new_path
    raise FileNotFoundError(f"Directory not found: {new_path}")


def audio_duration(file_length: int) -> str:
    """Get the formatted (H/M/S) duration of an audio file.

    Arguments:
        [int] - lenght of the audio in milliseconds
    Returns:
        [str] - the full duration of the podcast file in H/M/S
    """
    song_duration = str(datetime.timedelta(milliseconds=file_length))

    format_duration = re.sub(
        r'(\d{1,2}):(\d\d):(\d\d)', r'\1h \2m \3s', song_duration)

    return format_duration


def calculate_cuts(ms_time: int) -> int:
    """Calculate the numbers of audio cuts based on the audio lenght.

    If it has to add 3 watermarks then there should be 3 + 1 cuts
    meaning that the return value is watermarks n + 1.

    Returns:
        [int] -- how many cuts to do in the podcast.

    """
    LOGGER.debug('setting automatic watermarks')
    two_hours = 7_200_000
    one_hour = 3_600_000

    if ms_time > two_hours:
        return 5
    if two_hours > ms_time > one_hour:
        return 4
    if ms_time < one_hour:
        return 3
    return 4


def convert_month_name(month):
    """Convert month number value to italian month name.

    Return:
        {dict} -- Dictionary with all the months by name and value.
    """
    months = {'01': 'Gennaio', '02': 'Febbraio', '03': 'Marzo',
              '04': 'Aprile', '05': 'Maggio', '06': 'Giugno',
              '07': 'Luglio', '08': 'Agosto', '09': 'Settembre',
              '10': 'Ottobre', '11': 'Novembre', '12': 'Dicembre'}
    return months[month]


def is_dev_mode(bypass=False):
    """Check if user is me. if yes dont upload to server.

    If I need to test uploading to the server then I must supply a value
    to bypass.

    Argument:
        bypass [bool] - if True, it nullifies the is_dev_mode - [default]: False
    """
    if bypass:
        return False
    if os.getenv('USER') in ['virgil', 'virgilsisoe', 'ubuntutest']:
        return True
    return False


def open_link(link):
    """Open a file path or a website link."""
    if OS_SYSTEM == 'Mac':
        subprocess.run(['open', link])
    elif OS_SYSTEM == 'Linux':
        subprocess.run(['xdg-open', link])


def open_log(msg, title="Error", icon="warning", _exit=True):
    """If fatal error ask user if wants to open log file."""
    msg += '\nOpen log file?'
    user = messagebox.askyesno(title=title, message=msg, icon=icon)
    if user:
        log_path = get_path("log") / "errors.log"
        open_link(log_path)
    if _exit:
        sys.exit()


if __name__ == '__main__':
    x = audio_duration(3123124)
    print(x)
