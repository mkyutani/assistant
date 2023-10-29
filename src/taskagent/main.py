import argparse
import io
import os
import sys
from dotenv import load_dotenv

import tools

def set_io_buffers():
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def main():
    set_io_buffers()

    load_dotenv()

    parser = argparse.ArgumentParser(description='Task agent')
    parser.add_argument('issue', nargs='?', default=None, help='issue')
#    parser.add_argument('--simple', action='store_true', help='simple query')
    parser.add_argument('--verbose', action='store_true', help='verbose')
    args = parser.parse_args()

    if args.issue is None:
        text = sys.stdin.read()
        response = tools.Simple().chat(text, args.verbose)
        print(response)
    else:
        tool_definition = tools.definitions.get(args.issue)
        if tool_definition is None:
            print('No such an issue', file=sys.stderr)
        else:
            tool = tools.create_instance(tool_definition)
            text = sys.stdin.read()
            response = tool.chat(text, args.verbose)
            print(response)