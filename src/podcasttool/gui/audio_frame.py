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
                   command=self.text_to_audio).grid(column=1, row=1, sticky=tk.E,
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
        """Add new combobox widget."""
        ttk.Combobox(self._audio_list_frame, value=self.const_vars(),
                     width=40).grid(column=1, row=self.list_len)
        self.list_len += 1

    def create_combobox(self):
        """Create combobox widget from the audio intro list."""
        for index, element in enumerate(self.audio_catalog["intro"]):
            ttk.Label(self._audio_list_frame, text=index +
                      1).grid(column=0, row=index)

            combo = ttk.Combobox(
                self._audio_list_frame, value=self.const_vars(), width=40)
            combo.grid(column=1, row=index, sticky=tk.W)

            if element not in self.const_vars():
                element = element.replace("_", " ")
            combo.set(element)

    def parse_frame(self):
        """Parse intro_frame frame for combobox widgets."""
        for widget in self._audio_list_frame.winfo_children():
            if "combobox" in widget.winfo_name():
                widget_data = widget.get()
                if widget_data:
                    yield widget_data

    def new_audio(self, current_catalog):
        for name in self.parse_frame():
            if name not in current_catalog:
                yield name

    def generate_new_audio(self, current_catalog):
        """Gnerate new audio files for the intro."""
        path = util.get_path("include/audio") / "new_intro"

        for index, name in enumerate(current_catalog, 10):

            msg = f"Generating audio for: {name}"
            ttk.Label(self._audio_frame, text=msg).grid(column=0, row=index)
            self.update()
            util.generate_audio(text=name, path=path)

    def new_intro(self):
        """Generate new audio files and modify the json catalog."""
        current_catalog = self._catalog["intro"]
        self.audio_catalog["intro"] = list(self.parse_frame())

        if current_catalog != self.audio_catalog["intro"]:
            self.generate_new_audio(self.new_audio(current_catalog))
            self.save_new()
        else:
            messagebox.showinfo(message="Nessuna modifica?", icon="question")

    def new_watermark(self):
        current_watermark = self._catalog["watermark"]
        self.audio_catalog["watermark"] = self.watermark.get()

        if current_watermark != self.audio_catalog["watermark"]:
            self.generate_new_audio([self.watermark.get()])
            self.save_new()
        else:
            messagebox.showinfo(message="Nessuna modifica?", icon="question")

    def save_new(self):
        with open(util.catalog_file(), "w") as f:
            json.dump(self.audio_catalog, f, indent=True)
        messagebox.showinfo(title="Done", message="Done!", icon="info")

    @staticmethod
    def const_vars():
        return ["$VAR{course_name}", "$VAR{teacher_name}",
                "$VAR{lesson_number}", "$VAR{part_number}",
                "$VAR{day}", "$VAR{month}", "$VAR{year}"]


class AudioExport(tk.Frame):
    """Audio section frame of the gui."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._audio_frame = ttk.Frame(self, width=300, height=100)
        self._audio_frame.grid(column=1, row=0, sticky=tk.W)
        self._audio_frame.grid_propagate(False)

        self.export_label = ttk.LabelFrame(
            self._audio_frame, text="Podcast export settings", padding=5)
        self.export_label.grid(column=0, row=0, )

        self._watermarks = ttk.Combobox(self.export_label, width=4,
                                        state='readonly',
                                        value=self._watermarks_list())
        self._watermarks.grid(column=1, row=1, sticky=tk.E)
        self._watermarks.current(0)

        self._bitrate = ttk.Combobox(self.export_label, width=4,
                                     state='readonly',
                                     value=self._bitrate_list())
        self._bitrate.grid(column=1, row=2, pady=2, sticky=tk.E)
        self._bitrate.current(1)

        self._sample_rate = ttk.Combobox(self.export_label, width=7,
                                         value=self._sample_rate_list(),
                                         state='readonly')
        self._sample_rate.grid(column=1, row=3)
        self._sample_rate.current(0)

        self._labels()

    def _labels(self):
        """Generate labels for audio frame."""
        labels = ["Watermarks", "Bitrate", "Sample rate"]

        for i, label in enumerate(labels, 1):
            style = 'label.TLabel' if "Export" in label else ""
            ttk.Label(self.export_label, text=label, style=style).grid(
                column=0, row=i, sticky=tk.W, padx=2)

    @staticmethod
    def _watermarks_list() -> list:
        """Generate a list to populate watermark_num combobox."""
        nums = [_ for _ in range(2, 9)]
        nums.insert(0, "auto")
        return nums

    @staticmethod
    def _bitrate_list() -> list:
        """Generate a list to populate bitrate combobox.

        Common audio birate:
            - 32k or 64k – generally acceptable only for speech
            - 96k – generally used for speech or low-quality streaming
            - 128k or 160k – mid-range bitrate quality
            - 192k – medium quality bitrate
            - 256k – a commonly used high-quality bitrate
            - 320k – highest level supported by the MP3 standard
        """
        return ['32k', '64k', '128k', '192k', '256k', '320k']

    @staticmethod
    def _sample_rate_list() -> list:
        """Generate a list to populate bitrate combobox."""
        return ['22050Hz', '44100Hz']

    @property
    def bitrate(self) -> str:
        """Return bitrate from options."""
        return self._bitrate.get()

    @property
    def sample_rate(self) -> str:
        """Return sample rate from options without the Hz."""
        return self._sample_rate.get().replace('Hz', '')

    @property
    def watermark_state(self) -> str:
        """Get watermark_toggle check button state."""
        return self._watermarks.get()

    @property
    def watermark_num(self) -> int:
        """Return number of cuts to make in audio from options."""
        if not self.watermark_state == "auto":
            return int(self._watermarks.get())
        return None
