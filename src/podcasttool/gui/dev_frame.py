"""Some utility functions."""
import os
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

        ttk.Label(parent, text='Upload file to test folder').grid(
            column=1, row=0, sticky=tk.W)
        self.delete_archive = ttk.Button(parent, text="Clean archive folder",
                                         command=delete_archive)
        self.delete_archive.grid(column=0, row=1)

        n_archive = len(list(archive_files()))
        archive_msg = f"There are {n_archive} html files in the archive"
        ttk.Label(parent, text=archive_msg).grid(column=1, row=1)

        ttk.Button(parent, text="Clean log folder",
                   command=self.clean_log).grid(column=0, row=2, stick=tk.W)

    @property
    def test_env(self):
        return self.test_value.get()

    def clean_log(self):
        log_path = util.get_path("log")
        for file in os.listdir(log_path):
            file_path = os.path.join(log_path, file)
            with open(file_path, "w") as f:
                pass
