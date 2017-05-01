# coding: utf-8

import re


class ParserError(Exception):
    pass


# class Function(object):
#     def __init__(self, name, descrption_line):
#         self.name = name
#         self.description_line = int(descrption_line)
#
#
# class CallTreeLine(object):
#     def __init__(self, index, func_name, func_level):
#         self.index = index
#         self.func_level = func_level
#
#
# class CallTreeLeaf(CallTreeLine):
#     def __init__(self, index, func_name, func_level,size):
#         super(CallTreeLine).__init__(self, index, func_name, func_level)
#         self.size


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
    pass
