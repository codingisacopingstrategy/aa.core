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
from textwrap import dedent


HASH_HEADER_RE = r'(^|\n)(?P<level>#{%s})[^#](?P<header>.*?)#*(\n|$)'
#HASH_HEADER_RE = re.compile(r'(^|\n)(?P<level>#{1,6})(?P<header>.*?)#*(\n|$)')
#SETEXT_HEADER_RE = re.compile(r'^.*?\n[=-]{3,}', re.MULTILINE)

HEADER_SECTION_FORM_TMPL = """
<form class="source">
<textarea>%s</textarea>
<p>
<input type="button" class="cancel" value="cancel" />
<input type="submit" class="submit" value="save" />
</p>
</form>
"""

HEADER_SECTION_TMPL = """
<div class="article">
%s
</div>
%s
"""

NON_HEADER_SECTION_TMPL = """
<div class="article">
%s
</article>
"""


class SectionEditExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        """ Add SectionEditPreprocessor to the Markdown instance. """

        md.preprocessors.add('section_edit_block', 
                                 SectionEditPreprocessor(md), 
                                 "_begin")


class SectionEditPreprocessor(markdown.preprocessors.Preprocessor):
   
    def parse(self, text, level=1):
        prev_start = 0
        seen_section = False
        for match in re.finditer(HASH_HEADER_RE % level, text):
            yield seen_section, prev_start, match.start(), text[prev_start:match.start()]
            seen_section = True
            prev_start = match.start() 
        yield seen_section, prev_start, len(text), text[prev_start:len(text)]

    def run(self, lines):
        """ Match and store Fenced Code Blocks in the HtmlStash. """

        text = "\n".join(lines)
        new_text = ""
        for is_header, start, end, chunk in self.parse(text):
            if is_header:
                form_elt = HEADER_SECTION_FORM_TMPL % chunk
                placeholder = self.markdown.htmlStash.store(form_elt, safe=True)
                new_text += HEADER_SECTION_TMPL % (chunk, placeholder)
            else:
                new_text += NON_HEADER_SECTION_TMPL % chunk

        return new_text.split("\n")


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
