import re
import sys
from time import sleep
import openai
from computer.environment import env, logger
from computer.util import get_all_assistants

def add_conversation_parsers(subparser):
    restart_parser = subparser.add_parser('restart', help='restart conversation')
    retrieve_parser = subparser.add_parser('retrieve', help='retrieve conversation')
    retrieve_parser.add_argument('-f', '--footnotes', action='store_true', help='print footnotes')
    select_parser = subparser.add_parser('select', help='select assistant')
    select_parser.add_argument('pattern', help='search pattern of assistants id or name')
    talk_parser = subparser.add_parser('talk', help='conversation with assistant')
    talk_parser.add_argument('message', nargs='?', help='message to assistant')
    talk_parser.add_argument('-a', '--assistant', help='assistant id or name')
    talk_parser.add_argument('-m', '--model', help='model name')
    unselect_parser = subparser.add_parser('unselect', help='unselect assistant')
    return subparser

def _select_assistant_by_pattern(pattern):
    assistants = get_all_assistants()
    matched_assistants = [a for a in assistants.data if re.search(pattern, f'{a.id}\r{a.name}')]
    return matched_assistants[0] if len(matched_assistants) == 1 else None

_message_template = '''
Which assistant best answers the following question?

### Question
{context}

### Rules
- Answer the assistant name simply

### Assistant candidates
{itemized_assistant_descriptions}
'''

def _select_assistant_name_by_chat_completions(auto_select_message):
    response = openai.chat.completions.create(
        model = env.get('OPENAI_MODEL_NAME'),
        messages = [
            { 'role': 'user', 'content': auto_select_message }
        ]
    )
    logger.debug(f'Auto select: {response}')

    try:
        selected_assistant_name = response.choices[0].message.content
    except Exception:
        selected_assistant_name = None

    return selected_assistant_name

def _select_assistant_by_context(context):
    original_chat_name = 'Chat completion'
    original_chat_instructions = 'Original ChatGPT chat completion'
    assistants = get_all_assistants()
    assistant_descriptions = [(a.name, a.instructions if a.instructions else '') for a in assistants.data if a.name]
    assistant_descriptions.append((original_chat_name, original_chat_instructions))
    itemized_assistant_descriptions = '\n'.join([f'- Name: {name}\n  Description: {description}' for (name, description) in assistant_descriptions])
    auto_select_message = _message_template.format(context=context, itemized_assistant_descriptions=itemized_assistant_descriptions)
    selected_name = _select_assistant_name_by_chat_completions(auto_select_message)
    for assistant_data in assistants.data:
        if selected_name == assistant_data.name:
            return assistant_data
    else:
        return None

def _select_assistant(pattern, message=None):
    assistant_profile = env.retrieve('assistant')
    if pattern:
        assistant = _select_assistant_by_pattern(pattern)
        if not assistant:
            print('Assistant id or name is ambiguous or not matched with any ones', file=sys.stderr)
            assistant_profile = None
            env.remove('assistant')
        else:
            print(f'Assistant {assistant.name} is assigned', file=sys.stderr)
            assistant_profile = { 'id': assistant.id, 'name': assistant.name}
            env.store('assistant', assistant_profile)
    elif assistant_profile:
        pass
    elif message:
        assistant = _select_assistant_by_context(message)
        if assistant is None:
            print('No assistant is assigned automatically', file=sys.stderr)
            assistant_profile = None
            env.remove('assistant')
        else:
            print(f'Assistant {assistant.name} is assigned', file=sys.stderr)
            assistant_profile = { 'id': assistant.id, 'name': assistant.name}
            env.store('assistant', assistant_profile)

    return assistant_profile

def _unselect_assistant():
    env.remove('assistant')

def _start_thread():
    thread = openai.beta.threads.create()
    logger.debug(f'Create thread: {thread}')
    thread_profile = { 'type': 'thread', 'id': thread.id, 'messages': None }
    env.store('thread', thread_profile)
    print('New thread is created', file=sys.stderr)
    return thread_profile

def _start_chat_completion():
    thread_profile = { 'type': 'chat-completion', 'id': None, 'messages': [] }
    env.store('thread', thread_profile)
    print('New chat completion is created', file=sys.stderr)
    return thread_profile

def _remove_thread():
    env.remove('thread')

def _select_thread_and_assistant(pattern, user_message):
    thread_profile = env.retrieve('thread')
    assistant_profile = env.retrieve('assistant')
    if not thread_profile or (thread_profile['type'] == 'thread' and not assistant_profile):
        assistant_profile = _select_assistant(pattern, user_message)
        if assistant_profile:
            thread_profile = _start_thread()
        else:
            thread_profile = _start_chat_completion()

def select(args):
    pattern = args.pattern
    separator = ' '

    assistant_profile = _select_assistant(pattern)
    if not assistant_profile:
        print('No assistant is selected', file=sys.stderr)
    else:
        print(separator.join([assistant_profile.id, assistant_profile.name]))

def unselect(args):
    _unselect_assistant()

def restart(args):
    _remove_thread()
    _unselect_assistant()

def _print_thread_messages(thread_profile, start_message_id=None, print_footnotes=True):
    thread_id = thread_profile['id']
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
                filename = 'missing'
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

def _talk_with_assistants(thread_profile, assistant_profile, user_message):
    thread_id = thread_profile['id']
    assistant_id = assistant_profile['id']

    message = openai.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_message)
    logger.debug(f'Create message: {message}')

    run = openai.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
    logger.debug(f'Create run: {run}')

    status = 'in_progress'
    while status in ['queued', 'in_progress', 'requires_action', 'cancelling']:
        sleep(10)
        result = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        logger.debug(f'Retrieve run: {result}')
        status = result.status

    if status == 'cancelled':
        print('Cancelled by user', file=sys.stderr)
    elif status == 'failed':
        print(f'Failed: {result.last_error.code}: {result.last_error.message}', file=sys.stderr)
    elif status == 'expired':
        print('Expired: Try again later', file=sys.stderr)
    else:
        _print_thread_messages(thread_profile, start_message_id=message.id, print_footnotes=False)

def _print_chat_completion_messages(thread_profile):
    messages = thread_profile['messages']
    message_separator = None
    for message_index, message in enumerate(messages, start=1):
        role = message['role']
        content = message['content']
        message_string = f'#{message_index}:{role}: {content}'

        if message_separator:
            print(message_separator)
        else:
            message_separator = '-' * 80
        print(message_string)
        logger.debug('Message: ' + re.sub(r'\s', '_', message_string))

def _talk_by_chat_completion(thread_profile, user_message):
        messages = thread_profile['messages']
        messages.append({ 'role': 'user', 'content': user_message })
        model = env.get('OPENAI_MODEL_NAME')
        response = openai.chat.completions.create(model=model, messages=messages)
        logger.debug(response)
        response_message = response.choices[0].message.content
        response_role = response.choices[0].message.role
        messages.append({'role': response_role, 'content': response_message})
        thread_profile['messages'] = messages
        env.store('thread', thread_profile)
        _print_chat_completion_messages(thread_profile)

def retrieve(args):
    print_footnotes = args.footnotes

    thread_profile = env.retrieve('thread')
    if thread_profile is None:
        print('No conversation history', file=sys.stderr)
    elif thread_profile['type'] == 'thread':
        _print_thread_messages(thread_profile, print_footnotes=print_footnotes)
    else:
        if print_footnotes is True:
            print('Ignore print_footnotes option because messages are created by chat completion', file=sys.stderr)
        _print_chat_completion_messages(thread_profile)

def talk(args):
    if args.model:
        env.set('OPENAI_MODEL_NAME', args.model)

    if args.message:
        user_message = args.message
    else:
        user_message = sys.stdin.read()

    if args.assistant:
        pattern = args.assistant
    else:
        pattern = None        

    _select_thread_and_assistant(pattern, user_message)
    thread_profile = env.retrieve('thread')
    assistant_profile = env.retrieve('assistant')
    if thread_profile['type'] == 'thread':
        _talk_with_assistants(thread_profile, assistant_profile, user_message)
    else:
        _talk_by_chat_completion(thread_profile, user_message)