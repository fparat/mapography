# coding: utf-8

import re

from mapography import model


_MAP_SEGMENTS = r"""
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

_MAP_MODULES = r"""
src\main.o:
start 00000000 end 0000072d length  1837 section .debug
start 00000000 end 0000009f length   159 section .info.
start 40000000 end 40000014 length    20 section sdata (.sdata)
start 00000008 end 00000022 length    26 section const (.sconst)
start 00003ae8 end 000045d2 length  2794 section vtext (.vtext)
start 4000a80c end 4000a81c length    16 section sbss (.sbss)

src\app\process.o:
start 0000172a end 000028a1 length  4471 section .debug
start 000001f4 end 0000029a length   166 section .info.
start 4000191c end 400029e4 length  4296 section sdata (.sdata)
start 00006cc4 end 00007f22 length  4702 section vtext (.vtext)
start 00000030 end 000000e0 length   176 section const (.sconst)

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


def test_modules():
    regex_module = r"(?P<name>.*):\n(?P<segments>(?:.+\n)*)\n"
    regex_segments = r"start\s+(?P<start>[0-9a-fA-F]+)\s+" \
                     r"end\s+(?P<end>[0-9a-fA-F]+)\s+" \
                     r"length\s+(?P<length>\d+)\s+section\s+(?P<name>.+)\n?"

    modules = []

    for m in re.finditer(regex_module, _MAP_MODULES):
        new_module = model.Module(m.group("name"))

        # print(m.group("segments"))
        for seg_descr in re.finditer(regex_segments, m.group("segments")):
            # print(seg_descr.group())
            new_module.add_segment(model.Segment(
                seg_descr.group("name"),
                seg_descr.group("start"),
                seg_descr.group("end")))

        modules.append(new_module)

    for module in modules:
        print(str(module))

    print()

    for module in modules:
        print(repr(module))

    print()


def test_call_tree():
    #  a  -  b  -  c
    #     |     +  d
    #     +  e  -  f
    #     +  g

    a = model.CallTree("function_a")
    b = model.CallTree("function_b")
    c = model.CallTree("function_c")
    d = model.CallTree("function_d")
    e = model.CallTree("function_e")
    f = model.CallTree("function_f")
    g = model.CallTree("function_g")

    b.add_node(c)
    b.add_node(d)
    e.add_node(f)
    a.add_node(b)
    a.add_node(e)
    a.add_node(g)

    print(a)


def test_all():
    test_segment()
    test_modules()
    test_call_tree()


if __name__ == "__main__":
    test_call_tree()
