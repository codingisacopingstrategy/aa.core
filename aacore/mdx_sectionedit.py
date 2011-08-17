#!/usr/bin/env python2

"""
    >>> import markdown
    >>> from mdx_sectionedit import SectionEditExtension
    >>> text = '''
    ... # Header 1
    ... Some text
    ... # Header2
    ... Some more text
    ... '''
    >>> myext = SectionEditExtension()
    >>> md = markdown.Markdown(extensions=[myext])
    >>> md.convert(text)
    u'<h1>Header 1</h1>\\n<p>Some text</p>\\n<form><textarea>\\n# Header 1\\nSome text</textarea></form>\\n\\n<h1>Header2</h1>\\n<p>Some more text</p>\\n<form><textarea># Header2\\nSome more text\\n</textarea></form>'
"""

import markdown, re


class SectionEditExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        """ Add SectionEditPreprocessor to the Markdown instance. """

        md.preprocessors.add('section_edit_block', 
                                 SectionEditPreprocessor(md), 
                                 "_begin")


class SectionEditPreprocessor(markdown.preprocessors.Preprocessor):
    
    def run(self, lines):
        """ Match and store Fenced Code Blocks in the HtmlStash. """
        seen_section = False
        text = []
        section = []
        for i, line in enumerate(lines):
            if line.startswith("# ") or i == (len(lines) - 1):
                if seen_section:
                    source = "\n\n<form><textarea>%s</textarea></form>" % self._escape("\n".join(section))
                    text.append(source)
                    section = []
                else:
                    seen_section = True
            text.append(line)
            section.append(line)
        return text

    def _escape(self, txt):
        """ basic html escaping """
        txt = txt.replace('&', '&amp;')
        txt = txt.replace('<', '&lt;')
        txt = txt.replace('>', '&gt;')
        txt = txt.replace('"', '&quot;')
        return txt


def makeExtension(configs=None):
    return SectionEditExtension()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
