#!/usr/bin/env python

'''
AddSections Extension for Python-Markdown
======================================

Wraps Document in <section> tags based on a hierarchy of header tags.
By default, adds a class = "sectionN" where N is the header level being wrapped.

Requires Python-Markdown 2.0+.

Basic usage:

    >>> import markdown
    >>> src = """
    ... # 1
    ... Section 1
    ... ## 1.1
    ... Subsection 1.1
    ... ## 1.2
    ... Subsection 1.2
    ... ### 1.2.1
    ... Hey 1.2.1 Special section
    ... ### 1.2.2
    ... #### 1.2.2.1
    ... # 2
    ... Section 2
    ... """.strip()
    >>> html = markdown.markdown(src, ['addsections'])
    >>> html.replace("\\n", "")
    u'<section class="section1" typeof="aa:section"><h1>1</h1><p>Section 1</p><section class="section2" typeof="aa:section"><h2>1.1</h2><p>Subsection 1.1</p></section><section class="section2" typeof="aa:section"><h2>1.2</h2><p>Subsection 1.2</p><section class="section3" typeof="aa:section"><h3>1.2.1</h3><p>Hey 1.2.1 Special section</p></section><section class="section3" typeof="aa:section"><h3>1.2.2</h3><section class="section4" typeof="aa:section"><h4>1.2.2.1</h4></section></section></section></section><section class="section1" typeof="aa:section"><h1>2</h1><p>Section 2</p></section>'

Divs instead of sections, custom class names:

    >>> src = """
    ... # Introduction
    ... # Body
    ... ## Subsection
    ... # Bibliography
    ... """.strip()
    >>> html = markdown.markdown(src, extensions=['addsections(tag=div,class=s%(LEVEL)d)'])
    >>> html.replace("\\n", "")
    u'<div class="s1" typeof="aa:section"><h1>Introduction</h1></div><div class="s1" typeof="aa:section"><h1>Body</h1><div class="s2" typeof="aa:section"><h2>Subsection</h2></div></div><div class="s1" typeof="aa:section"><h1>Bibliography</h1></div>'


Known Issue: structures like:
# ONE
### TOO Deep
## Level 2
# TWO

Produces confusing results (the ## gets placed inside the ###)

'''
import markdown, re
from markdown import etree


def add_sections (tree, tag, tagclass, typeof, moveAttributes=True):
    def do(parent, n, tag, tagclass):
        tagname = "h%d" % n
        wrapper = None
        children = list(parent)
        for i, child in enumerate(children):
            # should allow lower level to stop as well
            m = re.search(r"h(\d+)", child.tag)
            if m:
                tag_level = int(m.group(1))

            if m and tag_level == n: # child.tag == tagname:
                # FOUND HEADER: START NEW WRAP
                wrapper = etree.Element(tag)
                if moveAttributes:
                    for key, value in child.attrib.items():
                        print key
                        wrapper.set(key, value)
                        del child.attrib[key]
                if typeof:
                    wrapper.set("typeof", typeof)
                if tagclass:
                    if '%(LEVEL)d' in tagclass:
                        tagclass = tagclass % {'LEVEL': n}
                        wrapper.set("class", tagclass)
                    else:
                        wrapper.set("class", tagclass)
                parent.remove(child)
                parent.insert(i, wrapper)
                wrapper.append(child)
            elif wrapper:
                # ADD SIBLING TO CURRENT WRAP 
                parent.remove(child)
                wrapper.append(child)
            else:
                # RECURSE
                do(child, n, tag, tagclass)

    for i in range(1, 7):
        do(tree, i, tag, tagclass)


class AddSectionsTreeprocessor(markdown.treeprocessors.Treeprocessor):
    def run(self, doc):
        add_sections(doc, self.config.get("tag")[0], self.config.get("class")[0], self.config.get("typeof")[0])


class AddSectionsExtension(markdown.Extension):
    def __init__(self, configs):
        self.config = {
            'tag': ['section', 'tag name to use, default: section'],
            'class': ['section%(LEVEL)d', 'class name, may include %(LEVEL)d to reference header-level (i.e. h1, h2)'],
            'typeof': ['aa:section', 'sets typeof attribute for rdfa']
        }
        for key, value in configs:
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        ext = AddSectionsTreeprocessor(md)
        ext.config = self.config
        md.treeprocessors.add("addsections", ext, "_end")


def makeExtension(configs={}):
    return AddSectionsExtension(configs=configs)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

