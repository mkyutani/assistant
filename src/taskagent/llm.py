import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI

from taskagent.env import Env

class LLM:

    _only_instance = None
    _model = None

    def __new__(cls):
        raise NotImplementedError('Cannot Generate Instance By Constructor')

    @classmethod
    def _internal_new(cls):
        return super().__new__(cls)

    @classmethod
    def get_instance(cls):
        if not cls._only_instance:
            cls._only_instance = cls._internal_new()
            model_name = os.environ.get('OPENAI_MODEL_NAME')
            openai_api_key = os.environ.get('OPENAI_API_KEY')
            if model_name is None:
                Env.logger().error('Missing OPENAI_MODEL_NAME in environment')
            if openai_api_key is None:
                Env.logger().error('Missing OPENAI_API_KEY in environment')
            else:
                cls._only_instance._model = ChatOpenAI(model_name=model_name, openai_api_key=openai_api_key)
        return cls._only_instance

    @classmethod
    def get_model(cls):
        return cls.get_instance()._model
