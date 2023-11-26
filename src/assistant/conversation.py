import re
import sys
from time import sleep
import openai
from assistant.environment import env, logger

def add_conversation_parsers(subparser):
    restart_parser = subparser.add_parser('restart', help='restart conversation')
    retrieve_parser = subparser.add_parser('retrieve', help='retrieve conversation')
    retrieve_parser.add_argument('-f', '--footnotes', action='store_true', help='print footnotes')
    select_parser = subparser.add_parser('select', help='select assistant')
    select_parser.add_argument('pattern', help='search pattern of assistants id or name')
    talk_parser = subparser.add_parser('talk', help='conversation with assistant')
    talk_parser.add_argument('message', nargs='?', help='message to assistant')
    talk_parser.add_argument('-a', '--assistant', help='assistant id or name')
    unselect_parser = subparser.add_parser('unselect', help='unselect assistant')
    return subparser

auto_select_message_template = '''
Which assistant best answers the following question?

### Question
{user_message}

### Rules
- Answer the assistant name simply

### Assistant candidates
{itemized_assistant_names}
'''

def _list_assistants():
    assistants = openai.beta.assistants.list()
    logger.debug(f'List assistants: {assistants}')
    return assistants

def _select_assistant_by_chat_completions(auto_select_message):
    response = openai.chat.completions.create(
        model = env.get('OPENAI_MODEL_NAME'),
        messages = [
            { 'role': 'user', 'content': auto_select_message }
        ]
    )
    logger.debug(f'Auto select: {response}')

    try:
        selected = response.choices[0].message.content
    except Exception:
        selected = None

    print(selected)

    return selected

def _auto_select_assistant(user_message):
    assistants = _list_assistants()
    itemized_assistant_names = '\n'.join(['- ' + ad.name for ad in assistants.data if ad.name])
    auto_select_message = auto_select_message_template.format(user_message=user_message, itemized_assistant_names=itemized_assistant_names)
    selected_name = _select_assistant_by_chat_completions(auto_select_message)
    for assistant_data in assistants.data:
        if selected_name == assistant_data.name:
            return assistant_data.id
    else:
        return None

def _select_assistant(pattern):
    all_assistants = openai.beta.assistants.list()
    matched_assistants = [a for a in all_assistants.data if re.search(pattern, f'{a.id}\r{a.name}')]
    return matched_assistants[0] if len(matched_assistants) == 1 else None

def select(args):
    pattern = args.pattern
    separator = ' '

    assistant = _select_assistant(pattern)
    if not assistant:
        print('Id or name is not matched or ambiguous', file=sys.stderr)
    else:
        env.store(('assistant', assistant.id))
        print(separator.join([assistant.id, assistant.name]))

def _unselect_assistant():
    env.remove('assistant')

def unselect(args):
    _unselect_assistant()

def _restart_assistant():
    thread = openai.beta.threads.create()
    logger.debug(f'Create thread: {thread}')
    if thread:
        env.store(('thread', thread.id))
    return thread

def restart(args):
    _restart_assistant()
    _unselect_assistant()

def _print_thread_messages(thread_id, start_message_id=None, print_footnotes=True):
    thread_messages = openai.beta.threads.messages.list(thread_id)
    logger.debug(f'List thread messages: {thread_messages}')

    if start_message_id is None:
        message_to_print = True
    else:
        message_to_print = False

    message_separator = None
    for message_index, thread_message in enumerate(reversed(thread_messages.data), start=1):
        if message_to_print is False:
            if thread_message.id == start_message_id:
                message_to_print = True
            else:
                continue

        answer = thread_message.content[0].text.value
        role = thread_message.role
        annotations = thread_message.content[0].text.annotations
        footnotes = []
        for note_index, annotation in enumerate(annotations, start=1):
            note_mark = f'[{note_index}]'
            file_id = annotation.file_citation.file_id
            if file_id is None or len(file_id) == 0:
                filename = 'missing-file-name'
            else:
                filename = openai.files.retrieve(file_id).filename
            quote = annotation.file_citation.quote
            footnotes.append(f'{note_mark} In {filename}.\n{quote}')
            if annotation.text is not None and len(annotation.text) > 0:
                answer = answer.replace(annotation.text, note_mark)

        message_string = f'#{message_index}:{role}: {answer}'
        footnotes_string = '\n'.join(footnotes)

        if message_separator:
            print(message_separator)
        else:
            message_separator = '-' * 80
        print(message_string)
        logger.debug('Message: ' + re.sub(r'\s', '_', message_string))
        if len(footnotes_string) > 0:
            if print_footnotes is True:
                print('-' * 8 + '\n' + footnotes_string)
                logger.debug('Footnotes: ' + re.sub(r'\s', '_', footnotes_string)[:80])

def retrieve(args):
    print_footnotes = args.footnotes

    thread_id = env.retrieve('thread')
    if thread_id is None:
        print('No conversation history', file=sys.stderr)
    else:
        _print_thread_messages(thread_id, print_footnotes=print_footnotes)

def talk(args):
    if args.message:
        message = args.message
    else:
        message = sys.stdin.read()

    if args.assistant:
        assistant = _select_assistant(args.assistant)
        if assistant is None:
            print('Id or name is not matched or ambiguous', file=sys.stderr)
            return
        assistant_id = assistant.id
        env.store(('assistant', assistant_id))
    else:
        assistant_id = env.retrieve('assistant')
        if assistant_id is None:
            assistant_id = _auto_select_assistant(message)
            if assistant_id is None:
                print('No assistant is assigned automatically', file=sys.stderr)
                return
            env.store(('assistant', assistant_id))
            print(f'Assistant {assistant_id} is assigned', file=sys.stderr)

    thread_id = env.retrieve('thread')
    if thread_id is None:
        thread = _restart_assistant()
        thread_id = thread.id

    message = openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )
    logger.debug(f'Create message: {message}')

    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    logger.debug(f'Create run: {run}')

    status = 'in_progress'
    while status in ['queued', 'in_progress', 'requires_action', 'cancelling']:
        sleep(10)
        result = openai.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        logger.debug(f'Retrieve run: {result}')
        status = result.status

    if status == 'cancelled':
        print('Cancelled by user', file=sys.stderr)
    elif status == 'failed':
        print(f'Failed: {result.last_error.code}: {result.last_error.message}', file=sys.stderr)
    elif status == 'expired':
        print('Expired: Try again later', file=sys.stderr)
    else:
        _print_thread_messages(thread_id, start_message_id=message.id, print_footnotes=False)
