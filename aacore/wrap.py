import html5lib
import lxml.etree
from lxml.cssselect import CSSSelector
import markdown


def eltAddClass (elt, classname):
    classes = elt.get("class", "").split()
    if classname not in classes:
        classes.append(classname)
    elt.set("class", " ".join(classes))


def treeSectionalize (tree, inheritAttributes=True,
        removeInheritedAttributes=True, CSSClass="section", startLevel=1,
        stopLevel=2):
    """
    Wrap headers in divs of class section that wraps header + subsequent
    (sibling) elements until a sibling header of the same level is found.
    """

    def wrapHeader (elt, inheritAttributes=True, removeInheritedAttributes=True):
        wrapper = lxml.etree.Element("div")
        # inherit timing...
        if inheritAttributes:
            for key in elt.attrib:
                wrapper.set(key, elt.get(key))
                if removeInheritedAttributes:
                    del elt.attrib[key]
        eltAddClass(wrapper, CSSClass)
        applist = [elt]
        
        for thing in elt.itersiblings():
            if thing.tag == elt.tag:
                break
            applist.append(thing)
        elt.getparent().replace(elt, wrapper)
        for x in applist:
            wrapper.append(x)

    # it's important to go from low to high numbers
    for n in range(startLevel, stopLevel):
        hn = CSSSelector("h%d"%n)
        for elt in hn(tree):
            wrapHeader(elt, inheritAttributes, removeInheritedAttributes)    


parser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("lxml"),
        namespaceHTMLElements=False)

if __name__ == "__main__":
    #import doctest
    #doctest.testmod()

    html = """
    <h1>header 1</h1>
    <p>
    some text
    <h2>blabalba</h2>
    some more text
    <h1>header 2</h1>
    <h2>blabalba</h2>
    some more text
    """

    md = """fdifudoifdjuofdi
    fdpofdipfdoifdpoifdpofdi
    # fdpoifduofdiufdoufd
    foifduofdiufdofd
    # fpoifdpofdifd
    fdpofdpoifd
    """

    print(type(parser))

    doc = parser.parse(html)
    print(type(doc))
    treeSectionalize(doc, startLevel=1, stopLevel=4)
    print lxml.etree.tostring(doc, pretty_print=True, encoding="UTF-8")

    html = markdown.markdown(md)
    doc = parser.parse(html)
    treeSectionalize(doc, CSSClass="bla")
    print lxml.etree.tostring(doc, pretty_print=True, encoding="UTF-8")
