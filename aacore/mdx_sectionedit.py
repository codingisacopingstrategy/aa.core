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
<input type="hidden" name="start" value="%s" />
<input type="hidden" name="stop" value="%s" />
<input type="button" class="cancel" value="cancel" />
<input type="submit" class="submit" value="save" />
</p>
</form>
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
        prev_end = 0
        header = None
        for match in re.finditer(HASH_HEADER_RE % level, text):
            yield header, prev_start, match.start(), text[prev_end:match.start()]
            header = text[match.start():match.end()]
            prev_start = match.start() 
            prev_end = match.end() 
        yield header, prev_start, len(text), text[prev_end:len(text)]

    def run(self, lines):
        """ Match and store Fenced Code Blocks in the HtmlStash. """

        text = "\n".join(lines)
        new_text = ""
        for header, start, end, body in self.parse(text):
            if header:
                form_elt = HEADER_SECTION_FORM_TMPL % (header + body, start, end)
                #placeholder = self.markdown.htmlStash.store(form_elt, safe=True)
                #new_text += "\n%s\n%s\n" % (chunk, placeholder)
                new_text += "\n%s\n%s\n%s\n" % (header, form_elt, body)
            else:
                new_text += body

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
