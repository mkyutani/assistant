import argparse
import io
import os
import sys
from time import sleep
from dotenv import load_dotenv

from assistant.assistant import add_assistant_parsers, create_assistant, list_assistants, restart_assistant, retrieve_assistant, select_assistant, talk_assistant
from assistant.file import add_file_parsers, create_file, list_files

command_functions = {
    'list': list_assistants,
    'select': select_assistant,
    'create': create_assistant,
    'restart': restart_assistant,
    'retrieve': retrieve_assistant,
    'talk': talk_assistant,
    'file': {
        'list': list_files,
        'create': create_file
    }
}

def set_io_buffers():
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def main():
    set_io_buffers()

    parser = argparse.ArgumentParser(description='assistant')
    command_subparser = parser.add_subparsers(dest='command', title='command', required=True)
    command_subparser = add_assistant_parsers(command_subparser)

    file_parser = command_subparser.add_parser('file', help='file command')
    file_subparser = file_parser.add_subparsers(dest='subcommand', title='file subcommand', required=True)
    file_subparser = add_file_parsers(file_subparser)

    args = parser.parse_args()

    if 'subcommand' in args:
        command_function = command_functions[args.command][args.subcommand]
    else:
        command_function = command_functions[args.command]
    command_function(args)

    return 0