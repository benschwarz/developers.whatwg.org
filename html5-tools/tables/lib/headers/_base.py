class HeadingMatcher(object):
    """Base class for headings matchers."""
    def matchAll(self, table):
        """Get a dict mapping each cell to a list of header cells with which
        it is associated

        table - a Table object for the html table to be processed"""
        raise NotImplementedError
    
    def isHeading(self, cell):
        return cell.isHeading
    
    def headersAttrHeaders(self, cell):
        """Get all headers that apply to cell via a headers attribute
        
        The value of @headers is split on whitespace to give a series of tokens
        Each token is used as an id for a getElementById rooted on the table
        If no matching header is found, the token is skipped
        Otherwise the matching heading is added to the list of headers
        """
        
        #What to do if an item is missing or is not a header?
        headers = []
        if not "headers" in cell.element.attrib:
            return None
        attr = cell.element.attrib["headers"]
        #The value of this attribute is a space-separated list of cell names
        for id in attr.split(" "):
            headerElements = self.table.element.xpath("//td[@id='%s']|//th[@id='%s']"%(id, id))
            if headerElements:
                match = headerElements[0]
            else:
                continue
            header = self.table.getCellByElement(match)
            if header is not None:
                headers.append(header)
        return headers
