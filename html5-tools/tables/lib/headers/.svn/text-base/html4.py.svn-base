import _base

class HeadingMatcher(_base.HeadingMatcher):
    """Cell -> headinglist matcher based on the HTML 4 specification

    Note that this specification is rather vauge, so there is some
    disagreement about the expected behaviour"""
    def __init__(self, useScopeAttr=True, useHeadersAttr=True):
        self.useScopeAttr = useScopeAttr
        self.useHeadersAttr = useHeadersAttr
    
    def matchAll(self, table):

        rv = {}
        self.table = table
        #Build a map of headers with @scope -> cells they apply to
        if self.useScopeAttr:
            scope_map = self.getScopeMap()
        #For each cell in the table, try to attach headers using @headers,
        #@scope and the implicit algorithm, in that order
        for slot in table:
            for cell in slot:
                #If the cell has a rowspan or colspan > 1 it will be
                #in multiple slots. In this case we only want to
                #process the cell once
                if cell in rv:
                    continue
                if self.useHeadersAttr:
                    rv[cell] = self.headersAttrHeaders(cell)
                    if rv[cell] is not None:
                        continue
                if self.useScopeAttr:
                    rv[cell] = self.scopeAttrHeaders(cell, scope_map)
                    if rv[cell] is not None:
                        continue
                #Finally we try the implicit algorithm. This therefore gets applied to all 
                #cells without any headers deriving from @scope or @headers. It's not
                #clear if this is right or if this algorithm is only supposed to be 
                #applied if there is no @scope or @headers in the whole table
                rv[cell] = self.implicitHeaders(cell)
                if cell not in rv:
                    rv[cell] = None
        return rv
    
    def implicitHeaders(self, cell):
        """Get headers using the implicit headers algorithm"""
        row_headers = []
        col_headers = []
        
        #In some cases with overlapping cells we might try to examine a cell
        #more than once to see if it is a heading
        cells_examined = []
        
        def checkAxis(axis, axis_headers, start_x, start_y):
            last_cell = None
            for current_cell in self.table.iterAxis((start_x, start_y),
                                                    axis=axis, dir=-1):
                if (self.isHeading(current_cell) and
                    current_cell not in axis_headers and
                    (not self.useScopeAttr or
                     not "scope" in current_cell.element.attrib)):
                    
                    axis_headers.append(current_cell)
                    #If a header cell has the headers attribute set,
                    #then the headers referenced by this attribute are
                    #inserted into the list and the search stops for the
                    #current direction.
                    if (self.useHeadersAttr and
                        "headers" in current_cell.element.attrib):
                        axis_headers += self.headersAttrHeaders(current_cell)
                        break
                else:
                    #The search in a given direction stops when the edge of the
                    #table is reached or when a data cell is found after a
                    #header cell.
                    if last_cell in axis_headers:
                        break
                last_cell = current_cell
        
        #Need to search over all rows and cols the cell covers
        
        #Start by searching up each column 
        for x_cell in range(cell.anchor[0], cell.anchor[0] + cell.colspan):
            checkAxis("col", col_headers, x_cell, cell.anchor[1]-1)
            
        for y_cell in range(cell.anchor[1], cell.anchor[1] + cell.rowspan):
            checkAxis("row", row_headers, cell.anchor[0]-1, y_cell)
        
        #Column headers are inserted after row headers, in the order
        #they appear in the table, from top to bottom.
        headers = row_headers[::-1] + col_headers[::-1]
        
        return headers
    
    def scopeAttrHeaders(self, cell, scopeMap=None):
        if scopeMap is None:
            scopeMap = self.getScopeMap(self.table)
        headers = []
        for header, cells in scopeMap.iteritems():
            if cell in cells:
                headers.append(header)
        if not headers:
            headers = None
        return headers
    
    def isHeading(self, cell):
        """Return a boolean indicating whether the element is a heading
        
        HTML 4 defines cells with the axis or scope attribute set to be headings"""
        return (cell.isHeading or "axis" in cell.element.attrib
                or "scope" in cell.element.attrib)
        
    
    def getScopeMap(self):
        """Return a dict matching a heading to a list of cells to which it is
        assosiated from the scope attribute"""
        rv = {}
        for heading_cell in self.table.headings:
            heading_element = heading_cell.element
            if not "scope" in heading_element.attrib:
                continue
            scope = heading_element.attrib["scope"]
            x,y = heading_cell.anchor
            if scope == "row":
                for s in range(heading_cell.rowspan):
                    rv[heading_cell] = [item for item in
                                        self.table.iterAxis((x+heading_cell.colspan, y+s), axis="row")]
            elif scope == "col":
                for s in range(heading_cell.colspan):
                    rv[heading_cell] = [item for item in
                                        self.table.iterAxis((x+s, y+heading_cell.rowspan), axis="col")]
            elif scope == "rowgroup":
                cells = []
                for rowgroup in self.table.rowgroups:
                    if y >= rowgroup.anchor[1] and y <= rowgroup.anchor[1] + rowgroup.span:
                        #This applies the heading to all other cells in the group
                        #below and to the right of the current heading
                        #This is hard to justify from the spec because it's
                        #not especially clear on this point
                        cells += [item for item in rowgroup if item != heading_cell and
                                  item.anchor[0] >= heading_cell.anchor[0] and
                                  item.anchor[1] >= heading_cell.anchor[1]]
                rv[heading_cell] = cells
            elif scope == "colgroup":
                cells = []
                for colgroup in self.table.colgroups:
                    if x >= colgroup.anchor[0] and x <= colgroup.anchor[0] + colgroup.span:
                        cells += [item for item in colgroup if item != heading_cell and
                                  item.anchor[0] >= heading_cell.anchor[0] and
                                  item.anchor[1] >= heading_cell.anchor[1]]
                rv[heading_cell] = cells
        return rv
