import argparse
import io
import sys

from computer.assistant import add_assistant_parsers, create_assistant, delete_assistant, list_assistants
from computer.config import add_config_parsers, list_config, print_config, set_config, unset_config
from computer.conversation import add_conversation_parsers, restart, retrieve, select, talk, unselect
from computer.file import add_file_parsers, create_file, list_files

command_functions = {
    'assistant': {
        'create': create_assistant,
        'delete': delete_assistant,
        'list': list_assistants
    },
    'config': {
        'list': list_config,
        'print': print_config,
        'set': set_config,
        'unset': unset_config
    },
    'file': {
        'create': create_file,
        'list': list_files
    },
    'restart': restart,
    'retrieve': retrieve,
    'select': select,
    'talk': talk,
    'unselect': unselect
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
    add_assistant_parsers(conversation_subparser)
    add_file_parsers(conversation_subparser)
    add_config_parsers(conversation_subparser)

    args = parser.parse_args()

    if 'subcommand' in args:
        command_function = command_functions[args.command][args.subcommand]
    else:
        command_function = command_functions[args.command]
    command_function(args)

    return 0