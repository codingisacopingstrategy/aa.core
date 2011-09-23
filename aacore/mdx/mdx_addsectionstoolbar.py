#!/usr/bin/env python

'''
'''

import markdown, re
from markdown import etree


def add_sectionstoolbar (tree, tag, tagclass, typeof, moveAttributes=True):
    def do(doc):
        children = list(doc)
        for i, child in enumerate(children):
            if child.tag == "section" \
                    and "section" in child.attrib.get('class')\
                    and child.attrib.get('data-section'):
                wrapper = etree.Element('div')
                wrapper.set("class", 'wrapper')
                for elt in list(child):
                    child.remove(elt)
                    wrapper.append(elt)
                if "section1" in child.attrib.get('class'):
                    a = etree.Element('a')
                    a.set("class", 'edit')
                    section = child.attrib.get('data-section')
                    a.set("href", 'edit/?section=%s' % section)
                    a.text = "edit"
                    nav = etree.Element('nav')
                    nav.append(a)
                    child.append(nav)
                child.append(wrapper)
            do(child)
    do(tree)

class AddSectionsToolbarTreeprocessor(markdown.treeprocessors.Treeprocessor):
    def run(self, doc):
        add_sectionstoolbar(doc, self.config.get("tag")[0], self.config.get("class")[0], self.config.get("typeof")[0])

class AddSectionsToolbarExtension(markdown.Extension):
    def __init__(self, configs):
        self.config = {
            'tag': ['section', 'tag name to use, default: section'],
            'class': ['section%(LEVEL)d', 'class name, may include %(LEVEL)d to reference header-level (i.e. h1, h2)'],
            'typeof': ['aa:section', 'sets typeof attribute for rdfa']
        }
        for key, value in configs:
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        ext = AddSectionsToolbarTreeprocessor(md)
        ext.config = self.config
        md.treeprocessors.add("addsectionstoolbar", ext, "_end")

def makeExtension(configs={}):
    return AddSectionsToolbarExtension(configs=configs)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

