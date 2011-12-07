#!/usr/bin/env python


import markdown
import re


DEL_INS_RE = r"(?P<type>--|\+\+)(?P<content>.+?)(--|\+\+)"


class DelInsExtension(markdown.Extension):
    def __init__(self, configs):
        self.config = {
            #'make_elt' : [make_elt, 'Callback to convert parts into an HTML/etree element (default <span>)'],
            #'namespace' : ['aa', 'Default namespace'],
        }
        # Override defaults with user settings
        for key, value in configs :
            self.setConfig(key, value)
        
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
        if type_ == "--":
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

