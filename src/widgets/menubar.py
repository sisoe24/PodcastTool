import os
import shutil
import pickle
import pathlib

import tkinter as tk
from tkinter import messagebox, ttk

from widgets.html_frame import archive_files

from utils import util
from startup import USER_AUDIO
from resources import _system_catalog_path, _catalog_file


class OptionsMenu(tk.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._html_media = tk.BooleanVar()

        use_mediaplayer = util.UserConfig().value('html_mediaplayer', False)
        self._html_media.set(use_mediaplayer)

        self.add_checkbutton(label='Use HTML Mediaplayer',
                             variable=self._html_media,
                             command=self._update_config)

        self.add_separator()

        self.add_command(label='Clean Log', command=self.clean_log)
        self.add_command(label='Clean Archive', command=self.delete_archive)

        self.add_separator()

        self.add_command(label='Reset Names/Audio', command=self.restore_json)

    def _update_config(self):

        data = util.UserConfig().data
        data.update({'html_mediaplayer': self._html_media.get()})

        with util.UserConfig(mode='wb') as file:
            pickle.dump(data, file)

    @ staticmethod
    def clean_log():
        log_path = util.get_path("log")
        for file in log_path.glob('*.log'):
            file_path = os.path.join(log_path, file)
            with open(file_path, "w") as _:
                pass

    @ staticmethod
    def restore_json():

        user = messagebox.askyesno(
            message="Newly created audio files will be deleted. Are you sure?")

        if not user:
            return

        shutil.copy(_system_catalog_path(), _catalog_file())

        for audio in pathlib.Path(USER_AUDIO).glob('*mp3'):
            os.remove(audio)

        messagebox.showinfo(message="done!")

    @ staticmethod
    def delete_archive():
        """Delete all the html archive files."""
        prompt = messagebox.askyesno(
            title='Conferma',
            message='Cancellare tutto l\'archivio html. Sei sicuro?')

        if not prompt:
            return

        for i in archive_files():
            os.remove(i)
        messagebox.showinfo(title='Conferma', message='Archivio cancellato!')


class CredentialsEntry(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('Update Credentials')

        h = self.winfo_screenheight() // 2
        w = self.winfo_screenwidth() // 2
        self.geometry(f'300x150+{w}+{h}')
        self.resizable(width=False, height=False)

        self._main = ttk.Frame(self, width=300, height=150)
        self._main.grid(column=0, row=0)
        self._main.grid_propagate(False)

        ttk.Label(self._main, text='Host').grid(row=0)
        ttk.Label(self._main, text='User').grid(row=1)
        ttk.Label(self._main, text='Password').grid(row=2)
        ttk.Label(self._main, text='Website').grid(row=3)

        self.host_entry = ttk.Entry(self._main, width=25)
        self.user_entry = ttk.Entry(self._main, width=25)
        self.pass_entry = ttk.Entry(self._main, width=25, show="*")
        self.web_entry = ttk.Entry(self._main, width=25)

        self.host_entry.grid(row=0, column=1)
        self.user_entry.grid(row=1, column=1)
        self.pass_entry.grid(row=2, column=1)
        self.web_entry.grid(row=3, column=1)

        self.save_credentials = ttk.Button(self._main, text='Save',
                                           command=self._save)
        self.save_credentials.grid(row=4, column=1, columnspan=2,
                                   sticky=tk.E, pady=5)

        self.config = util.UserConfig()
        self.load_credentials()

    def _save(self):
        data = {}

        data['host'] = self.host_entry.get()
        data['user'] = self.user_entry.get()
        data['pass'] = self.pass_entry.get()
        data['web'] = self.web_entry.get()

        web = data['web']
        if web.endswith('/'):
            web = web[:-1]

        data['elearning_url'] = f'{web}/elearning'
        data['test_url'] = f'{web}/images/didattica/virgil_test'
        data['podcast_url'] = f'{web}/images/didattica/PODCAST'
        data['plugin_url'] = f'{web}/plugins/content/1pixelout/player.swf'

        with util.UserConfig(mode='wb') as config_file:
            pickle.dump(data, config_file)

        self.destroy()

    def load_credentials(self):
        self.host_entry.insert(tk.END, self.config.value('host'))
        self.user_entry.insert(tk.END, self.config.value('user'))
        self.pass_entry.insert(tk.END, self.config.value('pass'))
        self.web_entry.insert(tk.END, self.config.value('web'))


class HelpMenu(tk.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_command(label='Update credentials', command=CredentialsEntry)

        self.add_separator()

        self.add_command(
            label='Open Log File',
            command=lambda: self.open_file("log", "debug.log")
        )

    @ staticmethod
    def open_file(_dir, file):
        util.open_link(os.path.join(util.get_path(_dir), file))


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
        self._help = HelpMenu()

        self.add_cascade(label='Audio Export', menu=self.audio)
        self.add_cascade(label='Options', menu=self.options)
        self.add_cascade(label='Help', menu=self._help)

    @property
    def watermarks(self):
        return self.audio.watermarks_num.get()

    @property
    def bitrate(self):
        return self.audio._bitrate.get()

    @property
    def sample_rate(self):
        return self.audio._sample_rate.get().replace('Hz', '')
