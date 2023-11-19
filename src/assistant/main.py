import argparse
import io
import os
import sys
from time import sleep
from dotenv import load_dotenv

from assistant.assistant import create_assistant, list_assistants, query_assistant

category_functions = {
    'list': list_assistants,
    'create': create_assistant,
    'query': query_assistant
}

def set_io_buffers():
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def main():
    set_io_buffers()

    parser = argparse.ArgumentParser(description='assistant')
    sps_category = parser.add_subparsers(dest='category', title='category', required=True)
    sp_list = sps_category.add_parser('list', help='list assistants')
    sp_list.add_argument('-L', '--long', action='store_true', help='output field separator')
    sp_list.add_argument('-S', '--separator', default=' ', help='output field separator')
    sp_create = sps_category.add_parser('create', help='create assistants')
    sp_create.add_argument('file', nargs='*', metavar='file', default=None, help='file path')
    sp_create.add_argument('-n', '--name', help='name')
    sp_create.add_argument('-i', '--instruction', help='instructions')
    sp_query = sps_category.add_parser('query', help='ask assistants')
    sp_query.add_argument('id', metavar='id', help='assistant id')
    sp_query.add_argument('-q', '--query', default=None, help='query string')
    args = parser.parse_args()

    category_function = category_functions.get(args.category)
    category_function(args)

    return 0