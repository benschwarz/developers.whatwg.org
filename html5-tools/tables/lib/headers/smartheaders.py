import _base

class HeadingMatcher(_base.HeadingMatcher):
    """Smart span algorithm, based on an idea by Simon Pieters and Ben Millard

    Essentially, headings only apply as far down/across the table as
    there are no other headers with the same colspan/rowspan. This
    version also has support for the headers attribute and for the
    scope attribute"""

    def matchAll(self, table):
        """
        The basic algorithm is:
           1. For each cell in the table:
              2. If the cell has a headers attribute which lists the id of one
              or more heading cells in the table, set those as the headers for
              the cell
              3. Otherwise select the headers of the cell from the scope
              attribute of the headers
            4: Return the cell -> headers mapping (dict)
        """
        
        rv = {}
        self.table = table
        
        #Create a header -> cells mapping based on @scope or auto
        headers = {}
        for cell in table.iterCells():
            if self.isHeading(cell):
                headers[cell] = self.associateCellsWithHeader(cell)
        
        #Invert the headers -> cells mapping to a cell -> headers mapping
        headers_dict = {}
        for k, v in headers.iteritems():
            if v is None:
                continue
            for cell in v:
                if cell not in headers_dict:
                    headers_dict[cell] = [k]
                else:
                    headers_dict[cell].append(k)
        
        for cell in table.iterCells():
            headers_attr_headers = self.headersAttrHeaders(cell)
            #If the cell has a headers attribute add those headers and no others
            if headers_attr_headers:
                rv[cell] = headers_attr_headers
            elif cell in headers_dict:
                rv[cell] = headers_dict[cell]
            else:
                rv[cell] = None
        return rv

    def isHeading(self, cell):
        """Is the current cell a heading. Here we assume all <th> cells and no
        <td> cells are headings"""
        return cell.isHeading
    
    def associateCellsWithHeader(self, header):
        """Return the cells associated with a header according to its scope;
        either via the smart span algorithm for scope in (auto, row, col) or
        by selecting all cells below/right of the header in the (row|col)groups
        it spans (scope in (rowgroup, colgroup))
        """
        
        scope = None
        if "scope" in header.element.attrib:
            scope = header.element.attrib["scope"].lower()
        if scope is None or scope not in ("row", "col", "rowgroup", "colgroup"):
            scope = "auto"
        
        cells = []
        
        if scope == "auto":
            cells = self.getCellsFromAxes(header, ("row", "col"))
        elif scope == "row":
            cells = self.getCellsFromAxes(header, ("row",), skip_heading_only_axes=False)
        elif scope == "col":
            cells = self.getCellsFromAxes(header, ("col",), skip_heading_only_axes=False)
        elif scope == "rowgroup":
            groups = self.getHeaderGroups(header, "row")
            assert len(groups) == 1
            cells = self.getCellsFromGroup(header, groups[0])
        elif scope == "colgroup":
            groups = self.getHeaderGroups(header, "col")
            for group in groups:
                cells.extend([item for item in
                              self.getCellsFromGroup(header, group) if item not in cells])
        return cells
    
    def getCellsFromAxes(self, header, axes, skip_heading_only_axes=True):
        """
        Get cells associated with a header using the smart span algorithm
        
        The algorthm is this:
        1. cell_list be the list of cells with which header is associated
        2. For each axis in axes:
           3. let span be the number of rows spanned by header on axis
           4. for each row or column spanned by header on axis:
               5. If skip_heading_only_axes is set and all the cells on the
                  current row/column are headings, go to step 4 for the next row/column
               6. let data_found be false
               7. let current_cell be the cell immediatley adjacent to the header
                  on the current row/column
               8. If current_cell is a heading:
                  9. If current_cell's span across the current axis is equal to
                     span and data_cell_found is True then go to step XX
                  10. Otherwise, if current_cell's span across the current axis is
                      greater than or equal to span add current_cell to cell_list
               11. Otherwise current_cell is a data cell. Add current_cell to cell_list
                   and set data_cell_found to be true
        12. Return cell_list
        
        Notes: This does not associate a cell that overlaps with the header cell
               It is not clear that the handling of groups of headers in the middle of the table
               is sophisticated enough; however we deal with simple cases where the headers match those
               at the begginning of the axis
        """
        
        cells = []
        for axis in axes:
            if axis == "row":
                min_index = header.anchor[1]
                max_index = header.anchor[1] + header.rowspan
            else:
                min_index = header.anchor[0]
                max_index = header.anchor[0] + header.colspan
            span = axis + "span"
            for axis_index in xrange(min_index, max_index):
                heading_span = getattr(header, span)
                data_cell_found = False
                if axis == "row":
                    start_index = (header.anchor[0]+header.colspan, axis_index)
                else:
                    start_index = (axis_index, header.anchor[1]+header.rowspan)
                
                current_headings = []
                
                #If all the cells in the row/col are headings, none apply to each other
                if skip_heading_only_axes:
                    all_headings = True
                    for cell in self.table.iterAxis(start_index, axis=axis, dir=1):
                        all_headings = self.isHeading(cell)
                        if not all_headings:
                            break
                    if all_headings:
                        continue
                    
                for cell in self.table.iterAxis(start_index, axis=axis, dir=1):
                    if self.isHeading(cell):
                        current_span = getattr(cell, span)
                        if heading_span == current_span and data_cell_found:
                            break
                        elif heading_span >= current_span:
                            cells.append(cell)
                    elif not self.isHeading(cell):
                        cells.append(cell)
                        data_cell_found = True
        return cells
    
    def getCellsFromGroup(self, header, group):
        """Get all the matching cells for a heading that scopes a group
        
        Matching cells are those that lie below and to the right of the header in
        the group (assuming ltr)"""
        
        rv = []
        for cell in group:
            if (cell.anchor[0] >= header.anchor[0] and cell.anchor[1] >= header.anchor[1]
                and cell != header):
                rv.append(cell)
        return rv
    
    def getHeaderGroups(self, cell, axis):
        """Get all  (row|col)groups spanned by cell
        
        axis - row or col"""
        
        property_map = {"col":(0, "colgroups"),
            "row":(1, "rowgroups")}
        rv = []
        idx, group_type = property_map[axis]
        for group in getattr(self.table, group_type):
            if (cell.anchor[idx] >= group.anchor[idx]):
                if cell.anchor[idx] < group.anchor[idx] + group.span:    
                    rv.append(group)
            else:
                if group.anchor[idx] < cell.anchor[idx] + getattr(cell, axis + "span"):
                    rv.append(group)
        return rv
