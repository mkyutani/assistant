import re
import sys
import openai

from assistant.environment import env, logger
from assistant.util import get_all_assistants, get_assistant_ids_from_names, get_file_ids_from_names

def add_assistant_parsers(subparser):
    delete_parser = subparser.add_parser('delete', help='delete assistants')
    delete_parser.add_argument('name', help='assistant name')
    delete_parser.add_argument('-s', '--strict', action='store_true', help='match name strictly')
    create_parser = subparser.add_parser('create', help='create assistants')
    create_parser.add_argument('-f', '--files', nargs='*', help='file names')
    create_parser.add_argument('-i', '--instruction', help='instructions')
    create_parser.add_argument('-n', '--name', help='name')
    list_parser = subparser.add_parser('list', help='list assistants')
    list_parser.add_argument('-L', '--long', action='store_true', help='long format')
    list_parser.add_argument('-S', '--separator', default=' ', help='output field separator')
    return subparser

def list_assistants(args):
    separator = args.separator
    long = args.long

    assistants = get_all_assistants()
    for assistant_data in assistants.data:
        id = assistant_data.id if assistant_data.id else 'None'
        name = assistant_data.name if assistant_data.name else 'None'
        model = assistant_data.model if assistant_data.model else 'None'
        instructions = re.sub(r'\s', '_', assistant_data.instructions if assistant_data.instructions else 'None')
        if len(instructions) > 40:
            instructions = instructions[0:38] + '..'
        tools = ';'.join([tool.type for tool in assistant_data.tools]) if assistant_data.tools else 'None'
        if long:
            print(separator.join([id, model, tools, name, instructions]))
        else:
            print(separator.join([id, name]))

def create_assistant(args):
    name = args.name
    filenames = args.files
    instructions = args.instruction
    file_purpose = 'assistants'
    separator = ' '

    if len(filenames) > 0:
        (file_ids, all_matched) = get_file_ids_from_names(filenames, purpose=file_purpose)
        if all_matched is False:
            for id, name in zip(file_ids, filenames):
                if id is None:
                    print(f'No files matched with {name}', file=sys.stderr)
            return
    else:
        file_ids = openai._types.NotGiven

    assistant = openai.beta.assistants.create(
        name=name,
        instructions=instructions if instructions is not None else 'You are a professional assistant.',
        model = env.get('OPENAI_MODEL_NAME'),
        tools=[{'type': 'retrieval'}],
        file_ids=file_ids
    )
    logger.debug(f'Create assistant object: {assistant}')

    env.store(('assistant', assistant.id))

    print(separator.join([assistant.id, assistant.name]))

def delete_assistant(args):
    name = args.name
    strict = args.strict

    matched_ids = get_assistant_ids_from_names([name], strict=strict)[0]
    if len(matched_ids) > 1:
        print(f'Ambiguous name: {name}', file=sys.stderr)
    elif len(matched_ids) == 0:
        print(f'No assistants matched with {name}', file=sys.stderr)
    else:
        id = matched_ids[0]
        deleted = openai.beta.assistants.delete(id)
        logger.debug(f'Delete assistant: {deleted}')
