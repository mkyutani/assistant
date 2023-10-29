import io
import os
import sys
from distutils.util import strtobool
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

load_dotenv()
openai_key = os.environ['OPENAI_API_KEY']
verbose = strtobool(os.environ.get('VERBOSE', 'False'))

llm = ChatOpenAI(model_name='gpt-3.5-turbo')

template = '''
{text}
'''

def set_io_buffers():
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def main():
    set_io_buffers()

    prompt = PromptTemplate(
        input_variables=['text'],
        template=template,
    )

    chain = LLMChain(llm=llm, prompt=prompt, verbose=verbose)

    print(chain(sys.stdin.read())['text'])
