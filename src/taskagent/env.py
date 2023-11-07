import os
import sys
from dotenv import load_dotenv
from loguru import logger

class Env:

    _logger = None

    @classmethod
    def init(cls):
        load_dotenv()
        cls._logger = logger
        cls._logger.remove()
        cls._logger.add(sys.stderr, level="INFO")
        cls._logger.add( 'logs/log.txt', level="DEBUG")
        return cls._logger

    @classmethod  
    def get(cls, name):
        return os.environment.get(name)

    @classmethod
    def logger(cls):
        return cls._logger
