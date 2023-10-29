from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from taskagent.llm import LLM

class BibTeX:

    def chat(self, text, verbose):
        template = '''
Convert BibTeX style reference to APA styles.

### Output rules
1. If the input reference text includes 'URL' tag, insert the URL at the end of the output in the format "URL: url". Otherwise not insert "URL" text.
2. Do not use line feeds, use white space instead.

### Input

BibTex style reference: {reference}

### Output format

APA style:
ACM style:
plain style:
abbrev style:
alpha style:
'''

        prompt = PromptTemplate(
            input_variables=['reference'],
            template=template
        )
        chain = LLMChain(llm=LLM.get_model(), prompt=prompt, verbose=verbose)
        return chain.run({'reference': text})