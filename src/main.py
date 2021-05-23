"""GUI interface of PodcastTool."""
import os
import logging
from datetime import datetime

from concurrent.futures import ThreadPoolExecutor

import tkinter as tk
from tkinter import (
    ttk,
    messagebox,
    filedialog
)

import util
from startup import OS_SYSTEM

from widgets import (
    MenuBar,
    HtmlFrame,
    MainFrame,
    AudioIntro,
    CatalogFrame,
    SelectPodcast
)

from tools import (
    PodcastFile,
    check_server_path,
    upload_to_server,
    generate_html
)

LOGGER = logging.getLogger('podcasttool.gui')


def _set_directory():
    """Set which folder to open.

    Return:
        {str} - path to which directory to open first at gui start.
    """
    # If user is me then open in test files directory.
    if util.is_dev_mode():
        initial_dir = os.path.join(os.getcwd(), 'other/Scrivania/ALP')
    else:
        initial_dir = os.path.join(os.environ['HOME'], 'Scrivania/Podcast')

    LOGGER.debug("gui initial directory: %s", initial_dir)

    return initial_dir


class MainPage(tk.Tk):
    """Main window frame."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        window_main = ttk.Notebook(self, width=1000, height=600)

        _page_main = ttk.Frame(window_main, width=1000, height=600)
        _page_main.grid(column=0, row=0)
        _page_main.grid_propagate(False)
        window_main.add(_page_main, text='Main')

        title = 'PodcastTool 2.3'

        self._test_upload = tk.BooleanVar(False)
        if util.is_dev_mode():
            title += ' - Developer mode'.upper()
            _test_check = ttk.Checkbutton(window_main, variable=self._test_upload,
                                          text='Upload to server virgil_test')
            _test_check.place(x=10, y=60)

        self.title(title)

        self.menubar = MenuBar()
        self.config(menu=self.menubar)

        app_x = 685
        app_y = 600

        # - position window center screen - #
        position_height = self.winfo_screenheight() // 2 - (app_y // 2)
        self.geometry(f'{app_x}x{app_y}-{100}+{position_height}')

        self.resizable(width=False, height=False)

        # window_main.grid_propagate(False)

        self.clock = ttk.Label(_page_main)
        self.clock.place(x=5, y=0)

        # catalogo page frame
        _page_catalog = ttk.Frame(window_main, width=1000, height=600)
        _page_catalog.grid(column=0, row=0)
        _page_catalog.grid_propagate(False)
        window_main.add(_page_catalog, text='Catalogo Nomi')
        CatalogFrame(_page_catalog).grid(column=0, row=0)

        # audio page frame
        _page_audio = ttk.Frame(window_main, width=1000, height=600)
        _page_audio.grid(column=0, row=0)
        _page_audio.grid_propagate(False)
        window_main.add(_page_audio, text='Audio')
        AudioIntro(_page_audio).grid(column=0, row=0)

        self.html = HtmlFrame(_page_main)
        self.html.place(x=390, y=0)

        self.main_class = MainFrame(_page_main, width=670, height=360)
        self.main_class.place(x=5, y=210)

        # XXX: debug only
        # window_main.select(_page_catalog)

        window_main.pack()
        self.podcast_obj = None

        self._conferm_btn = ttk.Button(_page_main, text='Conferma e procedi',
                                       state='disable', command=self._run)
        self._conferm_btn.place(x=105, y=65)

        self._select_btn = ttk.Button(_page_main, text='Seleziona file',
                                      command=self.check_credentials)
        # self._select_btn.invoke()
        self._select_btn.focus_set()
        self._select_btn.place(x=5, y=65)

        self._labels_style()
        self.time()

    def time(self):
        """Clock label for the gui."""
        date = datetime.now().strftime("%d/%m %H:%M:%S")
        self.clock.config(text=date, style="clock.TLabel")
        self.clock.after(1000, self.time)

    def check_credentials(self):
        if util.UserConfig().is_empty():

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
            self.main_class.podcast_obj = self.podcast_obj
            self.main_class.confirm_button = self._conferm_btn
            self.main_class.insert_text()
            self._select_btn["state"] = "disable"

    def _run(self):
        """Run the podcastool main script when button is pressed."""
        self._rename_files()

        display_msg = self.main_class.log_frame.display_msg
        self.main_class.log_frame._log_label.config(text='Job Status')

        display_msg("Creazione podcast in corso...")

        test_upload = self._test_upload.get()
        with ThreadPoolExecutor() as executor:
            for file in self.main_class.proccesed_files():
                self.update()

                display_msg(file)

                file_path = os.path.join(self.podcast_obj.path, file)
                f1 = executor.submit(PodcastFile, file_path)
                podcast = f1.result()
                f2 = executor.submit(podcast.generate_podcast,
                                     self.menubar.bitrate,
                                     self.menubar.sample_rate,
                                     self.menubar.watermarks)

                try:
                    LOGGER.debug('podcast executor status: %s', f2.result())
                except Exception as err:
                    LOGGER.critical('error in podcast pool executor: %s',
                                    err, exc_info=True)
                    util.open_log('Error when creating podcast')
                    return

        if podcast.missing_audio:
            display_msg(
                f'! Missing audio files: {podcast.missing_audio}', 'yellow'
            )
        display_msg("Fatto!\n")

        check_path = list(podcast.files_to_upload())[0]["server_path"]
        server_path = check_server_path(check_path, test_upload)

        display_msg("Caricamento podcast su server...")
        with ThreadPoolExecutor() as executor:
            for file in podcast.files_to_upload():
                self.update()
                display_msg(os.path.basename(file['path']))
                f1 = executor.submit(upload_to_server,
                                     file["path"], server_path, test_upload)

                try:
                    LOGGER.debug(
                        'server upload executor status:%s', f1.result())
                except Exception as e:
                    LOGGER.critical('error when uploading to server: %s',
                                    e, exc_info=True)
                    util.open_log('Error when uploading to server')

        display_msg("Fatto!\n")

        generate_html(podcast.html_page, test_upload)
        display_msg("Pagina html generata")

        self._conferm_btn["state"] = 'disable'

        self.html.copy_button = "normal"
        self.html.preview_button = "normal"
        self.html.status('Pronto', 'green')

        self.update()
        messagebox.showinfo(title="PodcastTool", message="Done!", icon="info")

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

    @ staticmethod
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
        # util.open_log(msg="Errore app startup.\nControllare errors.log?")


if __name__ == '__main__':
    run()
