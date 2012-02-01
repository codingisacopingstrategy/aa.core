#! /usr/bin/env python


'''
Del/Ins Extension for Python-Markdown
=====================================

Wraps the inline content in ins/del tags.

Tested with Python-Markdown 2.0+.

Basic usage:

    >>> import markdown
    >>> src = """This is ++added content++ and this is ~~deleted content~~""" 
    >>> html = markdown.markdown(src, ['del_ins'])
    >>> print(html)
    <p>This is <ins>added content</ins> and this is <del>deleted content</del>
    </p>
'''


import re
import markdown
from markdown.inlinepatterns import SimpleTagPattern


DEL_RE = r"(\~\~)(.+?)(\~\~)"
INS_RE = r"(\+\+)(.+?)(\+\+)"


class DelInsExtension(markdown.extensions.Extension):
    """ Add smart_emphasis extension to Markdown class."""

    def extendMarkdown(self, md, md_globals):
        """ Modify inline patterns. """
        md.inlinePatterns.add('del', SimpleTagPattern(DEL_RE, 'del'), '<not_strong')
        md.inlinePatterns.add('ins', SimpleTagPattern(INS_RE, 'ins'), '<not_strong')


def makeExtension(configs={}):
    return DelInsExtension(configs=dict(configs))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
