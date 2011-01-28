import _base
from collections import defaultdict

class HeadingMatcher(_base.HeadingMatcher):
    """Cell -> Headings list mapping using the September 2007 HTML 5
    algorithm"""
    def matchAll(self, table):
        rv = defaultdict(lambda:None)
        self.table = table
        scope_map = self.scopeAttributeHeaders()
        #Invert the headers->cells map
        for header, cells in scope_map.iteritems():
            for cell in cells:
                if cell not in rv:
                    rv[cell] = [header]
                else:
                    rv[cell].append(header)
        return rv
    
    def scopeAttributeHeaders(self):
        """Return a dict matching a heading to a list of cells to which it is
        assosiated"""
        rv = {}
        for heading_cell in self.table.headings:
            heading_element = heading_cell.element
            if "scope" in heading_element.attrib:
                scope = heading_element.attrib["scope"]
            else:
                scope = None
            x,y = heading_cell.anchor
            if scope == "row":
                #The cell != heading cell thing is not in the spec
                rv[heading_cell] = [item for item in 
                                    self.table.iterAxis((x+1, y), "row") 
                                    if not item.isHeading]
            elif scope == "col":
                rv[heading_cell] = [item for item in 
                                    self.table.iterAxis((x, y+1), axis="col") 
                                    if not item.isHeading]
            elif scope == "rowgroup":
                cells = []
                for rowgroup in self.table.rowgroups:
                    if (heading_cell.anchor[1] >= rowgroup.anchor[1] and
                        heading_cell.anchor[1] < rowgroup.anchor[1] + rowgroup.span):
                        cells += [item for item in rowgroup
                                  if item.anchor[0] >= heading_cell.anchor[0] and
                                  item.anchor[1] >= heading_cell.anchor[1] and
                                  not item.isHeading]
                rv[heading_cell] = cells
            elif scope == "colgroup":
                cells = []
                for colgroup in self.table.colgroups:
                    if (heading_cell.anchor[0] >= colgroup.anchor[0] and
                        heading_cell.anchor[0] < colgroup.anchor[0] + colgroup.span):
                        cells += [item for item in colgroup 
                                  if item.anchor[0] >= heading_cell.anchor[0] and
                                  item.anchor[1] >= heading_cell.anchor[1] and
                                  not item.isHeading]
                rv[heading_cell] = cells
            else:
                if x>0 and y>0:
                    #Do not assign the heading to any cells
                    continue
                elif y == 0:
                    rv[heading_cell] = [item for item in 
                                        self.table.iterAxis((x, y+1), axis="col") 
                                        if not item.isHeading]
                elif x == 0:
                    rv[heading_cell] = [item for item in 
                                        self.table.iterAxis((x+1, y), "row") if 
                                        not item.isHeading]
        return rv
