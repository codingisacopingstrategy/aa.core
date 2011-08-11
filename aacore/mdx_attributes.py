#!/usr/bin/env Python
"""
Attribute Extension for Python-Markdown
=============================================

Added parsing of Attribute Setters to Python-Markdown.

A simple example:

# Section
@style: left: 100px; top: 250px
@about: http://foo.bar/goo.ogg

becomes
<h1 style="left: 100px; top: 250px" about="http://foo.bar/goo.ogg">Section</h1>

Markdown blocks are text separated by blank lines.

"""

import markdown, re
from markdown import etree

class AttributesProcessor(markdown.blockprocessors.BlockProcessor):
    """ Block Processor Attribute Lines """

    RE = re.compile(r'(^|\n)@(?P<key>\w+)\s*:\s*(?P<value>.+)(\n|$)')
    # RE = re.compile(r'(^|\n)[ ]{0,3}:[ ]{1,3}(.*?)(\n|$)')

    def test(self, parent, block):
        return bool(self.RE.search(block))

    def debug (self, parent, blocks):
        print "="*20        
        print "parent"
        print "="*20        
        print etree.tostring(parent)
        print "="*20        
        print "block", len(blocks), blocks[-1] == ""
        print "="*20
        print blocks[0]
        print "="*20
        print "||\n".join(blocks[1:])
        print "="*20        

    def run(self, parent, blocks):
        """
        parent is an etree Element, blocks is a list of unicode strings

        A BLOCK WITH:
        line
        @key:value
        @foo:bar

        Needs to separate the text from the @ lines and push back to reprocess leading lines.
        """

        # self.debug(parent, blocks)
        block = blocks.pop(0)

        # SPLIT LEADING NON @ LINES 
        if not block.startswith("@"):
            # SPLIT OFF THE LEADING TEXT
            pre = ""
            lines = block.splitlines()
            for (i, line) in enumerate(lines):
                if not line.startswith("@"):
                    if pre: pre += "\n"
                    pre += line
                else:
                    # post is from this line on...
                    post = "\n".join(lines[i:])
                    break
            # SIMPLY PUSH PRE AND POST SEPARATELY ONTO BLOCKS AND LET EACH GET PROCESSES SEPARATELY
            blocks.insert(0, pre)
            if post: blocks.insert(1, post)
        else:        
            # DO NORMAL PROCESSING: Apply @key=value to lastChild
            lastChild = self.lastChild(parent)
            for line in block.splitlines():
                m = self.RE.search(line)
                if m:
                    d = m.groupdict()
                    lastChild.set(d.get("key"), d.get("value"))
                else:
                    blocks.insert(0, line)

class AttributesExtension(markdown.Extension):
    """ Add @attribute: value support. """

    def extendMarkdown(self, md, md_globals):
        """ Add an instance of AttributeProcessor to BlockParser. """
        md.parser.blockprocessors.add('attributes',
                                      AttributesProcessor(md.parser),
                                      '>ulist')

def makeExtension(configs={}):
    return AttributesExtension(configs=configs)

