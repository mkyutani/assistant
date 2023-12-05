import sys
from computer.environment import config, env

def add_config_parsers(subparser):
    subcommand_parser = subparser.add_parser('config', help='config command')
    subcommand_subparser = subcommand_parser.add_subparsers(dest='subcommand', title='config subcommand', required=True)
    list_parser = subcommand_subparser.add_parser('list', help='List items')
    print_parser = subcommand_subparser.add_parser('print', help='Print item')
    print_parser.add_argument('name', help='name')
    remove_parser = subcommand_subparser.add_parser('remove', help='Remove item')
    remove_parser.add_argument('name', help='name')
    set_parser = subcommand_subparser.add_parser('set', help='Set item')
    set_parser.add_argument('name', help='name')
    set_parser.add_argument('value', nargs='?', help='value')

def _print_config(name=None):
    try:
        if name:
            values = {name: config.retrieve(name)}
        else:
            values = config.retrieve_all()

        for name, value in values.items():
            print(f'{name}={value}')
    except KeyError:
        print('No such a configuration item', file=sys.stderr)

def list_config(args):
    _print_config()

def print_config(args):
    _print_config(name=args.name)

def set_config(args):
    name = args.name
    value = args.value

    if not value:
        name_with_value = name.split('=', 1)
        name = name_with_value[0]
        if len(name_with_value) == 2:
            value = name_with_value[1]
        else:
            value = ''

    try:
        config.store(name, value)
    except KeyError:
        print('No such a configuration item', file=sys.stderr)

def remove_config(args):
    try:
        config.remove(args.name)
    except KeyError:
        print('No such a configuration item', file=sys.stderr)