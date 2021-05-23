import os
import json
import shutil

from startup import USER_CATALOG, USER_AUDIO

CURRENT_DIR = os.path.dirname(__file__)


def _system_catalog_path():
    return os.path.join(CURRENT_DIR, 'data/catalog.json')


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

    sys_audio = os.path.join(CURRENT_DIR, 'audio')
    parse_path = [USER_AUDIO, sys_audio]

    for path in parse_path:
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('mp3'):
                    library_dict[filename] = dirpath
    return library_dict
