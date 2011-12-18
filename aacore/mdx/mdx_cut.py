#! /usr/bin/env Python


"""
    >>> import markdown
    >>> txt = '''
    ... This is preliminary content
    ... 
    ... 8<
    ... 
    ... # This is my first section
    ... 
    ... This is some additional content
    ... 
    ... ## This is another one
    ... 
    ... 8<
    ... 
    ... - This is my first section
    ... - This is some additional content
    ... 
    ... This is another one
    ... '''
    >>> html = markdown.markdown(txt, extensions=['cut'])
    >>> html.replace("\\n", "")
    u'<p>This is preliminary content</p><section><h1>This is my first section</h1><p>This is some additional content</p><h2>This is another one</h2></section><section><ul><li>This is my first section</li><li>This is some additional content</li></ul><p>This is another one</p></section>'
"""


import re
import markdown


class CutProcessor(markdown.blockprocessors.BlockProcessor):
    RE = r'8\<(?P<header>.*?)'
    # Detect cut on any line of a block.
    SEARCH_RE = re.compile(r'(^|\n)%s(\n|$)' % RE)
    # Match a cut on a single line of text.
    MATCH_RE = re.compile(r'^%s$' % RE)

    def test(self, parent, block):
        last_child = self.lastChild(parent)
        return (bool(self.SEARCH_RE.search(block))
                or (last_child is not None and last_child.tag == "section"))

    def run(self, parent, blocks):
        last_child = self.lastChild(parent)
        block = blocks.pop(0)
        match = self.MATCH_RE.match(block)
        if match:
            print(match.groupdict())
            section = markdown.util.etree.SubElement(parent, 'section')
            section.text = match.groupdict()['header']
        else:
            self.parser.parseChunk(last_child, block)


class CutExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        """ Add an instance of CutProcessor to BlockParser. """
        md.parser.blockprocessors.add('cut', CutProcessor(md.parser),
                                      '_begin')


def makeExtension(configs={}):
    return CutExtension(configs=configs)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
