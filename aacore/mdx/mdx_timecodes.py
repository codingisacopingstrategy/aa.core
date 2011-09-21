#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
    Active Archives timecode to (timed) section preprocessor
    ========================================================

    Turns SRT-style timecode patterns into markdown level-2 headers and markups
    timecodes with RDFA as aa:start/aa:end values (where aa is the active
    archives namespace

    >>> import markdown
    >>> from mdx_timecodes import TimeCodesExtension
    >>> text = '''
    ... 00:03:21 --> 00:45:56
    ... Some text
    ... '''
    >>> myext = TimeCodesExtension()
    >>> md = markdown.Markdown(extensions=[myext])
    >>> md.convert(text)
    u'<h2 typeof="aa:clip"> %%aa:start::00:03:21%% --&gt; %%aa:end::00:45:56%%</h2>\\n<p>Some text</p>'
    >>> text = '''
    ... 00:03:21 -->
    ... Some text
    ... '''
    >>> myext = TimeCodesExtension()
    >>> md = markdown.Markdown(extensions=[myext])
    >>> md.convert(text)
    u'<h2 typeof="aa:clip"> %%aa:start::00:03:21%% --&gt;</h2>\\n<p>Some text</p>'
    >>> text = '''
    ... 00:03:21,012 --> 00:03:28,032
    ... Some text
    ... '''
    >>> myext = TimeCodesExtension()
    >>> md = markdown.Markdown(extensions=[myext])
    >>> md.convert(text)
    u'<h2 typeof="aa:clip"> %%aa:start::00:03:21,012%% --&gt; %%aa:end::00:03:28,032%%</h2>\\n<p>Some text</p>'
"""


import markdown, re


TIMECODE_RE = re.compile(
    r"""^
    (?P<start> ((\d\d):)? (\d\d): (\d\d) ([,.]\d{1,3})?)
    \s* --> \s*
    (?P<end> ((\d\d):)? (\d\d): (\d\d) ([,.]\d{1,3})?)?
    \s*
    (?P<otherstuff>.+)
    $""",
    re.X | re.M
)

def replace_timecodes(lines):
    """docstring for replace_timecodes"""
    param_type = type(lines)
    if param_type == "str":
        lines = lines.split('\n')
    newlines = []
    for line in lines:
        m = TIMECODE_RE.search(line)
        if m:
            newline = u"## "
            start = m.group('start')
            newline += "{@data-start=" + start + "}"
            newline += "%%aa:start::" + m.group('start') + "%% &rarr;"
            end = m.group('end')
            if end:
                newline += "{@data-end=" + end + "}"
                newline += u" %%aa:end::" + end + "%%"
            if m.group('otherstuff'):
                newline += m.group('otherstuff')
            newlines.append(newline )
        else:
            newlines.append(line)

    if param_type == "str":
        return '\n'.join(newlines)
    else:
        return newlines


class TimeCodesExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        """ Add TimeCodesPreprocessor to the Markdown instance. """

        md.preprocessors.add('timecodes_block', 
                                 TimeCodesPreprocessor(md), 
                                 "_begin")


class TimeCodesPreprocessor(markdown.preprocessors.Preprocessor):
    
    def run(self, lines):
        """ Match and store Fenced Code Blocks in the HtmlStash. """
        return replace_timecodes(lines)


def makeExtension(configs=None):
    return TimeCodesExtension()


if __name__ == "__main__":
#    import doctest
#    doctest.testmod()

    text = """
00:03:21 --> 00:45:56 Stuff!{@data-section=1}
Some text
""".strip()
 
    print markdown.markdown(text, ['timecodes', 'semanticdata'])
#<h2>%%aa:start::00:03:21%% &rarr; %%aa:end::00:45:56%%</h2>
#.. <p>Some text</p>



