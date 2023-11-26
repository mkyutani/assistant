import argparse
import io
import sys

from assistant.assistant import add_assistant_parsers, create_assistant, list_assistants
from assistant.conversation import add_conversation_parsers, restart, retrieve, select, talk
from assistant.file import add_file_parsers, create_file, list_files

command_functions = {
    'assistant': {
        'create': create_assistant,
        'list': list_assistants
    },
    'file': {
        'create': create_file,
        'list': list_files
    },
    'restart': restart,
    'retrieve': retrieve,
    'select': select,
    'talk': talk
}

def set_io_buffers():
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def main():
    set_io_buffers()

    parser = argparse.ArgumentParser(description='conversation')
    conversation_subparser = parser.add_subparsers(dest='command', title='conversation command', required=True)
    add_conversation_parsers(conversation_subparser)

    assistant_parser = conversation_subparser.add_parser('assistant', help='assistant command')
    assistant_subparser = assistant_parser.add_subparsers(dest='subcommand', title='assistant subcommand', required=True)
    add_assistant_parsers(assistant_subparser)

    file_parser = conversation_subparser.add_parser('file', help='file command')
    file_subparser = file_parser.add_subparsers(dest='subcommand', title='file subcommand', required=True)
    add_file_parsers(file_subparser)

    args = parser.parse_args()

    if 'subcommand' in args:
        command_function = command_functions[args.command][args.subcommand]
    else:
        command_function = command_functions[args.command]
    command_function(args)

    return 0