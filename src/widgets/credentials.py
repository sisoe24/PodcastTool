import pickle
import tkinter as tk
from tkinter import ttk

from ..app import CustomDialog
from ..utils import UserConfig


class CredentialsEntry(CustomDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('Update Credentials')

        ttk.Label(self._layout, text='Host').grid(row=0, sticky=tk.E)
        ttk.Label(self._layout, text='User').grid(row=1, sticky=tk.E)
        ttk.Label(self._layout, text='Password').grid(row=2, sticky=tk.E)
        ttk.Label(self._layout, text='Website').grid(row=3, sticky=tk.E)

        self.host_entry = ttk.Entry(self._layout, width=27)
        self.user_entry = ttk.Entry(self._layout, width=27)
        self.pass_entry = ttk.Entry(self._layout, width=27, show="*")
        self.web_entry = ttk.Entry(self._layout, width=27)

        self.host_entry.grid(row=0, column=1)
        self.user_entry.grid(row=1, column=1)
        self.pass_entry.grid(row=2, column=1)
        self.web_entry.grid(row=3, column=1)

        self._save_btn.config(command=self._save)

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

