import os
import shutil

import tkinter as tk
from tkinter import (messagebox)

from .html_frame import archive_files
from podcasttool import util, open_link


class OptionsMenu(tk.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_command(label='Clean Log', command=self.clean_log)
        self.add_command(label='Clean Archive', command=self.delete_archive)

        self.add_separator()

        self.add_command(label='Reset Names/Audio', command=self.restore_json)

    @staticmethod
    def clean_log():
        log_path = util.get_path("log")
        for file in log_path.glob('*.log'):
            file_path = os.path.join(log_path, file)
            with open(file_path, "w") as _:
                pass

    @staticmethod
    def restore_json():
        original_json = os.path.join(
            util.get_path("docs"), ".catalog_names.json")

        user = messagebox.askyesno(
            message="Newly created audio files will be deleted. Are you sure?")
        if user:
            new_json = util.catalog_file()
            shutil.copy(original_json, new_json)
            new_audio_dir = util.get_path("include/audio/new_audio")

            for audio in new_audio_dir.glob('*mp3'):
                os.remove(audio)

            messagebox.showinfo(message="done!")

    @staticmethod
    def delete_archive():
        """Delete all the html archive files."""
        prompt = messagebox.askyesno(
            title='Conferma', message='Cancellare tutto l\'archivio html. Sei sicuro?')
        if prompt:
            for i in archive_files():
                os.remove(i)
            messagebox.showinfo(
                title='Conferma', message='Archivio cancellato!')


class DevMenu(tk.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._test_env = tk.BooleanVar()
        self._test_env.set(False)

        self.add_checkbutton(label='Test Upload',
                             onvalue=1, offvalue=0,
                             variable=self._test_env)


class HelpMenu(tk.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_command(
            label='Change credentials',
            command=lambda: self.open_file('src/podcasttool', '.env')
        )

        self.add_separator()

        self.add_command(
            label='Open Log File',
            command=lambda: self.open_file("log", "debug.log")
        )

    @staticmethod
    def open_file(_dir, file):
        open_link(os.path.join(util.get_path(_dir), file))


class AudioMenu(tk.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_cascade(label='Waterkmarks', menu=self._get_watermarks())
        self.add_cascade(label='Bitrate', menu=self._get_bitrate())
        self.add_cascade(label='Sample Rate', menu=self._get_sample_rate())

    def _get_sample_rate(self):
        self._sample_rate = tk.StringVar()
        self._sample_rate.set('44100Hz')

        _sample_rate = tk.Menu(self, tearoff=0)
        for sample in ['22050Hz', '44100Hz']:
            _sample_rate.add_radiobutton(
                label=sample, variable=self._sample_rate)
        return _sample_rate

    def _get_watermarks(self):
        self.watermarks_num = tk.StringVar()
        self.watermarks_num.set('Auto')

        watermarks = tk.Menu(self, tearoff=0)
        watermarks.add_radiobutton(label='Auto', variable=self.watermarks_num)

        for i in range(2, 9):
            watermarks.add_radiobutton(label=str(i),
                                       variable=self.watermarks_num)

        return watermarks

    def _get_bitrate(self):
        self._bitrate = tk.StringVar()
        self._bitrate.set('64k')

        _bitrate = tk.Menu(self, tearoff=0)
        for rate in ['32k', '64k', '128k', '192k', '256k', '320k']:
            _bitrate.add_radiobutton(label=rate, variable=self._bitrate)
        return _bitrate


class MenuBar(tk.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.audio = AudioMenu()
        self.options = OptionsMenu()
        self.dev = DevMenu()
        self._help = HelpMenu()

        self.add_cascade(label='Audio', menu=self.audio)
        self.add_cascade(label='Options', menu=self.options)
        self.add_cascade(label='Developer', menu=self.dev)
        self.add_cascade(label='Help', menu=self._help)

    def test_env(self):
        return self.dev._test_env.get()

    def watermarks(self):
        return self.audio.watermarks_num.get()

    def bitrate(self):
        return self.audio._bitrate.get()

    def sample_rate(self):
        return self.audio._sample_rate.get().replace('Hz', '')
