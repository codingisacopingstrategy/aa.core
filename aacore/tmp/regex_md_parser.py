#!/usr/bin/env python2
"""
Parses 
"""

import re


HASH_HEADER_RE = r'(^|\n)(?P<level>#{%s})[^#](?P<header>.*?)#*(\n|$)'


def parse(text, level=1):
    prev_start = 0
    seen_section = False
    for match in re.finditer(HASH_HEADER_RE % level, text):
        yield seen_section, prev_start, match.start(), text[prev_start:match.start()]
        seen_section = True
        prev_start = match.start() 
    yield seen_section, prev_start, len(text), text[prev_start:len(text)]


text = """
http://blablablabla.com
# header
fdfddffdfd
fdfdfdfd
http://otherurl
# fdfdfdfdfd
dffdfdfdfdfd
## fdfdfdfdfdfdfd
fdsffdfd
dffdfdfd
http://spork
# blabla
dfffd
"""

if __name__ == '__main__':
    import markdown
    from textwrap import dedent

    newtext = "<style>section { border: 1px solid black; }</style>" 
    newtext += "<style>article { border: 1px solid red; }</style>" 
    newtext += "<style>form { border: 1px solid blue; }</style>" 
    for is_header, start, end, chunk in parse(text):
        if is_header:
            newtext += dedent("""\
            <section>
                <nav><a href="#">edit</a></nav>
                <article>
                %s
                </article>
                <form>
                    <textarea>%s</textarea>
                    <p>
                        <input type="button" value="cancel">
                        <input type="submit" value="save">
                    </p>
                </form>
            </section>\
            """ % (markdown.markdown(chunk), chunk))
        else:
            newtext += dedent("""\
            <section>
                <article>
                %s
                </article>
            </section>\
            """ % markdown.markdown(chunk))

    print(newtext)
