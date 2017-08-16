# coding: utf-8

import re

from mapography.model import CallTree, Segment, Module


class ParserError(Exception):
    pass


def extract_segments(maptext):
    """
    Extract the segments extract from map file content
    :param maptext: map file content string
    :return: segments extract string
    """
    segments_header = """                               --------
                               Segments
                               --------
"""

    start = maptext.find(segments_header)
    if start < 0:
        raise ParserError("Cannot find segments")

    end = maptext.find("\n\n\n", start)
    if end < 0:
        raise ParserError("Cannot find segments")

    return maptext[start + len(segments_header):end + 1]


def parse_segments(segments_string, strict=True):
    """
    Parse the segments and returns a list of dictionaries of the elements
    :param segments_string: segments as printed in the map file
    :param strict: if True the function raises a ParseError exception when
    incoherent data is found
    :return: list of dictionaries for each element with the following keys:
        - name: of the segment
        - start: address of the segment as integer
        - end: address of the segment as integer
        - length: of the segment
    """
    # dict(name, start, end, length)

    segments_dicts = []

    for line in segments_string.split('\n'):
        if line.strip():
            items = line.split()
            items_d = {items[2*n]: items[2*n+1] for n in range(len(items)//2)}

            seg = {
                'name': items_d['segment'],
                'start': int(items_d['start'], 16),
                'end': int(items_d['end'], 16),
                'length': int(items_d['length']),
            }

            if strict and seg['length'] != seg['end'] - seg['start']:
                raise ParserError("Segment '{}': length given doesn't match "
                                  "with start and end".format(seg['name']))

            segments_dicts.append(seg)

    return segments_dicts


def make_segments(segments_dict):
    return [Segment(seg_dict['name'], seg_dict['start'], seg_dict['end'])
            for seg_dict in segments_dict]


def get_segments(maptext):
    """
    Map file content string -> list of Segment objects
    Shortcut for make_segments(parse_segments(extract_segments(maptext)))
    :param maptext:  map file content string
    :return: list of Segment objects
    """
    return make_segments(parse_segments(extract_segments(maptext)))


def extract_modules(maptext):
    """
    Extract the modules from map file content
    :param maptext: map file content string
    :return: modules extract string
    """
    header = """-------
                               Modules
                               -------
"""
    start = maptext.find(header)
    if start < 0:
        raise ParserError("Cannot find modules")

    end = maptext.find("\n\n\n", start)
    if end < 0:
        raise ParserError("Cannot find modules")

    return maptext[start+len(header):end+1]


def parse_modules(modules_string):
    blocs = [[line.strip() for line in bloc.splitlines() if line.strip()]
             for bloc in modules_string.split('\n\n')]

    modules = []
    for bloc in blocs:
        module = {'name': bloc[0][:bloc[0].rfind(':')], 'sections': []}
        for line in bloc[1:]:
            items = line.split()
            items_d = {items[2*n]: items[2*n+1] for n in range(len(items)//2)}
            module['sections'].append(items_d)
        modules.append(module)

    return modules


def make_modules(modules_dicts):
    modules = []
    for module_dict in modules_dicts:
        segments = [Segment(s['section'], s['start'], s['end'])
                    for s in module_dict['sections']]
        modules.append(Module(module_dict['name'], segments))

    return modules


def get_modules(maptext):
    return make_modules(parse_modules(extract_modules(maptext)))


def extract_call_tree(maptext):
    """
    Extract the call tree from map file content
    :param maptext: map file content string
    :return: call tree string
    """
    call_tree_header = """                              ---------
                              Call tree
                              ---------
"""

    start = maptext.find(call_tree_header)
    if start < 0:
        raise ParserError("Cannot find call tree")

    end = maptext.find("\n\n\n\n", start)
    if end < 0:
        raise ParserError("Cannot find call tree")

    return maptext[start+len(call_tree_header):end+1]


CALL_TREE_REGEX = re.compile(r"""
(?P<index>\d+)
(?P<level>(?:[ >+|])+)
\(?(?P<func_name>[^: )]+)\)?
(?:
    (?:[:\s]*\((?P<size>\d+)\))
    |
    (?:\s+[->]+\s+(?P<ref>\d+))
    |
    .*(?P<ellipsis>[.]{3})
)
""", flags=re.VERBOSE)


def parse_call_tree(call_tree_string):
    """
    Parse the call tree and returns a list of dictionaries of the elements
    :param call_tree_string: call tree as printed in the map file
    :return: list of dictionaries for each element with the following keys:
        - index: index of the element as printed
        - func_name: name of the function
        - level: level of indentation denoting the call hierarchy, root is 0
        - size and ref: only one is defined, the other is None. When defined,
        size is the stack size of the function, ref is the index at which the
        size is given
    """
    # dict(index, func_name, level, size, ref, ellipsis)

    call_tree_dicts = []

    # For each match, get and normalize its dict, and store in list
    for match in re.finditer(CALL_TREE_REGEX, call_tree_string):
        element = match.groupdict()

        # Normalize values to int

        for key in ('index', 'size', 'ref'):
            try:
                element[key] = int(element[key])
            except (ValueError, TypeError):
                pass

        level = element['level']
        element['level'] = level.count('|') + level.count('+')

        element['ellipsis'] = bool(element['ellipsis'])

        call_tree_dicts.append(element)

    # Check the matching of 'index' attribute with the position in the list
    # For now it just raise an exception at the first non-matching case,
    # consider adding an attempt to fix it if necessary
    # The first index is 1 so we start to push a None in position 0
    call_tree_dicts.insert(0, None)
    for position, element in enumerate(call_tree_dicts):
        if element is not None and element['index'] != position:
            raise ParserError("Index {} doesn't match position {}".format(
                element['index'], position))

    return call_tree_dicts


def make_call_tree(elements):
    call_tree = CallTree()

    for element in elements:
        if element is not None and element['size'] is not None:
            call_tree.add_function(element['func_name'], element['size'])

    call_stack = []
    for element in elements:
        if element is not None:
            call_stack_delta = 1 + element['level'] - len(call_stack)
            if element['level'] == 0:
                call_stack = [element]
                call_tree.connect(element['func_name'], None)
            else:
                call_tree.connect(element['func_name'],
                                  call_stack[call_stack_delta-2]['func_name'])
                for pop_num in range(1 - call_stack_delta):
                    call_stack.pop()
                call_stack.append(element)
    return call_tree


def get_call_tree(maptext):
    """
    Map file content string -> CallTree object
    Shortcut for make_call_tree(parse_call_tree(extract_call_tree(maptext)))
    :param maptext:  map file content string
    :return: CallTree object
    """
    return make_call_tree(parse_call_tree(extract_call_tree(maptext)))


def extract_symbols(maptext):
    """
    Extract the symbols section from map file content
    :param maptext: map file content string
    :return: symbol section of the map file as string
    """
    symbols_header = """                               -------
                               Symbols
                               -------
"""

    start = maptext.find(symbols_header)
    if start < 0:
        raise ParserError("Cannot find 'Symbols' section")

    return maptext[start + len(symbols_header):]



SYMBOL_REGEX = re.compile(r"""    (?P<name>\w+)
    \s+
    (?P<address>[0-9a-fA-F]+)
    \s+
    defined\ in\ 
    (?P<module_defined>.+?)
    \s*
    (?:section\ 
        (?P<section>.+?)(?:\ \((?P<section2>.+?)\).*?(?P<init>initialized)?)?
    )?
    \n\s*
    (?:
        (?:used\ in\ (?P<module_used>.+(?:\n\s+.+)*\n)+?)
        |
        (?:(?P<not_used>\*\*\*\ not\ used\ \*\*\*)\n)
    )?""", flags=re.VERBOSE)


def parse_symbols(symbols_string):
    """
    Parse the symbols section and returns a list of dictionaries of the elements
    :param symbols_string: symbols as printed in the map file
    :return:
    """

    symbols_dicts = []

    # For each match, get and normalize its dict, and store in list
    for match in re.finditer(SYMBOL_REGEX, symbols_string):
        element = match.groupdict()
        # TODO: finish
        print(element)
        symbols_dicts.append(element)

    return symbols_dicts


