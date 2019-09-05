"""GUI interface of PodcastTool."""
import logging
import platform
import subprocess

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from dotenv import load_dotenv, find_dotenv

from podcasttool import util
from podcasttool.gui import AudioFrame, HtmlFrame, CatalogFrame, MainFrame


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

        CatalogFrame(_page_catalog).grid(column=0, row=0)

        audio_class = AudioFrame(_page_audio)
        audio_class.grid(column=0, row=0)

        html_class = HtmlFrame(_page_main)
        html_class.place(x=390, y=0)

        MainFrame(_page_main, audio_class, html_class, width=670,
                  height=360).place(x=5, y=210)
        self._labels_style()

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

    @staticmethod
    def _labels_style():
        """Create style configuration for labels."""

        default_size = 17
        os_size = default_size if OS_SYSTEM == 'Mac' else default_size - 6
        style = ttk.Style()
        style.theme_use('default')
        style.configure('label.TLabel', font=('TkDefaultFont', os_size,))


def run():
    """Run gui."""
    try:
        app = MainPage()
        app.mainloop()
    except Exception as error:
        LOGGER.critical(str(error), exc_info=True)
        INFO_LOGGER.error('Errore app startup. controlla log/errors.log')


if __name__ == '__main__':
    run()
