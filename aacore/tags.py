"""
Code is derived from
http://effbot.org/zone/django-simple-template.htm
"""


import re
import os
from aacore.utils import dewikify


def render_tpl(template):
    """
    >>> txt = "this is a {% template tag %}"
    >>> print(render_tpl(txt))
    >>> txt = "this is a {% template tag not closed"
    >>> print(render_tpl(txt))
    >>> txt = "this is all our pages: {% list_pages %}"
    >>> print(render_tpl(txt))
    >>> txt = "this is all our pages: {% list_pages ldskjdslkdsj"
    >>> print(render_tpl(txt))
    >>> txt = "this is all our pages: {% list_pages "
    >>> print(render_tpl(txt))
    """
    next = iter(re.split("({%|%})", template)).next
    data = []
    try:
        token = next()
        while 1:
            if token == "{%": # variable
                data.append(render_tag(next()))
                if next() != "%}":
                    pass
            else:
                data.append(token) # literal
            token = next()
    except StopIteration:
        pass
    return data


def render_tag(tag):
    tag = tag.strip()
    if tag == "list_pages":
        return list_pages()
    else:
        return "<mark>%s doesn't exists</mark>" % tag


def list_pages():
    return '<ul><li>' + '</li><li>'.join(['<a href="../%s">%s</a>' % (page, dewikify(page)) for page in os.listdir('/home/aleray/work/aa.new/aa.core/run/repositories')]) + '</li></ul>'


if __name__ == "__main__":
    import doctest
    doctest.testmod()
