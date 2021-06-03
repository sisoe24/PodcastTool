"""Select podcast file from the gui.

Here is where the selection is happening. 
GUI can select or or more file at once. If selection is only 1 file, then its
going to check for other podcast in the same directory comparing the file
modification date.

It also check whetever the folder from where the file comes
is correct since it uses that folder name to find the server path.

The class also returns a dictionary with the date from the file that is used
in the suggestion section of the gui when the date written by user is wrong.
"""

import os
import logging
import pathlib
import platform

from datetime import datetime

import regex

from startup import critical

LOGGER = logging.getLogger('podcasttool.widgets.selectframe')


def format_date(date):
    """Formate date object from datetime module and return %Y-%m-%d."""
    human_date = datetime.fromtimestamp(date)
    formatted_date = human_date.strftime('%Y-%m-%d')
    return formatted_date


def get_date(file_path: str) -> str:
    """Check if the written date is the same as the last modification date.

    If not then suggests to the user if he wants to automatically correct.

    Arguments:
        file_path {str} -- path of the file to check the date.

    Returns:
        {dict} - a dict with today, creation and modification date.
    """
    os_system = platform.system()

    if os_system == 'Darwin':
        create_time = os.stat(file_path).st_birthtime
    elif os_system == 'Linux':
        create_time = os.stat(file_path).st_ctime

    mod_time = os.path.getmtime(file_path)

    file_attr = {
        "creation": format_date(create_time),
        "modification": format_date(mod_time)
    }

    return file_attr


def _extract_lesson(podcast_file):
    """Extract the lesson number from the podcast file.

        Return:
            tuple - {pathlib obj} path of podcast file, {str} lesson number.
    """
    file_path = pathlib.Path(podcast_file)
    extract_lesson = "_".join(file_path.name.split('_')[4:6])
    try:
        lesson_num = regex.search(
            r'(?<=[L|l]\w+_)(\d{1,2})', extract_lesson).group()

    except AttributeError:
        LOGGER.critical('no lesson match: %s', file_path.name, exc_info=True)
        critical("Nessun match in lezione!\nTip: Puoi selezionare piu file insieme")
    return file_path, lesson_num


def _match_lesson(podcast_file):
    """Search for same podcast lesson in parent directory of current podcast.

    Argument:
        podcast_file {str} - podcast file absolute path.
    """
    file_path, lesson_num = _extract_lesson(podcast_file)
    compare_date = get_date(file_path)["creation"]

    for file in sorted(file_path.parent.glob('*wav')):
        check_lesson = "_".join(file.name.split('_')[4:6])

        match_lesson = regex.search(r'[L|l]\w+_' + lesson_num, check_lesson)
        file_vecchio = regex.search(r'vecchio', file.name)

        if match_lesson and not file_vecchio:

            file_date = get_date(file)["creation"]

            if file_date == compare_date:
                LOGGER.debug('matching date of creation: %s', file.name)
                yield str(file.name)


class SelectPodcast:
    """Select podcast file from disk."""

    def __init__(self, selection):
        self._selection = selection

    @property
    def group_selection(self):
        """Return the tuple selection from the gui."""
        return self._selection

    @property
    def single_selection(self):
        """Return a single file from the tuple selection of the gui."""
        return self._selection[0]

    @property
    def path(self):
        """Return file path."""
        return os.path.dirname(self.single_selection)

    @property
    def podcast_list(self):
        """Check whetever the file is just one or more.

        If file is only one then search for other matching file based on the
        _match_lesson() function.
        If file 2 ore more then just grab those.
        """
        selected_files = self.group_selection
        if len(selected_files) == 1:
            valid_podcasts = [i for i in _match_lesson(selected_files[0])]
        elif len(selected_files) > 1:
            valid_podcasts = [os.path.basename(i) for i in selected_files]
        else:
            raise FileNotFoundError("No file passed")
        return valid_podcasts

    @property
    def date(self):
        """Call get_date method and return file creation and mod date."""
        return get_date(self.single_selection)
