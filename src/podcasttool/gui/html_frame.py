import os
import pathlib
import platform
import subprocess
from functools import partial

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import pyperclip
from podcasttool import util

if platform.system() == 'Darwin':
    OS_SYSTEM = 'Mac'
elif platform.system() == 'Linux':
    OS_SYSTEM = 'Linux'
else:
    print('sorry your OS is not supported')


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


class HtmlFrame(tk.Frame):
    """Html section of the gui."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._html_frame = ttk.LabelFrame(self, width=300, height=90,
                                          text="HTML")
        self._html_frame.grid(column=0, row=0)
        self._html_frame.grid_propagate(False)

        status_font = 20 if OS_SYSTEM == 'Mac' else 14
        self.status_var = tk.StringVar(value="Non pronto")
        self._status_display = tk.Label(self._html_frame,
                                        textvariable=self.status_var,
                                        font=('TkDefaultFont', status_font))
        self._status_display.grid(column=1, row=1)
        self._status_display.configure(background="red")

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
        labels = ["Status:    ", "Web:"]
        for index, label in enumerate(labels, 1):
            ttk.Label(self._html_frame, text=label).grid(
                column=0, row=index, stick=tk.W)


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
