#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
    Active Archives: Timecodes
    ========================================================

    Preprocessor:

    Turns SRT-style timecode patterns into markdown level-2 headers and markups
    timecodes with RDFA as aa:start/aa:end values (where aa is the active
    archives namespace

    Tree Processor:
    Fills in implicit end times:
    Elements with data-start attributes, but no data-end get "auto-set" by subsequent
    siblings data-start values. NB: only data-end attributes get set (inner/visible markup is not touched)

    >>> import markdown
    >>> from mdx_timecodes import TimeCodesExtension
"""

import markdown, re

TIMECODE_RE = re.compile(
    r"""^
    (?P<start> (?P<startdate>\d\d\d\d-\d\d-\d\d)? \s* ((\d\d):)? (\d\d): (\d\d) ([,.]\d{1,3})?)
    \s* --> \s*
    (?P<end> (?P<enddate>\d\d\d\d-\d\d-\d\d)? \s* ((\d\d):)? (\d\d): (\d\d) ([,.]\d{1,3})?)?
    \s*
    (?P<otherstuff>.*)
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

class TimeCodesPreprocessor(markdown.preprocessors.Preprocessor):
    def run(self, lines):
        """ Match and store Fenced Code Blocks in the HtmlStash. """
        return replace_timecodes(lines)

####################
class TimeCodesTreeprocessor(markdown.treeprocessors.Treeprocessor):
    """
    This Tree Processor adds explicit endtimes to timed sections where a subsequent sibling element has a start time.
    """
    def run(self, doc):
        fill_missing_ends(doc)
        # print doc.find("*[@data-start]")

def fill_missing_ends (node):
    children = list(node)
    for i, child in enumerate(children):
        fill_missing_ends(child)
        if child.get("data-start") and not child.get("data-end"):
            start = child.get("data-start")
            # print "start without end", child, start
            for sibling in children[i+1:]:
                if sibling.get("data-start"):
                    # print "found matching end", sibling.get("data-start")
                    child.set("data-end", sibling.get("data-start"))
                    break
####################

class TimeCodesExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('timecodes_block', TimeCodesPreprocessor(md), "_begin")

        ext = TimeCodesTreeprocessor(md)
        ext.config = self.config
        md.treeprocessors.add("timecodes", ext, "_end")

def makeExtension(configs=None):
    return TimeCodesExtension()


if __name__ == "__main__":
    import doctest
    doctest.testmod()

    text = """
2011-11-28 00:01:00 -->
00:02:00 --> 
00:03:00 --> 00:04:00
Hello
""".strip()
    print markdown.markdown(text, ['timecodes', 'semanticdata'])



