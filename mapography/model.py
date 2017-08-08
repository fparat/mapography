# coding: utf-8

__author__ = "Franck PARAT"


def _parse_address(address, base=16):
    if not isinstance(address, int):
        address = int(address, base)
    if address < 0:
        raise ValueError("Negative address")
    return address


class Segment(object):
    def __init__(self, name, start, end):
        self.name = str(name)
        self._start = None
        self._end = None

        self.start = start
        self.end = end

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, address):
        self._start = _parse_address(address)

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, address):
        self._end = _parse_address(address)

    def __len__(self):
        return self.end - self.start

    def __str__(self):
        return "Segment '{}', start {:#x}, end {:#x}, length {}".format(
            self.name, self.start, self.end, len(self))

    def __repr__(self):
        return "Segment(name='{}', start={:#x}, end={:#x})".format(
            self.name, self.start, self.end)


class Module (object):
    def __init__(self, name, segments=None):
        self.name = str(name)

        if segments is not None:
            for segment in segments:
                if not isinstance(segment, Segment):
                    raise ValueError("Not a Segment")
            else:
                self.segments = list(segments)
        else:
            self.segments = []

    def add_segment(self, segment):
        if not isinstance(segment, Segment):
            raise ValueError("Not a Segment")
        self.segments.append(segment)

    def __len__(self):
        return sum([len(segment) for segment in self.segments])

    def __str__(self):
        return "{}\n{}".format(
            self.name, '\n'.join([str(s) for s in self.segments]))

    def __repr__(self):
        return "Module('{}', {})".format(self.name, repr(self.segments))


class Symbol(object):
    def __init__(self, name, address):
        self.name = str(name)
        self._address = _parse_address(address)

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, address):
        self._address = _parse_address(address)

        
class CallTreeNode(object):
    def __init__(self, name, calls=None, size=None):
        self.name = str(name)
        self.size = size
        if calls is not None:
            for call in calls:
                if not isinstance(call, CallTreeNode):
                    raise ValueError("Not a CallTree")
            else:
                self.calls = list(calls)
        else:
            self.calls = []

    def add_call(self, call_tree):
        if isinstance(call_tree, CallTreeNode):
            self.calls.append(call_tree)
        else:
            raise ValueError("Not a CallTree")
            
    def __str__(self):
        if self.size is None:
            selftree_init = " - {}".format(self.name)
        else:
            selftree_init = " - {} ({})".format(self.name, self.size)

        if not self.calls:
            return selftree_init

        subtree = []
        for call in self.calls:
            subtree.append(str(call))

        selftree = selftree_init + "\n".join(subtree)
        selftree = selftree.replace("\n", "\n" + (" " * len(selftree_init)))
        return selftree

    def __repr__(self):
        return "CallTree({})".format(self.name)


class CallTree(object):
    def __init__(self):
        self.functions = dict()
        self.roots = set()

    def add_function(self, name, size, calls=None, pointer=False,
                     recursive=False):
        self.functions[name] = {
            'name': name,
            'size': int(size),
            'calls': set() if calls is None else set(calls),
            'pointer': bool(pointer),
            'recursive': bool(recursive)
        }

    def connect(self, called_name, caller_name):
        if called_name not in self.functions:
            raise ValueError("Function must be declared using add_function")

        if caller_name is None:
            self.roots.add(called_name)
        elif caller_name in self.functions:
            self.functions[caller_name]['calls'].add(called_name)
        else:
            raise ValueError("Function must be declared using add_function")

    def call_paths(self):
        """
        Search all the possible function call paths
        :return: list of path infos, a path info being a tuple
        (list of (function names, function size), stack size)
        """
        call_paths = []
        
        def inspect_node(path):
            func = self.functions[path[-1][0]]
            neighbors = []
            if not func['calls']:
                call_paths.append((sum(c[1] for c in path), path))
            else:
                for call in func['calls']:
                    inspect_node(path + [(call, self.functions[call]['size'])])
        
        for root in self.roots:
            inspect_node([(root, self.functions[root]['size'])])
        call_paths.sort(key=lambda p: p[1][0])  # sort alphabetically
        call_paths.sort(key=lambda p: p[0], reverse=True)  # sort by size

        return call_paths

    def longest_path(self):
        """ Return the longest call path (see call_paths) """
        return max(self.call_paths(), key=lambda n: n[1],
                   default=([], 0))

    def draw_call_tree(self):
        """ Returns formatted string representing the call tree """
        # easy way maybe not efficient but good enough for now: use CallTreeNode
        nodes = {func['name']: CallTreeNode(func['name'], size=func['size'])
                 for func in self.functions.values()}

        for name, node in nodes.items():
            for called in self.functions[name]['calls']:
                node.add_call(nodes[called])

        return '\n'.join([str(nodes[root]) for root in sorted(self.roots)])

    def __str__(self):
        s = "{}: \n".format(self.__class__.__name__)
        for func_name, func in self.functions.items():
            s += "{} ({})\n".format(func['name'], func['size'])
            for call in func['calls']:
                s += "    " + call + '\n'
        s += "----\nroots: " + ", ".join(self.roots) + "\n"
        return s
