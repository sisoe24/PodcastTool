import os
import pathlib
import logging

from difflib import get_close_matches

import tkinter as tk
from tkinter import ttk

import regex
# from PIL import Image, ImageTk

from podcasttool import util
from podcasttool import OS_SYSTEM
from podcasttool import CATALOG_NAMES

COURSES_NAMES = CATALOG_NAMES['corsi'].keys()
TEACHERS_NAMES = CATALOG_NAMES['docenti'].keys()

LOGGER = logging.getLogger('podcast_tool.gui.main')
INFO_LOGGER = logging.getLogger('status_app.gui.main')


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


class LogFrame(tk.Frame):
    """Log section of the gui."""
    _row_number = 0

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.grid_propagate(False)

        self._log_frame = ttk.Frame(parent, borderwidth=3, relief='sunken',
                                    width=670, height=360)
        self._log_frame.grid(column=0, row=0, rowspan=2, columnspan=2,
                             sticky=tk.N)
        self._log_frame.grid_propagate(False)

        self._log_label = None

        self._label_img = ttk.Label(self._log_frame, name='logo', width=500)
        # self._label_img.place(x=150, y=10)
        # self.insert_img(get_image("warning"))

    def insert_img(self, img):
        """Insert image in error frame."""
        self._label_img.configure(image=img)
        self._label_img.image = img

    def row_increment(self):
        """Increment row number from the same error label frame.

        In order to display messages on top of eacher other need to increment.
        """
        self._row_number += 1

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

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.grid_propagate(False)

        font_size = 21 if OS_SYSTEM == 'Mac' else 15
        widget_width = 47 if OS_SYSTEM == 'Mac' else 51

        self._text_box = tk.Text(parent, width=widget_width, height=4,
                                 borderwidth=1, relief='sunken',
                                 font=('TkDefaultFont', font_size))
        self._text_box.place(x=5, y=95)

        self.log_frame = LogFrame(self)

        self.podcast_obj = None
        self.confirm_button = None

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

    def insert_text(self):
        """Write file name into text widget."""
        # self.podcast_obj = podcast_object
        for file in self.podcast_obj.podcast_list:
            self.text_widget.insert(tk.INSERT, file + '\n')

        self._parse_lines()

    @property
    def _get_lines(self) -> list:
        """Return a list of the files names written in the text widget.

        Text widgets appends an empty line at the end.
        """
        return [_ for _ in self.text_widget.get('1.0',
                                                'end').splitlines() if _]

    def _parse_lines(self):
        """Iterate over each file name and check for syntax errors if any."""
        for index, file in enumerate(self._get_lines, 1):
            self.log_frame.create_label_frame(row=index + 1,
                                              text=f'Linea {index}:')
            self.tag_text(index)
            try:
                self._check_course_errors(file, index)
                self._check_edition_errors(file, index)
                self._check_date_errors(file, index)
                self._check_teacher_errors(file, index)
                self._check_lesson_errors(file, index)
                self._check_part_errors(file, index)

            except Exception as error:
                LOGGER.critical('no suggestion error: %s',
                                error, exc_info=True)
                open_log(message="Impossibile riconoscere nome")

        self.check_errors()

    def _tag_errors(self, index_match: tuple, line_num, tag):
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

    def _check_course_errors(self, filename: str, line_num: int):
        """Check for errors in the course name.

        Arguments:
            filename {str} - filename to parse for errors.
            line_num {int} - the current line number in the text widget.
        """
        course_match = regex.search(r'^[A-Z]{3}', filename, regex.I)
        tag = f"c{line_num}"
        if course_match.group() not in COURSES_NAMES:
            self._tag_errors(course_match.span(), line_num, tag)
            self.log_frame.display_msg(
                get_similar_words(course_match.group(), "c"),
                self._tag_color(tag))
        else:
            self._tag_remove(tag)

    def _check_edition_errors(self, filename, line_num):
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
            self.log_frame.display_msg(f"- ? manca edizione corso")
        else:
            self._tag_remove(tag)

    def _check_date_errors(self, filename, line_num):
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
            self._tag_errors(numbers_match.span(), line_num, tag)

            # TODO: this may fail because is not parsing the real podcast
            # but just the variabile with the last podcast
            self.log_frame.display_msg(
                f'- {numbers_match.group()} -> {self.podcast_obj.date}',
                self._tag_color(tag))
        else:
            self._tag_remove(tag)

    def _check_teacher_errors(self, filename, line_num):
        """Check for errors in the teacher name.

        Arguments:
            filename {str} - filename to parse for errors.
            line_num {int} - the current line number in the text widget.
        """
        teacher_match = regex.search(r'(?<=_)[A-Z]_[A-Za-z]+', filename)

        tag = f"t{line_num}"

        if teacher_match.group() not in TEACHERS_NAMES:
            self._tag_errors(teacher_match.span(), line_num, tag)
            self.log_frame.display_msg(
                get_similar_words(teacher_match.group(), "t"),
                self._tag_color(tag))
        else:
            self._tag_remove(tag)

    def _check_lesson_errors(self, filename, line_num):
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
            self._tag_errors(word_match.span(), line_num, tag)
            self.log_frame.display_msg(
                f"- {word_match.group()} -> Lezione",
                self._tag_color(tag))
        else:
            self._tag_remove(tag)

    def _check_part_errors(self, filename, line_num):
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
            self._tag_errors(word_match.span(), line_num, tag)
            self.log_frame.display_msg(
                f"- {word_match.group()} -> Parte", self._tag_color(tag))
        else:
            self._tag_remove(tag)

    def _text_errors(self):
        """Get the error tags in the text widget.

        Return:
            True {bool} - if there are errors.
            False {bool} - if there are no errors.
        """
        errors = []
        for tag in self.text_widget.tag_names():
            if tag != "sel" and self.text_widget.tag_nextrange(f'{tag}', 1.0):
                errors.append(tag)
        return errors

    def check_errors(self):
        """Check if there are any errors.
        If yes then enable refresh button and insert x sign img.
        if no then enable confirm button and proceed further.
        """
        if self._text_errors():
            # self.log_frame.insert_img(get_image("x"))
            self._refresh_frame()
        else:
            self.log_frame.refresh_widgets("errori")
            self.text_widget["state"] = "disabled"
            # self.log_frame.insert_img(get_image("ok"))
            self.confirm_button["state"] = "active"

    def _refresh_frame(self):
        """Create the refresh button if there are any errors."""
        refresh_frame = self.log_frame.create_label_frame(
            row=1, text="ERRORI TROVATI!")
        ttk.Button(refresh_frame, text='Refresh', command=self.refresh).pack()

    def refresh(self):
        """Method to be called from refresh button.

        Clean the error widget and restart the parsing of text widget lines.
        """
        self.log_frame.refresh_widgets("linea")
        self._parse_lines()

    def proccesed_files(self):
        """Return a list of the file to be processed by the final script."""
        valid_files = [_ for _ in self._get_lines if _]
        return valid_files
