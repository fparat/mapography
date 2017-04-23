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
        return "{}\n{}".format(self.name, '\n'.join([str(s) for s in self.segments]))

    def __repr__(self):
        return "Module('{}', {})".format(self.name, repr(self.segments))


class Symbol(object):
    pass


