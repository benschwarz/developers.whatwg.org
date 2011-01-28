#!/usr/bin/env python
import sys
sys.path.insert(0, "/home/james/html5/html5lib/trunk/python/src")

import cgi
import urllib2
import cgitb
cgitb.enable()

import headers

data = cgi.FieldStorage()
uri = data.getfirst("uri")

if uri is not None:
    print "content-type:text/plain;charset=utf-8\n"
    tree = headers.getTree(urllib2.urlopen(uri))
    print headers.printOutline(tree).encode("utf-8")
else:
    print "content-type:text/html;charset=utf-8\n"
    print """
    <!doctype html>
    <title>HTML Headings Analyser</title>
    <h1>HTML Heading Analyser</h1>
    <form>
    <label>
    URI:
    <input type="url" name="uri">
    </label>
    <input type="submit" value="See Outline">
    </form>"""