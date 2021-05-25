import os
import sys
import shutil
import pickle
import pathlib
import subprocess

import tkinter as tk
from tkinter import messagebox, ttk, filedialog

from widgets.html_frame import archive_files

from utils import util, UserConfig
from startup import LOG_PATH, USER_AUDIO
from utils.resources import _system_catalog_path, _catalog_file


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

        self.config = UserConfig()
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

        with UserConfig(mode='wb') as config_file:
            pickle.dump(data, config_file)

        self.destroy()

    def load_credentials(self):
        self.host_entry.insert(tk.END, self.config.value('host'))
        self.user_entry.insert(tk.END, self.config.value('user'))
        self.pass_entry.insert(tk.END, self.config.value('pass'))
        self.web_entry.insert(tk.END, self.config.value('web'))


def _update_config(setting):

    data = UserConfig().data
    data.update(setting)

    with UserConfig(mode='wb') as file:
        pickle.dump(data, file)


class OptionsMenu(tk.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        _use_html = tk.BooleanVar()
        _html_key = 'html_mediaplayer'
        _use_html_config = UserConfig().value(_html_key, False)
        _use_html.set(_use_html_config)

        self.add_checkbutton(label='Use HTML Mediaplayer',
                             variable=_use_html,
                             command=lambda: _update_config(
                                 {_html_key: _use_html.get()}
                             ))

        self._is_dev_mode = tk.BooleanVar()
        self._dev_mode_key = 'dev_mode'
        _dev_mode_config = UserConfig().value(self._dev_mode_key, False)
        self._is_dev_mode.set(_dev_mode_config)

        self.add_checkbutton(label='Enable Developer mode',
                             variable=self._is_dev_mode, command=self._reboot)

        self.add_separator()

        self.add_command(label='Set Podcast Folder', command=self._set_folder)

        self.add_separator()

        self.add_command(label='Update credentials', command=CredentialsEntry)

    @staticmethod
    def _set_folder():
        folder = filedialog.askdirectory()
        _update_config({'initial_dir': folder})

    def _reboot(self):
        user = messagebox.askyesno(title='PodcastTool',
                                   message='Please relaunch the application')

        if user:
            _update_config({self._dev_mode_key: self._is_dev_mode.get()})
            sys.exit()
        else:
            self._is_dev_mode.set(not user)


class TaskMenu(tk.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_command(label='Clean Log', command=self.clean_log)
        self.add_command(label='Clean Archive', command=self.delete_archive)

        self.add_separator()
        self.add_command(label='Create Linux App shortcut',
                         command=self.delete_archive)
        self.add_separator()

        self.add_command(label='Reset Names/Audio', command=self.restore_json)
        self.add_separator()

    # @staticmethod
    # def create_shortcut(self):
    #     path = os.path.join(os.getcwd(), 'resourcers',
    #                         'scripts', 'create_desktop.sh')
    #     subprocess.run(['sudo', 'bash', path])

    @staticmethod
    def clean_log():
        for file in pathlib.Path(LOG_PATH).glob('*.log'):
            with open(file, "w") as _:
                pass

        messagebox.showinfo(title='PodcastTool', message='Done')

    @staticmethod
    def restore_json():

        user = messagebox.askyesno(
            message="Newly created audio files will be deleted. Are you sure?")

        if not user:
            return

        shutil.copy(_system_catalog_path(), _catalog_file())

        for audio in pathlib.Path(USER_AUDIO).glob('*mp3'):
            os.remove(audio)

        messagebox.showinfo(title='PodcastTool', message='Done')

    @staticmethod
    def delete_archive():
        """Delete all the html archive files."""
        for i in archive_files():
            os.remove(i)

        messagebox.showinfo(title='PodcastTool', message='Done')


class GoMenu(tk.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_command(
            label='Log',
            command=lambda: util.open_link(os.path.join(LOG_PATH))
        )

        self.add_command(
            label='Configuration',
            command=lambda: util.open_link(
                os.path.join(os.getenv('HOME'),  ".podcasttool"))
        )

        self.add_command(
            label='Resources',
            command=lambda: util.open_link(
                os.path.join(os.getcwd(),  "resources"))
        )

        self.add_separator()


class AudioMenu(tk.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_cascade(label='Waterkmarks', menu=self._get_watermarks())
        self.add_cascade(label='Bitrate', menu=self._get_bitrate())
        self.add_cascade(label='Sample Rate', menu=self._get_sample_rate())

    def _get_sample_rate(self):
        self._sample_rate = tk.StringVar()
        self._sample_rate.set('44100Hz')

        _sample_rate = tk.Menu(self)
        for sample in ['22050Hz', '44100Hz']:
            _sample_rate.add_radiobutton(
                label=sample, variable=self._sample_rate)
        return _sample_rate

    def _get_watermarks(self):
        self.watermarks_num = tk.StringVar()
        self.watermarks_num.set('Auto')

        watermarks = tk.Menu(self)
        watermarks.add_radiobutton(label='Auto', variable=self.watermarks_num)

        for i in range(2, 9):
            watermarks.add_radiobutton(label=str(i),
                                       variable=self.watermarks_num)

        return watermarks

    def _get_bitrate(self):
        self._bitrate = tk.StringVar()
        self._bitrate.set('64k')

        _bitrate = tk.Menu(self)
        for rate in ['32k', '64k', '128k', '192k', '256k', '320k']:
            _bitrate.add_radiobutton(label=rate, variable=self._bitrate)
        return _bitrate


class MenuBar(tk.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.audio = AudioMenu(tearoff=False)
        self.options = OptionsMenu(tearoff=False)
        self._go = GoMenu(tearoff=False)
        self._help = TaskMenu(tearoff=False)

        self.add_cascade(label='Audio', menu=self.audio)
        self.add_cascade(label='Go', menu=self._go)
        self.add_cascade(label='Options', menu=self.options)
        self.add_cascade(label='Tasks', menu=self._help)

    @property
    def watermarks(self):
        return self.audio.watermarks_num.get()

    @property
    def bitrate(self):
        return self.audio._bitrate.get()

    @property
    def sample_rate(self):
        return self.audio._sample_rate.get().replace('Hz', '')
