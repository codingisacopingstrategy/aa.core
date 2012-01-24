#! /usr/bin/env python2


"""
Active Archives Markdown init function
======================================

It gathers the various AA Extensions for Python-Markdown

Requires Python-Markdown 2.0+.
"""


import markdown
try: from markdown.util import etree
except ImportError: from markdown import etree
import mdx_semanticwikilinks
import mdx_semanticdata
import mdx_sectionedit
import mdx_addsections
import mdx_timecodes
import mdx_del_ins
import mdx_cite
#import mdx_cut

from aacore.utils import url_for_pagename
import urlparse


def make_link(rel, target, label, default_link_rel=None, filter_=None):
    """
    Custom implementation of the SemanticWikilinks make_link function.
    Returns ElementTree Element.
    """
    a = etree.Element('a')
    #import pdb; pdb.set_trace();
    parts = urlparse.urlparse(target)
    # FIXME: This was added to give anchor support within a wiki page.
    #        Many link styles are not taken into account yet.
    if parts.fragment and not (parts.scheme or parts.netloc):
        href = "#%s" % parts.fragment
    elif parts.scheme:
        href = target
        a.set('target', '_blank')
    else:
        href = url_for_pagename(target)
    a.set('href', href)
    if filter_:
        a.set('data-filter', filter_)
    if rel == "aa:embed":
        img = etree.Element('img')
        img.set('src', '/static/aacore/img/ajax-loader.gif')
        a.append(img)
    else:
        a.text = label or target
    if rel:
        a.set('rel', rel)
    elif default_link_rel:
        a.set('rel', default_link_rel)
    return a


#"""
#    <a rel="aa:link" href="/pages/Anthology_walk%2Btalk_Brussels">
#        <span about="/pages/Anthology_walk%2Btalk_Brussels">
#            <span property="aa:linklabel">this anthology</span>
#            <span property="aa:linktarget" content="Anthology walk+talk Brussels"></span>
#        </span>
#    </a>
#"""
#def make_link (rel, target, label, default_link_rel=None):
#    """ More semantically complete version, asserts linktarget and label (if different) via nested spans. """
#    a = markdown.etree.Element('a')
#    href = url_for_pagename(target)
#    a.set('href', href)

#    if rel:
#        a.set('rel', rel)
#    elif default_link_rel:
#        a.set('rel', default_link_rel)

#    label = label or target
#    span = markdown.etree.Element('span')
#    span.set('about', href)
#    a.append(span)

#    if label != target:
#        label_span = markdown.etree.Element('span')
#        label_span.set("property", "aa:linklabel")
#        label_span.text = label
#        span.append(label_span)

#        target_span = markdown.etree.Element('span')
#        target_span.set("property", "aa:linktarget")
#        target_span.set("content", target)
#        span.append(target_span)
#    else:
#        # Only include aa:linktarget
#        target_span = markdown.etree.Element('span')
#        target_span.set("property", "aa:linktarget")
#        target_span.text = target
#        span.append(target_span)

#    return a

def get_markdown(default_link_rel="aa:link"):
    """
    This is a function to return a Active Archive markdown instance.
    Returns a Markdown instance.
    """
    return markdown.Markdown(output_format="html5", extensions=[
            "headerid",
            "attr_list",
            #"abbr",
            "def_list",
            "fenced_code",
            "footnotes",
            #"tables"
            "meta",
            mdx_semanticwikilinks.makeExtension(configs=[
                ('make_link', make_link),
                ('default_link_rel', default_link_rel)]),
            #mdx_cut.makeExtension(),
            mdx_semanticdata.makeExtension(),
            mdx_timecodes.makeExtension(),
            mdx_del_ins.makeExtension(),
            mdx_cite.makeExtension(),
            mdx_addsections.makeExtension(configs=[('class', 'section%(LEVEL)d')]),
            ],
        )


def get_simple_markdown(default_link_rel="aa:link"):
    """
    This is a function to return a Active Archive markdown instance.
    Returns a Markdown instance.
    """
    return markdown.Markdown(output_format="html5", extensions=[
            "attr_list",
            #"abbr",
            "def_list",
            "fenced_code",
            #"footnotes",
            #"tables"
            #"meta",
            mdx_semanticwikilinks.makeExtension(configs=[
                ('make_link', make_link),
                ('default_link_rel', default_link_rel)]),
            #mdx_cut.makeExtension(),
            mdx_semanticdata.makeExtension(),
            #mdx_timecodes.makeExtension(),
            mdx_del_ins.makeExtension(),
            mdx_cite.makeExtension(),
            #mdx_addsections.makeExtension(configs=[('class', 'section%(LEVEL)d')]),
            ],
        )


if __name__ == "__main__":
    import doctest
    doctest.testmod()
