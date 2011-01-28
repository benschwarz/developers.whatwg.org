# coding=utf-8
import itertools

import html5lib
from html5lib import constants

def skipWhitespace(value, initialIndex):
    """Take a string value and an index into the string and return the index
    such that value[index] points to the first non-whitespace character in
    value[initialIndex:]"""
    index = initialIndex
    while value[index] in html5lib.constants.spaceCharacters:
        index += 1
    return index

def parseNonNegativeInteger(input_str):
    """HTML 5 algorithm for parsing a non-negative integer from an attribute"""
    position = 0
    value = 0
    position = skipWhitespace(input_str, position)
    if position == len(input_str):
        raise ValueError
    elif input_str[position] not in html5lib.constants.digits:
        raise ValueError
    else:
        while (position < len(input_str) and
               input_str[position] in html5lib.constants.digits):
            value *= 10
            value += int(input_str[position])
            position += 1
    return value

class TableParser(object):
    def parse(self, table):
        """Parse the table markup into a table structure, based on the HTML5
        algorithm"""
        #We index from 0 not 1; changes to enable this are marked with comments starting #ZIDX
        
        #1. Let xmax be zero.
        #2. Let ymax be zero.
        self.x_max = 0
        self.y_max = 0
        
        #3. Let the table be the table represented by the table element.
        #The xmax and ymax variables give the table's extent. The table is
        #initially empty.
        self.the_table = Table(table)
        
        #4. If the table element has no table children, then return the table
        #(which will be empty), and abort these steps.
        if not len(table):
            return self.the_table
    
        #5. Let the current element be the first element child of the table element.
        currentElement = table[0]
            
        #6. While the current element is not one of the following elements, advance
        #the current element to the next child of the table
        while currentElement.tag not in ("caption", "colgroup", "thead", "tbody",
                                         "tfoot", "tr"):
            currentElement = currentElement.getnext()
            if currentElement is None:
                return self.the_table
        
        #7. If the current element is a caption, then that is the caption element
        #associated with the table. Otherwise, it has no associated caption element.
        if currentElement.tag == "caption":
            self.the_table.caption = currentElement
            #8. If the current element is a caption, then while the current element
            #is not one of the following elements, advance the current element to
            #the next child of the table:
            while currentElement.tag not in ("colgroup", "thead", "tbody",
                                             "tfoot", "tr"):
                currentElement = currentElement.getnext()
                if currentElement is None:
                    return self.the_table
        
        #9. If the current element is a colgroup, follow these substeps:
        while currentElement.tag == "colgroup":
            #9.1 Column groups. Process the current element according to the
            # appropriate one of the following two cases:
        
            #If the current element has any col element children 
            if "col" in currentElement:
                #9.1.1.1 Let xstart have the value xmax+1.
                x_start = self.x_max + 1
                columns = currentElement.xpath("col")
                #9.1.1.2 Let the current column be the first col element child of the
                #colgroup element.
                for current_column in columns:
                    #9.1.1.3 Columns. If the current column col element has a span
                    #attribute, then parse its value using the rules for parsing
                    #non-negative integers. If the result of parsing the value is not an error or
                    #zero, then let span be that value. Otherwise, if the col element
                    #has no span attribute, or if trying to parse the attribute's value
                    #resulted in an error, then let span be 1.
                    if "span" in currentElement.attrib:
                        try:
                            span = parseNonNegativeInteger(currentElement.attrib["span"])
                        except ValueError:
                            span =  1
                    else:
                        span = 1
                    #9.1.1.4 Increase xmax by span.
                    self.x_max += span
                    #9.1.1.5 Let the last span columns in the table correspond to the
                    #current column col element.
                    for col_num in range(span):
                        self.the_table.columns.append(column)
                        #9.1.1.6 If current column is not the last col element child
                        #of the colgroup element, then let the current column be
                        #the next col element child of the colgroup element, and
                        #return to the third step of this innermost group of steps
                        #(columns).
                
                    #9.1.1.7 Let all the last columns in the table  from x=xstart
                    #to x=xmax  form a new column group, anchored at the slot
                    #(xstart, 1), with width xmax-xstart-1, corresponding to the
                    #colgroup element.
                    
                    #ZIDX coordinates are (x_start-1,0)
                    self.the_table.colgroups.append(
                        ColGroup(self.the_table,currentElement,(x_start-1,0),
                                 self.x_max-x_start-1))
                
            #If the current element has no col element children 
            else:
                #9.1.2.1 If the colgroup element has a span attribute, then
                #parse its value using the rules for parsing non-negative
                #integers. If the result of parsing the value is not an
                #error or zero, then let span be that value. Otherwise, if
                #the colgroup element has no span attribute, or if trying to
                #parse the attribute's value resulted in an error, then let
                #span be 1.
                if "span" in currentElement.attrib:
                    try:
                        span = parseNonNegativeInteger(currentElement.attrib["span"])
                    except ValueError:
                        span =  1
                else:
                    span = 1
                #9.1.2 Increase xmax by span.
                self.x_max += span
                #9.1.3 Let the last span columns in the table form a new
                #column group, anchored at the slot (xmax-span+1, 1), with
                #width span, corresponding to the colgroup element.

                #ZIDX coordinates are (self.x_max-span,0)
                self.the_table.colgroups.append(
                    ColGroup(self.the_table, currentElement,
                             (self.x_max-span, 0), span))

            #9.2 Advance the current element to the next child of the table.
            currentElement = currentElement.getnext()
            if currentElement is None:
                return self.the_table
            
            #9.3 While the current element is not one of the following
            #elements, advance the current element to the next child of the
            #table:
            while currentElement.tag not in ("colgroup", "thead", "tbody",
                                             "tfoot", "tr"):
                currentElement = currentElement.getnext()
                if currentElement is None:
                    return self.the_table
            #If the current element is a colgroup element, jump to step 1 in
            #these substeps (column groups).
    
        #10. Let ycurrent be zero. When the algorithm is aborted, if ycurrent
        #does not equal ymax, then that is a table model error.
        self.y_current = 0
        #11. Let the list of downward-growing cells be an empty list.
        self.downward_growing_cells = []
        while True:
            #12. Rows. While the current element is not one of the following
            #elements, advance the current element to the next child of the table:
            while currentElement.tag not in ("thead", "tbody", "tfoot", "tr"):
                currentElement = currentElement.getnext()
                if currentElement is None:
                    if self.y_current != self.y_max:
                        self.the_table.model_error.append("XXX")
                    return self.the_table
            if currentElement.tag == "tr":
                #13. If the current element is a tr, then run the algorithm for
                #processing rows (defined below), then return to the
                #previous step (rows).
                self.processRow(currentElement)
            else:
                #14. Otherwise, run the algorithm for ending a row group.
                self.endRowGroup()
                #15. Let ystart have the value ymax+1.
                y_start = self.y_max + 1
                #16. For each tr element that is a child of the current
                #element, in tree order, run the algorithm for processing
                #rows
                for tr_element in currentElement.xpath("tr"):
                    self.processRow(tr_element)
                #17/ If ymax ≥ ystart, then let all the last rows in the
                #table from y=ystart to y=ymax form a new row group,
                #anchored at the slot with coordinate (1, ystart), with
                #height ymax-ystart+1, corresponding to the current element.
                if self.y_max >= y_start:
                    #ZIDX coordinates are (0,y_start-1)
                    self.the_table.rowgroups.append(
                        RowGroup(self.the_table, currentElement, (0,y_start-1),
                                 self.y_max-y_start+1))
                #18. Run the algorithm for ending a row group again.
                self.endRowGroup()
                #19. Return to step 12 (rows).

                #XXX?
            currentElement = currentElement.getnext()
            if currentElement is None:
                if self.the_table.unfilledSlots():
                    self.the_table.model_errors.append("Unfilled slots in table")
                return self.the_table
    
    def endRowGroup(self):
        #1. If ycurrent is less than ymax, then this is a table model error.
        while self.y_current < self.y_max:
            self.the_table.error = True
            #2. While ycurrent is less than ymax, follow these steps:
            #2.1 Increase ycurrent by 1.
            self.y_current += 1
            #2.2 Run the algorithm for growing downward-growing cells.
            self.growDownwardCells()
        #3. Empty the list of downward-growing cells.
        self.downward_growing_cells = []
    
    def processRow(self, row_element):
        #1. Increase ycurrent by 1.
        self.y_current += 1
        #2. Run the algorithm for growing downward-growing cells.
        self.growDownwardCells()
        #3. Let xcurrent be 1.
        x_current = 1
        #4. If the tr element being processed contains no td or th elements,
        #then abort this set of steps and return to the algorithm above.
        #5. Let current cell be the first td or th element in the tr
        #element being processed.
        for current_cell in row_element.xpath("td|th"):
            #6. While xcurrent is less than or equal to xmax and the slot with
            #coordinate (xcurrent, ycurrent) already has a cell assigned to it,
            #increase xcurrent by 1.
            
            #ZIDX Coordinates are (x_current-1, y_current-1)
            while x_current < self.x_max and (x_current-1, self.y_current-1) in self.the_table and self.the_table[x_current-1, self.y_current-1]:
                x_current += 1
            #7.If xcurrent is greater than xmax, increase xmax by 1 (which will
            #make them equal).
            if x_current > self.x_max:
                self.x_max += 1
                assert x_current == self.x_max
            #8. If the current cell has a colspan attribute, then parse that
            #attribute's value, and let colspan be the result.
            #If parsing that value failed, or returned zero, or if the attribute
            #is absent, then let colspan be 1, instead.
            if 'colspan' in current_cell.attrib:
                try:
                    colspan = parseNonNegativeInteger(current_cell.attrib['colspan'])
                    if colspan == 0:
                        colspan = 1
                except ValueError:
                    colspan = 1
            else:
                colspan = 1
            #9. If the current cell has a rowspan attribute, then parse that
            #attribute's value, and let rowspan be the result.
            #If parsing that value failed or if the attribute is absent, then
            #let rowspan be 1, instead
            #10. If rowspan is zero, then let cell grows downward be true, and set
            #rowspan to 1. Otherwise, let cell grows downward be false.
            if 'rowspan' in current_cell.attrib:
                try:
                    rowspan = parseNonNegativeInteger(current_cell.attrib['rowspan'])
                    if rowspan == 0:
                        cell_grows_downwards = True
                        rowspan = 1
                    else:
                        cell_grows_downwards = False
                except ValueError:
                    rowspan = 1
            else:
                rowspan = 1
            
            #11. If xmax < xcurrent+colspan-1, then let xmax be
            #xcurrent+colspan-1.
            if self.x_max < x_current + colspan - 1:
                self.x_max = x_current + colspan - 1
            
            #12. If ymax < ycurrent+rowspan-1, then let ymax be
            #ycurrent+rowspan-1.
            if self.y_max < self.y_current + rowspan - 1:
                self.y_max = self.y_current + rowspan - 1
                
            #14. Let the slots with coordinates (x, y) such that xcurrent ≤ x <
            #xcurrent+colspan and ycurrent ≤ y < ycurrent+rowspan be covered by
            #a new cell c, anchored at (xcurrent, ycurrent), which has width
            #colspan and height rowspan, corresponding to the current cell
            #element.
            
            #ZIDX Coordinates are (x_current-1, y_current-1)
            new_cell = Cell(current_cell, (x_current-1, self.y_current-1), rowspan,
                             colspan)
            for x in range(x_current, x_current+colspan):
                for y in range(self.y_current, self.y_current+rowspan):
                    #ZIDX Slot indicies are (x-1, y-1)
                    self.the_table.appendToSlot((x-1,y-1), new_cell)    
            
            #15. Increase xcurrent by colspan.
            x_current += colspan
            
            #16. If current cell is the last td or th element in the tr element
            #being processed, then abort this set of steps and return to the
            #algorithm above.
            
            #17. Let current cell be the next td or th element in the tr element
            #being processed.

            #18. Return to step 5 (cells).
        
    def growDownwardCells(self):
        #1. If the list of downward-growing cells is empty, do nothing.
        #Abort these steps; return to the step that invoked this algorithm.
        if self.downward_growing_cells:
            #2. Otherwise, if ymax is less than ycurrent, then increase ymax
            #by 1 (this will make it equal to ycurrent).
            if self.y_max < self.y_current:
                self.y_max += 1
                assert self.y_max == self.y_current
            #3. For each {cell, cellx, width} tuple in the list of downward-growing
            #cells, extend the cell cell so that it also covers the slots with
            #coordinates (x, ycurrent), where cellx ≤ x < cellx+width-1.
            for (cell, cell_x, width) in self.downward_growing_cells:
                for x in range(cell_x, cell_x+width-1):
                    self.the_table.appendToSlot(x, self.y_current)


class Table(object):
    """Representation of a full html table"""
    def __init__(self, element):
        self.element = element #associated lxml element
        self.data = [] #List of Cells occupying each slot in the table
        self.colgroups = [] #List of colgroups in the table
        self.rowgroups = []
        self.columns = []
        self.caption = None #text of the table <caption>
        self.model_errors = [] #List of table model errors
        self.elementToCell = {} #Mapping between lxml elements and Cell objects
                                #to use in getCellByElement
        
    def __getitem__(self, slot):
        return self.data[slot[1]][slot[0]]
    
    def __contains__(self, slot):
        try:
            self.data[slot[1]][slot[0]]
            return True
        except IndexError:
            return False
    
    def __iter__(self):
        """Iterate over all the slots in a table in row order, returning a list
        of cells in each slot (overlapping cells may lead to > 1 cell per slot)"""
        x_max,y_max = self.x_max+1,self.y_max+1
        for x in range(x_max):
            for y in range(y_max):
                yield self[x,y]
    
    def iterCells(self):
        """Iterate over all cells in the table"""
        emitted_cells = set()
        for slot in self:
            for cell in slot:
                if cell not in emitted_cells:
                    emitted_cells.add(cell)
                    yield cell
    
    def iterAxis(self, starting_slot, axis="row", dir=1):
        """Iterate over all the cells (not slots) along one row or column in
        the table"""
        x,y = starting_slot
        emitted_cells = []
        if axis == "row":
            if dir == 1:
                x_end = self.x_max + 1
            else:
                x_end=-1
            indicies = [(x,y) for x,y in zip(range(starting_slot[0], x_end, dir),
                                             itertools.repeat(starting_slot[1]))]
        elif axis == "col":
            if dir == 1:
                y_end = self.y_max + 1
            else:
                y_end=-1
            indicies = [(x,y) for x,y in zip(itertools.repeat(starting_slot[0]),
                                             range(starting_slot[1], y_end, dir))]
        else:
            raise ValueError, "Unknown axis %s. Axis must be either 'row' or 'col'"%(axis,)

        for x,y in indicies:
            for cell in self[x,y]:
                if cell not in emitted_cells:
                    emitted_cells.append(cell)
                    yield cell
    
    def getXMax(self):
        try:
            return len(self.data[0])-1
        except IndexError:
            return -1
    
    def getYMax(self):
        return len(self.data)-1
    
    x_max = property(getXMax)
    y_max = property(getYMax)
    
    def unfilledSlots(self):
        rv = []
        for x in range(self.x_max):
            for y in range(self.y_max):
                if not self[x,y]:
                    rv.append((x,y))
        return rv
    
    def expandTable(self, slot):
        """Grow the storage to encompass the slot slot"""
         #Add any additional rows needed 
        if slot[1] > self.y_max:
            for i in range(slot[1]-self.y_max):
                self.data.append([[] for j in range(self.x_max+1)])
        #Add any additional columns needed
        if slot[0] > self.x_max:
            x_max = self.x_max
            for y in range(self.y_max+1):
                for x in range(slot[0]-x_max):
                    self.data[y].append([])
        assert all([len(item) == len(self.data[0]) for item in self.data])
    
    def appendToSlot(self, slot, item):
        """Add a Cell to a slot in the table"""
        if slot not in self:
            self.expandTable(slot)
        assert slot in self
        if self[slot]:
            #If there is already a cell assigned to the slot this is a
            #table model error
            self.model_errors.append("Multiple cells in slot %s"%str(slot))
        self.data[slot[1]][slot[0]].append(item)
        
        #Add the item to the element-cell mapping:
        if item.element in self.elementToCell:
            assert self.elementToCell[item.element] == item
        else:
            self.elementToCell[item.element] = item

    def getHeadings(self):
        """List of all headings in the table"""
        headings = []
        for slot in self:
            for cell in slot:
                if cell.isHeading and cell not in headings:
                    headings.append(cell)
        return headings
    headings = property(getHeadings)
    
    def row(self, index):
        """All the slots in a row"""
        return self.data[index-1]
    
    def col(self, index):
        """All the slots on a column"""
        return [row[index-1] for row in self.data[:]]
    
    def getCellByElement(self, element):
        """Return the cell object corresponding to the Element 'element'
        or None"""
        return self.elementToCell.get(element)
    
class Cell(object):
    """Cell type"""
    def __init__(self, element, anchor, rowspan, colspan):
        self.element = element
        self.anchor = anchor
        self.rowspan = rowspan
        self.colspan = colspan
    
    isHeading = property(lambda self:self.element.tag == "th", None, "Is the cell a <th> cell")

class Group(object):
    """Base class for row/column groups. These define a rectangle of cells
    anchored on a particular slot with a particular span across one axis of the
    table"""
    def __init__(self, table, element, anchor, span):
        self.table = table
        self.element = element
        self.anchor = anchor #Slot in the table to which the cell is anchored
        self.span = span #colspan or rowspan
    
    def __iter__(self):
        raise NotImplementedError
    
class RowGroup(Group):
    def __init__(self, table, element, anchor, span):
        Group.__init__(self, table, element, anchor, span)
        assert self.anchor[0] == 0
    def __iter__(self):
        """Return each unique cell in the row group"""
        emitted_elements = []
        for y in range(self.anchor[1], self.anchor[1]+self.span):
            for x in range(self.table.x_max+1):
                slot = self.table[x,y]
                for cell in slot:
                    if cell not in emitted_elements:
                        yield cell
                        emitted_elements.append(cell)
    
class ColGroup(Group):
    def __init__(self, table, element, anchor, span):
        Group.__init__(self, table, element, anchor, span)
        assert self.anchor[1] == 0
    
    def __iter__(self):
        """Return each unique cell in the column group"""
        emitted_elements = []
        for x in range(self.anchor[0], self.anchor[0]+self.span):
            for y in range(self.table.y_max+1):
                slot = self.table[x,y]
                for cell in slot:
                    if cell not in emitted_elements:
                        yield cell
                        emitted_elements.append(cell)