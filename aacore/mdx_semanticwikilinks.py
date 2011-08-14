#!/usr/bin/env python

'''
SemanticWikiLinks Extension for Python-Markdown
======================================

Converts links of style [[rel :: target | label]], where rel and label are optional. 
Customizable with make_link option as to what the actual element is.
Requires Python-Markdown 2.0+.

Basic usage:

    >>> import markdown
    >>> text = "Some text with a [[WikiLink]]."
    >>> html = markdown.markdown(text, ['semanticwikilinks'])
    >>> html
    u'<p>Some text with a <a href="WikiLink">WikiLink</a>.</p>'

Define a custom URL builder:

    >>> def make_rdfa(rel, target, label):
    ...     elt = markdown.etree.Element("span")
    ...     elt.set("property", rel)
    ...     elt.set("value", target)
    ...     elt.text = label or target
    ...     return elt
    >>> md = markdown.Markdown(extensions=['semanticwikilinks'], 
    ...         extension_configs={'semanticwikilinks' : [('make_link', make_rdfa)]})
    >>> md.convert('[[ Speaker :: Sherry Turkle | Ms. Turkle ]]')
    u'<p><span property="Speaker" value="Sherry Turkle">Ms. Turkle</span></p>'

'''

import markdown
import re

wikilink_pattern = r"""
\[\[\s*
    (?:(?P<rel>[^\]#]+?) \s* ::)? \s*
    (?P<target>.+?) \s*
    (?:\| \s* (?P<label>[^\]]+?) \s*)?
\]\]
""".strip()

def make_link (rel, target, label):
    a = markdown.etree.Element('a')
    a.set('href', target)
    a.text = label or target
    if rel:
        a.set('rel', rel)
    return a

class WikiLinkExtension(markdown.Extension):
    def __init__(self, configs):
        self.config = {
            'make_link' : [make_link, 'Callback to convert link parts into an HTML/etree element (<a></a>)'],
        }
        # Override defaults with user settings
        for key, value in configs :
            self.setConfig(key, value)
        
    def extendMarkdown(self, md, md_globals):
        self.md = md
    
        # append to end of inline patterns
        pat = WikiLinkPattern(self.config, md)
        md.inlinePatterns.add('wikilink', pat, "<not_strong")

class WikiLinkPattern(markdown.inlinepatterns.Pattern):

    def __init__(self, config, md=None):
        markdown.inlinepatterns.Pattern.__init__(self, '', md)
        # self.markdown = md # done by super
        self.compiled_re = re.compile("^(.*?)%s(.*?)$" % wikilink_pattern, re.DOTALL | re.X)
        self.config = config

    def getCompiledRegExp (self):
        return self.compiled_re
  
    def handleMatch(self, m):
        """ return etree """
        d = m.groupdict()
        fn = self.config['make_link'][0]
        return fn(d.get("rel"), d.get("target"), d.get("label"))    

def makeExtension(configs={}) :
    return WikiLinkExtension(configs=configs)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

