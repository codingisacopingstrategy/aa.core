#!/usr/bin/env python2

# TODO: Pick a license

"""
Converts django filters and tags
"""

import markdown, re
from django.template import Context, Template

class DjangoTemplateExtension(markdown.Extension):
    def __init__(self, configs={}):
        self.config = {
            'context': [Context({}), 'Rendering context instance'],
        }
        for key, value in configs:
            self.setConfig(key, value)


    def extendMarkdown(self, md, md_globals):
        """ Add DjangoTemplatePreprocessor to the Markdown instance. """

        ext = DjangoTemplatePreprocessor(md)
        ext.config = self.config
        md.preprocessors.add('django_template_block', ext, ">section_edit_block")


class DjangoTemplatePreprocessor(markdown.preprocessors.Preprocessor):

    def run(self, lines):
        text = "\n".join(lines)
        t = Template("{% load filters aatags %}" + text)
        c = self.config.get("context")[0]
        return t.render(c).split("\n")


def makeExtension(configs=None):
    return DjangoTemplateExtension()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
