import json
import os
import re
import sys
from time import sleep
import openai

from assistant.environment import env, logger

def add_assistant_parsers(subparser):
    list_parser = subparser.add_parser('list', help='list assistants')
    list_parser.add_argument('-L', '--long', action='store_true', help='long format')
    list_parser.add_argument('-S', '--separator', default=' ', help='output field separator')
    create_parser = subparser.add_parser('create', help='create assistants')
    create_parser.add_argument('-f', '--file_ids', help='file ids (comma separated)')
    create_parser.add_argument('-i', '--instruction', help='instructions')
    create_parser.add_argument('-n', '--name', help='name')
    query_parser = subparser.add_parser('query', help='ask assistants')
    query_parser.add_argument('id', default=None, help='assistant id')
    query_parser.add_argument('-q', '--query', default=None, help='query string')
    return subparser

def list_assistants(args):
    separator = args.separator
    long = args.long

    assistants = openai.beta.assistants.list()
    logger.debug(assistants)
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
            print(separator.join([id, model, name]))

def create_assistant(args):
    name = args.name
    instructions = args.instruction
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

    env.save_strings('assistant', [assistant.id])

    print(assistant.id)

def query_assistant(args):
    if args.query:
        query = args.query
    else:
        query = sys.stdin.read()
    if args.id:
        assistant_id = args.id
    else:
        assistant_id = env.load_strings('assistant')[0]

    assistant = openai.beta.assistants.retrieve(assistant_id=assistant_id)
    logger.debug(f'Retrieve assistant object: {assistant}')

    files = []
    for file_id in assistant.file_ids:
        file = openai.files.retrieve(file_id)
        logger.debug(f'Retrieve file object: {file}')
        files.append(file)

    thread = openai.beta.threads.create()
    logger.debug(f'Create thread object: {thread}')

    message = openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=query
    )
    logger.debug(f'Create message object: {message}')

    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    logger.debug(f'Create run object: {run}')

    status = 'in_progress'
    while status == 'in_progress':
        sleep(10)
        result = openai.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        logger.debug(f'Retrieve run object: {result}')
        status = result.status

    if status != 'completed':
        logger.error(f'Failed to retrieve, status={status}')
    else:
        thread_messages = openai.beta.threads.messages.list(thread.id)
        logger.debug(f'List thread messages: {thread_messages}')

        data_index = 1
        for data in reversed(thread_messages.data):
            answer = data.content[0].text.value
            role = data.role
            annotations = data.content[0].text.annotations
            footnotes = []
            note_index = 1
            for annotation in annotations:
                note_mark = f'[{note_index}]'
                filename = [f.filename for f in files if f.id == annotation.file_citation.file_id][0]
                quote = annotation.file_citation.quote
                footnotes.append(f'{note_mark} In {filename}.\n{quote}')
                answer = answer.replace(annotation.text, note_mark)
                note_index = note_index + 1

            message_string = f'#{data_index}:{role}: {answer}'
            footnotes_string = '\n'.join(footnotes)

            logger.debug(message_string)
            print(message_string)
            if len(footnotes_string) > 0:
                logger.debug(footnotes_string)
                print('----\n' + footnotes_string)

            data_index = data_index + 1
