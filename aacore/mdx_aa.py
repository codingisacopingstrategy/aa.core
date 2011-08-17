#!/usr/bin/env python

'''
Markdown init function that gathers the various AA Extensions for Python-Markdown
======================================

Requires Python-Markdown 2.0+.

'''
import markdown

def get_aa_markdown ():
    return markdown.Markdown(extensions=["semanticwikilinks", "semanticdata", "addsections"])

if __name__ == "__main__":
    import doctest
    doctest.testmod()

