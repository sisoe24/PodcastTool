"""Audio widget frame of the gui.

This module can modify the existing audio intro files and set the export audio
options for the final podcast file that is going to be uploaded to internet.
Default export options are:
    Bitrate: 64k.
    Sample Rate: 22050Hz.
    Watermark cuts: auto.
"""
import os
import json

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

from podcasttool import util


class AudioIntro(tk.Frame):
    """Audio intro modification section of the gui."""
    _catalog = util.catalog_names()
    _new_audio = []
    list_len = len(_catalog["intro"])

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.audio_catalog = self._catalog

        self._audio_frame = ttk.Frame(self,)
        self._audio_frame.grid(column=0, row=0)

        self._audio_list_frame = ttk.LabelFrame(
            self._audio_frame, text="Audio intro", padding=1)
        self._audio_list_frame.grid(column=0, row=0)

        self.create_combobox()

        ttk.Button(self._audio_list_frame, text="aggiungi casella",
                   command=self.add_combobox).grid(column=1, row=20)
        ttk.Button(self._audio_list_frame, text="Salva nuova lista",
                   command=self.new_intro).grid(column=1, row=20, sticky=tk.E,
                                                pady=5, padx=5)

        water_frame = ttk.LabelFrame(self._audio_frame, text="Watermark",
                                     padding=1)
        water_frame.grid(column=0, row=3, sticky=tk.W)

        self.watermark = ttk.Combobox(water_frame, width=42)
        self.watermark.grid(column=0, row=4, sticky=tk.E)
        self.watermark.set(self._catalog["watermark"])

        save_watermark = ttk.Button(water_frame,
                                    text="Salva nuovo watermark",
                                    command=self.new_watermark)
        save_watermark.grid(column=0, row=5, sticky=tk.E, pady=5, padx=5)

        create_frame = ttk.LabelFrame(
            self._audio_frame, text="Crea text audio", padding=1)
        create_frame.grid(column=0, row=6, sticky=tk.W)

        ttk.Label(create_frame, text="text:").grid()

        self.text_entry = ttk.Entry(create_frame, width=40)
        self.text_entry.grid(column=1, row=0)

        ttk.Button(create_frame, text="Crea audio",
                   command=self.text_to_audio).grid(column=1, row=1,
                                                    sticky=tk.E,
                                                    pady=5, padx=5)

        ttk.Label(create_frame, text="lang:").grid(column=0, row=1,
                                                   sticky=tk.W)
        self._lang_select = ttk.Combobox(create_frame, value=["it", "en"],
                                         state="readonly", width=2)
        self._lang_select.grid(column=1, row=1, sticky=tk.W)
        self._lang_select.current(0)

    def text_to_audio(self):
        """Generate text to audio files."""
        ask_user = filedialog.asksaveasfilename()
        if ask_user:
            path, filename = os.path.split(ask_user)
            util.generate_audio(text=self.text_entry.get(),
                                filename=filename, path=path,
                                lang=self._lang_select.get())

    def add_combobox(self):
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

            msg = f"Generating audio for: {name}"
            ttk.Label(self._audio_frame, text=msg).grid(column=0, row=index)
            self.update()
            util.generate_audio(text=name, path=util.USER_AUDIO)

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
        with open(util.catalog_file(), "w") as json_file:
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
