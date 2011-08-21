#!/usr/bin/env python

'''
'''
import markdown, re
from markdown import etree


def add_sectionstoolbar (tree, tag, tagclass, typeof, moveAttributes=True):
    def do(doc):
        children = list(doc)
        for i, child in enumerate(children):
            print(i)
            print(child)
            m = re.search(r"h(\d+)", child.tag)
            if m:
                tag_level = int(m.group(1))
                a = etree.Element('a')
                a.set("class", 'edit')
                a.set("href", '#')
                a.text = "edit"
                nav = etree.Element('nav')
                nav.append(a)
                c = child
                doc.remove(child)
                doc.insert(i, c)
                doc.insert(i, nav)
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


text = """
<section>
    <h1>test</h1>
    <p>some text</p>
    <section>
        <h2>level 2 header</h2>
        <p>some more text</p>
    </section>
</section>
"""

if __name__ == "__main__":
    #import doctest
    #doctest.testmod()
    doc = etree.fromstring(text)

    def do(doc):
        children = list(doc)
        for i, child in enumerate(children):
            print(i)
            print(child)
            m = re.search(r"h(\d+)", child.tag)
            if m:
                tag_level = int(m.group(1))
                a = etree.Element('a')
                a.set("class", 'edit')
                nav = etree.Element('nav')
                nav.append(a)
                c = child
                doc.remove(child)
                doc.insert(i, c)
                doc.insert(i, nav)
            do(child)

#TODO: to wrap all children and remove form and reinsert it after


    do(doc)
    print(etree.tostring(doc))


