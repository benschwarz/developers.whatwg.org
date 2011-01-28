#!/usr/bin/env python2.4
import sys
import os
#sys.path.insert(0, os.path.expanduser("~/lib/python/"))
#sys.path.insert(0, os.path.expanduser("~/lib/python2.4/site-packages/"))

import urllib
import httplib2
import urlparse
import cgi
#import cgitb
#cgitb.enable()

import html5lib
from html5lib.treebuilders import simpletree

from genshi.template import MarkupTemplate
from genshi.builder import tag

try:
    import psyco
    psyco.full()
except ImportError:
    pass

tagClasses = {"element":"markup element-name",
              "attr_name":"markup attribute-name",
              "attr_value":"markup attribute-value",
              "comment":"markup comment",
              "doctype":"markup doctype",
              "text":"text",
              "text_marker":"marker text_marker",
              "comment_marker":"marker comment_marker",
              "doctype_marker":"marker doctype_marker"}

class ParseTreeHighlighter(object):    
    def makeStream(self, node, indent=-2):
        if node.type not in (simpletree.Document.type,
                             simpletree.DocumentFragment.type):
            indent+=2
            rv = self.serializeNode(node, indent)
        else:
            rv = tag()
        for child in node.childNodes:
            rv.append(self.makeStream(child, indent))
        return rv

    def serializeNode(self, node, indent):
        rv = tag(" "*indent+"|")
        if node.type == simpletree.TextNode.type:
            text = node.value.split("\n")
            rv.append(tag(tag.code("#text: ", class_=tagClasses["text_marker"]),
                      tag.code(text[0], class_=tagClasses["text"])))
            for line in text[1:]:
                rv.append(tag(tag("\n" + " "*indent+"|"),
                              tag.code(line, class_=tagClasses["text"])))
        elif node.type == simpletree.Element.type:
            rv.append(tag.code(node.name, class_=tagClasses["element"]))
            if node.attributes:
                for key, value in node.attributes.iteritems():
                    rv.append(tag(" ", tag.code(key,
                                                class_=tagClasses["attr_name"]),
                              "=", tag.code("\""+value+"\"",
                                            class_=tagClasses["attr_value"])))
        elif node.type == simpletree.CommentNode.type:
            rv.append(tag(tag.code("#comment: ", class_=tagClasses["comment_marker"]),
                      tag.code(node.data, class_=tagClasses["comment"])))
        elif node.type == simpletree.DocumentType.type:
            rv.append(tag(tag.code("DOCTYPE: ", class_=tagClasses["doctype_marker"]),
                          tag.code(node.name, class_=tagClasses["doctype"])))
        rv.append(tag("\n"))
        return rv

class InnerHTMLHighlighter(object):
    def makeStream(self, node, indent=-2):
        if node.type == simpletree.Element.type:
            indent+=2
        if node.type not in (simpletree.Document.type,
                             simpletree.DocumentFragment.type):
            rv = self.serializeNode(node, indent)
        else:
            rv = tag()
        for child in node.childNodes:
            rv.append(self.makeStream(child, indent))
        if node.type == simpletree.Element.type:
            rv.append(tag.code("</" + node.name + ">",
                               class_=tagClasses["element"]))
        return rv
    
    def serializeNode(self, node, indent):
        if node.type == simpletree.TextNode.type:
            if (node.parent.name not in html5lib.constants.rcdataElements
                and node.parent.name != "plaintext"):
                value = cgi.escape(node.value, True)
            else:
                value = node.value
            if node.parent.name in ("pre", "textarea"):
                value = "\n" + value
            rv = tag.code(value, class_="text")
        elif node.type == simpletree.Element.type:
            rv = tag("")
            rv.append(tag.code("<" + node.name, class_=tagClasses["element"]))
            if node.attributes:
                for key, value in node.attributes.iteritems():
                    value = cgi.escape(value, True)
                    rv.append(tag(" ", tag.code(key,
                                                class_=tagClasses["attr_name"]),
                              "=", tag.code("\""+value+"\"",
                                            class_=tagClasses["attr_value"])))
            rv.append(tag.code(">", class_=tagClasses["element"]))    
        elif node.type == simpletree.CommentNode.type:
            rv = tag.code("<!--"+node.data+"-->", class_=tagClasses["comment"])
        elif node.type == simpletree.DocumentType.type:
            rv = tag.code("<!DOCTYPE " + node.name + ">", class_=tagClasses["doctype"])
        return rv

class Response(object):
    def __init__(self, document):
        self.parser = html5lib.HTMLParser()
        self.document = document
        
    def parse(self, source):
        return self.parser.parse(source)

    def responseString(self, document):
        raise NotImplementedError

class ParseTree(Response):
    max_source_length=1024
    def generateResponseStream(self, source, tree):
        template = MarkupTemplate(open("output.xml").read())
        treeHighlighter = ParseTreeHighlighter()
        htmlHighlighter = InnerHTMLHighlighter()

        parseTree = treeHighlighter.makeStream(tree)
        innerHTML = htmlHighlighter.makeStream(tree)
        
        #Arguably this should be defined in the document
        if (len(source) <= self.max_source_length or
            self.document.uri and len(self.document.uri) < self.max_source_length):
            viewURL = self.viewUrl()
        else:
            viewURL=""
        
        stream = template.generate(inputDocument=source,
                                   parseTree = parseTree,
                                   innerHTML = innerHTML,
                                   parseErrors=self.parser.errors,
                                   sourceString = source,
                                   viewURL=viewURL)
        return stream

    def responseString(self):
        source = self.document.source
        tree = self.parse(source)
        source = source.decode(self.parser.tokenizer.stream.charEncoding, "ignore")
        stream = self.generateResponseStream(source, tree)
        return stream.render('html', doctype=("html", "", ""))

    def viewUrl(self):
        if self.document.uri and len(self.document.source)>self.max_source_length:
            params = {"uri":self.document.uri}
        else:
            params = {"source":self.document.source}
        params["loaddom"]=1
        parameters = urllib.urlencode(params)
        urlparts = ["", "", "parsetree.py", parameters, ""]
        return urlparse.urlunsplit(urlparts)

class TreeToJS(object):
    def serialize(self, tree):
        rv = []
        rv.append("var node = document.getElementsByTagName('html')[0];")
        #Remove the <html> node
        rv.append("var currentNode = node.parentNode;")
        rv.extend(["currentNode.removeChild(node);"])
        for node in tree:
            if node.name == "html":
                rv.extend(self.buildSubtree(node))
                break
        return "\n".join(rv)
    
    def buildSubtree(self, node):
        rv = []
        rv.extend(self.serializeNode(node))
        for i, child in enumerate(node.childNodes):
            rv.extend(self.buildSubtree(child))
        #Set the current node back to the node constructed when we were called
        rv.append("currentNode = currentNode.parentNode;")    
        return rv
    
    def serializeNode(self, node):
        rv = []
        if node.type == simpletree.TextNode.type:
            rv.append("node = document.createTextNode('%s');"%self.escape(node.value))
        elif node.type == simpletree.Element.type:
            rv.append("node = document.createElement('%s');"%self.escape(node.name))
            if node.attributes:
                for key, value in node.attributes.iteritems():
                    rv.append("attr = node.setAttribute('%s', '%s')"%(key,self.escape(value)))
        elif node.type == simpletree.CommentNode.type:
            rv.append("node = document.createComment('%s')"%self.escape(node.data))
    
        rv.append("currentNode.appendChild(node)")
        #Set the current node to the node we just inserted
        rv.append("currentNode = currentNode.childNodes[currentNode.childNodes.length-1];")
        return rv
    
    def escape(self, str):
        replaces = (
            ("\\", "\\\\"),
            ("\b", "\\b"),
            ("\f", "\\f"),
            ("\n", "\\n"),
            ("\r", "\\r"),
            ("\t", "\\t"),
            ("\v", "\\v"),
            ("\"",  "\\\""),
            ("'", "\\'")
            )
        for key, value in replaces:
            str = str.replace(key, value)
        return str

class LoadSource(Response):
    attr_val_is_uri=('href', 'src', 'action', 'longdesc')

    def rewriteLinks(self, tree):
        uri = self.document.uri
        if not uri:
            return
        baseUri = urlparse.urlsplit(uri)
        for node in tree:
            if node.type == simpletree.Element.type and node.attributes:
                for key, value in node.attributes.iteritems():
                    if key in self.attr_val_is_uri:
                        node.attributes[key] = urlparse.urljoin(uri, value)

    def insertHtml5Doctype(self, tree):
        doctype = simpletree.DocumentType("html")
        tree.insertBefore(doctype, tree.childNodes[0])

    def parse(self, source):
        return self.parser.parse(source)

    def generateResponseStream(self, tree):
        template = MarkupTemplate("""<html xmlns="http://www.w3.org/1999/xhtml"
                                xmlns:py="http://genshi.edgewall.org/">
                                <head><script>${jsCode}</script></head>
                                <body></body>
                                </html>""")
        jsGenerator = TreeToJS()
        jsCode = jsGenerator.serialize(tree)
        stream = template.generate(jsCode = jsCode)
        return stream

    def responseString(self):
        tree = self.parse(self.document.source)
        self.rewriteLinks(tree)
        stream = self.generateResponseStream(tree)
        doctype=None
        for node in tree.childNodes:
            if node.type == simpletree.DocumentType.type:
                doctype = (tree.childNodes[0].name, "", "")
                break
        
        return stream.render('html', doctype=doctype)

class Error(Response):
    def generateResponseStream(self):
        template = MarkupTemplate(open("error.xml").read())
        stream = template.generate(document=self.document)
        return stream
    
    def responseString(self):
        stream = self.generateResponseStream()
        return stream.render('html', doctype=("html", "", ""))

class Document(object):
    errors = {"CANT_LOAD":1, "INVALID_URI":2, "INTERNAL_ERROR":3}
    def __init__(self, uri=None, source=None, ua=None):
        
        self.uri = uri
        self.source = source

        self.error=None
        
        if not source and uri:
            try:
                self.source = self.load(ua)
            except:
                self.error = self.errors["INTERNAL_ERROR"]
        elif not source and not uri:
            self.error = self.errors["INVALID_URI"]
        
    def load(self, ua=None):
        
        http = httplib2.Http()
        uri = self.uri
        
        #Check for invalid URIs
        if not (uri.startswith("http://") or uri.startswith("https://")):
            self.error = self.errors["INVALID_URI"]
            return
        
        headers = {}
        
        if ua:
            headers ={"User-Agent":ua}
        
        response=None
        content=None
        
        try:
            response, content = http.request(uri, headers=headers)
        except:
            self.error = self.errors["CANT_LOAD"]
        
        if content:
            return content
        else:
            self.error = self.errors["CANT_LOAD"]
            return

def cgiMain():
    print "Content-type: text/html; charset=utf-8\n\n"
    
    form = cgi.FieldStorage()
    source = form.getvalue("source")
    if not source:
        uri = form.getvalue("uri")
    else:
        uri=None
    ua = form.getvalue("ua")
    if source:
        uri=None

    loadDOM = form.getvalue("loaddom")
    
    try:
        document = Document(uri=uri, source=source, ua=ua)
    except:
        #This should catch any really unexpected error
        if "cgitb" in locals():
            raise
        else:
            print "Unexpected internal error"
            return
        
    if document.error:
        respStr = error(document)
    else:
        try:
            if loadDOM:
                resp = LoadSource(document)
            else:
                resp = ParseTree(document) 
            respStr = resp.responseString()
        except:
            if "cgitb" in locals():
                raise
            else:
                document.error = document.errors["INTERNAL_ERROR"]
                respStr = error(document)
    
    print respStr

def error(document):
    resp = Error(document)
    return resp.responseString()
    
if __name__ == "__main__":
    cgiMain()
