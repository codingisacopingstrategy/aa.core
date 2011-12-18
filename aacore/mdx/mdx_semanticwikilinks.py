#! /usr/bin/env python


'''
SemanticWikiLinks Extension for Python-Markdown
===============================================

Converts links of style [[rel :: target | label || pipeline ]], where rel,
label and pipeline are optional.  Customizable with make_link option as to what
the actual element is.

Requires Python-Markdown 2.0+.


Basic usage:

    >>> text = "Some text with a [[WikiLink]]."
    >>> html = markdown.markdown(text, ['semanticwikilinks'])
    >>> print(html)
    <p>Some text with a <a href="WikiLink">WikiLink</a>.</p>
    >>> text = "[[http://activearchives.org/]], [[#id|anchor]], [[../index.html|a relative link]], [[/|an absolute link]], [[/index.html|another absolute link]]"
    >>> html = markdown.markdown(text, ['semanticwikilinks'])
    >>> print(html)
    <p>Some text with a <a href="http://activearchives.org/">http://activearchives.org/</a>.</p>

Define a custom URL builder:

    >>> def make_rdfa(rel, target, label, default_link_rel=None, filter_=None):
    ...     elt = etree.Element("span")
    ...     elt.set("property", rel)
    ...     elt.set("value", target)
    ...     elt.text = label or target
    ...     return elt
    >>> md = markdown.Markdown(extensions=['semanticwikilinks'],
    ...         extension_configs={'semanticwikilinks' : [('make_link', make_rdfa)]})
    >>> html = md.convert('[[ Speaker :: Sherry Turkle | Second Self ]]')
    >>> print(html)
    <p><span property="aa:Speaker" value="Sherry Turkle">Second Self</span></p>

Change the default namespace ("aa"):

    >>> md = markdown.Markdown(extensions=['semanticwikilinks'],
    ...         extension_configs={'semanticwikilinks' : [('namespace', 'mynamespace')]})
    >>> html = md.convert('[[ Speaker :: Sherry Turkle | Second Self ]]')
    >>> print(html)
    <p><a href="Sherry Turkle" rel="mynamespace:Speaker">Second Self</a></p>

Specify a pipeline, converted into a data-filter attribute. This is used by the
active archives wiki to apply filters on the resources:

    >>> md = markdown.Markdown(extensions=['semanticwikilinks'])
    >>> html = md.convert('[[ embed::http://video.constantvzw.org/AAworkshop/saturdaytimelapse.ogv || extract:audio|embed:html5audio ]]')
    >>> print(html)
    <p><a data-filter="extract:audio|embed:html5audio" href="http://video.constantvzw.org/AAworkshop/saturdaytimelapse.ogv" rel="aa:embed">http://video.constantvzw.org/AAworkshop/saturdaytimelapse.ogv</a></p>

TODO: an optional function to wikify names (it is already possible to achieve
this with the custom 'make_link' function)
'''


import markdown
try: from markdown import etree
except ImportError: from markdown.util import etree
import re


WIKILINK_RE = r"""
\[\[\s*
    (?:((?P<namespace>\w+):)?(?P<rel>[^\]#]+?) \s* ::)? \s*
    (?P<target>.+?) \s*
    (?:\|(?!\|) \s* (?P<label>.+?) \s*)?
    (?:\|\| \s* (?P<filter>.+?) \s*)?
\]\](?!\])
""".strip()


def make_link(rel, target, label, default_link_rel=None, filter_=None):
    a = etree.Element('a')
    a.set('href', target)
    a.text = label or target
    if rel:
        a.set('rel', rel)
    elif default_link_rel:
        a.set('rel', default_link_rel)
    if filter_:
        a.set('data-filter', filter_)
    return a


class SemanticWikiLinkExtension(markdown.Extension):
    def __init__(self, configs):
        self.config = {
            'make_link': [make_link, 'Callback to convert link parts into an HTML/etree element (<a></a>)'],
            'default_link_rel': [None, 'Default link rel'],
            'namespace': ['aa', 'Default namespace'],
        }
        # Override defaults with user settings
        for key, value in configs:
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        self.md = md

        # append to end of inline patterns
        pat = SemanticWikiLinkPattern(self.config, md)
        md.inlinePatterns.add('semanticwikilink', pat, "<not_strong")


class SemanticWikiLinkPattern(markdown.inlinepatterns.Pattern):

    def __init__(self, config, md=None):
        markdown.inlinepatterns.Pattern.__init__(self, '', md)
        # self.markdown = md # done by super
        self.compiled_re = re.compile("^(.*?)%s(.*?)$"
                                      % WIKILINK_RE, re.DOTALL | re.X)
        self.config = config

    def getCompiledRegExp(self):
        return self.compiled_re

    def handleMatch(self, m):
        """ Returns etree """
        d = m.groupdict()
        fn = self.config['make_link'][0]
        namespace = d.get("namespace") or self.config['namespace'][0]
        rel = d.get("rel")
        if rel:
            rel = "%s:%s" % (namespace, d.get("rel"))
        filter_ = d.get("filter")
        return fn(rel, d.get("target"), d.get("label"),
                  self.config['default_link_rel'][0], filter_=filter_)


def makeExtension(configs={}):
    return SemanticWikiLinkExtension(configs=configs)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
