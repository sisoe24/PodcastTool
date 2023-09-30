"""GUI interface of PodcastTool."""
import logging
import os
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import filedialog, messagebox, ttk

from .app.version import __version__
from .startup import APP_GEOMETRY, COLORS, RESOURCES_PATH, critical, open_path
from .tools import (PodcastFile, check_server_path, generate_html,
                    upload_to_server)
from .utils import UserConfig, total_time
from .widgets import (AudioFrame, CatalogFrame, HtmlFrame, MainFrame, MenuBar,
                      SelectPodcast)

LOGGER = logging.getLogger('podcasttool.gui')
LOGGER.debug('main current directory: %s', os.path.dirname(__file__))

dev_mode = UserConfig().value('dev_mode', False)


def _set_directory():
    """Set which folder to open.

    Return:
        {str} - path to which directory to open first at gui start.
    """
    # If user is me then open in test files directory.
    if dev_mode:
        samples = os.path.join(RESOURCES_PATH, 'samples', 'ALP')
        initial_dir = UserConfig().value('initial_dir', samples)
    else:
        initial_dir = os.path.join(os.environ['HOME'], 'Scrivania/Podcast')

    LOGGER.debug("Initial directory: %s", initial_dir)

    return initial_dir


def _debug_executor(executor):

    try:
        LOGGER.debug('podcast executor status: %s', executor.result())
    except Exception as err:
        critical(f'Error when creating podcast: {err}')


class CatalogPage(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        CatalogFrame(self).pack()


class AudioPage(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        AudioFrame(self).pack()


class PodcastPage(ttk.Frame):
    def __init__(self, menubar, * args, **kwargs):
        super().__init__(*args, **kwargs)

        self.menubar = menubar

        self.html = HtmlFrame(self)
        self.html.grid(column=0, row=0, columnspan=3)

        self.main_frame = MainFrame(self)
        self.main_frame.grid(column=0, row=1, columnspan=3, padx=10)

        self._open_folder_btn = ttk.Button(
            self, text='Apri Cartella Podcast',
            command=lambda: open_path(self.podcast_obj.path)
        )

        self._select_btn = ttk.Button(self, text='Seleziona file',
                                      command=self.check_credentials)
        self._select_btn.grid(column=1, row=2, sticky=tk.E)
        self._select_btn.focus_set()

        self._conferm_btn = ttk.Button(self, text='Conferma e procedi',
                                       command=self._run, state='disable')
        self._conferm_btn.grid(column=2, row=2, columnspan=2,
                               pady=15, padx=10, sticky=tk.E)

        self.display_msg = self.main_frame.log_frame.display_msg

        self._refresh_btn = self.main_frame._refresh_btn

    def check_credentials(self):
        if UserConfig().is_empty():

            messagebox.showwarning(title='PodcastTool',
                                   message='Update Credentials first!')
        else:
            self.files_select()

    def files_select(self):
        """Select the podcast file to parse."""

        open_files = filedialog.askopenfilenames(initialdir=_set_directory())

        LOGGER.debug("selected files: %s", open_files)

        self.podcast_obj = SelectPodcast(open_files)
        if open_files:
            self.main_frame.podcast_obj = self.podcast_obj
            self.main_frame.confirm_button = self._conferm_btn
            self.main_frame.insert_text()
            self._select_btn["state"] = "disable"

    # @total_time
    def _run(self):
        """Run the podcastool main script when button is pressed."""
        self._rename_files()

        self.main_frame.log_frame.delete_labels()

        self.display_msg("Creazione podcast in corso...")

        test_upload = self.menubar.test_upload()

        with ThreadPoolExecutor() as executor:
            for file in self.main_frame.proccesed_files():
                self.display_msg(file)
                file_path = os.path.join(self.podcast_obj.path, file)
                f1 = executor.submit(PodcastFile, file_path)
                podcast = f1.result()
                f2 = executor.submit(podcast.generate_podcast,
                                     self.menubar.bitrate,
                                     self.menubar.sample_rate,
                                     self.menubar.watermarks)
            self.update()
        _debug_executor(f2)

        if podcast.missing_audio:
            self.display_msg(
                f'! Missing audio files: {podcast.missing_audio}', 'yellow')

        self.display_msg("Fatto!\n")

        # generate html page before so if no internet connection
        # the archive will still be created
        self.html.page = generate_html(podcast.html_page, test_upload)

        check_path = list(podcast.files_to_upload())[0]["server_path"]
        server_path = check_server_path(check_path, test_upload)

        self.display_msg("Caricamento podcast su server...")

        with ThreadPoolExecutor() as executor:
            for file in podcast.files_to_upload():
                self.display_msg(os.path.basename(file['path']))
                f1 = executor.submit(upload_to_server,
                                     file["path"], server_path, test_upload)
            self.update()

        _debug_executor(f1)
        self.display_msg("Fatto!\n")

        self._conferm_btn["state"] = 'disable'

        self.html.copy_button = "normal"
        self.html.preview_button = "normal"
        self.html.status('Pronto', COLORS.ready_html())

        self.update()
        self._open_folder_btn.grid(
            column=0, row=2, rowspan=3, sticky=tk.W, padx=10)

    def _rename_files(self):
        """Rename the wrong typed podcast names."""
        old_names = self.podcast_obj.podcast_list
        new_names = self.main_frame.proccesed_files()
        for old, new in zip(old_names, new_names):
            if old.split("_")[-1:] == new.split("_")[-1:]:
                if old != new:
                    old_name = os.path.join(self.podcast_obj.path, old)
                    new_name = os.path.join(self.podcast_obj.path, new)
                    os.rename(old_name, new_name)


class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # HACK: apparently on virtualbox scaling doesnt work properly
        self.tk.call('tk', 'scaling', '1.30')
        ttk.Style().theme_use('clam')

        self._set_title()
        self._set_geometry()

        self.menubar = MenuBar()
        self.config(menu=self.menubar)

        _layout = ttk.Notebook(self)

        _podcast_page = PodcastPage(menubar=self.menubar)
        _layout.add(_podcast_page, text='Podcast')

        _catalog_page = CatalogPage()
        _layout.add(_catalog_page, text='Catalog')

        _audio_page = AudioPage()
        _layout.add(_audio_page, text='Audio')

        # _layout.select(_catalog_page)

        _layout.pack(fill=tk.BOTH)

    def _set_geometry(self):

        h = (self.winfo_screenheight() // 2) - (APP_GEOMETRY.width // 2)
        w = (self.winfo_screenwidth() // 2) - (APP_GEOMETRY.height // 2)

        self.geometry(f'{APP_GEOMETRY.width}x{APP_GEOMETRY.height}-{w}+{h}')

        self.resizable(width=False, height=False)

    def _set_title(self):
        title = f'PodcastTool {__version__}'
        if dev_mode:
            title += ' - DEVELOPER MODE'
        self.title(title)


def run():
    """Run gui."""

    try:

        app = MainWindow()
        app.mainloop()
    except Exception as error:
        critical(msg="Errore app startup.")


if __name__ == '__main__':
    run()
