#!/usr/bin/env python
import sys
import os
import urlparse
import urllib2
import cgi
import cgitb
cgitb.enable()
import itertools
import httplib

import html5lib
from html5lib import treewalkers
import lxml.etree
import genshi
from genshi.template import MarkupTemplate
from genshi.core import QName, Attrs
from genshi.core import START, END, TEXT, COMMENT, DOCTYPE
    
import tableparser
import headers
from headers import html4, html5, experimental, smartcolspan, smartrowspan, smartheaders

debug=True

class InspectorException(Exception):
    """Base class for our local exceptions"""
    def __init__(self, type):
        self.type = type

class InputError(InspectorException):
    pass

class URIError(InspectorException):
    pass

class DocumentError(InspectorException):
    pass

#From the html5lib test suite
def GenshiAdapter(treewalker, tree):
    """Generator to convert html5lib treewalker tokens into Genshi
    stream tokens"""
    text = None
    for token in treewalker(tree):
        token_type = token["type"]
        if token_type in ("Characters", "SpaceCharacters"):
            if text is None:
                text = token["data"]
            else:
                text += token["data"]
        elif text is not None:
            assert type(text) in (unicode, None)
            yield TEXT, text, (None, -1, -1)
            text = None

        if token_type in ("StartTag", "EmptyTag"):
            yield (START,
                   (QName(token["name"]),
                    Attrs([(QName(attr),value) for attr,value in token["data"]])),
                   (None, -1, -1))
            if token_type == "EmptyTag":
                token_type = "EndTag"

        if token_type == "EndTag":
            yield END, QName(token["name"]), (None, -1, -1)

        elif token_type == "Comment":
            yield COMMENT, token["data"], (None, -1, -1)

        elif token_type == "Doctype":
            yield DOCTYPE, (token["name"], None, None), (None, -1, -1)

        else:
            pass # FIXME: What to do?

    if text is not None:
        yield TEXT, text, (None, -1, -1)

def parse(document):
    """Parse a html string or file-like object into a lxml tree"""
    if hasattr(document, "info"):
        charset = document.info().getparam("charset")
    else:
        charset="utf-8"
    parser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("lxml"))
    tree = parser.parse(document, encoding=charset).getroot()
    return tree

def copySubtree(in_root, out_root):
    """Copy all the desendants of in_node to out_node"""
    out_root.text = in_root.text
    out_root.tail = in_root.tail
    for element in in_root.iterchildren():
        if isinstance(element.tag, basestring):
            new_element = lxml.etree.SubElement(out_root, element.tag, attrib=element.attrib)
            copySubtree(element, new_element)
        elif element.tag is lxml.etree.Comment:
            new_element = lxml.etree.Comment(element.text)
            new_element.tail = element.tail
            out_root.append(new_element)

class TableAnnotator(object):
    """Class for taking an lxml <table> element, and annotating a copy with
    information about the headings relating to each cell"""
    def __init__(self, heading_matcher):
        """heading_matcher - a headers.HeadingMatcher """
        self.heading_matcher = heading_matcher
        self.tw = treewalkers.getTreeWalker("etree", lxml.etree)
        self.heading_counter = itertools.count()
    
    def annotate(self, in_tree, id):
        #Store some temporary state in the class
        self.in_tree = in_tree
        self.id = id
        self.table = tableparser.TableParser().parse(in_tree)
        self.headings_map = self.heading_matcher.matchAll(self.table)
        self.heading_ids = {} #mapping of headings to id values
        
        self.out_tree = lxml.etree.Element("table")
        #Copy the input tree into the output
        copySubtree(in_tree, self.out_tree)
        
        self.element_map = self.make_input_output_map()
        
        for in_element, out_element in self.element_map.iteritems():
            cell = self.table.getCellByElement(in_element)
            if not cell:
                continue
            headings = self.headings_map[cell]
            if headings:
                self.annotate_cell(cell, headings, out_element)
        
        return (self.table, GenshiAdapter(self.tw, self.out_tree))        

    def make_input_output_map(self):
        """Create a dict mapping input tree elements to output tree elements"""
        element_map = {}
        for in_element, out_element in itertools.izip(self.in_tree.iterdescendants(),
                                                      self.out_tree.iterdescendants()):
            if in_element.tag in ("td","th"):
                cell = self.table.getCellByElement(in_element)
                if not cell:
                    continue
            element_map[in_element] = out_element
        return element_map

    def annotate_cell(self, cell, headings, out_element):
        """Annotate cell with a list of all the headings it is associated with
        and attributs to be used by script and AT to make the association"""
        #Create a container element for the annotation
        container = lxml.etree.Element("div", attrib={"class":"__tableparser_heading_container"})
        #Add a paragraph to the cell identifying the headings
        title = lxml.etree.SubElement(container, "p", attrib={"class":"__tableparser_heading_title"})
        title.text = "Headings:"
        #Now create a list of actual headings
        heading_list = lxml.etree.SubElement(container, "ul", attrib={"class":"__tableparser_heading_list"})
        for heading in headings:
            #Check if the heading is one we have encountered before.
            #If not, add a unique identifier for it to use in the highlighting script
            if heading not in self.heading_ids:
                self.annotate_heading(heading)
            #For each heading, copy the list items to the cell
            heading_data = lxml.etree.Element("li", attrib={"class":"__tableparser_heading_listitem"})
            copySubtree(heading.element, heading_data)
            heading_list.append(heading_data)

            #Add a ref to the heading to the headers attribute for use in AT
            self.add_string_list_attr("headers", out_element, self.heading_ids[heading])
        out_element.insert(0, container)
        container.tail = out_element.text
        out_element.text=""
    
    def annotate_heading(self, heading):
        """Add id abd classnames o headings so they can be referenced from cells"""
        i= self.heading_counter.next()
        id = "__tableparser_heading_id_%s_%i"%(self.id, i)
        heading_out_element = self.element_map[heading.element]
        heading_out_element.attrib['id'] = id
        self.heading_ids[heading] = id
    
    def add_string_list_attr(self, attr_name, element, value):
        """Add a class name to an element""";
        if attr_name in element.attrib:
            element.attrib[attr_name] += " " + value
        else:
            element.attrib[attr_name] = value

    def add_class(self, element, class_name):
        return self.add_string_list_attr("class", element, class_name)


class Response(object):
    status = None
    
    def __init__(self, environ):
        self.headers = {}
        self.environ = environ
        self.body = self.create_body()
    
    def create_body(self, environ):
        return ""
    
    def send(self):
        print "Status: %i %s"%(self.status, httplib.responses[self.status])
        for header, value in self.headers.iteritems():
            print "%s: %s"%(header, value)
        print "\r"
        if self.environ["REQUEST_METHOD"] != "HEAD":
            print self.body

class OK(Response):
    status = 200
    def __init__(self, environ):
        Response.__init__(self, environ)
        self.headers["Content-type"] = "text/html; charset=utf-8"

class MethodNotAllowed(Response):
    status = 405
    def __init__(self, environ):
        Response.__init__(self, environ)
        self.headers = {"Allow":"GET, POST, HEAD"}

class InternalServerError(Response):
    status = 500

class Error(OK):
    def create_body(self):
        form = self.environ["cgi_storage"]
        out_template = MarkupTemplate(open("error.xml"))
        stream = out_template.generate(uri=(form.getfirst("uri") or ""), errorType=self.environ["error_type"])
        return stream.render('html', doctype=("html", "", ""))

class TableHeadersResponse(OK):
    headers_algorithms = {"html4":(html4, ["scope", "headers"]),
                          "html5":(html5, []),
                          "experimental":(experimental, ["scope", "headers",
                                                         "b_headings",
                                                         "strong_headings"]),
                          "smartcolspan":(smartcolspan,
                                            ["no_headings_if_spans_data_col"]),
                          "smartheaders":(smartheaders, [])}
    template_filename = "table_output.html"

    def create_body(self):
        form = self.environ["cgi_storage"]
        
        input_type = form.getfirst("input_type")
        if input_type == "type_uri":
            uri = form.getfirst("uri") or ""
            if not uri:
                raise InputError("MISSING_URI")
            else:
                if urlparse.urlsplit(uri)[0] not in ("http", "https"):
                    raise URIError("INVALID_SCHEME")
                try:
                    source = urllib2.urlopen(uri)
                except urllib2.URLError:
                    raise URIError("CANT_LOAD")
        elif input_type == "type_source":
            source = form.getfirst("source")
            if not source:
                raise InputError("MISSING_SOURCE")
        else:
            raise InputError("INVALID_INPUT")
        
        self.tables = parse(source).xpath("//table")
        if not self.tables:
            raise DocumentError("NO_TABLES")
        
        algorithm = form.getfirst("algorithm")
        
        headings_module, algorithm_options = self.headers_algorithms[algorithm]
        #This defaults all missing arguments to false, which is perhaps not
        #quite right
        args = [bool(form.getfirst(value)) for value in algorithm_options]
        sys.stderr.write(repr(args) + "\n")
        self.heading_matcher = headings_module.HeadingMatcher(*args)
        
        data = self._get_data()
        out_template = MarkupTemplate(open(self.template_filename))
        stream = out_template.generate(data=data)
        return stream.render('html', doctype=("html", "", ""))

    def _get_data(self):
        annotator = TableAnnotator(self.heading_matcher)
        data = [annotator.annotate(table, str(i)) for i, table in enumerate(self.tables)]
        return data

def main():
    environ = os.environ.copy()
    environ["cgi_storage"] = cgi.FieldStorage()

    #Check for the correct types of HTTP request
    if environ["REQUEST_METHOD"] not in ("GET", "POST", "HEAD"):
        response = MethodNotAllowed(environ)
        response.send()
        sys.exit(1)
    
    try:
        response = TableHeadersResponse(environ)
    except InspectorException, e:
        if hasattr(e, "type"):
            environ["error_type"] = e.type 
        else:
            environ["error_type"] = "UNKNOWN_ERROR"
        sys.stderr.write(repr(e.__dict__))
        response = Error(environ)
    except:
        raise
    response.send()


if __name__ == "__main__":
    main()
