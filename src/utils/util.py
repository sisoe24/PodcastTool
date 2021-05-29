"""Reusable utility functions."""
import os
import re
import logging
import pathlib
import datetime
import requests
import urllib.request

import gtts


LOGGER = logging.getLogger('podcasttool.util')


def is_online():
    try:
        # requests.get('https://translate.google.com')
        urllib.request.urlopen('https://translate.google.com')
        return True
    except Exception as e:
        LOGGER.critical('Computer appears to be offline')
        return False


def generate_audio(text, path, filename="", lang='it'):
    """Generate the audio cues.

    Arguments:
        text {str} - what is going to be spoke in the audio cue.
        file_name {str} - the name of the saved file.
        path {str} - relative path of where to save the file.

    Keyword Arguments:
        lang {str} - the language for the audio(default: 'it')
    """
    if not is_online():
        return

    if not filename:
        filename = text.replace(" ", "_")
    else:
        filename = filename.replace(" ", "_")

    path = os.path.abspath(path)
    msg = 'gTTS had some problem! Check log file.'

    try:
        LOGGER.debug('Try to create gtts class')
        speak = gtts.gTTS(text=text, lang=lang)

    except Exception as error:
        msg += '\nFailed to create gtts class'
        LOGGER.critical('%s', msg, exc_info=True)
        return False
    else:
        try:
            LOGGER.debug('Try to save gtts audio')
            speak.save(f'{path}/{filename}.mp3')

        except Exception as error:
            msg += '\nFailed to create gtts audio'
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
        r'(\d{1,2}):(\d\d):(\d\d)(.+)?', r'\1h \2m \3s', song_duration)

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


if __name__ == '__main__':
    if os.path.exists('test.mp3'):
        os.remove('test.mp3')
    is_online()