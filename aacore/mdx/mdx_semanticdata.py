#!/usr/bin/env python

'''
SemanticData Extension for Python-Markdown
======================================

Converts %%property :: value | display%%, where display is optional. 
Customizable with make_metadata option as to what the actual element is.
Requires Python-Markdown 2.0+.

Basic usage:

    >>> import markdown
    >>> text = "%%dc:author :: Sherry Turkle | Turkle's%% %%dc:title::Second Self%% was an early book on the social aspects of computation."
    >>> html = markdown.markdown(text, ['semanticdata'])
    >>> html
    u'<p><span content="Sherry Turkle" property="dc:author">Turkle\\'s</span> <span content="Second Self" property="dc:title">Second Self</span> was an early book on the social aspects of computation.</p>'

'''

import markdown
import re

#pattern = r"""
#\%\%\s*
#    (?:(?P<property>[^\]#]+?) \s* ::) \s*
#    (?P<value>.+?) \s*
#    (?:\| \s* (?P<display>[^\]]+?) \s*)?
#\%\%
#""".strip()

pattern = r"""
\%\%\s*
    (?:((?P<namespace>\w+):)?(?P<rel>[^\%#]+?) \s* ::)? \s*
    (?P<target>.+?) \s*
    (?:\| \s* (?P<label>[^\]]+?) \s*)?
\%\%
""".strip()

def make_elt (rel, target, label):
    elt = markdown.etree.Element('span')
    elt.set('content', target)
    elt.text = label or target
    if rel:
        elt.set('property', rel)
    return elt

class SemanticDataExtension(markdown.Extension):
    def __init__(self, configs):
        self.config = {
            'make_elt' : [make_elt, 'Callback to convert parts into an HTML/etree element (default <span>)'],
            'namespace' : ['aa', 'Default namespace'],
        }
        # Override defaults with user settings
        for key, value in configs :
            self.setConfig(key, value)
        
    def extendMarkdown(self, md, md_globals):
        self.md = md
    
        # append to end of inline patterns
        pat = SemanticDataPattern(self.config, md)
        md.inlinePatterns.add('semanticdata', pat, "<not_strong")

class SemanticDataPattern(markdown.inlinepatterns.Pattern):

    def __init__(self, config, md=None):
        markdown.inlinepatterns.Pattern.__init__(self, '', md)
        # self.markdown = md # done by super
        self.compiled_re = re.compile("^(.*?)%s(.*?)$" % pattern, re.DOTALL | re.X)
        self.config = config

    def getCompiledRegExp (self):
        return self.compiled_re
  
    def handleMatch(self, m):
        """ Returns etree """
        d = m.groupdict()
        fn = self.config['make_elt'][0]
        namespace = d.get("namespace") or self.config['namespace'][0]
        rel = d.get("rel")
        if rel:
            rel = "%s:%s" % (namespace, d.get("rel"))
        return fn(rel, d.get("target"), d.get("label"))

#    def handleMatch(self, m):
#        """ return etree """
#        d = m.groupdict()
#        fn = self.config['make_elt'][0]
#        return fn(d.get("property"), d.get("value"), d.get("display"))    

def makeExtension(configs={}) :
    return SemanticDataExtension(configs=configs)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

