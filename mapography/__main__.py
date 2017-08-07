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
    'calls': ['tree', 'paths', 'longest']  # function calls
}


def make_argparser():
    argparser = argparse.ArgumentParser(prog='mapography')
    subargparsers = argparser.add_subparsers(
        dest='command',
        help='Available commands: {}'.format(', '.join(COMMANDS.keys())),
        metavar='command')

    for command in COMMANDS.keys():
        argparser_calls = subargparsers.add_parser(command)
        argparser_calls.add_argument('subcommand', choices=COMMANDS[command],
                                     help='Command to execute. Available '
                                          'subcommands are: {}'
                                     .format(', '.join(COMMANDS[command])),
                                     metavar='subcommand')

    argparser.add_argument('-i', help='Input file', required=True,
                           metavar='input_file')
    argparser.add_argument('-o', help='Output file', metavar='output_file')
    argparser.add_argument('-p', required=True, help='Parser choice: {}'
                           .format(', '.join(PARSERS.keys())), metavar='parser')

    return argparser


def test_argparse():
    argtests = [
        # 'mapography -h'.split(),
        'mapography -p cosmic -i test/samples/cosmic/cosmic.map -o out.txt calls paths'.split(),
        'mapography -p cosmic -i test/samples/cosmic/cosmic.map calls longest'.split()
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
        call_tree = mapparser.make_call_tree(
            mapparser.parse_call_tree(
                mapparser.extract_call_tree(maptext)))

        if args.subcommand == 'tree':
            result = str(call_tree)
        elif args.subcommand == 'paths':
            result = '\n'.join([str(path) for path in call_tree.call_paths()])
        elif args.subcommand == 'longest':
            result = str(call_tree.longest_path())
        else:
            raise ValueError('Invalid subcommand: {}'.format(args.subcommand))

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

