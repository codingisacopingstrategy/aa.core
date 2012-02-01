#! /usr/bin/env python
#-*- coding:utf-8 -*-


"""
Active Archives: Timecodes
==========================

Preprocessor:

Turns SRT-style timecode patterns into markdown level-2 headers and markups
timecodes with RDFA as aa:start/aa:end values (where aa is the active
archives namespace

Tree Processor:
Fills in implicit end times:
Elements with data-start attributes, but no data-end get "auto-set" by
subsequent siblings data-start values. NB: only data-end attributes get set
(inner/visible markup is not touched)

>>> src = '''
... 2011-11-28 00:01:00 -->
... 00:02:00 -->
... 00:03:00 --> 00:04:00
... Hello
... '''.strip()

>>> html = markdown.markdown(src, ['timecodes'])
>>> print(html)
<h2>%%aa:start::2011-11-28 00:01:00%% &rarr; {: data-start="2011-11-28 00:01:00" }</h2>
<h2>%%aa:start::00:02:00%% &rarr; {: data-start="00:02:00" }</h2>
<h2>%%aa:start::00:03:00%% &rarr; %%aa:end::00:04:00%% {: data-start="00:03:00" data-end="00:04:00" }</h2>
<p>Hello</p>

>>> html = markdown.markdown(src, ['attr_list', 'timecodes', 'semanticdata'])
>>> print(html)
<h2 data-end="00:02:00" data-start="2011-11-28 00:01:00"><span content="2011-11-28 00:01:00" property="aa:start">2011-11-28 00:01:00</span> &rarr;</h2>
<h2 data-end="00:03:00" data-start="00:02:00"><span content="00:02:00" property="aa:start">00:02:00</span> &rarr;</h2>
<h2 data-end="00:04:00" data-start="00:03:00"><span content="00:03:00" property="aa:start">00:03:00</span> &rarr; <span content="00:04:00" property="aa:end">00:04:00</span></h2>
<p>Hello</p>
"""


import re
import markdown
from markdown.util import etree


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
ATTR_RE = re.compile(r'(?P<otherstuff>.*){:(?P<attributes>.*)}')


def replace_timecodes(lines):
    newlines = []
    for line in lines:
        m = TIMECODE_RE.search(line)
        if m:
            start = m.group('start')
            end = m.group('end')
            otherstuff = m.group('otherstuff') or ''

            mm = ATTR_RE.search(otherstuff)
            attr = ''
            if mm:
                otherstuff = mm.group('otherstuff') or ''
                attr = mm.group('attributes')

            if end:
                line = '## %%%%aa:start::%(start)s%%%% %%%%aa:end::%(end)s%%%% %(otherstuff)s{: %(attr)s data-start="%(start)s" data-end="%(end)s" }' % locals()
            else:
                line = '## %%%%aa:start::%(start)s%%%% %(otherstuff)s{: %(attr)s data-start="%(start)s" }' % locals()
        newlines.append(line)
    return newlines


class TimeCodesPreprocessor(markdown.preprocessors.Preprocessor):
    def run(self, lines):
        return replace_timecodes(lines)


class TimeCodesTreeprocessor(markdown.treeprocessors.Treeprocessor):
    """ This Tree Processor adds explicit endtimes to timed sections where a
    subsequent sibling element has a start time.
    """
    def run(self, doc):
        fill_missing_ends(doc)


def fill_missing_ends(node):
    children = list(node)
    for i, child in enumerate(children):
        fill_missing_ends(child)
        if child.get("data-start") and not child.get("data-end"):
            start = child.get("data-start")
            # print "start without end", child, start
            for sibling in children[i + 1:]:
                if sibling.get("data-start"):
                    # print "found matching end", sibling.get("data-start")
                    data_end = sibling.get("data-start")
                    child.set("data-end", data_end) 
                    #<span content="00:38:10" property="aa:start" title="aa:start::00:38:10" class="deduced">00:38:10</span>
                    end = etree.SubElement(child, 'span')
                    end.set('content', data_end)
                    end.set('property', "aa:end")
                    end.set('title', "aa:end::%s" % data_end)
                    end.set('class', "deduced")
                    end.text = data_end
                    break


class TimeCodesExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('timecodes_block', TimeCodesPreprocessor(md), 
                             "_begin")

        ext = TimeCodesTreeprocessor(md)
        ext.config = self.config
        md.treeprocessors.add("timecodes", ext, "_end")


def makeExtension(configs=None):
    return TimeCodesExtension()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
