import os
from langchain.chat_models import ChatOpenAI

class LLM:

    _only_instance = None

    def __new__(cls):
        raise NotImplementedError('Cannot Generate Instance By Constructor')

    @classmethod
    def __internal_new__(cls):
        model_name = os.environ['OPENAI_MODEL_NAME']
        openai_api_key = os.environ['OPENAI_API_KEY']
        cls.model = ChatOpenAI(model_name=model_name, openai_api_key=openai_api_key)
        return super().__new__(cls)

    @classmethod
    def get_instance(cls):
        if not cls._only_instance:
            cls._only_instance = cls.__internal_new__()
        return cls._only_instance

    @classmethod
    def get_model(cls):
        return cls.get_instance().model