import os
import glob

import simplejson
import html5lib

import tableparser
import headers

"""Test harness for headers code
The input is json format in a file testdata/headers/*.test

the file format is:
 {"tests":
          {"input":"html input string",
            "cases":[
                     ["algorithm_name", {"algorithm_option":option_value}, 
                       {"cell textContent":[list of header text content]}
                     ],
                      more cases... 
                    ]
           },
           more tests ...
 }
Each cell in input must have textContent that is unique in the table"""

matchers = dict([(item, getattr(headers, item).HeadingMatcher) for item in 
                 ("html4", "html5", "experimental", "smartcolspan", 
                  "smartheaders")])

def childText(node, addTail=False):
    """Return the textContent of an lxml node"""
    if node.text:
        rv = node.text
    else:
        rv = ""
    for child in node:
        child_text = childText(child, True)
        if child_text is not None:
            rv += child_text
    if addTail and node.tail is not None:
        rv += node.tail
    return rv

def parseTable(document):
    parser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("lxml"))
    tree = parser.parse(document)
    table = tree.xpath("//table")[0]
    tparser = tableparser.TableParser()
    return tparser.parse(table)

def compareHeaders(text_cell_map, headers_map, expected_results):
    """Actually compare the headers"""
    for cell_text, expected_headers_text in expected_results.iteritems():
        cell = text_cell_map[cell_text]
        expected_headers = set([text_cell_map[item] for item in expected_headers_text])
        received_headers = set(headers_map[cell] or [])
        try:
            assert received_headers == expected_headers
        except AssertionError:
            print "Cell:", cell_text
            print "Expected:", expected_results[cell_text]
            print "Got:", [childText(item.element) for item in received_headers]
            raise

def runtest(testdata):
    table = parseTable(testdata["input"])
    print "Input", testdata["input"]
    text_cell_map = {} #mapping between the textContent and cells
    for cell in table.iterCells():
        text_cell_map[childText(cell.element)] = cell

    for case in testdata["cases"]:
        algorithm, args, expected_results = case
        
        #Need to do unicode -> str conversion on kwargs
        kwargs = {}
        for k,v in args.iteritems():
            kwargs[str(k)] = v

        print "algorithm", algorithm
        print "args", kwargs

        matcher = matchers[algorithm](**kwargs)
        headers_map = matcher.matchAll(table)

        for result in expected_results:
            compareHeaders(text_cell_map, headers_map, expected_results)
    

def test_tableparser():
    """Load all the tests"""
    for testfile in glob.glob("testdata/headers/*.test"):
        tests = simplejson.load(open(testfile))
        for test in tests["tests"]:
            yield runtest, test
