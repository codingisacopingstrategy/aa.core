#!/usr/bin/env python2

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
    $""",
    re.X | re.M
)


class TimeCodesExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        """ Add TimeCodesPreprocessor to the Markdown instance. """

        md.preprocessors.add('timecodes_block', 
                                 TimeCodesPreprocessor(md), 
                                 "_begin")


class TimeCodesPreprocessor(markdown.preprocessors.Preprocessor):
    
    def run(self, lines):
        """ Match and store Fenced Code Blocks in the HtmlStash. """
        newlines = []
        for line in lines:
            m = TIMECODE_RE.search(line)
            if m:
                newline = u"## %%aa:start::" + m.group('start') + "%% &rarr;"
                if m.group('end'):
                    newline += u" %%aa:end::" + m.group('end') + "%%"
                newlines.append(newline )
            else:
                newlines.append(line)
        return newlines

    def _escape(self, txt):
        """ basic html escaping """
        txt = txt.replace('&', '&amp;')
        txt = txt.replace('<', '&lt;')
        txt = txt.replace('>', '&gt;')
        txt = txt.replace('"', '&quot;')
        return txt


def makeExtension(configs=None):
    return TimeCodesExtension()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
