#! /usr/bin/env python2

'''
Active Archives Markdown init function 
======================================
It gathers the various AA Extensions for Python-Markdown

Requires Python-Markdown 2.0+.
'''

import markdown
import mdx_semanticwikilinks
import mdx_semanticdata
import mdx_sectionedit_lite
import mdx_addsections
import mdx_addsectionstoolbar
import mdx_timecodes
import mdx_django_template
from .utils import wikify


def make_link (rel, target, label):
    """
    Custom implementation of the SemanticWikilinks make_link function.
    Returns ElementTree Element. 
    """
    a = markdown.etree.Element('a')
    a.set('href', '/pages/' + wikify(target))
    a.text = label or target
    if rel:
        a.set('rel', rel)
    return a


def get_aa_markdown (context=None):
    """
    This is a function to return a Active Archive markdown instance.
    Returns a Markdown instance.
    """
    if context:
        djtmpl_cfg = [('context', context)]
    else:
        djtmpl_cfg = []
    return markdown.Markdown(extensions=[
            "extra",
            mdx_semanticwikilinks.makeExtension(configs=[('make_link', make_link)]),
            mdx_semanticdata.makeExtension(),
            mdx_timecodes.makeExtension(),
            mdx_sectionedit_lite.makeExtension(),
            mdx_addsections.makeExtension(configs=[('class','annotation%(LEVEL)d'),]),
            mdx_addsectionstoolbar.makeExtension(),
            mdx_django_template.makeExtension(configs=djtmpl_cfg),
            ],
        ) 


def get_aa_markdown_ajax (context=None):
    """
    This is a function to return a Active Archive markdown instance.
    Returns a Markdown instance.
    """
    if context:
        djtmpl_cfg = [('context', context)]
    else:
        djtmpl_cfg = []
    return markdown.Markdown(extensions=[
            "extra",
            mdx_semanticwikilinks.makeExtension(configs=[('make_link', make_link)]),
            mdx_semanticdata.makeExtension(),
            mdx_timecodes.makeExtension(),
            mdx_sectionedit_lite.makeExtension(),
            #mdx_addsections.makeExtension(configs=[('class','annotation%(LEVEL)d'),]),
            #mdx_addsectionstoolbar.makeExtension(),
            mdx_django_template.makeExtension(configs=djtmpl_cfg),
            ],
        ) 


if __name__ == "__main__":
    import doctest
    doctest.testmod()
