# coding: utf-8


def tree(maptext, parser):
    return str(parser.get_call_tree(maptext).draw_call_tree())


def paths(maptext, parser):
    call_tree = parser.get_call_tree(maptext)
    return '\n'.join([str(path) for path in call_tree.call_paths()])


def longest(maptext, parser):
    return str(parser.get_call_tree(maptext).longest_path())


