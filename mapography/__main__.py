# coding: utf-8

import sys
import argparse

from mapography import parser, commands

__author__ = "Franck PARAT"


PARSERS = {
    'cosmic': parser.cosmic
}

VIEWERS = {}

COMMANDS = {
    'calls': ['tree', 'paths', 'longest'],  # function calls
    'modules': ['list', 'sizes']
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
        'mapography cosmic calls longest test/samples/cosmic/cosmic.map'.split(),
        'mapography cosmic modules list test\samples\cosmic\cosmic.map'.split(),
        'mapography  cosmic modules sizes test\samples\cosmic\cosmic.map'.split()
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

    func = getattr(commands.commands[args.command], args.subcommand)
    result = func(maptext, mapparser)

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

