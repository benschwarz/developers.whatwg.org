import domtreewalker
from domtreewalker import NodeFilter
import lxml.etree
import html5lib

heading_tags = ("h1", "h2", "h3", "h4", "h5", "h6")

def outline_filter(n):
    #Skip any descendants of headings.
    if (n.getparent() is not None and
        (n.getparent().tag == 'h1' or n.getparent().tag == 'h2' or
         n.getparent().tag == 'h3' or n.getparent().tag == 'h4' or
         n.getparent().tag == 'h5' or n.getparent().tag == 'h6' or
         n.getparent().tag == 'header')):
        return NodeFilter.FILTER_REJECT

    #Skip any blockquotes.
    elif (n.tag == 'blockquote'):
        return NodeFilter.FILTER_REJECT
  
    #Accept HTML elements in the list given in the prose
    elif (n.tag == 'body' or
          n.tag == 'section' or n.tag == 'nav' or
          n.tag == 'article' or n.tag == 'aside' or
          n.tag == 'h1' or n.tag == 'h2' or
          n.tag == 'h3' or n.tag == 'h4' or
          n.tag == 'h5' or n.tag == 'h6' or
          n.tag == 'header'):
        return NodeFilter.FILTER_ACCEPT
    else:
        # Skip the rest.
        return NodeFilter.FILTER_SKIP

def copyTree(treewalker):
    """Copy the tree in a dom treewalker into a new lxml.etree tree"""
    node_map = {} #Mapping between nodes in the output tree and those
                  #in the input tree
    
    def copySubtree(in_root, out_root):
        treewalker.currentNode = in_root
        out_root.text = in_root.text
        out_root.tail = in_root.tail
        node = treewalker.firstChild()
        while node is not None:
            if isinstance(node.tag, basestring):
                new_node = lxml.etree.SubElement(out_root, node.tag,
                                                attrib=node.attrib)
                copySubtree(node, new_node)
            elif node.tag is lxml.etree.Comment:
                new_node = lxml.etree.Comment(node.text)
                new_element.tail = node.tail
                out_root.append(new_element)
            node_map[new_node] = node
            
            treewalker.currentNode = node
            node = treewalker.nextSibling()
    
    new_root = lxml.etree.Element(treewalker.currentNode.tag)
    for k, v in treewalker.currentNode.attrib.iteritems():
        new_root.attrib[k] = v
    node_map[new_root] = treewalker.currentNode
    copySubtree(treewalker.currentNode, new_root)
    
    return new_root, node_map

def mutateTreeToOutline(outline_tree):
    for node in outline_tree.iterdescendants():
        parent = node.getparent()
        this_idx = parent.index(node)
        if (node.tag in list(heading_tags) + ["header"] and
            this_idx != 0):
            new_sectioning_element = lxml.etree.Element("section")
            if (node.tag == "header" or
                (node.tag in heading_tags and parent[0].tag in heading_tags and
                 node.tag[-1] <= parent[0].tag[-1]) or
                parent[0].tag not in list(heading_tags) + ["header"]):
                #Insert the new sectioning element as the immediately following
                #sibling of the parent sectioning element
                grandparent = parent.getparent()
                grandparent.insert(grandparent.index(parent) + 1, new_sectioning_element)
                #move all the elements from the current heading element up to
                #the end of the parent sectioning element into the new
                #sectioning element
                while len(parent) > this_idx:
                    child = parent[this_idx]
                    parent.remove(child)
                    new_sectioning_element.append(child)
            else:
                this_idx = parent.index(node)
                parent.remove(node)
                new_sectioning_element.append(node)
                while (len(parent) > this_idx and
                       parent[this_idx].tag in heading_tags and
                       parent[this_idx].tag[-1] > node.tag[-1]):
                    child = parent[this_idx]
                    parent.remove(child)
                    new_sectioning_element.append(child)
                parent.insert(this_idx, new_sectioning_element)
    return outline_tree

def printOutline(outline_tree):
    rv = []
    def print_node(node, indent):
        for child in node:
            if child.tag in list(heading_tags) + ["header"]:
                rv.append("-"*(indent-2) + child.text)
            else:
                print_node(child, indent+2)
            
    print_node(outline_tree, 0)
    return "\n".join(rv)
    
def getOutlineTree(html_file):
    p = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("etree",
                                                                      lxml.etree, fullTree=False))
    t = p.parse(html_file)
    dtw = domtreewalker.DOMTreeWalker(t, outline_filter)
    #tb = html5lib.treebuilders.getTreeBuilder("etree", lxml.etree)()
    outline_tree, node_map = copyTree(dtw)
    outline_tree = mutateTreeToOutline(outline_tree)
    return outline_tree