import json
import os
import sys
from enum import Enum
from loguru import logger as loguru_logger

class Env:

    def __new__(cls, *args, **kargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Env, cls).__new__(cls)

            cls._logger = loguru_logger
            cls._logger.remove()
            cls._logger.add(sys.stderr, level='INFO')
            cls._logger.add( 'log/log.txt', level='DEBUG')

            cls._data_dir = os.path.expanduser('~') + '/.assistant'
            os.makedirs(cls._data_dir, exist_ok=True)
            cls._memory_path = f'{cls._data_dir}/memory.json'
            cls._memory = {}
            cls._load_memory()

        return cls._instance

    @classmethod
    def _load_memory(cls):
        try:
            with open(f'{cls._memory_path}', 'r') as f:
                cls._memory = json.load(f)
            cls._logger.debug(f'Load memory: {cls._memory}')
        except Exception as e:
            cls._logger.debug(f'Failed to load memory from {cls._memory_path}')

        cls._memory_loaded = True

    @classmethod
    def _save_memory(cls):
        try:
            with open(f'{cls._memory_path}', 'w') as f:
                json.dump(cls._memory, f, ensure_ascii=True)
            cls._logger.debug(f'Save memory: {cls._memory}')
        except Exception as e:
            cls._logger.debug(f'Failed to save memory to {cls._memory_path}')

    def __init__(self):
        pass

    def _get_memory(self, name):
        return self._memory.get(name)

    def _set_memory(self, name, value):
        self._memory[name] = value

    def _remove_memory(self, name):
        try:
            del self._memory[name]
        except KeyError:
            pass

    def get(self, name):
        return os.environ.get(name)

    def set(self, name, value):
        os.environ[name] = value

    def logger(self):
        return self._logger

    def data_dir(self):
        return self._data_dir

    def retrieve(self, name):
        return self._get_memory(name)

    def store(self, name, value):
        self._set_memory(name, value)
        self._save_memory()

    def remove(self, name):
        self._remove_memory(name)
        self._save_memory()

class Config:

    _global_config_names = [
        'auto_select_model_name',
        'assistant_always_reassigned'
    ]

    def __new__(cls, *args, **kargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Config, cls).__new__(cls)

            config = env.retrieve('config')
            if not config:
                config = {}

            for n in cls._global_config_names:
                if not n in config:
                    config[n] = None

            env.store('config', config)

        return cls._instance

    def retrieve(self, name):
        if name not in self._global_config_names:
            raise KeyError

        config = env.retrieve('config')
        value = config.get(name)
        return value

    def retrieve_all(self):
        config = env.retrieve('config')
        return config

    def store(self, name, value):
        if name not in self._global_config_names:
            raise KeyError

        config = env.retrieve('config')
        config[name] = value
        env.store('config', config)

    def remove(self, name):
        if name not in self._global_config_names:
            raise KeyError

        config = env.retrieve('config')
        config[name] = None
        env.store('config', config)

env = Env()
logger = Env().logger()
config = Config()