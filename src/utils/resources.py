import json
import logging
import os
import shutil

from ..startup import RESOURCES_PATH, USER_AUDIO, USER_CATALOG, critical

LOGGER = logging.getLogger('podcasttool.resources')


def _system_catalog_path():
    return os.path.join(RESOURCES_PATH, 'data', 'catalog.json')


def _catalog_file():
    """Return catalog file path.

    File should always be in the same directory where the src code is.
    """

    if not os.path.exists(USER_CATALOG):
        shutil.copy(_system_catalog_path(), USER_CATALOG)

    return USER_CATALOG


def catalog(value="") -> dict:
    """Return catalog names dictionary.

    Keyword Arguments:
        value {str} -- can grab directly its value is passed (default: {""})

    Returns:
        dict -- catalog of names
    """
    with open(_catalog_file()) as json_file:
        json_data = json.load(json_file)

    if value:
        return json_data[value]

    return json_data


def audio_library():
    """Create a dictionary with all the files from the library.

    Returns:
        [dict] - - dictionary with key files names and values paths.

    """
    library_dict = {}

    sys_audio = os.path.join(RESOURCES_PATH, 'audio')
    parse_path = [USER_AUDIO, sys_audio]

    for path in parse_path:
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                if not filename.startswith('.'):

                    file_path = os.path.join(dirpath, filename)
                    file_size = os.path.getsize(file_path)

                    if filename.endswith('mp3') and file_size > 0:
                        library_dict[filename] = dirpath
                    else:
                        critical(f'Invalid file: {filename}')

    return library_dict
