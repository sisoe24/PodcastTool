"""Some utility functions."""
import os
import shutil

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from podcasttool import util
from .html_frame import archive_files


def delete_archive():
    """Delete all the html archive files."""
    prompt = messagebox.askyesno(
        title='Conferma', message='Cancellare tutto l\'archivio. Sei sicuro?')
    if prompt:
        for i in archive_files():
            os.remove(i)
        messagebox.showinfo(title='Conferma', message='Archivio cancellato!')


class DevFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.test_value = tk.BooleanVar()
        test_btn = ttk.Checkbutton(parent, text='test env',
                                   variable=self.test_value)
        test_btn.grid(column=0, row=0, sticky=tk.W)

        self._bypass = tk.BooleanVar()
        bypass_dev = ttk.Checkbutton(parent, text="bypass dev",
                                     variable=self._bypass)
        bypass_dev.grid(column=0, row=1, sticky=tk.W)

        ttk.Label(parent, text='Upload file to test folder').grid(
            column=1, row=0, sticky=tk.W)
        self.delete_archive = ttk.Button(parent, text="Clean archive",
                                         command=delete_archive)
        self.delete_archive.grid(column=0, row=2)

        n_archive = len(list(archive_files()))
        archive_msg = f"There are {n_archive} html files in the archive"
        ttk.Label(parent, text=archive_msg).grid(column=1, row=2)

        ttk.Button(parent, text="Clean log",
                   command=self.clean_log).grid(column=0, row=3, stick=tk.W)

        ttk.Button(parent, text="Reset json",
                   command=self.restore_json).grid(column=0, row=4, stick=tk.W)

        ttk.Label(parent, text="restore json catalog to original form").grid(
            column=1, row=4, stick=tk.E)

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
