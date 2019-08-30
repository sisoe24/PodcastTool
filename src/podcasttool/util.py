"""Reusable utility functions."""
import os
import json
import time
import pathlib
import logging
import datetime
import subprocess

import regex
from dotenv import load_dotenv, find_dotenv

# from podcasttool import logger

load_dotenv(find_dotenv())
LOGGER = logging.getLogger('podcast_tool.utlity')


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


def get_path(directory: str) -> str:
    """Search for the path in main working directory.

    Get path of the argument string directory if is in root PodcastTool folder.
    """
    file_path = pathlib.Path(os.path.dirname(__file__))
    for path in file_path.parents:
        if path.parts[-1] == 'PodcastTool':
            new_path = path.joinpath(directory)
            break
    if directory in ['archive', 'log'] and not os.path.exists(new_path):
        os.mkdir(new_path)
    elif not os.path.exists(new_path):
        LOGGER.critical('path not found: %s', new_path)
        exit()
    return new_path


def audio_library():
    """Create a dictionary with all the files from the library.

    Returns:
        [dict] - - dictionary with key files names and values paths.

    """
    library_path = get_path('include/audio')
    library_dict = {}
    for dirpath, _, filenames in os.walk(library_path):
        for filename in filenames:
            if filename.endswith('mp3'):
                library_dict[filename] = dirpath
    return library_dict


def audio_duration(file_length: int) -> str:
    """Get the formatted (H/M/S) duration of an audio file.

    Arguments:
        [int] - lenght of the audio in milliseconds
    Returns:
        [str] - the full duration of the podcast file in H/M/S
    """
    song_duration = str(datetime.timedelta(milliseconds=file_length))

    format_duration = regex.sub(
        r'^(\d{1,2}):(\d\d):(\d\d).+', r'\1h \2m \3s', song_duration)

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


@profile
def catalog_names() -> dict:
    """Open json catalog of names to grab the teachers and courses names."""
    # json file should always be in
    # the same directory of where the src code is
    json_file = os.path.join(
        os.path.dirname(__file__), 'catalog_names.json')
    try:
        with open(json_file) as json_file:
            LOGGER.debug('parsing json file: %s', json_file)
            json_data = json.load(json_file)
            return json_data
    except FileNotFoundError:
        print('no json file found!', json_file)
        LOGGER.warning('No json file found: %s', json_file)
        exit()


def convert_month_name():
    """Convert month number value to italian month name.

    Return:
        {dict} -- Dictionary with all the months by name and value.
    """
    return {'01': 'Gennaio', '02': 'Febbraio', '03': 'Marzo',
            '04': 'Aprile', '05': 'Maggio', '06': 'Giugno',
            '07': 'Luglio', '08': 'Agosto', '09': 'Settembre',
            '10': 'Ottobre', '11': 'Novembre', '12': 'Dicembre'}


def get_server_path(uploading_file: str) -> str:
    """Extract root course name from file path and create server path.

    Arguments:
        [str] -- path like string of the file to parse.

    Returns:
        [str] -- path like string of the server path.
    """
    root_folder = '/'.join(uploading_file.split('/')[-2:])
    server_path = os.environ['FONDERIE_PODCAST'] + root_folder
    return server_path


def dev_mode(bypass=False):
    """Check if user is me. if yes then perform some operations.

    Perform some operations like:
        cleaning tmp folders and files
        NOT uploading to server
        enable debug console
    If I need to test uploading to the server then I must supply a value
    to bypass.

    Argument:
        bypass [bool] - if True, it nullifies the dev_mode - [default]: False
    """
    if bypass:
        ask = input("You have bypassed dev_mode! are you sure? y/n\n> ")
        if ask == "y":
            subprocess.call(['/bin/zsh', '-i', '-c', 'deltmp'])
            return None
    try:
        if str(pathlib.Path().home()) == os.environ["HOME_DIR"]:
            subprocess.call(['/bin/zsh', '-i', '-c', 'deltmp'])
            return True
    except KeyError:
        # means that .env file hasnt been updated to include HOME_DIR yet
        pass
    return None


DEV_MODE = dev_mode(bypass=False)
if __name__ == '__main__':
    pass
    # print(a)