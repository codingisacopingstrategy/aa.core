import urllib
import re


TIMECODE_RE = re.compile(
    r"""^
    (^
    ((?P<seq>\d+)\r?\n)?
    (?P<start> ((\d\d):)? (\d\d): (\d\d) ([,.]\d{1,3})?)
    \s* --> \s*
    (?P<end> ((\d\d):)? (\d\d): (\d\d) ([,.]\d{1,3})?)?
    \s*)
    $""",
    re.X | re.M
)


def wikify (name):
    """
    Turns a "raw" name into a URL wiki name (aka slug)
    Requires: name may be unicode, str
    Returns: str

    (1) Spaces turn into underscores.
    (2) The First letter is forced to be Uppercase (normalization).
    (3) For the rest, non-ascii chars get percentage escaped.
    (Unicode chars be (properly) encoded to bytes and urllib.quote'd to double escapes like "%23%25" as required)
    """
    name = name.strip()
    name = name.replace(" ", "_")
    if len(name):
        name = name[0].upper() + name[1:]
    if (type(name) == unicode):
        # urllib.quoting(unicode) with accents freaks out so encode to bytes
        name = name.encode("utf-8")
    name = urllib.quote(name, safe="")
    return name


def dewikify (name):
    """
    Turns URL name/slug into a proper name (reverse of wikify).
    Requires: name may be unicode, str
    Returns: str

    NB dewikify(wikify(name)) may produce a different name (first letter gets capitalized)
    """
    if (type(name) == unicode):
        # urllib.unquoting unicode with accents freaks! so encode to bytes
        name = name.encode("utf-8")
    name = urllib.unquote(name)
    name = name.replace("_", " ")
    return name


def parse_header_sections(input_lines):
    """
    Takes a markdown text and parses it according to level 1 headers (atx-style)
    Returns a tuples of 3 elements:
    1. ressource url : None or url
    2. header: None or markdown header
    3. lines: an array of the section lines
    """

    saw_url = False
    url = None
    header = None
    lines = []
    for line in input_lines:
        if line.startswith('# '):
            # We found a header. If we saw a url before it then that belongs to the next block:
            if saw_url:
                new_url = lines.pop()
            else:
                new_url = None

            # Emit the previous block:
            if url or header or lines:
                yield url, header, lines

            # Set up the next block:
            saw_url = False
            url = new_url
            header = line
            lines = []
        else:
            # Check for a url (this check may have to be stricter).
            # This only matters if the next line turns out to be a header.
            saw_url = line.startswith('http://')
            lines.append(line)
    yield url, header, lines


def parse_timed_sections(input_lines):
    """
    Takes an "active archive SRT" text and split it according to timecodes
    Returns a tuple:
    1. Timecode: the timecode as string
    2. An array of the body lines

    >>> txt = '''
    ... 00:00:48,850 --> 00:00:50,820
    ... There's an old joke.
    ... 00:00:48,850 -->
    ... Two elderly women are
    ... at a Catskill mountain resort.
    ... '''
    >>> for (timecode, lines) in parse_timed_sections(txt.splitlines()):
    ...     print (timecode, lines)
    ('00:00:48,850 --> 00:00:50,820', ["There's an old joke."])
    ('00:00:48,850 -->', ['Two elderly women are', 'at a Catskill mountain resort.'])
    """
    timecode = None
    lines = []
    for line in input_lines:
        if TIMECODE_RE.match(line):
            if lines != ['']:
                yield (timecode, lines)
            lines = []
            timecode = line
        else:
            lines.append(line)
    if lines != ['']:
        yield (timecode, lines)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
