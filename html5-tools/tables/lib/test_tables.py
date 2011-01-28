import os
import glob

import simplejson
import html5lib
import lxml.etree

import tableparser

def parseDocument(document):
    parser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("etree", lxml.etree))
    tree = parser.parse(document)
    return tree

def compareSlots(expected, actual):
    assert actual.x_max >= 0 and actual.y_max >= 0
    for x in range(0, actual.x_max):
        for y in range(0, actual.y_max):
            expected_cells = expected[y][x]
            actual_cells = actual[x,y]
            assert len(expected_cells) == len(actual_cells)
            for i in range(len(expected_cells)):
                assert expected_cells[i] == actual_cells[i].element.text

def compareGroup(expected, actual):
    assert len(expected) == len(actual)
    for grp_actual, grp_expected in zip(actual, expected):
        print "Slot: expected %s got %s"%(str(grp_expected["slot"]), str(grp_actual.anchor))
        assert tuple(grp_expected["slot"]) == grp_actual.anchor
        print "Tag: expected %s got %s"%(str(grp_expected["tag"]), str(grp_actual.element.tag))
        assert grp_expected["tag"] == grp_actual.element.tag
        if "height" in grp_expected:
            print "Height: expected %s got %s"%(str(grp_expected["height"]), str(grp_actual.span))
            assert grp_expected["height"] == grp_actual.span
        else:
            print "Width: expected %s got %s"%(str(grp_expected["width"]), str(grp_actual.span))
            assert grp_expected["width"] == grp_actual.span

def runtest(testdata):
    table = parseDocument(testdata["data"]).xpath("//table")[0]
    tparser = tableparser.TableParser()
    actual = tparser.parse(table)
    compareSlots(testdata["slots"], actual)
    
    compareGroup(testdata["rowgroups"], actual.rowgroups)
    compareGroup(testdata["colgroups"], actual.colgroups)
    
    if testdata["caption"] is not None:
        assert actual.caption.text == testdata["caption"]
    else:
        assert actual.caption == None

def test_tableparser():
    for testfile in glob.glob("testdata/*.test"):
        tests = simplejson.load(open(testfile))
        for test in tests["tests"]:
            yield runtest, test