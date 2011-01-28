#XXX
#import sys
#import os
#sys.path.insert(0, os.path.abspath("../html5lib/python/src/"))

import support
import headers
import cStringIO
import glob

def compareExpected(test):
    tree = headers.getOutlineTree(test["data"])
    received = headers.printOutline(tree)
    print "Data\n%s\nReceived\n%s\nExpected:\n%s"%(test["data"], received, test["outline"])
    assert received == test["outline"]

def testAll():
    for fn in glob.glob("tests/*.dat"):
        for test in support.TestData(fn):
            compareExpected(test)