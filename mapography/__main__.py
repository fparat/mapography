# coding: utf-8

import sys
import argparse

from mapography import parser, model

__author__ = "Franck PARAT"


PARSERS = {
    'cosmic': parser.cosmic
}

VIEWERS = {}

COMMANDS = {
    'calls': ['tree', 'paths', 'longest'],  # function calls
    'modules': ['list']
}


def make_argparser():
    argparser = argparse.ArgumentParser(prog='mapography')

    argparser.add_argument(
        'p',
        choices=PARSERS.keys(),
        help='Available parsers: {}'.format(', '.join(PARSERS.keys())),
        metavar='parser')

    subargparsers = argparser.add_subparsers(
        dest='command',
        help='Available commands: {}'.format(', '.join(COMMANDS.keys())),
        metavar='command')

    for command in COMMANDS.keys():
        argparser_calls = subargparsers.add_parser(command)
        argparser_calls.add_argument(
            'subcommand',
            choices=COMMANDS[command],
            help='Command to execute. Available subcommands are: {}'
            .format(', '.join(COMMANDS[command])),
            metavar='subcommand')

    argparser.add_argument('i', help='Input file', metavar='input_file')
    argparser.add_argument('-o', help='Output file', metavar='output_file')

    return argparser


def test_argparse():
    argtests = [
        # 'mapography -h'.split(),
        'mapography -o out.txt cosmic calls paths test/samples/cosmic/cosmic.map'.split(),
        'mapography cosmic calls longest test/samples/cosmic/cosmic.map'.split()
    ]

    argparser = make_argparser()

    print(argparser.print_help())

    for arguments in argtests:
        print(arguments)
        args = argparser.parse_args(arguments[1:])
        print(args)
        execute(args)


def execute(args):
    mapparser = PARSERS[args.p]

    with open(args.i) as i:
        maptext = i.read()

    if args.command == 'calls':
        call_tree = mapparser.get_call_tree(maptext)

        if args.subcommand == 'tree':
            result = str(call_tree.draw_call_tree())
        elif args.subcommand == 'paths':
            result = '\n'.join([str(path) for path in call_tree.call_paths()])
        elif args.subcommand == 'longest':
            result = str(call_tree.longest_path())
        else:
            raise ValueError('Invalid subcommand: {}'.format(args.subcommand))

    elif args.command == 'modules':
        modules = mapparser.get_modules(maptext)

        if args.subcommand == 'list':
            result = '\n\n'.join(str(m) for m in modules)

    if args.o is not None:
        with open(args.o, 'w') as o:
            o.write(result)
    else:
        print(result)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        args = make_argparser().print_help()
        sys.exit()
    else:
        args = make_argparser().parse_args(sys.argv[1:])

    execute(args)

