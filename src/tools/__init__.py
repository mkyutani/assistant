from .simple import Simple
from .bibtex import BibTeX

definitions = {
    'bibtex': { 'class': 'BibTeX', 'description': 'Convert BibTeX style reference to other styles' }
}

def create_instance(tool_definition):
    return globals()[tool_definition['class']]()