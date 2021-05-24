"""Html frame of the gui.

From here you can open open the website directly, open a preview of the html
even though it uses an audio player that is located on the server, thus it will
not work on the preview window and copy the html page on the os clipboard using
an external module 'pyperclip'.
"""

import os
import time
import pathlib
import tempfile
import webbrowser

from functools import partial

import tkinter as tk
from tkinter import ttk

# import pyperclip

from utils import UserConfig
from startup import USER_ARCHIVE, OS_SYSTEM


def archive_files():
    """Get all the html archives files."""
    path = pathlib.Path(USER_ARCHIVE).glob('*html')
    for file in sorted(path):
        yield file


def _last_archive_created():
    """Get the last created html file from the archive directory.

    Returns:
        {str} -- file path of the last html page.

    """
    mod = {file: os.stat(file).st_mtime for file in archive_files()}
    for filepath, mtime in mod.items():
        if mtime == max(mod.values()):
            return filepath
    return None


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

        self._page = ""

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

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, value):
        self._page = value

    def _copy_html(self):
        """Copy the main page generated after the script is completed."""
        self.clipboard_append(self.page)
        # pyperclip.copy(self.page)
        self.status('Copiato', 'RoyalBlue1')
        self.bell()

    def _open_link(self, page: str):
        """Open website or preview html page."""
        if page == 'web':
            link = UserConfig().data['elearning_url']
            webbrowser.open(link)
        elif page == 'preview':
            with tempfile.NamedTemporaryFile('r+', suffix='.html') as f:
                f.write(self.page)
                webbrowser.open('file://' + f.name)
                f.seek(0)
                time.sleep(1)
