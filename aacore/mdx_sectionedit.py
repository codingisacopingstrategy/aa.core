#!/usr/bin/env python2

# TODO: Pick a license

"""
mdx_sectionedit
===============

Created for the needs of Active Archive wiki, this extension stashes the
document implicit sections (defined by level one headers) into textarea and
wraps those in form elements with all the necessary information to allow per
section edition.

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

By the [Active Archives](http://activearchives.org/) contributors.

Dependencies:
* [Python 2.3+](http://python.org)
* [Markdown 2.0+](http://www.freewisdom.org/projects/python-markdown/)
"""

import markdown, re
from textwrap import dedent
# from django.template import Context, Template


# TODO: Level 2 header support
# TODO: Setext style header support
HASH_HEADER_RE = r'(^|\n)(?P<level>#{%s})[^#](?P<header>.*?)#*(\n|$)'
#HASH_HEADER_RE = re.compile(r'(^|\n)(?P<level>#{1,6})(?P<header>.*?)#*(\n|$)')
#SETEXT_HEADER_RE = re.compile(r'^.*?\n[=-]{3,}', re.MULTILINE)

#HEADER_SECTION_FORM_TMPL = """
#<form action="edit/" method="post" accept-charset="utf-8" class="source">
#<textarea>%s</textarea>
#<p>
#<input type="hidden" name="start" value="%s" />
#<input type="hidden" name="end" value="%s" />
#<input type="button" class="cancel" value="cancel" />
#<input type="submit" class="submit" value="save" />
#</p>
#</form>
#"""

HEADER_SECTION_FORM_TMPL = """
<form action="edit/" method="post" accept-charset="utf-8" class="source">
<textarea>%s</textarea>
<p>
<input type="hidden" name="start" value="%s" />
<input type="hidden" name="end" value="%s" />
<input type="button" class="cancel" value="cancel" />
<input type="submit" class="submit" value="save" />
</p>
</form>
"""

def doformat(self, header, start, end, content):
    # print(header, start, end, content)
    # print("------")
    if header:
        # t = Template("{% csrf_token %}")
        # c = self.config.get("context")[0]
        # csrf_token =  t.render(c)
        # form_elt = HEADER_SECTION_FORM_TMPL % (csrf_token, self._escape(content), start, end)
        form_elt = HEADER_SECTION_FORM_TMPL % (self._escape(content), start, end)
        placeholder = self.markdown.htmlStash.store(form_elt, safe=True)
        return "\n%s\n%s\n" % (content, placeholder)
    else:
        return content

class SectionEditExtension(markdown.Extension):
    def __init__(self, configs={}):
        self.config = {
            'context': [None, 'context'],
#            'context': [Context({}), 'Rendering context instance'],
            'format': [doformat, 'Formating function'],
        }
        for key, value in configs:
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        """ Add SectionEditPreprocessor to the Markdown instance. """

        ext = SectionEditPreprocessor(md)
        ext.config = self.config
        md.preprocessors.add('section_edit_block', ext, "_begin")


class SectionEditPreprocessor(markdown.preprocessors.Preprocessor):

    def parse(self, text, level=1):
        """ Parses header (implicit) sections 
        Yields:
            1. The header or None
            2. The start offset of the section
            3. The end offset of the section
            4. The content of the section
        """
        prev_start = 0
        prev_end = 0
        header = None
        for match in re.finditer(HASH_HEADER_RE % level, text):
            yield (header, prev_start, match.start(), text[prev_start:match.start()])
            header = text[match.start():match.end()]
            prev_start = match.start() 
            prev_end = match.end() 
        yield (header, prev_start, len(text), text[prev_start:len(text)])

    def run(self, lines):
        """ Stores source code in form elements """

        text = "\n".join(lines)
        new_text = ""
        for header, start, end, content in self.parse(text):
            fun = self.config.get("format")[0]
            new_text += fun(self, header, start, end, content)

        return new_text.split("\n")

    def _escape(self, txt):
        """ basic html escaping """
        txt = txt.replace('&', '&amp;')
        txt = txt.replace('<', '&lt;')
        txt = txt.replace('>', '&gt;')
        txt = txt.replace('"', '&quot;')
        return txt


def makeExtension(configs={}):
    return SectionEditExtension(configs=configs)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
