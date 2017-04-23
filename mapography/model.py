# coding: utf-8

__author__ = "Franck PARAT"


class Segment(object):
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, address):
        self._start = int(address, 16)

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, address):
        self._end = int(address, 16)

    def __len__(self):
        return self.end - self.start

    def __str__(self):
        return "Segment '{}', start {:#x}, end {:#x}, length {}".format(
            self.name, self.start, self.end, len(self))

    def __repr__(self):
        return "Segment(name='{}', start={:#x}, end={:#x})".format(
            self.name, self.start, self.end)


class Module (object):
    pass


class Symbol(object):
    pass


