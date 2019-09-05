import os
import pathlib
import logging
import platform

from datetime import datetime
from difflib import get_close_matches

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

import regex
from PIL import Image, ImageTk

from podcasttool import util
from podcasttool import podcasttools
from podcasttool import PodcastFile, upload_to_server, generate_html

if platform.system() == 'Darwin':
    OS_SYSTEM = 'Mac'
elif platform.system() == 'Linux':
    OS_SYSTEM = 'Linux'
else:
    print('sorry your OS is not supported')

CATALOG_NAMES = util.catalog_names()
COURSES_NAMES = CATALOG_NAMES['corsi'].keys()
TEACHERS_NAMES = CATALOG_NAMES['docenti'].keys()

LOGGER = logging.getLogger('podcast_tool.gui.main')
INFO_LOGGER = logging.getLogger('status_app.gui.main')


def _match_lesson(podcast_file):
    """Search for same podcast lesson in directory."""
    path = pathlib.Path(podcast_file)
    date_selected_file = get_date(path)["creation"]
    lezione_search = "_".join(path.name.split('_')[4:6])

    try:
        _, num = regex.search(r'([L|l]\w+)_(\d)', lezione_search).groups()
        LOGGER.debug('extracting lesson number: %s', lezione_search)
    except AttributeError:
        LOGGER.critical('something went totally wrong no match found')
        INFO_LOGGER.critical('Controlla log/errors.log')
        exit()

    for file in sorted(path.parent.glob('*wav')):
        lezione_check = "_".join(file.name.split('_')[4:6])

        valid_lesson = regex.search(r'[L|l]\w+_' + num, lezione_check)
        file_vecchio = regex.search(r'vecchio', file.name)

        date_file = get_date(file)["creation"]
        if valid_lesson and not file_vecchio:
            if date_file == date_selected_file:
                LOGGER.debug('file that match date of creation: %s', file.name)
                yield str(file.name)


def check_folder(podcast_folder):
    """Check if the folder name is correct otherwise quit."""
    # on linux if podcast_folder is empty, it will return a tuple
    # so need to convert in string before to catch the error
    path = os.path.dirname(str(podcast_folder))
    folder_name = os.path.split(path)[1][:3]
    LOGGER.debug('checking if folder name is valid: %s', folder_name)

    if folder_name not in COURSES_NAMES:
        msg = f'Nome cartella sbagliato: {folder_name}.'
        LOGGER.critical('wrong folder name: %s', folder_name)
        INFO_LOGGER.critical('Controlla log/errors.log')
        messagebox.showerror(title='Fatal Error', message=msg)
        exit()


def get_similar_words(wrong_name: str, catalog: str) -> str:
    """If user writes the wrong name try suggesting valid alternative.

    Arguments:
        wrong_name {str} - the not found word that the user has written
        catalog {str} - the type of list in where to search:
                        c = courses (list of courses)
                        t = teachers (list of teachers)
    Returns:
        [str] -- return the correct word choosen by the user.

    """
    if catalog == 'c':
        check_list = COURSES_NAMES
    elif catalog == 't':
        check_list = TEACHERS_NAMES

    similar_name = get_close_matches(wrong_name, check_list, cutoff=0.6)
    possibile_names = [i for i in similar_name]
    choice = f"- {wrong_name} -> {possibile_names}"
    return choice


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
    if OS_SYSTEM == 'Mac':
        create_time = os.stat(file_path).st_birthtime
    elif OS_SYSTEM == 'Linux':
        create_time = os.stat(file_path).st_ctime

    today = datetime.today().strftime('%Y-%m-%d')
    mod_time = os.path.getmtime(file_path)

    file_attr = {
        "today": today,
        "creation": format_date(create_time),
        "modification": format_date(mod_time)
    }

    return file_attr


def images_path() -> tuple():
    """Get images path from image directory.

    Returns:
        [tuple] - tuple list of images absolute path

    """
    img_directory = util.get_path("include/img")
    img_list = pathlib.Path(os.path.join(img_directory)).glob('*png')
    return [i for i in sorted(img_list)]


def get_image(img, get_path=False):
    """Get ImageTK object with image.
    Arguments:
        img {str} - the name of the image to get.
                    (warning, x, ok, logo, icon, sorry)
        get_path {bool} - if True then returns only the path not the object
                        [default] : False.
    """
    images = {
        "warning": "", "x": "", "ok": "", "logo": "", "icon": "", "sorry": ""
    }
    for name, path in zip(images.keys(), images_path()):
        images[name] = path
    if get_path:
        return images[img]
    return ImageTk.PhotoImage(Image.open(images[img]))


def _set_directory():
    """Set which folder to open.

    If user is me then open in test files directory.

    Return:
        {str} - path to which directory to open first at gui start.
    """
    if util.DEV_MODE:
        initial_dir = os.path.join(
            os.environ['TEST_FILES_REAL'], 'ALP/MULO')
    else:
        initial_dir = os.path.join(pathlib.Path(
            os.path.dirname(__file__)).home(), 'Scrivania/Podcast')
    return initial_dir


def _message_box(msg: str, exit_script=''):
    """Message pop up window.

    Arguments:
        msg {str} -- string to print on the message

    Keyword Arguments:
        exit_script {str} -- quits the script if argument is passed
        (default: '')
    """
    if exit_script:
        messagebox.showerror(title='EXIT', message=msg)
        exit()
    else:
        messagebox.showinfo(title=msg, message=msg)


class LogFrame(tk.Frame):
    """Error section of the gui."""
    _row_number = 0

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.grid_propagate(False)

        self._log_frame = ttk.Frame(parent, borderwidth=3, relief='sunken',
                                    width=670, height=360)
        self._log_frame.grid(column=0, row=0, rowspan=2, columnspan=2,
                             sticky=tk.N)
        self._log_frame.grid_propagate(False)

        # creating this and assigning it to None because of the create_label_frame
        # method in which I need to referencing it and pylint gives me error
        # if i dont declarate on the init method.
        # dont like it though should fine better solution
        self._log_label = None

        self._label_img = ttk.Label(self._log_frame, name='logo', width=500)
        self.insert_img(get_image("warning"))
        self._label_img.place(x=150, y=10)

    def insert_img(self, img):
        """Insert image in error frame."""
        self._label_img.configure(image=img)
        self._label_img.image = img

    @classmethod
    def row_increment(cls):
        """Increment row number from the same error label frame.

        In order to display messages on top of eacher other need to increment.
        """
        cls._row_number += 1

    @property
    def row_number(self):
        """Get the row number in error label frame where to display the msg."""
        return self._row_number

    def refresh_widgets(self, name):
        """Refresh widgets in error label frame."""
        for widget in self._log_frame.winfo_children():
            if name in str(widget):
                widget.destroy()

    def create_label_frame(self, row=0, text=""):
        """Create error label frame for the suggestion messages."""
        self._log_label = ttk.LabelFrame(
            self._log_frame, text=text, padding=5, name=text.lower())
        self._log_label.grid(column=0, row=row,
                             pady=5, sticky=tk.W)
        return self._log_label

    def display_msg(self, message: str, color=''):
        """Display message errors with suggestion in the error label frame."""
        ttk.Label(self._log_label, background=color, text=message,
                  style='label.TLabel').grid(column=0, row=self.row_number,
                                             sticky=tk.W)
        self.row_increment()


class MainFrame(tk.Frame):
    """Main Core of the gui."""
    file_names = []

    def __init__(self, parent, audio_class, html_class, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.grid_propagate(False)

        ttk.Label(parent, text='Podcast files:',
                  style='label.TLabel').place(x=5, y=65)

        font_size = 21 if OS_SYSTEM == 'Mac' else 15
        widget_width = 47 if OS_SYSTEM == 'Mac' else 51
        self._text_box = tk.Text(parent, width=widget_width, height=4,
                                 borderwidth=1, relief='sunken',
                                 font=('TkDefaultFont', font_size))
        self._text_box.place(x=5, y=95)

        self.audio = audio_class
        self.html = html_class

        self._file_path = None
        self.error_frame = LogFrame(self)

        self.test_value = tk.IntVar()
        test_btn = ttk.Checkbutton(parent, text='test',
                                   variable=self.test_value)
        test_btn.place(x=7, y=40)

        self._conferm_btn = ttk.Button(parent, text='Conferma e procedi',
                                       state='disabled', command=self._run)
        self._conferm_btn.place(x=230, y=55)

        self._select_btn = ttk.Button(parent, text='Seleziona file',
                                      command=self.files_select)
        self._select_btn.invoke()
        self._select_btn.focus_set()
        self._select_btn.place(x=120, y=55)

    @property
    def select_button(self):
        return self._select_btn

    @select_button.setter
    def select_button(self, value):
        self._select_btn["state"] = value

    @property
    def conferm_button(self):
        return self._conferm_btn

    @conferm_button.setter
    def conferm_button(self, value):
        self._conferm_btn["state"] = value
        self._conferm_btn.focus_set()

    @property
    def text_widget(self):
        """Return the text widget element."""
        return self._text_box

    def tag_text(self, line_num):
        """Create text tags with colors for the text widget."""
        tag_color = self.text_widget.tag_configure
        tag_color(f'c{line_num}', background='tomato')
        tag_color(f'e{line_num}', background='DodgerBlue2')
        tag_color(f'd{line_num}', background='khaki2')
        tag_color(f't{line_num}', background='indian red')
        tag_color(f'l{line_num}', background='turquoise1')
        tag_color(f'p{line_num}', background='green yellow')

    def _tag_color(self, tag):
        """Return the color name for the tag."""
        return self.text_widget.tag_cget(tag, "background")

    def _tag_remove(self, tag):
        """Remove tag from text."""
        self.text_widget.tag_remove(tag, "1.0", "end")

    @property
    def file_path(self):
        """Return file path."""
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        """Set the file path of the current parsing podcast.

        Argument:
            value - {str} - file to be parsed for the path.
        """
        self._file_path = os.path.dirname(value)

    def files_select(self):
        """Select the podcast file to parse."""
        open_file = (os.environ["TEST_FILE"],)

        # open_file = filedialog.askopenfilenames(initialdir=_set_directory())
        try:
            check_folder(open_file[0])
        except IndexError:
            INFO_LOGGER.info("Nessun file selezionato?")
        else:
            self.file_path = open_file[0]
            self._files_validate(open_file)

    def _files_validate(self, open_file):
        """Check whetever the file is just one or more.

        If file is only one then search for other matching file based on the
        _match_lesson() function.
        If file 2 ore more then just grab those.
        """
        if len(open_file) == 1:
            valid_podcasts = [i for i in _match_lesson(open_file[0])]
        elif len(open_file) > 1:
            valid_podcasts = [os.path.basename(i) for i in open_file]

        self._insert_to_text(valid_podcasts)

    def _insert_to_text(self, valid_files):
        """Write file name into text widget."""
        for file in valid_files:
            self.file_names.append(file)
            self.text_widget.insert(tk.INSERT, file + '\n')

        self._parse_lines()

    def _refresh_img_logo(self):
        """refresh which img logo is displayed based on the gui state."""
        # TODO: not currently using
        for widget in self.error_frame.winfo_children():
            if not regex.search(r'logo', str(widget)):
                widget.destroy()

    @property
    def _get_lines(self) -> list:
        """Return a list of the files names written in the text widget.

        Text widgets appends an empty line at the end.
        """
        return [_ for _ in self.text_widget.get('1.0',
                                                'end').splitlines() if _]

    def _parse_lines(self):
        """Iterate over each file name and check for syntax errors if any."""

        def _tag_errors(index_match: tuple, line_num, tag):
            """Add tag to errors in text widget so they can be marked/colored.

            Arguments:
                line_num {int} - current line number in the text widget.
                index_match {tuple(int)} - two int, start to end index word.
                    'regex method .span() works perfect'.
                tag {str} - which tag to mark.
            """
            start, end = index_match
            self.text_widget.tag_add(f'{tag}',
                                     f'{line_num}.{start}',
                                     f'{line_num}.{end}')

        def _check_course_errors(filename: str, line_num: int):
            """Check for errors in the course name.

            Arguments:
                filename {str} - filename to parse for errors.
                line_num {int} - the current line number in the text widget.
            """
            course_match = regex.search(r'^[A-Z]{3}', filename, regex.I)
            tag = f"c{line_num}"
            if course_match.group() not in COURSES_NAMES:
                _tag_errors(course_match.span(), line_num, tag)
                self.error_frame.display_msg(
                    get_similar_words(course_match.group(), "c"),
                    self._tag_color(tag))
            else:
                self._tag_remove(tag)

        def _check_edition_errors(filename, line_num):
            """Check for errors in the edition section.

            Arguments:
                filename {str} - filename to parse for errors.
                line_num {int} - the current line number in the text widget.
            """
            edition_match = regex.search(r'''
                        (?<=^[A-Z]{3})
                        ([A-Z]{1,3}|\d{1,3})
                        (?=_)''', filename, regex.I | regex.X)
            tag = f"e{line_num}"
            if not edition_match:
                self.error_frame.display_msg(f"- ? manca edizione corso")
            else:
                self._tag_remove(tag)

        def _check_date_errors(filename, line_num):
            """Check for errors in the date section.

            If no match is made by the first regex, fallback to the second
            where it will find any 6 to 8 digits long numbers.

            Arguments:
                filename {str} - filename to parse for errors.
                line_num {int} - the current line number in the text widget.
            """
            date_match = regex.search(r'''
                                    20[1-3][0-9]
                                    (?(?=0)0[1-9]|1[0-2])
                                    (?(?=3)(3[0-1])|[0-2][0-9])
                                    ''', filename, regex.X)
            fallback = regex.compile(r'\d{6,8}')

            tag = f"d{line_num}"

            if not date_match:
                numbers_match = fallback.search(filename)
                _tag_errors(numbers_match.span(), line_num, tag)

                # TODO when refreshing the error this fails
                # file_path = os.path.join(self.file_path, filename)
                # compare_date = get_date(file_path=file_path)

                self.error_frame.display_msg(
                    f'- {numbers_match.group()} -> {"compare_date"}',
                    self._tag_color(tag))
            else:
                self._tag_remove(tag)

        def _check_teacher_errors(filename, line_num):
            """Check for errors in the teacher name.

            Arguments:
                filename {str} - filename to parse for errors.
                line_num {int} - the current line number in the text widget.
            """
            teacher_match = regex.search(r'(?<=_)[A-Z]_[A-Za-z]+', filename)

            tag = f"t{line_num}"

            if teacher_match.group() not in TEACHERS_NAMES:
                _tag_errors(teacher_match.span(), line_num, tag)
                self.error_frame.display_msg(
                    get_similar_words(teacher_match.group(), "t"),
                    self._tag_color(tag))
            else:
                self._tag_remove(tag)

        def _check_lesson_errors(filename, line_num):
            """Check for errors in the lesson section.

            If no match is made by the first regex, fallback to the second
            where it will find any word starting by L.

            Arguments:
                filename {str} - filename to parse for errors.
                line_num {int} - the current line number in the text widget.
            """
            lesson_match = regex.compile(r'(L|l)ezione_\d{1,2}(?=_)', regex.I)
            fallback = regex.compile(r'(?<=_)L[a-z]+(?=_\d{1,2})', regex.I)

            tag = f"l{line_num}"

            if not lesson_match.search(filename):
                word_match = fallback.search(filename)
                _tag_errors(word_match.span(), line_num, tag)
                self.error_frame.display_msg(
                    f"- {word_match.group()} -> Lezione",
                    self._tag_color(tag))
            else:
                self._tag_remove(tag)

        def _check_part_errors(filename, line_num):
            """Check for errors in the part section.

            If no match is made by the first regex, fallback to the second
            where it will find any word starting by P.

            Arguments:
                filename {str} - filename to parse for errors.
                line_num {int} - the current line number in the text widget.
            """
            part_match = regex.compile(r'(P|p)arte_\d(?=\.)', regex.I)
            fallback = regex.compile(r'(?<=_)P[a-z].+?(?=_\d)', regex.I)

            tag = f"p{line_num}"

            if not part_match.search(filename):
                word_match = fallback.search(filename)
                _tag_errors(word_match.span(), line_num, tag)
                self.error_frame.display_msg(
                    f"- {word_match.group()} -> Parte", self._tag_color(tag))
            else:
                self._tag_remove(tag)

        for index, file in enumerate(self._get_lines, 1):
            self.error_frame.create_label_frame(row=index + 1,
                                                text=f'Linea {index}:')
            self.tag_text(index)
            try:
                _check_course_errors(file, index)
                _check_edition_errors(file, index)
                _check_date_errors(file, index)
                _check_teacher_errors(file, index)
                _check_lesson_errors(file, index)
                _check_part_errors(file, index)

            except Exception as error:
                INFO_LOGGER.debug('--> DEBUG error: %s', error, exc_info=True)
                _message_box(f'Nome irriconoscibile per suggerimenti: {file}')

        self._check_error_tag()

    def _text_errors(self):
        """Check if there are any errors in the text widget.

        Return:
            True {bool} - if there are errors.
            False {bool} - if there are no errors.
        """
        errors = []
        for tag in self.text_widget.tag_names():
            if tag != "sel" and self.text_widget.tag_nextrange(f'{tag}', 1.0):
                errors.append(tag)
        return errors

    def _check_error_tag(self):
        if self._text_errors():
            self.error_frame.insert_img(get_image("x"))
            self._refresh_frame()

        if not self._text_errors():
            self.error_frame.refresh_widgets("errori")

            self.conferm_button = 'active'
            self.select_button = 'disabled'
            self.text_widget['state'] = 'disabled'

            self.error_frame.insert_img(get_image("ok"))

    def _refresh_frame(self):
        """Create the refresh button if there are any errors."""
        refresh_frame = self.error_frame.create_label_frame(
            row=1, text="ERRORI TROVATI!")
        ttk.Button(refresh_frame, text='Refresh', command=self.refresh).pack()

    def refresh(self):
        """Method to be called from refresh button.

        Clean the error widget and restart the parsing of text widget lines.
        """
        self.error_frame.refresh_widgets("linea")
        self._parse_lines()

    def process_files(self):
        """Return a list of the file to be processed by the final script."""
        valid_files = [os.path.join(self.file_path, i)
                       for i in self._get_lines if i]
        return valid_files

    def _run(self):
        """Run the podcastool main script when button is pressed."""
        self._rename_files()

        podcasttools.ERROR_FRAME = self.error_frame
        podcasttools.TKINTER = self

        for file in self.process_files():
            podcast = PodcastFile(file)
            podcast.generate_podcast(bitrate=self.audio.bitrate,
                                     sample_rate=self.audio.sample_rate,
                                     num_cuts=self.audio.watermark_num)

        for file in podcast.files_to_upload():
            upload_to_server(file["path"], file["server_path"],
                             test_env=self.test_value.get())

        generate_html(podcast.html_page)

        self.conferm_button = 'disable'

        self.html.copy_button = "normal"
        self.html.preview_button = "normal"
        self.html.status('Pronto', 'green')

        _message_box('Done!')

    def _rename_files(self):
        """Rename the wrong typed podcast names."""
        for old, new in zip(self.file_names, self._get_lines):
            if old != new:
                LOGGER.debug('renaming from %s to %s', old, new)
                old_name = os.path.join(self.file_path, old)
                new_name = os.path.join(self.file_path, new)
                os.rename(old_name, new_name)
