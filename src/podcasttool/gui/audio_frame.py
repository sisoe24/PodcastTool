"""Audio frame widget of the gui."""
import tkinter as tk
from tkinter import ttk


class AudioFrame(tk.Frame):
    """Audio section frame of the gui."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self._audio = ttk.Frame(self, width=300, height=100)
        self._audio.grid(column=2, row=2, rowspan=2, sticky=tk.N)
        self._audio.grid_propagate(False)

        self._watermarks = ttk.Combobox(self._audio, width=4, state='readonly',
                                        value=self._watermarks_list())
        self._watermarks.grid(column=1, row=1, sticky=tk.E)
        self._watermarks.current(0)

        self._bitrate = ttk.Combobox(self._audio, width=4, state='readonly',
                                     value=self._bitrate_list())
        self._bitrate.grid(column=1, row=2, pady=2, sticky=tk.E)
        self._bitrate.current(1)

        self._sample_rate = ttk.Combobox(self._audio, width=7,
                                         value=self._sample_rate_list(),
                                         state='readonly')
        self._sample_rate.grid(column=1, row=3)
        self._sample_rate.current(0)

        self._labels()

    def _labels(self):
        """Generate labels for audio frame."""
        labels = ['Export options', "Watermarks", "Bitrate", "Sample rate"]
        for i, label in enumerate(labels):
            style = 'label.TLabel' if "Export" in label else ""
            ttk.Label(self._audio, text=label, style=style).grid(
                column=0, row=i, sticky=tk.W)

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
