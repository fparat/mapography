# coding: utf-8

import re

from mapography import model


_MAP_SEGMENTS = """
start 00000000 end 00000008 length     8 segment rchw
start 00000008 end 00003ae8 length 15072 segment const
start 00003ae8 end 00021274 length 120716 segment vtext
start 00060000 end 00061000 length  4096 segment vect
start 40000000 end 4000a80c length 43020 segment sdata, initialized
start 00021288 end 0002ba94 length 43020 segment sdata, from
start 4000a80c end 4000a840 length    52 segment sbss
start 00000000 end 0002048b length 132235 segment .debug
start 00000000 end 00001ed3 length  7891 segment .info.
start 00021274 end 00021288 length    20 segment .init
"""


def test_segment():
    regex = r"start\s+(?P<start>[0-9a-fA-F]+)\s+end\s+(?P<end>[0-9a-fA-F]+)\s+" \
            r"length\s+(?P<length>\d+)\s+segment\s+(?P<name>.+)\n?"

    segments = []
    for m in re.finditer(regex, _MAP_SEGMENTS):
        new_segment = model.Segment(m.group("name"), m.group("start"), m.group("end"))
        try:
            assert len(new_segment) == int(m.group("length"))
        except:
            raise AssertionError("Length is {} instead of {}".format(
                len(new_segment), m.group("length")))
        segments.append(new_segment)

    for segment in segments:
        print(str(segment))

    print()

    for segment in segments:
        print(repr(segment))

    print()


if __name__ == "__main__":
    test_segment()
