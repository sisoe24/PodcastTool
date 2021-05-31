import os
import sys
import shutil
import pickle
import pathlib
import subprocess

import tkinter as tk
from tkinter import messagebox, ttk, filedialog

from app import CustomDialog
from utils import util, UserConfig
from startup import (
    open_path,
    LOG_PATH,
    USER_AUDIO,
    SYS_CONFIG_PATH,
    RESOURCES_PATH
)

from utils.resources import (
    _system_catalog_path,
    _catalog_file
)

from widgets.html_frame import archive_files
from widgets.credentials import CredentialsEntry


def _update_config(setting):

    data = UserConfig().data
    data.update(setting)

    with UserConfig(mode='wb') as file:
        pickle.dump(data, file)


class OptionsMenu(tk.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_command(label='Set Podcast Folder', command=self._set_folder)
        self.add_separator()

        self._is_dev_mode = tk.BooleanVar()
        self._dev_mode_key = 'dev_mode'
        _dev_mode_config = UserConfig().value(self._dev_mode_key, False)
        self._is_dev_mode.set(_dev_mode_config)
        self.add_command(label='Update credentials', command=CredentialsEntry)

        self.add_separator()

        self.add_checkbutton(label='Enable Developer mode',
                             variable=self._is_dev_mode, command=self._reboot)

        self._test_upload = tk.BooleanVar(False)
        self.add_checkbutton(label='Upload to ftp/virgil_test',
                             variable=self._test_upload)

        _use_html = tk.BooleanVar()
        _html_key = 'html_mediaplayer'
        _use_html_config = UserConfig().value(_html_key, False)
        _use_html.set(_use_html_config)

        self.add_checkbutton(label='Use Flash Mediaplayer',
                             variable=_use_html,
                             command=lambda: _update_config(
                                 {_html_key: _use_html.get()}
                             ))

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


class RunMenu(tk.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_command(label='Clean Log', command=self.clean_log)
        self.add_command(label='Clean Archive', command=self.delete_archive)

        self.add_separator()
        self.add_command(label='Create bash setup', command=self.bash_setup)
        self.add_separator()

        self.add_command(label='Reset Names/Audio', command=self.restore_json)

    @staticmethod
    def bash_setup():

        cmd = f"alias podcasttool='bash {RESOURCES_PATH}/scripts/podcasttool.sh'"
        with open(os.path.join(os.getenv('HOME'), '.bashrc'), 'r+') as f:
            if f.read().find('alias podcasttool') == -1:
                f.write(cmd)

        messagebox.showinfo(title='PodcastTool', message='Done')

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

        messagebox.showinfo(
            title='PodcastTool',
            message='Done.\nApplication must be restarted manually')
        sys.exit()

    @staticmethod
    def delete_archive():
        """Delete all the html archive files."""
        for i in archive_files():
            os.remove(i)

        messagebox.showinfo(title='PodcastTool', message='Done')


class GoMenu(tk.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_command(label='Log', command=lambda: open_path(LOG_PATH))

        self.add_command(
            label='Resources',
            command=lambda: open_path(RESOURCES_PATH)
        )

        self.add_command(
            label='Configuration',
            command=lambda: open_path(SYS_CONFIG_PATH)
        )


class CreateAudio(CustomDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('Create Audio sample')

        ttk.Label(self._layout, text='Text').grid(row=0, sticky=tk.E)
        ttk.Label(self._layout, text='Language').grid(row=1, sticky=tk.E)

        self._text_entry = ttk.Entry(self._layout, width=24)
        self._lang_select = ttk.Combobox(self._layout, state="readonly",
                                         value=["it", "en"], width=5)
        self._lang_select.current(0)

        self._text_entry.grid(row=0, column=1)
        self._lang_select.grid(row=1, column=1, sticky=tk.W)

        self._save_btn.config(command=self.text_to_audio)

    def text_to_audio(self):
        """Generate text to audio files."""
        ask_user = filedialog.asksaveasfilename(
            initialfile=self._text_entry.get())
        if not ask_user:
            return

        path, filename = os.path.split(ask_user)
        if not util.generate_audio(text=self._text_entry.get(),
                                   filename=filename, path=path,
                                   lang=self._lang_select.get()):
            messagebox.showerror(title='PodcastTool',
                                 message='Problem Creating Audio. Check log file')


class AudioMenu(tk.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_cascade(label='Waterkmarks', menu=self._get_watermarks())
        self.add_cascade(label='Bitrate', menu=self._get_bitrate())
        self.add_cascade(label='Sample Rate', menu=self._get_sample_rate())

        self.add_separator()

        self.add_command(label='Create Audio sample',
                         command=CreateAudio)

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
        self._help = RunMenu(tearoff=False)

        self.add_cascade(label='Audio', menu=self.audio)
        self.add_cascade(label='Options', menu=self.options)
        self.add_cascade(label='Run', menu=self._help)
        self.add_cascade(label='Go', menu=self._go)

    def test_upload(self):
        return self.options._test_upload.get()

    @property
    def watermarks(self):
        return self.audio.watermarks_num.get()

    @property
    def bitrate(self):
        return self.audio._bitrate.get()

    @property
    def sample_rate(self):
        return self.audio._sample_rate.get().replace('Hz', '')
