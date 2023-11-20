import os
import sys
from dotenv import load_dotenv
from loguru import logger as loguru_logger

class Env:

    def __new__(cls, *args, **kargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(Env, cls).__new__(cls)
            load_dotenv()
            cls._data_dir = os.path.expanduser('~') + '/.assistant'
            os.makedirs(cls._data_dir, exist_ok=True)
            cls._logger = loguru_logger
            cls._logger.remove()
            cls._logger.add(sys.stderr, level="INFO")
            cls._logger.add( 'log/log.txt', level="DEBUG")
        return cls._instance

    def __init__(self):
        pass

    def get(self, name):
        return os.environ.get(name)

    def logger(self):
        return self._logger

    def data_dir(self):
        return self._data_dir

    def save_strings(self, property, values):
        with open(f'{self._data_dir}/{property}', 'w') as fd:
            for value in values:
                print(value, file=fd)

    def load_strings(self, property):
        try:
            with open(f'{self._data_dir}/{property}', 'r') as fd:
                values = fd.readlines()
            values = [v.strip() for v in values]
            values = [v for v in values if len(v) > 0]
            return values
        except Exception as e:
            return None

env = Env()
logger = Env().logger()