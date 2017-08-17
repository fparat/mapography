# coding: utf-8

import sys
import argparse
from pprint import pprint, pformat

from mapography import parser

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
            
        elif args.subcommand == 'sizes':
            # Find section names
            secnames = set(seg.name for m in modules for seg in m.segments)
            
            # Find and regroup the modules by section type, sorted
            sizes = []
            for secname in secnames:
                section = {'name': secname, 'modules': []}
                for m in modules:
                    for seg in m.segments:
                        if seg.name == secname:
                            section['modules'].append((m.name, len(seg)))
                            break
                section['modules'].sort(key=lambda m: m[1], reverse=True)
                sizes.append(section)
            # the complicated lambda is for putting names starting with '.' at the end
            sizes.sort(key=lambda s: ['1','0'][s['name'][0].isalpha()] + s['name'])
            
            
            # Formatting
            results = []
            for section in sizes:
                module_list = '\n'.join(['{} ({})'.format(*m) 
                                         for m in section['modules']])
                bloc = '{}:\n{}'.format(section['name'], module_list)
                results.append(bloc)
            result = '\n\n'.join(results)
            # result = pformat(sizes, width=120)

    else:
        raise ValueError('Invalid command: ' + args.command)

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

