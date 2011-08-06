#!/usr/bin/env python2

"""
Fenced Style Extension for Python Markdown
=========================================

This extension adds Fenced Style Blocks to Python-Markdown.

    >>> import markdown
    >>> text = '''
    ... A paragraph before a fenced style block:
    ... 
    ... ~~~
    ... Fenced style block
    ... ~~~
    ... '''
    >>> html = markdown.markdown(text, extensions=['fenced_style'])
    >>> html
    u'<p>A paragraph before a fenced style block:</p>\\n<div>Fenced style block\\n</div>'

Works with safe_mode also (we check this because we are using the HtmlStash):

    >>> markdown.markdown(text, extensions=['fenced_style'], safe_mode='replace')
    u'<p>A paragraph before a fenced style block:</p>\\n<div>Fenced style block\\n</div>'
    
Include tilde's in a style block and wrap with blank lines:

    >>> text = '''
    ... ~~~~~~~~
    ... 
    ... ~~~~
    ... 
    ... ~~~~~~~~'''
    >>> markdown.markdown(text, extensions=['fenced_style'])
    u'<div>\\n~~~~\\n\\n</div>'

Multiple blocks and language tags:

    >>> text = '''
    ... ~~~~{.python}
    ... block one
    ... ~~~~
    ... 
    ... ~~~~.html
    ... <p>block two</p>
    ... ~~~~'''
    >>> markdown.markdown(text, extensions=['fenced_style'])
    u'<div class="python">block one\\n</div>\\n\\n<div class="html">&lt;p&gt;block two&lt;/p&gt;\\n</div>'

Copyright 2007-2008 [Waylan Limberg](http://achinghead.com/).

Project website: <http://www.freewisdom.org/project/python-markdown/Fenced__Style__Blocks>
Contact: markdown@freewisdom.org

License: BSD (see ../docs/LICENSE for details) 

Dependencies:
* [Python 2.3+](http://python.org)
* [Markdown 2.0+](http://www.freewisdom.org/projects/python-markdown/)

"""

import markdown, re

# Global vars
FENCED_STYLE_BLOCK_RE = re.compile( \
    r'(?P<fence>^={3,})[ ]*(\{?\.(?P<class>[a-zA-Z0-9_-]*)\}?)?[ ]*\n(?P<style>.*?)(?P=fence)[ ]*$', 
    re.MULTILINE|re.DOTALL
    )
STYLE_WRAP = '<div%s>\n\n%s\n\n</div>'
CLASS_TAG = ' class="%s"'


class FencedStyleExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        """ Add FencedStyleBlockPreprocessor to the Markdown instance. """

        md.preprocessors.add('fenced_style_block', 
                                 FencedStyleBlockPreprocessor(md), 
                                 "_begin")


class FencedStyleBlockPreprocessor(markdown.preprocessors.Preprocessor):
    
    def run(self, lines):
        """ Match Fenced Style Blocks"""
        text = "\n".join(lines)
        while 1:
            m = FENCED_STYLE_BLOCK_RE.search(text)
            if m:
                _class = ''
                if m.group('class'):
                    _class = CLASS_TAG % m.group('class')
                style = STYLE_WRAP % (_class, m.group('style'))
                #placeholder = self.markdown.htmlStash.store(style, safe=True)
                text = '%s\n%s\n%s' % (text[:m.start()], style, text[m.end():])
            else:
                break
        return text.split("\n")


def makeExtension(configs=None):
    return FencedStyleExtension()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
