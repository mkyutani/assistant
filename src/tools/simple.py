from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from taskagent.llm import LLM

class Simple:

    def chat(self, text, verbose):
        prompt = PromptTemplate(
            input_variables=['text'],
            template='{text}',
        )
        chain = LLMChain(llm=LLM.get_model(), prompt=prompt, verbose=verbose)
        return chain.run(text)