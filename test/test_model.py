# coding: utf-8

import re

from mapography import model, parser
import mapography.parser.cosmic


with open("samples/segments.txt") as sf:
    _MAP_SEGMENTS = sf.read()

with open("samples/modules.txt") as sf:
    _MAP_MODULES = sf.read()

with open("samples/call_tree.txt") as sf:
    _MAP_CALL_TREE = sf.read()


def test_segment():
    regex = r"start\s+(?P<start>[0-9a-fA-F]+)\s+end\s+(?P<end>[0-9a-fA-F]+)\s+"\
            r"length\s+(?P<length>\d+)\s+segment\s+(?P<name>.+)\n?"

    segments = []
    for m in re.finditer(regex, _MAP_SEGMENTS):
        new_segment = model.Segment(m.group("name"), m.group("start"),
                                    m.group("end"))
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

    a = model.CallTreeNode("function_a", size=10)
    b = model.CallTreeNode("function_b", size=20)
    c = model.CallTreeNode("function_c", size=30)
    d = model.CallTreeNode("function_d", size=40)
    e = model.CallTreeNode("function_e", size=50)
    f = model.CallTreeNode("function_f", size=60)
    g = model.CallTreeNode("function_g", size=70)

    b.add_call(c)
    b.add_call(d)
    e.add_call(f)
    a.add_call(b)
    a.add_call(e)
    a.add_call(g)

    print(repr(a))
    print(str(a))
    print()


def test_cosmic_parser():
    import csv
    with open("out.txt", "w", newline='') as o:
        call_tree_text = parser.cosmic.extract_call_tree(_MAP_CALL_TREE)
        call_tree_dicts = parser.cosmic.parse_call_tree(call_tree_text)
        csvf = csv.DictWriter(o, call_tree_dicts[1].keys())
        csvf.writeheader()
        for element in call_tree_dicts:
            if element is not None:
                csvf.writerow(element)
    print("Call tree element sample:\n{}".format(call_tree_dicts[1]))
    print()

    call_tree = parser.cosmic.make_call_tree(call_tree_dicts)
    print(call_tree)

    print()


def test_all():
    test_segment()
    test_modules()
    test_call_tree()
    test_cosmic_parser()


if __name__ == "__main__":
    test_all()
