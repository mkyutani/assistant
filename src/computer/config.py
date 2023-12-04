from computer.environment import env

def add_config_parsers(subparser):
    subcommand_parser = subparser.add_parser('config', help='config command')
    subcommand_subparser = subcommand_parser.add_subparsers(dest='subcommand', title='config subcommand', required=True)
    list_parser = subcommand_subparser.add_parser('list', help='List items')
    print_parser = subcommand_subparser.add_parser('print', help='Print item')
    print_parser.add_argument('name', help='name')
    set_parser = subcommand_subparser.add_parser('set', help='Set item')
    set_parser.add_argument('name', help='name')
    set_parser.add_argument('value', nargs='?', help='value')
    unset_parser = subcommand_subparser.add_parser('unset', help='Unset item')
    unset_parser.add_argument('name', help='name')

def _print_config(name=None):
    config = env.retrieve('config')
    if config:
        for c in config:
            if not name or c == name:
                print(f'{c}={config.get(c)}')

def list_config(args):
    _print_config()

def print_config(args):
    name = args.name
    _print_config(name=name)

def set_config(args):
    name = args.name
    value = args.value

    config = env.retrieve('config')
    if not config:
        config = {}

    if not value:
        nv = name.split('=', 1)
        name = nv[0]
        if len(nv) == 2:
            value = nv[1]
        else:
            value = ''
    config[name] = value

    env.store('config', config)

def unset_config(args):
    name = args.name

    config = env.retrieve('config')
    if config:
        try:
            del config[name]
            env.store('config', config)
        except Exception:
            pass