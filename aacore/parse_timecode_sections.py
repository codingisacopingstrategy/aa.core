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
        #import pdb; pdb.set_trace()
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
