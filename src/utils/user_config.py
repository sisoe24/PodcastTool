import os
import pickle

from src.startup import USER_CONFIG


class UserConfig:
    def __init__(self, mode='rb'):
        self._mode = mode
        self._file = USER_CONFIG

    def __enter__(self):
        self._open = open(self._file, self._mode)
        return self._open

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._open.close()

    @property
    def file(self):
        return self._file

    @property
    def data(self):
        if self.get_size() > 0:
            with open(self._file, 'rb') as file:
                return pickle.load(file)

    def value(self, key, default=''):
        try:
            value = self.data[key]
        except (KeyError, TypeError):
            return default
        else:
            if value:
                return value
            return default

    def is_empty(self):
        if self.get_size() <= 0:
            return True
        for key, value in self.data.items():
            if key in ['host', 'user', 'pass', 'web']:
                if not value:
                    return True
        return False

    def get_size(self):
        return os.path.getsize(self._file)
