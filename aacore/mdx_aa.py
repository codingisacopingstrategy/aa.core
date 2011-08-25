#!/usr/bin/env python

'''
Markdown init function that gathers the various AA Extensions for Python-Markdown
======================================

Requires Python-Markdown 2.0+.

'''
import markdown
import mdx_semanticwikilinks
import mdx_semanticdata
import mdx_sectionedit
import mdx_addsections
import mdx_addsectionstoolbar
import mdx_timecodes
from .utils import wikify


def make_link (namespace, rel, target, label):
    print(namespace)
    a = markdown.etree.Element('a')
    a.set('href', '/pages/' + wikify(target))
    a.text = label or target
    if rel:
        a.set('rel', namespace + ":" + rel)
    return a


def get_aa_markdown ():
    return markdown.Markdown(extensions=[
            "extra",
            mdx_semanticwikilinks.makeExtension(configs=[('make_link', make_link)]),
            mdx_semanticdata.makeExtension(),
            mdx_timecodes.makeExtension(),
            mdx_sectionedit.makeExtension(),
            mdx_addsections.makeExtension(configs=[('class','annotation%(LEVEL)d'),]),
            mdx_addsectionstoolbar.makeExtension(),
            ],
        ) 


if __name__ == "__main__":
    import doctest
    doctest.testmod()
