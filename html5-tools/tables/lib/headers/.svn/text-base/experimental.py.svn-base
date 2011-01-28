import html4

class HeadingMatcher(html4.HeadingMatcher):
    def __init__(self, useScopeAttr=True, useHeadersAttr=True,
                 useTdBHeadings=False, useTdStrongHeadings=False,):
        self.useScopeAttr = useScopeAttr
        self.useHeadersAttr = useHeadersAttr
        self.useTdBHeadings = useTdBHeadings
        self.useTdStrongHeadings = useTdStrongHeadings
    
    def implicitHeaders(self, cell):
        row_headers = []
        col_headers = []
        
        #In some cases with overlapping cells we might try to examine a cell
        #more than once to see if it is a heading
        cells_examined = []
        
        def checkAxis(axis, axis_headers, start_x, start_y):
            axis_all_headings = True
            
            #Check if the cell is in a row/column that is all headings; if it
            #is do not add other headers from along that axis
            if axis=="row":
                origin = (0, cell.anchor[1])
            else:
                assert axis == "col"
                origin = (cell.anchor[0],1)
            
            for current_cell in self.table.iterAxis(origin,
                                               axis=axis, dir=1):
                if not self.isHeading(current_cell):
                    axis_all_headings = False
                    break
            
            if not axis_all_headings:
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
                        #The search in a given direction stops when the edge of the
                        #table is reached or when a data cell is found after a
                        #header cell.
                        if last_cell in axis_headers:
                            break
                    last_cell == current_cell
        
        #Need to search over all rows and cols the cell covers
        
        #Start by searching up each column
        for x_cell in range(cell.anchor[0], cell.anchor[0] + cell.colspan):
            checkAxis("col", col_headers, x_cell, cell.anchor[1]-1)
        
        #Then search along the row
        for y_cell in range(cell.anchor[1], cell.anchor[1] + cell.rowspan):
            checkAxis("row", row_headers, cell.anchor[0]-1, y_cell)
        
        #Column headers are inserted after row headers, in the order
        #they appear in the table, from top to bottom.
        headers = row_headers[::-1] + col_headers[::-1]
        
        return headers
    
    def isHeading(self, cell):
        """HTML 4 defines cells with the axis attribute set to be headings"""
        heading = cell.isHeading
        if ((not cell.element.text or not cell.element.text.strip())
            and len(cell.element)):
            import sys
            if self.useTdBHeadings and cell.element[0].tag == "b":
                heading = True
            if self.useTdStrongHeadings and cell.element[0].tag == "strong":
                heading = True
        return heading
