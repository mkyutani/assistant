import re
import openai

from assistant.environment import env, logger

def add_assistant_parsers(subparser):
    create_parser = subparser.add_parser('create', help='create assistants')
    create_parser.add_argument('-f', '--file_ids', help='file ids (comma separated)')
    create_parser.add_argument('-i', '--instruction', help='instructions')
    create_parser.add_argument('-n', '--name', help='name')
    list_parser = subparser.add_parser('list', help='list assistants')
    list_parser.add_argument('-L', '--long', action='store_true', help='long format')
    list_parser.add_argument('-S', '--separator', default=' ', help='output field separator')
    return subparser

def list_assistants(args):
    separator = args.separator
    long = args.long

    assistants = openai.beta.assistants.list()
    logger.debug(f'List assistants: {assistants}')
    for assistant_data in assistants.data:
        id = assistant_data.id if assistant_data.id else 'None'
        name = assistant_data.name if assistant_data.name else 'None'
        model = assistant_data.model if assistant_data.model else 'None'
        instructions = re.sub(r'\s', '_', assistant_data.instructions if assistant_data.instructions else 'None')
        if len(instructions) > 10:
            instructions = instructions[0:8] + '..'
        tools = ';'.join([tool.type for tool in assistant_data.tools]) if assistant_data.tools else 'None'
        if long:
            print(separator.join([id, model, tools, name, instructions]))
        else:
            print(separator.join([id, name]))

def create_assistant(args):
    name = args.name
    instructions = args.instruction
    separator = ' '
    if args.file_ids:
        file_ids = args.file_ids.split(',')
    else:
        file_ids = []

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