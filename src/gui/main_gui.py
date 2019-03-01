"""Need major refrectoring here."""
import os
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

import utility
from generate_podcast import PodcastGenerator, ServerUploader, HtmlGenerator

if platform.system() == 'Darwin':
    OS_SYSTEM = 'Mac'
elif platform.system() == 'Linux':
    OS_SYSTEM = 'Linux'
else:
    print('sorry your OS is not supported')

# search and load .env file
load_dotenv(find_dotenv())

# ================== LOGGING ================== #
LOGGER = logging.getLogger('podcast_tool')
LOGGER.setLevel(logging.DEBUG)

FORMATTER = logging.Formatter(
    '%(filename)-20s %(funcName)-25s %(levelname)-10s %(message)s')
CH_FORMATTER = logging.Formatter(
    '[%(levelname)s] - %(module)s:%(lineno)d:%(funcName)s() - %(message)s')

CRITICAL_LOG = logging.StreamHandler()
CRITICAL_LOG.setLevel(logging.WARNING)
CRITICAL_LOG.setFormatter(CH_FORMATTER)
LOGGER.addHandler(CRITICAL_LOG)

LOG_PATH = utility.get_path('log')

DEBUG_LOW = logging.FileHandler(f'{LOG_PATH}/debug_low.log', 'w')
DEBUG_LOW.setLevel(logging.DEBUG)
DEBUG_LOW.setFormatter(FORMATTER)
LOGGER.addHandler(DEBUG_LOW)

COURSES_NAMES = utility.catalog_names()['corsi'].keys()
TEACHERS_NAMES = utility.catalog_names()['docenti'].keys()


def _match_lesson(podcast_file):
    """Search for same podcast lesson in directory."""
    path = pathlib.Path(podcast_file)
    date_selected_file = get_file_date(path, lesson_check=True)
    lezione_search = "_".join(path.name.split('_')[4:6])

    try:
        _, num = regex.search(r'([L|l]\w+)_(\d)', lezione_search).groups()
        LOGGER.debug(f'extracting lesson number: {lezione_search}')
    except AttributeError:
        LOGGER.critical('something went totally wrong no match found')
        exit()

    for file in sorted(path.parent.glob('*wav')):
        # for file in sorted(path.parent.iterdir()):
        lezione_check = "_".join(file.name.split('_')[4:6])

        valid_lesson = regex.search(r'[L|l]\w+_' + num, lezione_check)
        file_vecchio = regex.search(r'vecchio', file.name)

        date_file = get_file_date(file, lesson_check=True)
        if valid_lesson and not file_vecchio:
            if date_file == date_selected_file:
                LOGGER.debug(f'file that match date of creation {file.name}')
                yield str(file.name)


def check_folder(podcast_folder):
    """Check if the folder name is correct otherwise quit."""
    path = os.path.dirname(podcast_folder)
    folder_name = os.path.split(path)[1][:3]
    LOGGER.debug(f'checking if folder name is valid: {folder_name}')

    if folder_name not in COURSES_NAMES:
        msg = f'Nome cartella sbagliato: {folder_name}.'
        LOGGER.critical(f'wrong folder name {folder_name}')
        messagebox.showerror(title='Fatal Error', message=msg)
        exit()


def get_similar_words(wrong_name: str, catalog: str) -> str:
    """If user writes the wrong name try suggesting valid alternative.

    Arguments:
        wrong_name {str} - the not found word that the user has written
        catalog {str} - the type of list in where to search:
                        c = corsi (list of courses)
                        d = docenti (list of teachers)
    If 'c' or 'd' is passed as an argument to type then the check will be done
    thru a list of choices.

    Returns:
        [str] -- return the correct word choosen by the user.

    """
    if catalog == 'c':
        check_list = COURSES_NAMES
    elif catalog == 'd':
        check_list = TEACHERS_NAMES

    similar_name = get_close_matches(wrong_name, check_list, cutoff=0.6)
    possibile_names = [i for i in similar_name]
    choice = f" - {wrong_name} -> {possibile_names}"
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
        human_date = str(datetime.datetime.fromtimestamp(mod_time))
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
    path = pathlib.Path(utility.get_path('archive')).glob('*html')
    for file in sorted(path):
        yield file


def last_archive_created():
    """Get the last created html page from the archive.

    Returns:
        [str] -- file path of the last html page.

    """
    mod = {file: os.stat(file).st_mtime for file in archive_files()}
    for filepath, mtime in mod.items():
        if mtime == max(mod.values()):
            return filepath


def delete_archive():
    """Delete all the html archive files."""
    prompt = messagebox.askyesno(
        title='Conferma', message='Cancellare tutto l\'archivio. Sei sicuro?')
    if prompt:
        for i in archive_files():
            os.remove(i)
        messagebox.showinfo(title='Conferma', message='Archivio cancellato!')


def get_image():
    """Get images from image directory.

    warning_img = index 0
    x_img =       index 1
    ok_img =      index 2
    logo =        index 3

    Returns:
        [tuple] -- tuple with 4 elements

    """
    img_path = pathlib.Path(os.path.join(
        os.path.dirname(__file__), 'img')).glob('*png')
    return [i for i in sorted(img_path)]


class HtmlFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._create_html_frame()

    # HTML WIDGETS
    def _create_html_frame(self):
        html_frame = ttk.Frame(self, width=300, height=210)
        # html_frame = tk.Frame(self, background='red', width=300, height=210)
        html_frame.grid(column=2, row=3, sticky=tk.N)
        html_frame.grid_propagate(False)

        html_label = ttk.Label(html_frame, text='HTML', style='label.TLabel')
        html_label.grid(column=0, row=0, sticky=tk.W)

        html_text = ttk.Label(html_frame, text='Status:    ')
        html_text.grid(column=0, row=1)

        self.status_var = tk.StringVar()
        self.status_var.set('Non Pronto')
        status_font = 20 if OS_SYSTEM == 'Mac' else 14
        self._status_display = tk.Label(html_frame,
                                        textvariable=self.status_var,
                                        font=('TkDefaultFont', status_font))
        self._status_display.grid(column=1, row=1, )

        self._html_status('Non Pronto', 'red')

        self._copy_btn = ttk.Button(html_frame,
                                    text='Copy HTML', state='disabled',
                                    command=self._copy_html)
        self._copy_btn.grid(column=3, row=1, padx=20)

        web_text = ttk.Label(html_frame, text='Web: ')
        web_text.grid(column=0, row=2, sticky=tk.W)

        web = partial(self._open_web, 'web')
        open_web_btn = ttk.Button(html_frame, text='Apri website',
                                  command=web)
        open_web_btn.grid(column=3, row=2, pady=5)

        preview = partial(self._open_web, 'preview')
        self._preview_btn = ttk.Button(html_frame, text='Preview HTML',
                                       state='disabled', command=preview)
        self._preview_btn.grid(column=1, row=2)

        #  ARCHIVE SECTION OF THE HTML FRAME
        html_archive = [i.name for i in archive_files()]

        archive_text = ttk.LabelFrame(html_frame, text='Archive: ')
        archive_text.grid(column=0, columnspan=4, row=3, sticky=tk.W)

        combo_width = 30 if OS_SYSTEM == 'Mac' else 34
        self._archive_combobox = ttk.Combobox(archive_text, value=html_archive,
                                              width=combo_width)
        self._archive_combobox.grid(column=0, columnspan=3, row=0, sticky=tk.W)

        archive_copy = ttk.Button(archive_text, text='copia archivio',
                                  command=self._copy_archive)
        archive_copy.grid(column=2, row=1, pady=5, padx=5, sticky=tk.E)

        del_archive_btn = ttk.Button(archive_text, text='cancella archivio',
                                     command=delete_archive)
        del_archive_btn.grid(column=0, row=1)

        hr1 = ttk.Separator(html_frame, orient='horizontal')
        hr1.grid(column=0, row=4, columnspan=4, pady=10, sticky=tk.EW)

    def _html_status(self, status, color):
        """Show html status message."""
        self.status_var.set(status)
        self._status_display.configure(background=color)

    def _copy_archive(self):
        """Copy the current selected archive html page."""
        selected_html = self._archive_combobox.get()
        file_path = os.path.join(utility.get_path('archive'), selected_html)
        with open(file_path) as file:
            pyperclip.copy(file.read())
        self.bell()

    def _copy_html(self):
        """Copy the main page generated after the script is completed."""
        with open(last_archive_created()) as file:
            pyperclip.copy(file.read())
        self._html_status('Copiato', 'RoyalBlue1')
        self.bell()

    def _open_web(self, page: str):
        """Open website page directly."""
        if page == 'web':
            open_link = 'http://www.fonderiesonore.it/elearning/'
        elif page == 'preview':
            open_link = last_archive_created()

        if OS_SYSTEM == 'Mac':
            subprocess.run(['open', open_link])
        elif OS_SYSTEM == 'Linux':
            subprocess.run(['xdg-open', open_link])


class AudioFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._create_audio_frame()

    def _get_watermark_num(self):
        if self._watermark_toggle.get() == 0:
            self._watermark['state'] = 'readonly'
        elif self._watermark_toggle.get() == 1:
            self._watermark['state'] = 'disabled'

    def _create_audio_frame(self):
        # audio = tk.Frame(self, background='green', width=300, height=100)
        audio = ttk.Frame(self, width=300, height=100)
        audio.grid(column=2, row=2, rowspan=2, sticky=tk.N)
        audio.grid_propagate(False)

        audio_label = ttk.Label(audio, text='Audio',
                                style='label.TLabel')
        audio_label.grid(column=0, row=0, sticky=tk.W)

        # watermarks
        watermark_text = ttk.Label(audio, style='audio.TLabel',
                                   text='Watermarks:   ')
        watermark_text.grid(column=0, row=1, sticky=tk.W)

        nums = [_ for _ in range(2, 9)]
        self._watermark = ttk.Combobox(audio, width=2,
                                       value=nums, state='disabled')
        self._watermark.grid(column=1, row=1, sticky=tk.E)
        self._watermark.current(1)

        auto_watermarks = ttk.Label(audio, text='auto', style='audio.TLabel')
        auto_watermarks.grid(column=2, columnspan=2,
                             padx=25, row=1, sticky=tk.E)

        self._watermark_toggle = tk.StringVar()
        self._watermark_toggle = tk.IntVar(value=1)
        self._watermark_auto = ttk.Checkbutton(audio,
                                               variable=self._watermark_toggle,
                                               command=self._get_watermark_num)
        self._watermark_auto.grid(column=3, row=1, sticky=tk.E)

        # bitrate
        bitrate_label = ttk.Label(audio, text='Bitrate:',
                                  style='audio.TLabel')
        bitrate_label.grid(column=0, row=2, sticky=tk.W)

        bitrate_list = ['32k', '64k', '128k', '192k', '256k', '320k']
        self._bitrate = ttk.Combobox(audio, width=4,
                                     value=bitrate_list,
                                     state='readonly')
        self._bitrate.grid(column=1, row=2, pady=2, sticky=tk.E)
        self._bitrate.current(1)

        # sample rate
        sample_frame_label = ttk.Label(audio, text='Sample rate:',
                                       style='audio.TLabel')
        sample_frame_label.grid(column=0, row=3, sticky=tk.W)

        sample_frame_list = ['22050Hz', '44100Hz']
        self._sample_frame = ttk.Combobox(audio, width=7,
                                          value=sample_frame_list,
                                          state='readonly')
        self._sample_frame.grid(column=1, row=3)
        self._sample_frame.current(1)


class MainCore(tk.Frame):
    valid_podcast = []
    path = ''

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.grid_propagate(False)

        text_font = 21 if OS_SYSTEM == 'Mac' else 15
        text_width = 47 if OS_SYSTEM == 'Mac' else 51
        self._text_box = tk.Text(parent, width=text_width, height=4,
                                 borderwidth=1, relief='sunken',
                                 font=('TkDefaultFont', text_font))
        self._text_box.place(x=5, y=70)

        self._error_frame = ttk.Frame(self, borderwidth=3, relief='sunken',
                                      width=670, height=400)
        self._error_frame.grid(column=0, row=2, rowspan=2, columnspan=2,
                               sticky=tk.N)
        self._error_frame.grid_propagate(False)

        self.test_value = tk.IntVar()
        test_btn = ttk.Checkbutton(parent, text='test mode',
                                   variable=self.test_value)
        test_btn.place(x=10, y=10)

        self.select_btn = ttk.Button(parent, text='Seleziona file',
                                     command=self._get_podcast_files)
        self.select_btn.place(x=575, y=37)

        self._conferm_btn = ttk.Button(parent, text='Conferma e procedi',
                                       state='disabled', command=self._main)
        self._conferm_btn.place(x=780, y=565)

        sign_img = ImageTk.PhotoImage(Image.open(get_image()[0]))
        self._label_img = ttk.Label(parent, image=sign_img)
        self._label_img.image = sign_img
        self._label_img.place(x=760, y=375)

        my_logo = ImageTk.PhotoImage(Image.open(get_image()[3]))
        self._logo_img = ttk.Label(self._error_frame,
                                   name='logo', image=my_logo)
        self._logo_img.image = my_logo
        self._logo_img.place(x=129, y=10)

        self.html = HtmlFrame(parent, width=300, height=100)
        self.html.place(x=700, y=135)

        self.audio = AudioFrame(parent, width=300, height=100)
        self.audio.place(x=700, y=40)

        progress_text = ttk.Label(parent, text='Progress',
                                  style='label.TLabel')
        progress_text.place(x=700, y=320)

        # TODO: need maximum number from podcast files
        self.progress = ttk.Progressbar(parent, maximum=4,
                                        orient=tk.HORIZONTAL,
                                        mode='indeterminate', length=300)
        self.progress.place(x=700, y=350)

    def _get_podcast_files(self):

        if OS_SYSTEM == 'Linux':
            initial_dir = os.path.join(pathlib.Path(
                os.path.dirname(__file__)).home(), 'Scrivania/Podcast')
        else:
            # initial_dir = os.path.join(
            # os.environ['TEST_FILES_FAKE'], 'ALP/ABLO')
            initial_dir = os.path.join(
                os.environ['TEST_FILES_REAL'], 'EMP/SCE4')

        open_file = filedialog.askopenfilename(initialdir=initial_dir)
        check_folder(open_file)

        self.path = os.path.dirname(open_file)

        self.valid_podcast = [i for i in _match_lesson(open_file)]

        if not self.valid_podcast:
            self._message_box('File invalido', exit_script='yes')

        self.insert_text()
        self._check_for_errors()

    def insert_text(self):
        for file in self.valid_podcast:
            self._text_box.insert(tk.INSERT, file + '\n')

    @property
    def get_text_lines(self):
        for line in self._text_box.get('1.0', 'end').splitlines():
            yield line

    def _check_for_errors(self):
        """Iterate over each podcast name and check for syntax error if any."""
        # check and delete if any errors
        for widget in self._error_frame.winfo_children():
            if not regex.search(r'logo', str(widget)):
                widget.destroy()

        # self._podcast_lines = self._text_box.get('1.0', 'end').splitlines()
        row_number = 0
        track_number = 1
        for line in zip(self.get_text_lines, self.valid_podcast):
            self._text_box.tag_remove(f'c{track_number}', '1.0', 'end')

            if line[0]:
                self._error_label_frame(track_number)

                # CORSO
                try:
                    corso = regex.search(r'^[A-Z]{3}', line[0], regex.I)

                    if corso.group() not in COURSES_NAMES:
                        index_c = corso.span()
                        self._text_box.tag_add(
                            f'c{track_number}',
                            f'{track_number}.{index_c[0]}',
                            f'{track_number}.{index_c[1]}')
                        c_msg = get_similar_words(corso.group(), 'c')
                        self._error_msg(track_number, c_msg, row_number)
                        row_number += 1
                except AttributeError:
                    self._message_box(f'Corso irriconoscibile: {line[0]}')

                # EDIZIONE
                edizione = regex.search(r'''
                        (?<=^[A-Z]{3})
                        ([A-Z]{1,3}|\d{1,3})
                        (?=_)''', line[0], regex.I | regex.X)
                if not edizione:
                    # check if there is already a placeholder for the edition
                    # if yes then just leave the tag
                    if self._text_box.get(f'{track_number}.3', f'{track_number}.5') != '__':
                        self._text_box.insert(f'{track_number}.4', '_')
                    self._text_box.tag_add(
                        f'c{track_number}', f'{track_number}.3')
                    e_msg = f"- _ -> manca edizione corso"
                    self._error_msg(track_number, e_msg, row_number)
                    row_number += 1

                # DATA REGISTRAZIONE
                try:
                    valid_data = regex.search(r'''
                                    20[1-3][0-9]
                                    (?(?=0)0[1-9]|1[0-2])
                                    (?(?=3)(3[0-1])|[0-2][0-9])
                                    ''', line[0], regex.X)
                    if not valid_data:
                        data = regex.search(r'\d{6,8}', line[0])
                        index_d = data.span()
                        self._text_box.tag_add(
                            f'c{track_number}',
                            f'{track_number}.{index_d[0]}',
                            f'{track_number}.{index_d[1]}')

                        file_path = os.path.join(self.path, line[1])
                        compare_date = get_file_date(file_path=file_path,
                                                     date=data.group())

                        date_msg = f'- {data.group()} -> {compare_date}'
                        self._error_msg(track_number, date_msg, row_number)
                        row_number += 1
                except AttributeError:
                    self._message_box(f'Data incompleta in {line[0]}')

                # DOCENTE
                try:
                    docente = regex.search(r'(?<=_)[A-Z]_[A-Za-z]+', line[0])

                    if docente.group() not in TEACHERS_NAMES:
                        index_n = docente.span()
                        self._text_box.tag_add(
                            f'c{track_number}',
                            f'{track_number}.{index_n[0]}',
                            f'{track_number}.{index_n[1]}')
                        d_msg = get_similar_words(docente.group(), 'd')
                        self._error_msg(track_number, d_msg, row_number)
                        row_number += 1
                except AttributeError:
                    self._message_box(f'Docente irriconoscibile: {line[0]} ')

                # LEZIONE
                try:
                    valid_lezione = regex.search(
                        r'(L|l)ezione_\d{1,2}(?=_)', line[0], regex.I)
                    if not valid_lezione:
                        lezione = regex.search(
                            r'(?<=_)L[a-z]+(?=_\d{1,2})', line[0], regex.I)
                        index_l = lezione.span()
                        self._text_box.tag_add(
                            f'c{track_number}',
                            f'{track_number}.{index_l[0]}',
                            f'{track_number}.{index_l[1]}')
                        l_msg = f" - {lezione.group()} -> Lezione"
                        self._error_msg(track_number, l_msg, row_number)
                        row_number += 1
                except AttributeError:
                    self._message_box(f'Lezione incompleta in: {line[0]} ',
                                      exit_script='yes')

                # PARTE
                try:
                    valid_parte = regex.search(
                        r'(P|p)arte_\d(?=\.)', line[0], regex.I)
                    if not valid_parte:
                        parte = regex.search(
                            r'(?<=_)P[a-z].+?(?=_\d)', line[0], regex.I)
                        index_p = parte.span()
                        self._text_box.tag_add(
                            f'c{track_number}',
                            f'{track_number}.{index_p[0]}',
                            f'{track_number}.{index_p[1]}')
                        p_msg = f" - {parte.group()} -> Parte"
                        self._error_msg(track_number, p_msg, row_number)
                        row_number += 1
                except AttributeError:
                    self._message_box(f'Parte incompleta in: {line[0]} ',
                                      exit_script='yes')

                self._text_box.tag_configure(
                    f'c{track_number}', background='red')

                track_number += 1
        self._error_check_tag()

    def _error_refresh(self):

        top_error = ttk.Frame(self._error_frame, borderwidth=1, relief='solid')
        top_error.grid(column=0, row=0, columnspan=3, sticky=tk.W + tk.E)
        # top_error.grid_propagate(False)

        error_warning = ttk.Label(top_error, text='Errori trovati!',
                                  style='options.TLabel')
        error_warning.grid(column=0, row=0, columnspan=1, sticky=tk.W)

        refresh_btn = ttk.Button(
            top_error, text='Refresh', command=self._check_for_errors)
        refresh_btn.grid(column=1, row=0, sticky=tk.E)

    def _error_label_frame(self, track_number: str,):
        self._error_line = tk.LabelFrame(self._error_frame,
                                         text=f'Traccia {track_number} suggerimenti',
                                         background='red')
        self._error_line.grid(column=0, row=track_number, pady=5, sticky=tk.W)

    def _error_msg(self, track_number: str, msg: str, row_number: int):
        error_w = ttk.Label(self._error_line, text=msg,
                            style='label1.TLabel')
        error_w.grid(column=0, row=track_number + row_number, sticky=tk.W)

    def _error_check_tag(self):
        errors = 0
        for i in range(1, len(self.valid_podcast) + 1):
            if self._text_box.tag_nextrange(f'c{i}', f'{i}.0'):
                self._conferm_btn['state'] = 'disabled'
                errors += 1

        if errors == 0 and self.valid_podcast:
            self._conferm_btn['state'] = 'normal'
            self._text_box['state'] = 'disabled'
            ok_img = ImageTk.PhotoImage(Image.open(get_image()[2]))
            self._label_img.configure(image=ok_img)
            self._label_img.image = ok_img

        elif errors > 0:
            x_img = ImageTk.PhotoImage(Image.open(get_image()[1]))
            self._label_img.configure(image=x_img)
            self._label_img.image = x_img
            self._error_refresh()

    def test_mode(self):
        pass

    def _main(self):
        """Common audio birate.

            - 32k or 64k – generally acceptable only for speech
            - 96k – generally used for speech or low-quality streaming
            - 128k or 160k – mid-range bitrate quality
            - 192k – medium quality bitrate
            - 256k – a commonly used high-quality bitrate
            - 320k – highest level supported by the MP3 standard
        """
        self._rename_files()
        set_bitrate = self.audio._bitrate.get()
        set_sample = self.audio._sample_frame.get().replace('Hz', '')

        if self.audio._watermark_toggle.get() == 0:
            watermark_n = int(self.audio._watermark.get())
        else:
            watermark_n = ''

        upload_files = [os.path.join(self.path, i)
                        for i in self.get_text_lines if i]

        self.progress.start()
        for file in upload_files:
            self.update()
            podcast = PodcastGenerator(file,
                                       bitrate=set_bitrate,
                                       sample_rate=set_sample,
                                       watermarks=watermark_n)
            exit('exit main ->')
        podcast_list = podcast.uploading_list
        html_data = podcast.html_page_info

        for file in podcast_list:
            self.update()
            ServerUploader(file, self.test_value.get())

        [_[0].append(_[1]) for _ in zip(html_data['audio_parts'].values(),
                                        ServerUploader.uploading_list)]
        # HtmlGenerator(html_data).podcast_file()
        HtmlGenerator(html_data)
        self.progress.stop()

        self.html._copy_btn['state'] = 'normal'
        self.html._preview_btn['state'] = 'normal'

        self.html._html_status('Pronto', 'green')
        self._message_box('Done!')

        # for now deactivate button so it cannot be done again
        # without restarting the script
        self._conferm_btn['state'] = 'disabled'
        self.select_btn['state'] = 'disabled'

    def _rename_files(self):
        """Rename the wrong typed podcast names."""
        for old, new in zip(self.valid_podcast, self.get_text_lines):
            if old != new:
                LOGGER.debug(f'renaming from {old} to {new}')
                old_name = os.path.join(self.path, old)
                new_name = os.path.join(self.path, new)
                os.rename(old_name, new_name)

    @staticmethod
    def _message_box(msg: str, exit_script=''):
        """Message pop up window.

        Arguments:
            msg {str} -- string to print on the message

        Keyword Arguments:
            exit_script {str} -- quits the script if argument is passed
            (default: '')
        """
        if exit_script:
            messagebox.showerror(title='Fatal Error', message=msg)
            exit()
        else:
            messagebox.showerror(title='Process Complete', message=msg)


class MainPage(tk.Tk):
    """Main window frame."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('Podcast Tools')
        app_x = 1000
        app_y = 600

        style_1 = ttk.Style()
        style_1.theme_use('default')
        style_1.configure('label.TLabel', font=('TkDefaultFont', 19, 'bold'))
        # # position window in middle of the screen
        # position_width = self.winfo_screenwidth() // 2 - (app_x // 2)
        # position_height = self.winfo_screenheight() // 2 - (app_y // 2)
        self.geometry(f'{app_x}x{app_y}-{0}+{500}')
        self.resizable(width=False, height=False)

        self.main_frame = ttk.Frame(self, width=1000, height=600)
        self.main_frame.grid(column=0, row=0)
        self.main_frame.grid_propagate(False)

        self.labels()

        self.error_frame = MainCore(self.main_frame, width=670, height=390)
        self.error_frame.place(x=5, y=200)

    def labels(self):
        default_size = 30
        os_size = default_size if OS_SYSTEM == 'Mac' else default_size - 6
        style = ttk.Style()
        style.theme_use('default')
        style.configure('options.TLabel', font=('TkDefaultFont', os_size))

        default_size1 = 19
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

        ttk.Label(self.main_frame, text='Options',
                  style='options.TLabel').place(x=800, y=0)

        # ttk.Label(self.main_frame, text='PodcastTool 2',
        #           style='options.TLabel').place(x=250, y=0)

        ttk.Label(self.main_frame, text='Podcast files:',
                  style='label.TLabel').place(x=5, y=39)


if __name__ == '__main__':
    APP_TOOL = MainPage()
    APP_TOOL.mainloop()
