#!/usr/bin/env python


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


import markdown
import re


DEL_INS_RE = r"(?P<type>\~\~|\+\+)(?P<content>.+?)(\~\~|\+\+)"


class DelInsExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        self.md = md
    
        # append to end of inline patterns
        pat = DelInsPattern(self.config, md)
        md.inlinePatterns.add('delins', pat, "<not_strong")


class DelInsPattern(markdown.inlinepatterns.Pattern):
    def __init__(self, config, md=None):
        markdown.inlinepatterns.Pattern.__init__(self, '', md)
        self.compiled_re = re.compile(r'^(.*?)' + DEL_INS_RE + r'(.*?)$')
        self.config = config

    def getCompiledRegExp (self):
        return self.compiled_re
  
    def handleMatch(self, m):
        """ Returns etree """
        d = m.groupdict()
        content = d.get("content")
        type_ = d.get("type")
        if type_ == "~~":
            elt = markdown.util.etree.Element('del')
        elif type_ == "++":
            elt = markdown.util.etree.Element('ins')
        elt.text = content
        return elt


def makeExtension(configs={}) :
    return DelInsExtension(configs=configs)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

