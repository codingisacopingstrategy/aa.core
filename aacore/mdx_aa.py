#!/usr/bin/env python

'''
AA Extension for Python-Markdown
======================================

Adds all the 
Requires Python-Markdown 2.0+.

'''
import markdown, re
from markdown import etree

class ActiveArchivesExtension(markdown.Extension):
    def __init__(self, configs):
        self.config = {
            'tag': ['section', 'tag name to use, default: section'],
            'class': ['section%(LEVEL)d', 'class name, may include %(LEVEL)d to reference header-level (i.e. h1, h2)']
        }
        for key, value in configs:
            self.setConfig(key, value)

    # ...

def makeExtension(configs={}):
    return ActiveArchivesExtension(configs=configs)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

