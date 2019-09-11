"""GUI interface of PodcastTool."""
import os
import logging
import pathlib
import subprocess

from datetime import datetime

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog


from podcasttool.gui import (
    SelectPodcast,
    HtmlFrame,
    AudioExport,
    AudioIntro,
    CatalogFrame,
    MainFrame,
    DevFrame,
)

from podcasttool import util
from podcasttool import OS_SYSTEM
from podcasttool import open_log
from podcasttool import podcasttools
from podcasttool import PodcastFile, upload_to_server, generate_html


LOGGER = logging.getLogger('podcast_tool.gui')
INFO_LOGGER = logging.getLogger('status_app.gui')


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


def align_windows():
    """Align terminal window on linux with wmctrl."""
    try:
        subprocess.run(
            ['wmctrl', '-r', 'Terminale', '-e', '0,800,0,600,600'])
    except FileNotFoundError:
        INFO_LOGGER.error('you are probably on mac and this doesnt work')


class MainPage(tk.Tk):
    """Main window frame."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('PodcastTool 2.2')

        app_x = 685
        app_y = 600

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

        self.clock = ttk.Label(_page_main)
        self.clock.place(x=5, y=0)

        # audio page frame
        _page_audio = ttk.Frame(window_main, width=1000, height=600)
        _page_audio.grid(column=0, row=0)
        _page_audio.grid_propagate(False)
        window_main.add(_page_audio, text='Audio options')
        AudioIntro(_page_audio).grid(column=0, row=0)

        # catalogo page frame
        _page_catalog = ttk.Frame(window_main, width=1000, height=600)
        _page_catalog.grid(column=0, row=0)
        _page_catalog.grid_propagate(False)
        window_main.add(_page_catalog, text='Catalogo Nomi')

        _page_dev = ttk.Frame(window_main, width=1000, height=600)
        _page_dev.grid(column=0, row=0)
        _page_dev.grid_propagate(False)
        window_main.add(_page_dev, text='Dev')

        CatalogFrame(_page_catalog).grid(column=0, row=0)

        self.dev = DevFrame(_page_dev)
        self.dev.grid(column=0, row=0)

        self.audio = AudioExport(_page_audio)
        self.audio.grid(column=1, row=0, sticky=tk.N, padx=5)

        self.html = HtmlFrame(_page_main)
        self.html.place(x=390, y=0)

        self.main_class = MainFrame(_page_main, width=670, height=360)
        self.main_class.place(x=5, y=210)

        window_main.pack()

        # ttk.Button(_page_main, text='Allinea finestre',
        #            command=align_windows).place(x=5, y=5)

        self.podcast_obj = None

        self._conferm_btn = ttk.Button(_page_main, text='Conferma e procedi',
                                       state='disable', command=self._run)
        self._conferm_btn.place(x=105, y=65)

        self._select_btn = ttk.Button(_page_main, text='Seleziona file',
                                      command=self.files_select)
        self._select_btn.invoke()
        self._select_btn.focus_set()
        self._select_btn.place(x=5, y=65)

        self._labels_style()
        self.time()

    def time(self):
        """Clock label for the gui."""
        date = datetime.now().strftime("%d/%m %H:%M:%S")
        self.clock.config(text=date, style="clock.TLabel")
        self.clock.after(1000, self.time)

    def files_select(self):
        """Select the podcast file to parse."""
        # open_files = filedialog.askopenfilenames(initialdir=_set_directory())
        open_files = (os.environ["TEST_FILE"],)
        self.podcast_obj = SelectPodcast(open_files)
        if open_files:
            self.main_class.podcast_obj = self.podcast_obj
            self.main_class.confirm_button = self._conferm_btn
            self.main_class.insert_text()
            self._select_btn["state"] = "disable"

    def _run(self):
        """Run the podcastool main script when button is pressed."""
        self._rename_files()

        podcasttools.ERROR_FRAME = self.main_class.log_frame
        podcasttools.TKINTER = self

        for file in self.main_class.proccesed_files():
            file_path = os.path.join(self.podcast_obj.path, file)
            podcast = PodcastFile(file_path)
            podcast.generate_podcast(bitrate=self.audio.bitrate,
                                     sample_rate=self.audio.sample_rate,
                                     num_cuts=self.audio.watermark_num)

        for file in podcast.files_to_upload():
            upload_to_server(file["path"], file["server_path"],
                             test_env=self.dev.test_env)

        generate_html(podcast.html_page)

        self._conferm_btn["state"] = 'disable'

        self.html.copy_button = "normal"
        self.html.preview_button = "normal"
        self.html.status('Pronto', 'green')

        messagebox.showinfo(title="Done!", message="Done!", icon="info")

    def _rename_files(self):
        """Rename the wrong typed podcast names."""
        old_names = self.podcast_obj.podcast_list
        new_names = self.main_class.proccesed_files()
        for old, new in zip(old_names, new_names):
            if old.split("_")[-1:] == new.split("_")[-1:]:
                if old != new:
                    old_name = os.path.join(self.podcast_obj.path, old)
                    new_name = os.path.join(self.podcast_obj.path, new)
                    os.rename(old_name, new_name)

    @staticmethod
    def _labels_style():
        """Create style configuration for labels."""
        default_size = 17
        os_size = default_size if OS_SYSTEM == 'Mac' else default_size - 6
        style = ttk.Style()
        style.theme_use('default')
        style.configure('label.TLabel', font=('TkDefaultFont', os_size,))

        default_size2 = 25
        os_size2 = default_size2 if OS_SYSTEM == 'Mac' else default_size2 - 6
        clock_style = ttk.Style()
        clock_style.theme_use('default')
        clock_style.configure('clock.TLabel', font=('TkDefaultFont', os_size2))


def run():
    """Run gui."""
    try:
        app = MainPage()
        app.mainloop()
    except Exception as error:
        LOGGER.critical(str(error), exc_info=True)
        open_log(msg="Errore app startup.\nControllare errors.log?")


if __name__ == '__main__':
    run()
