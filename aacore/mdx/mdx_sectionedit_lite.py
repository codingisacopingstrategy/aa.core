"""
"""

import markdown, re


HASH_HEADER_RE = r'(^|\n)(?P<level>#{%s})[^#](?P<header>.*?)#*(\n|$)'


def split_re (pattern, text, returnLeading=False):
    """
    Splits a text according to the given pattern.
    returns a generator of tuples of 4 values
    >>> text = '''
    ... # 1
    ... Section 1
    ... ## 1.1
    ... Subsection 1.1
    ... ## 1.2
    ... Subsection 1.2
    ... ### 1.2.1
    ... Hey 1.2.1 Special section
    ... ### 1.2.2
    ... #### 1.2.2.1
    ... # 2
    ... Section 2
    ... '''
    >>> pattern = re.compile(HASH_HEADER_RE % 1, re.I | re.M)
    >>> for (header, body, start, end) in split_re(pattern, text):
    ...     print("%s --> %s" % (start, end))
    ...     print(header + body)
    0 --> 117
    <BLANKLINE>
    # 1
    Section 1
    ## 1.1
    Subsection 1.1
    ## 1.2
    Subsection 1.2
    ### 1.2.1
    Hey 1.2.1 Special section
    ### 1.2.2
    #### 1.2.2.1
    117 --> 132
    <BLANKLINE>
    # 2
    Section 2
    <BLANKLINE>
    """
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

    >>> text = """
    ... # 1
    ... Section 1
    ... ## 1.1
    ... Subsection 1.1
    ... ## 1.2
    ... Subsection 1.2
    ... ### 1.2.1
    ... Hey 1.2.1 Special section
    ... ### 1.2.2
    ... #### 1.2.2.1
    ... # 2
    ... Section 2
    ... """
    >>> import json
    >>> for (i, section) in enumerate(sectionalize(text)):
    ...     print json.dumps(section, sort_keys=True, indent=4)
    {
        "body": "Section 1\\n## 1.1\\nSubsection 1.1\\n## 1.2\\nSubsection 1.2\\n### 1.2.1\\nHey 1.2.1 Special section\\n### 1.2.2\\n#### 1.2.2.1", 
        "depth": 1, 
        "end": 117, 
        "header": "\\n# 1\\n", 
        "sectionnumber": 1, 
        "start": 0
    }
    {
        "body": "Subsection 1.1", 
        "depth": 2, 
        "end": 36, 
        "header": "\\n## 1.1\\n", 
        "sectionnumber": 2, 
        "start": 14
    }
    {
        "body": "Subsection 1.2\\n### 1.2.1\\nHey 1.2.1 Special section\\n### 1.2.2\\n#### 1.2.2.1", 
        "depth": 2, 
        "end": 117, 
        "header": "\\n## 1.2\\n", 
        "sectionnumber": 3, 
        "start": 36
    }
    {
        "body": "Hey 1.2.1 Special section", 
        "depth": 3, 
        "end": 94, 
        "header": "\\n### 1.2.1\\n", 
        "sectionnumber": 4, 
        "start": 58
    }
    {
        "body": "#### 1.2.2.1", 
        "depth": 3, 
        "end": 117, 
        "header": "\\n### 1.2.2\\n", 
        "sectionnumber": 5, 
        "start": 94
    }
    {
        "body": "", 
        "depth": 4, 
        "end": 117, 
        "header": "#### 1.2.2.1", 
        "sectionnumber": 6, 
        "start": 105
    }
    {
        "body": "Section 2\\n", 
        "depth": 1, 
        "end": 132, 
        "header": "\\n# 2\\n", 
        "sectionnumber": 7, 
        "start": 117
    }
    >>> text = """# Section 1 {@about="some ressource"}
    ... Some content
    ... # Section 2 {@about="some other ressource"}
    ... Some more content
    ... """
    >>> text = """# blka {@about="http://url/of/th/ressource"} {@style=top: 200px; left: 450px; width: 300px; height: 400px;} kjhdskqjh
    ... 
    ... {% page_list %}
    ... 
    ... # bal {@about="http://url/of/th/ressource"} {@style=top: 50px; left: 50px; width: 300px; height: 400px;}
    ... 
    ... test bla
    ... """
    >>> for (i, section) in enumerate(sectionalize(text)):
    ...     print json.dumps(section, sort_keys=True, indent=4)
    '''
    pattern = re.compile(HASH_HEADER_RE % depth, re.I | re.M)

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
        pattern = re.compile(HASH_HEADER_RE % "1,10", re.I | re.M)
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
    import doctest
    doctest.testmod()

    from textwrap import dedent
    text = dedent("""
        # One
        Hello
        # Two
        
        Second section, testing
        # Three
        
        """.strip())

#    text = "1|2|3|4"
#    print text
#    print  "0123456"
#    for (h, b, start, end) in split_re(re.compile("\|"), text):
#        print h, b, start, end
    
    from pprint import pprint
    sections = sectionalize(text)
    pprint(sections)

    

#    html = markdown.markdown(text, ['sectionedit_lite'])
#    print html


