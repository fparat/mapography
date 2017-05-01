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
        self.functions[name] = dict(
            name=name,
            size=int(size),
            calls=set() if calls is None else set(calls),
            pointer=bool(pointer),
            recursive=bool(recursive))

    def connect(self, called_name, caller_name):
        if called_name not in self.functions:
            raise ValueError("Function must be declared using add_function")

        if caller_name is None:
            self.roots.add(called_name)
        elif caller_name in self.functions:
            self.functions[caller_name]['calls'].add(called_name)
        else:
            raise ValueError("Function must be declared using add_function")

    def longest_path(self):
        def inspect_node(name):
            func = self.functions[name]
            neighbors = []
            for n in func['calls']:
                print(n)
                neighbors.append(inspect_node(n))
            best_neighbor = max(neighbors, key=lambda n: n[1],
                                default=([name], func['size']))
            return best_neighbor[0].insert(0, name), \
                   best_neighbor[1] + func['size']

        calls = [inspect_node(root) for root in self.roots]
        longest_path = max(calls, key=lambda n: n[1],
                           default=(['No root function found'], 0))
        return longest_path



    def __str__(self):
        s = "{}: {}, {}".format(
            self.__class__.__name__,
            self.functions,
            [r['name'] for r in self.roots])
        return s
