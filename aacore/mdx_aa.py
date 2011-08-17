#!/usr/bin/env python

'''
Markdown init function that gathers the various AA Extensions for Python-Markdown
======================================

Requires Python-Markdown 2.0+.

'''
import markdown
import mdx_semanticwikilinks
import mdx_semanticdata
import mdx_addsections
import mdx_timecodes
import mdx_sectionedit

def get_aa_markdown ():
    return markdown.Markdown(extensions=[
        mdx_semanticwikilinks.makeExtension(),
        mdx_semanticdata.makeExtension(),
        mdx_addsections.makeExtension(),
        mdx_timecodes.makeExtension(),
        mdx_sectionedit.makeExtension(),
        ])

if __name__ == "__main__":
    import doctest
    doctest.testmod()

