"""
Splits a markdown source into a flat list of sections.

Markdown extension adds {@data-section=%d} attribute markup to headers.

Provides: sectionalize

"""

import markdown, re

HASH_HEADER = r'(^|\n)(?P<level>[#]{%s})[^#](?P<header>.*?)[#]*(\n|$)'
HASH_OR_TIMECODE_HEADER = r"""
(^|\n)
( (?P<level>[#]{%s}) [^#] (?P<header>.*?) [#]* )
|
( (?P<start> ((\d\d):)? (\d\d): (\d\d) ([,.]\d{1,3})?) \s* --> \s* (?P<end> ((\d\d):)? (\d\d): (\d\d) ([,.]\d{1,3})?)? )
(\n|$)""".strip()

def split_re (pattern, text, returnLeading=False):
    cur = None
    header = None
    start = None
    for match in pattern.finditer(text):
        if cur != None:
            yield (header, text[cur:match.start()], start, match.start())
        start = match.start()
        if returnLeading and cur == None and start > 0:
            # yields the text leading up to the first match as a leading section
            # (with blank for matching header)
            yield ('', text[:start], 0, start)
        header = text[match.start():match.end()]
        cur = match.end() 
    if cur != None:
        yield (header, text[cur:], start, len(text))

def sectionalize (wikitext, depth=1, sections=None, textstart=0):
    '''
    Takes a wikitext and returns a list section dictionaries in form:
    { sectionindex: 0, header: "", body: "", start: charindex, end: charindex }
    NB: Source texts overlap depending on hierarchy of headers (see example).

    Takes a text, returns a list in the form [ (headerline, bodylines), ... ]
    ie [ ("# Title", "This is the title.\n\More lines"), ("# Introduction", "Intro text"), ... ]

    '''
    if depth == 2:
        pattern = re.compile(HASH_OR_TIMECODE_HEADER % depth, re.I | re.M | re.X)
    else:    
        pattern = re.compile(HASH_HEADER % depth, re.I | re.M)

    sectionnumber = 0
    if sections == None:
        sections = []

    for header, body, start, end in split_re(pattern, wikitext):
        section = {}
        section['sectionnumber'] = len(sections) + 1
        section['start'] = textstart + start
        section['end'] = textstart + end
        section['header'] = header
        section['body'] = body
        section['depth'] = depth        
        sections.append(section)
        if depth < 10 and body:
            sectionalize(body, depth + 1, sections, textstart + len(header) + start)
    return sections


def sectionalize_replace (originaltext, sectionnumber, sectiontext):
    sections = sectionalize(originaltext)
    pre = originaltext[:sections[sectionnumber]['start']]
    post = originaltext[sections[sectionnumber]['end']:]
    return pre + sectiontext + post


class SectionEditExtension(markdown.Extension):
    def __init__(self, configs={}):
        self.config = {
        }
        for key, value in configs:
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        """ Add SectionEditPreprocessor to the Markdown instance. """

        ext = SectionEditPreprocessor(md)
        ext.config = self.config
        md.preprocessors.add('section_edit_block', ext, ">timecodes_block")


class SectionEditPreprocessor(markdown.preprocessors.Preprocessor):
    def run(self, lines):
        """ Adds section numbers to sections """
        newlines = []
        pattern = re.compile(HASH_OR_TIMECODE_HEADER % "1,10", re.I | re.M | re.X)
        i = 0
        for line in lines:
            if pattern.match(line):
                newlines.append(line.rstrip() + " {@data-section=%d}" % (i+1))
                i += 1
            else:
                newlines.append(line)
        return newlines


def makeExtension(configs={}):
    return SectionEditExtension(configs=configs)


if __name__ == "__main__":
#    import doctest
#    doctest.testmod()

#    import sys
#    pat = re.compile(HASH_OR_TIMECODE_HEADER, re.X)
#    print "pat", pat
#    sys.exit(0)

    text = """
# Test{@style=left: 250px; top: 100px;}

Hello world.

00:01:00 --> 00:02:17

This is a timed annotation

00:03:00 -->

At three minutes.

""".strip()

    from pprint import pprint
    sections = sectionalize(text)
    pprint(sections)

 
#    html = markdown.markdown(text, ['sectionedit'])
#    print html


