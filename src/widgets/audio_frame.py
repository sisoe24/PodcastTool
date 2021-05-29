"""Audio widget frame of the gui.

This module can modify the existing audio intro files and set the export audio
options for the final podcast file that is going to be uploaded to internet.
Default export options are:
    Bitrate: 64k.
    Sample Rate: 22050Hz.
    Watermark cuts: auto.
"""
import json

import tkinter as tk
from tkinter import (
    ttk,
    messagebox,
)

from startup import USER_AUDIO
from utils import util, catalog
from utils.resources import _catalog_file


class AudioFrame(ttk.Frame):
    """Audio intro modification section of the gui."""
    # TODO: should be nice to order by selecting the column
    _catalog = catalog()
    _new_audio = []
    list_len = len(_catalog["intro"])

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.audio_catalog = self._catalog

        self._audio_frame = ttk.Frame(self,)
        self._audio_frame.grid(column=0, row=0, pady=5)

        self._audio_list_frame = ttk.LabelFrame(
            self._audio_frame, text="Audio intro", padding=1)
        self._audio_list_frame.grid(column=0, row=0, pady=5)

        self.create_combobox()

        # ttk.Button(self._audio_list_frame, text="aggiungi casella",
        #            command=self.add_combobox).grid(column=1, row=20)

        ttk.Button(self._audio_list_frame, text="Salva",
                   command=self.new_intro).grid(column=1, row=20, sticky=tk.E,
                                                pady=5, padx=5)

        water_frame = ttk.LabelFrame(self._audio_frame, text="Watermark",
                                     padding=1)
        water_frame.grid(column=0, row=3, pady=10, sticky=tk.W)

        self._watermak_text = tk.StringVar()
        self.watermark = ttk.Entry(water_frame,
                                   textvariable=self._watermak_text,
                                   width=43)
        self.watermark.grid(column=0, row=4, padx=5, sticky=tk.E)
        self._watermak_text.set(self._catalog["watermark"])

        save_watermark = ttk.Button(water_frame, text="Salva",
                                    command=self.new_watermark)
        save_watermark.grid(column=0, row=5, sticky=tk.E, pady=5, padx=5)

    def __add_combobox(self):
        """Add new combobox widget if user wants."""
        ttk.Combobox(self._audio_list_frame, value=self.const_vars(),
                     width=40).grid(column=1, row=self.list_len)
        self.list_len += 1

    def create_combobox(self):
        """Create combobox widget from the audio intro list."""
        for index, element in enumerate(self.audio_catalog["intro"]):
            ttk.Label(self._audio_list_frame, text=index +
                      1).grid(column=0, row=index)

            combo = ttk.Combobox(self._audio_list_frame, width=40,
                                 value=self.const_vars())
            combo.grid(column=1, row=index, sticky=tk.W)

            if element not in self.const_vars():
                element = element.replace("_", " ")
            combo.set(element)

    def parse_frame(self):
        """Parse audio list frame for combobox widgets and get their values."""
        for widget in self._audio_list_frame.winfo_children():
            if "combobox" in widget.winfo_name():
                widget_data = widget.get()
                if widget_data:
                    yield widget_data

    def new_audio(self, current_intro):
        """Get the elements in the audio.

        Get the audio list frame and check if there are new names.

        Arguments:
            current_intro [list] - the current audio intro list.
        """
        for name in self.parse_frame():
            if name not in current_intro:
                yield name

    def generate_new_audio(self, audio_list):
        """Gnerate new audio files for the intro.

        Arguments:
            audio_list {list/tuple} - iterable variable to generate new audio
        """
        for index, name in enumerate(audio_list, 10):

            if util.generate_audio(text=name.lower(), path=USER_AUDIO):
                msg = f"Generating audio for: {name}"
                # TODO: message should be done in the final messagebox
                ttk.Label(self._audio_frame, text=msg).grid(
                    column=0, row=index)
                self.update()
            else:
                messagebox.showerror(
                    title='PodcastTool',
                    message='Problem Creating Audio. Check log file')

    def new_intro(self):
        """Check if audio intro was modified."""
        current_catalog = self._catalog["intro"]
        new_catalog = self.audio_catalog["intro"] = list(self.parse_frame())
        new_intro_list = self.new_audio(current_catalog)

        self.compare_current(current_catalog, new_catalog, new_intro_list)

    def new_watermark(self):
        """Check if current watermark was modified."""
        current_watermark = self._catalog["watermark"]
        new_watermark = self.audio_catalog["watermark"] = self.watermark.get()

        self.compare_current(current_watermark, new_watermark, [new_watermark])

    def compare_current(self, current_value, new_value, audio_list):
        """Compare if current_value catalog was modified.
        If yes then create new audio from list and save into catalog.

        Arguments:
            current_value - value of catalog dictionary to be compared
            new_value - value of catalog dictionary to be compared
            audio_list {list} - a list from where to generate the new audio
        """
        if current_value != new_value:
            self.generate_new_audio(audio_list)
            self.save_new()
        else:
            messagebox.showinfo(message="Nessuna modifica?", icon="question")

    def save_new(self):
        """Save modifications in catalog json file."""
        with open(_catalog_file(), "w") as json_file:
            json.dump(self.audio_catalog, json_file, indent=True)
        messagebox.showinfo(title="PodcastTool", message="Done!", icon="info")

    @staticmethod
    def const_vars():
        """Return a list of string placeholders for variables names that
        can be used in the audio intro.
        """
        return ["$VAR{course_name}", "$VAR{teacher_name}",
                "$VAR{lesson_number}", "$VAR{part_number}",
                "$VAR{day}", "$VAR{month}", "$VAR{year}"]
