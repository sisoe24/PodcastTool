"""GUI interface of PodcastTool."""
import os
import json
import pathlib
import logging
import datetime
import platform
import subprocess

from functools import partial
from difflib import get_close_matches

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

import regex
import pyperclip
from PIL import Image, ImageTk
from dotenv import load_dotenv, find_dotenv

from podcasttool import util
from podcasttool import podcasttools
from podcasttool import PodcastFile, upload_to_server, generate_html


if platform.system() == 'Darwin':
    OS_SYSTEM = 'Mac'
elif platform.system() == 'Linux':
    OS_SYSTEM = 'Linux'
else:
    print('sorry your OS is not supported')

# search and load .env file
load_dotenv(find_dotenv())

LOGGER = logging.getLogger('podcast_tool.gui')
INFO_LOGGER = logging.getLogger('status_app.gui')

CATALOG_NAMES = util.catalog_names()
COURSES_NAMES = CATALOG_NAMES['corsi'].keys()
TEACHERS_NAMES = CATALOG_NAMES['docenti'].keys()


def _match_lesson(podcast_file):
    """Search for same podcast lesson in directory."""
    path = pathlib.Path(podcast_file)
    date_selected_file = get_file_date(path, lesson_check=True)
    lezione_search = "_".join(path.name.split('_')[4:6])

    try:
        _, num = regex.search(r'([L|l]\w+)_(\d)', lezione_search).groups()
        LOGGER.debug('extracting lesson number: %s', lezione_search)
    except AttributeError:
        LOGGER.critical('something went totally wrong no match found')
        INFO_LOGGER.critical('Controlla log/errors.log')
        exit()

    for file in sorted(path.parent.glob('*wav')):
        # for file in sorted(path.parent.iterdir()):
        lezione_check = "_".join(file.name.split('_')[4:6])

        valid_lesson = regex.search(r'[L|l]\w+_' + num, lezione_check)
        file_vecchio = regex.search(r'vecchio', file.name)

        date_file = get_file_date(file, lesson_check=True)
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


def get_file_date(file_path: str, date='', lesson_check='') -> str:
    """Check if the written date is the same as the last modification date.

    If not then suggests to the user if he wants to automatically correct.

    Arguments:
        file_path {str} -- path of the file to check the date.
        date {str} -- the numeric date to make the comparison

    Returns:
        {str} -- a numeric date.

    """
    # get creation_time
    if OS_SYSTEM == 'Mac':
        create_time = os.stat(file_path).st_birthtime
    elif OS_SYSTEM == 'Linux':
        create_time = os.stat(file_path).st_ctime

    # get last_mod_time
    mod_time = os.path.getmtime(file_path)
    if lesson_check:
        human_date = str(datetime.datetime.fromtimestamp(create_time))
        date, _ = human_date.split(' ')
        return date

    file_attr = {}
    file_attr['last_mod_time'] = mod_time
    file_attr['creation_time'] = create_time
    file_attr['written_date'] = date

    for key, value in file_attr.items():
        if key == 'written_date':
            formatted_date = value
        else:
            human_date = datetime.datetime.fromtimestamp(value)
            formatted_date = human_date.strftime('%Y.%m.%d')
        file_attr[key] = formatted_date

    # get today date
    today = datetime.datetime.today().strftime('%Y.%m.%d')

    today_msg = f'oggi [{today}] '
    creation_msg = f'creato [{file_attr["creation_time"]}] '
    modified_msg = f'modificato [{file_attr["last_mod_time"]}]'

    return today_msg + creation_msg + modified_msg


def archive_files():
    """Get all the html archives files."""
    path = pathlib.Path(util.get_path('archive')).glob('*html')
    for file in sorted(path):
        yield file


def last_archive_created():
    """Get the last created html file from the archive directory.

    Returns:
        {str} -- file path of the last html page.

    """
    mod = {file: os.stat(file).st_mtime for file in archive_files()}
    for filepath, mtime in mod.items():
        if mtime == max(mod.values()):
            return filepath
    return None


def delete_archive():
    """Delete all the html archive files."""
    # XXX currently is not begin used anymore. I could move it to util?
    prompt = messagebox.askyesno(
        title='Conferma', message='Cancellare tutto l\'archivio. Sei sicuro?')
    if prompt:
        for i in archive_files():
            os.remove(i)
        messagebox.showinfo(title='Conferma', message='Archivio cancellato!')


def get_imagex() -> tuple():
    """Get images from image directory.

        warning image = index 0
        x image       = index 1
        ok image      = index 2
        logo          = index 3
        icon app      = index 4
        sorry image   = index 5

    Returns:
        [tuple] -- tuple list of images absolute path

    """

    img_directory = util.get_path("include/img")
    img_list = pathlib.Path(os.path.join(img_directory)).glob('*png')
    return [i for i in sorted(img_list)]


def get_image(img):
    image_dict = {
        "warning": "", "x": "", "ok": "", "logo": "", "icon": "", "sorry": ""
    }
    for image in zip(image_dict.keys(), get_imagex()):
        image_dict[image[0]] = image[1]
    # return image_dict[img]
    return ImageTk.PhotoImage(Image.open(image_dict[img]))


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


class CatalogFrame(tk.Frame):
    """Catalog page of the gui."""
    _catalog_list = CATALOG_NAMES
    _updated_names = {}

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        _catalog_frame = ttk.Frame(self, width=420, height=800)
        _catalog_frame.grid(column=0, row=0, rowspan=2)

        _options_frame = ttk.Frame(self, width=300, height=500)
        _options_frame.grid(column=1, row=0, sticky=tk.N)
        _options_frame.grid_propagate(False)

        self._tree_list = ttk.Treeview(_catalog_frame, height=24,
                                       columns=("names_short", "names_long"))
        self._tree_list.grid(column=0, row=0, columnspan=3, rowspan=3)
        self._generate_tree_columns()

        # load list frame
        _label_lista = ttk.LabelFrame(_options_frame, text="Liste nomi")
        _label_lista.grid(column=3, row=0, sticky=tk.NW)

        self._selected_catalog = ttk.Combobox(_label_lista,
                                              value=["docenti", "corsi"],
                                              width=10, state="readonly")
        self._selected_catalog.grid(column=0, row=0, pady=10, sticky=tk.E)

        ttk.Button(_label_lista, text="Carica lista",
                   command=self._load_catalog).grid(column=1, row=0, padx=10)

        # insert new frame
        _insert_frame = ttk.LabelFrame(_options_frame,
                                       text="Aggiungi nuovo nome")
        _insert_frame.grid(column=3, row=1, sticky=tk.N)

        ttk.Label(_insert_frame, text="abbr.").grid(column=0, row=1,
                                                    sticky=tk.W)
        self._short_name = ttk.Entry(_insert_frame)
        self._short_name.grid(column=1, row=1)

        ttk.Label(_insert_frame, text="intero").grid(column=0, row=2,
                                                     sticky=tk.W)
        self._long_name = ttk.Entry(_insert_frame)
        self._long_name.grid(column=1, row=2)

        ttk.Label(_insert_frame, text="lang").grid(column=0, row=3,
                                                   sticky=tk.W)
        self._lang_select = ttk.Combobox(_insert_frame, value=["it", "en"],
                                         state="readonly", width=5)
        self._lang_select.grid(column=1, row=3, sticky=tk.W)
        self._lang_select.current(0)

        ttk.Button(_insert_frame, text="Aggiungi",
                   command=self._insert_to_catalog).grid(column=1, row=3,
                                                         sticky=tk.E)

        self._btn_save = ttk.Button(_options_frame, text="Salva modifiche",
                                    state="disabled",
                                    command=self._save_new_catalog)
        self._btn_save.grid(column=3, row=2, pady=15)

        ttk.Button(_options_frame, text="Cancella nome selezionato",
                   command=self._delete_selected).grid(column=3, row=3)

    @property
    def save_button(self):
        """Get save button state."""
        return self._btn_save["state"]

    @save_button.setter
    def save_button(self, value):
        """Set save button state."""
        self._btn_save["state"] = value

    @property
    def _language(self):
        """Return the language selected: it or eng."""
        return self._lang_select.get()

    def _course_name_size(self, course_name):
        """Check if name course is 3 letters long otherwise raise error."""
        if self.get_catalog == "corsi" and not len(course_name) == 3:
            raise ValueError("Course name has to be 3 letters long")

    def _generate_tree_columns(self):
        """Generate columns for the treeview widget."""
        self._tree_list["show"] = "headings"
        self._tree_list.heading('names_short', text='Nome abbreviato')
        self._tree_list.column('names_short', width=150)
        self._tree_list.heading('names_long', text='Nome intero')
        self._tree_list.column('names_long', width=300)

        self._tree_list.tag_configure("oddrow", background='gray90')
        self._tree_list.tag_configure("evenrow", background='gray99')

    @property
    def get_catalog(self):
        """Return the catalog name selected from the combobox widget."""
        return self._selected_catalog.get()

    def _refresh_list(self):
        """Refresh (delete) list in treeview widget when loading other list."""
        self._tree_list.delete(*self._tree_list.get_children())

    def _load_catalog(self):
        """Load name list into treeview widget."""
        self._refresh_list()

        # self._btn_insert["state"] = "active"

        row_colors = ["oddrow", "evenrow"]
        catalog_names = sorted(self._catalog_list[self.get_catalog].items())
        for index, names in enumerate(catalog_names):
            if index % 2 == 0:
                self._tree_list.insert('', index, names[0],
                                       tags=(row_colors[index - index]))
            else:
                self._tree_list.insert('', index, names[0],
                                       tags=(row_colors[index - index + 1]))

            self._tree_list.set(names[0], 'names_short', names[0])
            try:
                self._tree_list.set(names[0], 'names_long',
                                    names[1]["course_name"])
            except TypeError:
                self._tree_list.set(names[0], 'names_long', names[1])

    def _delete_selected(self):
        """Delete selected element from treeview widget."""
        try:
            selected_item = self._tree_list.selection()[0]
        except IndexError:
            messagebox.showinfo(title="Cancella",
                                message="Nessun nome selezionato")
            return
        confirm = messagebox.askyesno(title="Cancella selezione",
                                      message=(f"Cancellare: {selected_item}?")
                                      )
        if confirm:
            self._tree_list.delete(selected_item)
            self._delete_from_catalog(selected_item)
            self.save_button = "active"

    def _delete_from_catalog(self, delete_key):
        """Delete key from class catalog list."""
        self._catalog_list[self.get_catalog].pop(delete_key)

    def _get_new_names(self):
        """Return a tuple with new names to insert taken from Entry widget.

        Return:
            tuple - short_name and long_name variables.
        """
        if not self._short_name.get() or not self._long_name.get():
            messagebox.showinfo(title="Errore", message="Nome invalido")
            return None

        _ = self._short_name.get().strip()

        # TODO: should do better checking of typos example:
        # if there are two spaces then it will insert 2 trailing
        if self.get_catalog == "docenti":
            short_name = _.replace(" ", "_").title()
        else:
            short_name = _.replace(" ", "_").upper()
        del _

        long_name = self._long_name.get().strip().title()
        return (short_name, long_name)

    def _insert_to_catalog(self):
        """Insert new name into treeview widget."""

        try:
            short_name, long_name = self._get_new_names()
            self._course_name_size(short_name)
            self._tree_list.insert("", 0, short_name)

        except TypeError:
            messagebox.showinfo(title="Errore",
                                message="Nessun nome inserito")

        except tk._tkinter.TclError:
            messagebox.showerror(title="Errore", message="Nome esiste già!")

        except ValueError:
            messagebox.showerror(
                title="nome corso",
                message="Nome del corso dovrebbe avere solo 3 lettere")
        else:
            self._tree_list.set(short_name, 'names_short', short_name)
            self._tree_list.set(short_name, 'names_long', long_name)

            if self.get_catalog == "docenti":
                self._catalog_list[self.get_catalog].update(
                    {short_name: long_name})

            else:
                self._catalog_list[self.get_catalog].update(
                    {short_name: {"course_name": long_name}})

            self._updated_names[self.get_catalog] = [long_name, self._language]
            self.save_button = "active"

    def _save_new_catalog(self):
        """Save new verison of catalog after delete or added new names."""
        with open(util.catalog_file(), "w") as json_file:
            json.dump(self._catalog_list, json_file, indent=True)
        if self._updated_names:
            self._update_audio_library()
        messagebox.showinfo(title="", message="Modifiche salvate!")

    def _update_audio_library(self):
        """Update audio library with deleting or adding the modifications."""
        for category, list_ in self._updated_names.items():
            name, lang = list_
            file_name = name.replace(" ", "_")
            util.generate_audio_clip(name, file_name,
                                     f"include/audio/{category}", lang)


class HtmlFrame(tk.Frame):
    """Html section of the gui."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._html_frame = ttk.Frame(self, width=300, height=90)
        self._html_frame.grid(column=2, row=3, sticky=tk.N)
        self._html_frame.grid_propagate(False)

        self._copy_btn = ttk.Button(self._html_frame, text='Copy HTML',
                                    state='disabled', command=self._copy_html)
        self._copy_btn.grid(column=3, row=1, padx=20)

        open_web = partial(self._open_link, 'web')
        ttk.Button(self._html_frame, text='Apri website',
                   command=open_web).grid(column=3, row=2, pady=5)

        open_preview = partial(self._open_link, 'preview')
        self._preview_btn = ttk.Button(self._html_frame, text='Preview HTML',
                                       state='disabled', command=open_preview)
        self._preview_btn.grid(column=1, row=2)

        status_font = 20 if OS_SYSTEM == 'Mac' else 14
        self.status_var = tk.StringVar(value="Non pronto")
        self._status_display = tk.Label(self._html_frame,
                                        textvariable=self.status_var,
                                        font=('TkDefaultFont', status_font))
        self._status_display.grid(column=1, row=1)
        self._status_display.configure(background="red")

        self._labels()

    def status(self, status, color):
        """Display html status message on gui

        Arguments:
            status {str} - the message to be displayed.
            color {str} - name of the background color(e.g. red, green, blue).
        """
        self.status_var.set(status)
        self._status_display.configure(background=color)

    def _labels(self):
        """Generate labels for the html frame."""
        ttk.Label(self._html_frame, text='HTML',
                  style='label.TLabel').grid(column=0, row=0, sticky=tk.W)
        ttk.Label(self._html_frame, text='Status:    ').grid(column=0, row=1)
        ttk.Label(self._html_frame, text='Web: ').grid(column=0, row=2,
                                                       sticky=tk.W)

    @property
    def preview_button(self):
        """Return copy button state."""
        return self._preview_btn["state"]

    @preview_button.setter
    def preview_button(self, value):
        """Set preview button state."""
        self._preview_btn["state"] = value

    @property
    def copy_button(self):
        """Return copy button state."""
        return self._copy_btn["state"]

    @copy_button.setter
    def copy_button(self, value):
        """Set copy button state."""
        self._copy_btn["state"] = value

    def _copy_html(self):
        """Copy the main page generated after the script is completed."""
        with open(last_archive_created()) as html_file:
            pyperclip.copy(html_file.read())
        self.status('Copiato', 'RoyalBlue1')
        self.bell()

    @staticmethod
    def _open_link(page: str):
        """Open website or preview html page."""
        if page == 'web':
            open_link = 'http://www.fonderiesonore.it/elearning/'
        elif page == 'preview':
            open_link = last_archive_created()

        if OS_SYSTEM == 'Mac':
            subprocess.run(['open', open_link])
        elif OS_SYSTEM == 'Linux':
            subprocess.run(['xdg-open', open_link])


class AudioFrame(tk.Frame):
    """Audio section frame of the gui."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._audio = ttk.Frame(self, width=300, height=100)
        self._audio.grid(column=2, row=2, rowspan=2, sticky=tk.N)
        self._audio.grid_propagate(False)

        self._watermarks = ttk.Combobox(self._audio, width=4,
                                        value=self._watermarks_list(),
                                        state='readonly')
        self._watermarks.grid(column=1, row=1, sticky=tk.E)
        self._watermarks.current(0)

        self._bitrate = ttk.Combobox(self._audio, width=4,
                                     value=self._bitrate_list(),
                                     state='readonly')
        self._bitrate.grid(column=1, row=2, pady=2, sticky=tk.E)
        self._bitrate.current(1)

        self._sample_rate = ttk.Combobox(self._audio, width=7,
                                         value=self._sample_rate_list(),
                                         state='readonly')
        self._sample_rate.grid(column=1, row=3)
        self._sample_rate.current(0)

        self._labels()

    def _labels(self):
        """Generate labels for audio frame."""
        ttk.Label(self._audio, text='Audio',
                  style='label.TLabel').grid(column=0, row=0, sticky=tk.W)
        ttk.Label(self._audio, style='audio.TLabel',
                  text='Watermarks:   ').grid(column=0, row=1, sticky=tk.W)
        ttk.Label(self._audio, text='Bitrate:',
                  style='audio.TLabel').grid(column=0, row=2, sticky=tk.W)
        ttk.Label(self._audio, text='Sample rate:',
                  style='audio.TLabel').grid(column=0, row=3, sticky=tk.W)
        ttk.Label(self._audio, text='Sample rate:',
                  style='audio.TLabel').grid(column=0, row=3, sticky=tk.W)

    @staticmethod
    def _watermarks_list() -> list:
        """Generate a list to populate watermark_num combobox."""
        nums = [_ for _ in range(2, 9)]
        nums.insert(0, "auto")
        return nums

    @staticmethod
    def _bitrate_list() -> list:
        """Generate a list to populate bitrate combobox.

        Common audio birate:
            - 32k or 64k – generally acceptable only for speech
            - 96k – generally used for speech or low-quality streaming
            - 128k or 160k – mid-range bitrate quality
            - 192k – medium quality bitrate
            - 256k – a commonly used high-quality bitrate
            - 320k – highest level supported by the MP3 standard
        """
        return ['32k', '64k', '128k', '192k', '256k', '320k']

    @staticmethod
    def _sample_rate_list() -> list:
        """Generate a list to populate bitrate combobox."""
        return ['22050Hz', '44100Hz']

    @property
    def bitrate(self) -> str:
        """Return bitrate from options."""
        return self._bitrate.get()

    @property
    def sample_rate(self) -> str:
        """Return sample rate from options without the Hz."""
        return self._sample_rate.get().replace('Hz', '')

    @property
    def watermark_state(self) -> str:
        """Get watermark_toggle check button state."""
        return self._watermarks.get()

    @property
    def watermark_num(self) -> int:
        """Return number of cuts to make in audio from options."""
        if not self.watermark_state == "auto":
            return int(self._watermarks.get())
        return None


class ErrorFrame(tk.Frame):
    """Error section of the gui."""
    _row_number = 0

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.grid_propagate(False)

        self._error_frame = ttk.Frame(parent, borderwidth=3, relief='sunken',
                                      width=670, height=360)
        self._error_frame.grid(column=0, row=0, rowspan=2, columnspan=2,
                               sticky=tk.N)
        self._error_frame.grid_propagate(False)

        # creating this and assigning it to None because of the create_label_frame
        # methodo in which I need to referencing it and pylint gives me error
        # if i dont declarate on the init method.
        # dont like it though should fine better solution
        self._error_label = None

        self._label_img = ttk.Label(self._error_frame, name='logo', width=500)
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
        for widget in self._error_frame.winfo_children():
            if name in str(widget):
                widget.destroy()

    def create_label_frame(self, row=0, text=""):
        """Create error label frame for the suggestion messages."""
        self._error_label = ttk.LabelFrame(
            self._error_frame, text=text, padding=5, name=text.lower())
        self._error_label.grid(column=0, row=row,
                               pady=5, sticky=tk.W)
        return self._error_label

    def display_errors(self, message: str, color=''):
        """Display message errors with suggestion in the error label frame."""
        ttk.Label(self._error_label, background=color, text=message,
                  style='label1.TLabel').grid(column=0, row=self.row_number,
                                              sticky=tk.W)
        self.row_increment()


class MainFrame(tk.Frame):
    """Main Core of the gui."""
    file_names = []

    def __init__(self, parent, audio_class, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.grid_propagate(False)

        ttk.Label(parent, text='Podcast files:',
                  style='label.TLabel').place(x=5, y=65)

        font_size = 21 if OS_SYSTEM == 'Mac' else 15
        widget_width = 47 if OS_SYSTEM == 'Mac' else 51
        self._text_box = tk.Text(parent, width=widget_width, height=4,
                                 borderwidth=1, relief='sunken',
                                 font=('TkDefaultFont', font_size))
        self._text_box.place(x=5, y=90)

        self.audio = audio_class

        self.html = HtmlFrame(parent, width=300, height=100)
        self.html.place(x=390, y=0)

        self._file_path = None
        self.error_frame = ErrorFrame(self)

        self.test_value = tk.IntVar()
        test_btn = ttk.Checkbutton(parent, text='test',
                                   variable=self.test_value)
        test_btn.place(x=7, y=40)

        self._conferm_btn = ttk.Button(parent, text='Conferma e procedi',
                                       state='disabled', command=self._run)
        self._conferm_btn.place(x=230, y=55)

        self._select_btn = ttk.Button(parent, text='Seleziona file',
                                      command=self.files_select)
        # self._select_btn.invoke()
        self._select_btn.focus_set()
        self._select_btn.place(x=120, y=55)

    @property
    def select_button(self):
        return self._selected_btn

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
        # open_file = (
        # "/Users/virgilsisoe/.venvs/PodcastTool/other/Scrivania/Podcast/ALP/MULO/MUL6_20130823_J_Lattanzio_Lezione_4_parte_2.wav",)
        open_file = filedialog.askopenfilenames(initialdir=_set_directory())
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
        for widget in self._error_frame.winfo_children():
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
                self.error_frame.display_errors(
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
                self.error_frame.display_errors(f"- ? manca edizione corso")
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
                # compare_date = get_file_date(file_path=file_path,
                #                              date=numbers_match.group())

                self.error_frame.display_errors(
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
                self.error_frame.display_errors(
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
                self.error_frame.display_errors(
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
                self.error_frame.display_errors(
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
                INFO_LOGGER.debug(
                    f'--> DEBUG error: {error} <--', exc_info=True)
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
            INFO_LOGGER.info('Nessun Errore!')

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


class MainPage(tk.Tk):
    """Main window frame."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('PodcastTool 2.2')

        app_x = 685
        app_y = 600

        style_1 = ttk.Style()
        style_1.theme_use('default')
        style_1.configure('label.TLabel', font=('TkDefaultFont', 19, 'bold'))

        # - position window center screen - #
        position_height = self.winfo_screenheight() // 2 - (app_y // 2)
        # position_width = self.winfo_screenwidth() // 2 - (app_y // 2)
        self.geometry(f'{app_x}x{app_y}-{100}+{position_height}')

        # >>>> on linux I have decided to put the app on the top right corner
        # because it needs the terminal to be open at the same time:
        # position_width = self.winfo_screenwidth()
        # self.geometry(f'{app_x}x{app_y}-{position_width}+{0}')

        self.resizable(width=False, height=False)

        window_main = ttk.Notebook(self, width=1000, height=600)
        # window_main.grid_propagate(False)

        # main page frame
        _page_main = ttk.Frame(window_main, width=1000, height=600)
        _page_main.grid(column=0, row=0)
        _page_main.grid_propagate(False)
        window_main.add(_page_main, text='Main')

        # audio page frame
        _page_audio = ttk.Frame(window_main, width=1000, height=600)
        _page_audio.grid(column=0, row=0)
        _page_audio.grid_propagate(False)
        window_main.add(_page_audio, text='Audio')

        # catalogo page frame
        _page_catalog = ttk.Frame(window_main, width=1000, height=600)
        _page_catalog.grid(column=0, row=0)
        _page_catalog.grid_propagate(False)
        window_main.add(_page_catalog, text='Catalogo Nomi')

        audio_class = AudioFrame(_page_audio)
        audio_class.grid(column=0, row=0)
        MainFrame(_page_main, audio_class, width=670,
                  height=360).place(x=5, y=210)
        CatalogFrame(_page_catalog).grid(column=0, row=0)
        self._labels_style()

        # self.ops_image(_page_audio)
        ttk.Label(_page_audio, text='OPS :(\nWORK IN PROGRESS.',
                  style='options.TLabel').place(x=50, y=100)
        # ===============

        window_main.pack()

        ttk.Button(_page_main, text='Allinea finestre',
                   command=self.align_windows).place(x=5, y=5)

    @staticmethod
    def align_windows():
        """Align terminal window on linux with wmctrl."""
        try:
            subprocess.run(
                ['wmctrl', '-r', 'Terminale', '-e', '0,800,0,600,600'])
        except FileNotFoundError:
            INFO_LOGGER.error('you are probably on mac and this doesnt work')

    def ops_image(self, parent):
        """Show image for work in progress page."""
        sorry_img = ImageTk.PhotoImage(Image.open(get_image()[5]))
        self._label_img = ttk.Label(parent, image=sorry_img, name='logo')
        self._label_img.image = sorry_img
        self._label_img.place(x=150, y=60)

    def _labels_style(self):
        """Create style configuration for labels."""
        default_size = 30
        os_size = default_size if OS_SYSTEM == 'Mac' else default_size - 6
        style = ttk.Style()
        style.theme_use('default')
        style.configure('options.TLabel', font=(
            'TkDefaultFont', os_size, 'bold'))

        default_size1 = 15
        os_size1 = default_size1 if OS_SYSTEM == 'Mac' else default_size1 - 6
        style_1 = ttk.Style()
        style_1.theme_use('default')
        style_1.configure('label.TLabel',
                          font=('TkDefaultFont', os_size1, 'bold'))

        default_size2 = 17
        os_size2 = default_size2 if OS_SYSTEM == 'Mac' else default_size2 - 6
        style_2 = ttk.Style()
        style_2.theme_use('default')
        style_2.configure('label1.TLabel', font=('TkDefaultFont', os_size2,))


def run():
    """Run gui."""
    INFO_LOGGER.info('Applicazione Partita')
    try:
        app = MainPage()
        app.mainloop()
    except Exception as error:
        LOGGER.critical(str(error), exc_info=True)
        INFO_LOGGER.error('Errore app startup. controlla log/errors.log')


if __name__ == '__main__':
    run()
