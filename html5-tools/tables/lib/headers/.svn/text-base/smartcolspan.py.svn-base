import _base

class HeadingMatcher(_base.HeadingMatcher):
    """Get a cell -> headers mapping using the method proposed by
    Ben Millard and Simon Pieters where headers are limited in scope to the
    next header down the column with the same colspan
    
    note - this algorithm has been superceeded by that in smartheaders.py"""

    def __init__(self, no_headings_if_spans_data_col = False):
        self.no_headings_if_spans_data_col = no_headings_if_spans_data_col

    def matchAll(self, table):
        rv = {}
        headers_dict = self.associateHeaders(table)
        for slot in table:
            for cell in slot:
                rv[cell] = headers_dict.get(cell)
        return rv

    def isHeading(self, table, cell):
        """Assume only <td> cells are headings"""
        return cell.isHeading
    
    def associateHeaders(self, table):
        rv = {}
        #For each cell at the top of the table
        cells_with_no_heading_col = []
        for current_heading in table.iterAxis((0, 0), axis="row", dir=1):
            #List of cells that span a column with no headings
            if self.isHeading(table, current_heading):
                #For each col this cell covers
                for x in range(current_heading.anchor[0], current_heading.anchor[0] + current_heading.colspan):
                    column_headings = [current_heading]
                    #Have we found the first data cell
                    td_found = False
                    for current_cell in table.iterAxis(
                        (x, current_heading.rowspan),
                        axis="col", dir=1):
                        if current_cell not in rv:
                            rv[current_cell] = []
                        #Go down the column
                        if self.isHeading(table, current_cell) and not td_found:
                            rv[current_cell].extend(column_headings)
                            column_headings.append(current_cell)
                        elif self.isHeading(table, current_cell):
                            for heading in column_headings[:]:
                                if heading.colspan == current_cell.colspan: 
                                    column_headings.remove(heading)
                            rv[current_cell].extend(column_headings[:])
                            column_headings.append(current_cell)
                        else:
                            td_found = True
                            rv[current_cell].extend(column_headings[:])
            else:
                #The top cell is not a heading cell. If scan down the column
                #for all data cells before we reach a heading cell
                
                #Give this a more sensible name
                top_cell = current_heading
                
                for x in range(top_cell.anchor[0], top_cell.anchor[0]+top_cell.colspan):
                    for current_cell in table.iterAxis((x, 0), axis="col", dir=1):
                        if not self.isHeading(table, current_cell):
                            cells_with_no_heading_col.append(current_cell)
                        else:
                            break
        if self.no_headings_if_spans_data_col:
            #Unassign headings from the cells
            for cell in cells_with_no_heading_col:
                rv[cell] = []
                
        return rv
