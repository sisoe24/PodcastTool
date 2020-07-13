"""Some utility functions."""
import os
import shutil

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from podcasttool import util, open_link
from .html_frame import archive_files


def delete_archive():
    """Delete all the html archive files."""
    prompt = messagebox.askyesno(
        title='Conferma', message='Cancellare tutto l\'archivio. Sei sicuro?')
    if prompt:
        for i in archive_files():
            os.remove(i)
        messagebox.showinfo(title='Conferma', message='Archivio cancellato!')


def get_server_path():
    return os.environ["FONDERIE_PODCAST"]


class DevFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        dev_options = ttk.LabelFrame(parent,
                                     text='Developer options (use with caution!)')
        dev_options.grid(column=0, row=0, sticky=tk.W)

        self.test_value = tk.BooleanVar()
        test_btn = ttk.Checkbutton(dev_options, text='Enable test uploading',
                                   variable=self.test_value)
        test_btn.grid(column=0, row=0, sticky=tk.W)

        self._bypass = tk.BooleanVar()
        bypass_dev = ttk.Checkbutton(dev_options, text="Bypass restriction",
                                     variable=self._bypass)
        bypass_dev.grid(column=0, row=1, sticky=tk.W)

        dev_log = ttk.LabelFrame(parent, text='Log options')
        dev_log.grid(column=0, row=1, sticky=tk.W)

        self.delete_archive = ttk.Button(dev_log, text="Clean archive",
                                         command=delete_archive)
        self.delete_archive.grid(column=0, row=0, sticky=tk.W)

        n_archive = len(list(archive_files()))
        archive_msg = f" - There are {n_archive} html files in the archive"
        ttk.Label(dev_log, text=archive_msg).grid(column=1, row=0)

        ttk.Button(dev_log, text="Clean log",
                   command=self.clean_log).grid(column=0, row=1, sticky=tk.W)

        ttk.Button(dev_log, text="Reset json",
                   command=self.restore_json).grid(column=0, row=2, sticky=tk.W)

        ttk.Label(dev_log, text="- Restore json catalog to original form").grid(
            column=1, row=2, sticky=tk.E)

        ttk.Button(dev_log, text='Show debug log',
                   command=self.debug_status).grid(column=0, row=4)

        server_frame = ttk.LabelFrame(parent, text='Server (work in progress...)')
        server_frame.grid(column=0, row=2, sticky=tk.W)

        server_path = ttk.Label(
            server_frame, text='Percorso server della cartella PODCAST: ')
        server_path.grid(column=0, row=0,  sticky=tk.W)

        self.path_entry = ttk.Entry(server_frame, width=60, state='readonly')
        self.path_entry.grid(column=0, row=1)

        self.path_entry.insert('0', get_server_path())

        self.save_path = ttk.Button(server_frame, text='Salva nuovo percorso',
                                    command=self.set_path, state='disabled')
        self.save_path.grid(column=0, sticky=tk.E, row=2, pady=5, padx=5)

    def set_path(self):
        print('inside')
        with open(util.ENV_FILE, 'r+') as env_file:
            env_file.seek(0)
            contents = env_file.read().replace(
                get_server_path(), self.path_entry.get())
            print(contents)
            env_file.write(contents)
            # env_file.truncate()
        print('outside')

    def debug_status(self):
        open_link(util.get_path("log") / "debug.log")

    def restore_json(self):
        original_json = util.get_path("docs") / ".catalog_names.json"
        user = messagebox.askyesno(
            message="new audio folder will be deleted. are you sure?")
        if user:
            new_json = util.catalog_file()
            shutil.copy(original_json, new_json)
            new_audio_dir = util.get_path("include/audio/new_audio")
            [os.remove(audio) for audio in new_audio_dir.iterdir()]
            messagebox.showinfo(message="done!")

    @property
    def test_env(self):
        return self.test_value.get()

    @property
    def bypass_dev(self):
        pass

    def clean_log(self):
        log_path = util.get_path("log")
        for file in os.listdir(log_path):
            file_path = os.path.join(log_path, file)
            with open(file_path, "w") as f:
                pass
