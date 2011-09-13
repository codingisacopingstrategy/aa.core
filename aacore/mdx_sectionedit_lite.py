import markdown, re

HASH_HEADER_RE = r'(^|\n)(?P<level>#{%s})[^#](?P<header>.*?)#*(\n|$)'

def split_re (pat, text, returnLeading=False):
    cur = None
    h = None
    start = None
    for m in pat.finditer(text):
        if cur != None:
            yield (h, text[cur:m.start()], start, m.start())
        start = m.start()
        if returnLeading and cur == None and start > 0:
            # yield the text leading up to the first match as a leading section (with blank for matching header)
            yield ('', text[:start], 0, start)
        h = text[m.start():m.end()]
        cur = m.end() 
    if cur != None:
        yield (h, text[cur:], start, len(text))

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
    >>> for (i, (h, t)) in enumerate(sectionalize(text)):
    ...     print "=== SECTION %d ===" % (i+1)
    ...     if h: print h.strip()
    ...     if t: print t.strip()
    ... 
    === SECTION 1 ===
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
    === SECTION 2 ===
    ## 1.1
    Subsection 1.1
    === SECTION 3 ===
    ## 1.2
    Subsection 1.2
    ### 1.2.1
    Hey 1.2.1 Special section
    ### 1.2.2
    #### 1.2.2.1
    === SECTION 4 ===
    ### 1.2.1
    Hey 1.2.1 Special section
    === SECTION 5 ===
    ### 1.2.2
    #### 1.2.2.1
    === SECTION 6 ===
    #### 1.2.2.1
    === SECTION 7 ===
    # 2
    Section 2
    '''

    if sections == None:
        sections = []
    pat = re.compile(HASH_HEADER_RE % depth, re.I | re.M)
    sectionnumber = 0
    for header, body, start, end in split_re(pat, wikitext):
        # print "===== SECTION %d =====" % (sectionindex + 1)
        section = {}
        section['sectionnumber'] = len(sections) + 1
        section['start'] = textstart + start
        section['end'] = textstart + end
        section['header'] = header
        section['body'] = body
        section['depth'] = depth        
        sections.append(section)
        if depth<10 and body:
            sectionalize(body, depth+1, sections, textstart + len(header) + start)
        # print text.strip()
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
        md.preprocessors.add('section_edit_block', ext, "_begin")

class SectionEditPreprocessor(markdown.preprocessors.Preprocessor):
    def run(self, lines):
        """ Adds section numbers to sections """
        newlines = []
        pat = re.compile(HASH_HEADER_RE % "1,10", re.I | re.M)
        i = 0
        for line in lines:
            if pat.match(line):
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

    text = """
# One
Hello
# Two

Second section, testing
# Three

""".strip()

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


