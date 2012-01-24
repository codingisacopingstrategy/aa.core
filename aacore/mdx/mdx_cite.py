#! /usr/bin/env python


'''
Cite Extension for Python-Markdown
==================================

Wraps the inline content into <cite> tags.

Tested with Python-Markdown 2.0+.

Basic usage:

    >>> import markdown
    >>> src = '"""Who Is Killing the Great Chefs of Europe?""" is the last movie I watched.'
    >>> html = markdown.markdown(src, ['cite'])
    >>> print(html)
    <p><cite>Who Is Killing the Great Chefs of Europe?</cite> is the last movie I watched.</p>
'''


import re
import markdown
from markdown.inlinepatterns import SimpleTagPattern



CITE_RE = r'(\"{3})(.+?)\2'

class CiteExtension(markdown.extensions.Extension):
    """ Add smart_emphasis extension to Markdown class."""

    def extendMarkdown(self, md, md_globals):
        """ Modify inline patterns. """
        #md.inlinePatterns.add('cite', SimpleTagPattern(CITE_RE, 'cite'), '>emphasis2')
        md.inlinePatterns.add('cite', SimpleTagPattern(CITE_RE, 'cite'), '<not_strong')

def makeExtension(configs={}):
    return CiteExtension(configs=dict(configs))


if __name__ == "__main__":
    import doctest
    doctest.testmod()

