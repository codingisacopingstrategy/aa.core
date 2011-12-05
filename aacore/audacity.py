from timecode import timecode_fromsecs


def audacity_to_srt(data, explicit=False):
    """
    >>> data = '''90,610022  90,610022   first section
    ... 345,271874  345,271874 second section'''
    >>> print(audacity_to_srt(data).strip())
    00:01:30.610 --> 
    <BLANKLINE>
    first section
    <BLANKLINE>
    00:05:45.272 --> 
    <BLANKLINE>
    second section

    >>> data = '''90,610022  345,271874   first section
    ... 345,271874  512,573912 second section'''
    >>> print(audacity_to_srt(data).strip())
    00:01:30.610 --> 
    <BLANKLINE>
    first section
    <BLANKLINE>
    00:05:45.272 --> 00:08:32.574
    <BLANKLINE>
    second section

    >>> data = '''90,610022  345,271874   first section
    ... 345,271874  512,573912 second section'''
    >>> print(audacity_to_srt(data, explicit=True).strip())
    00:01:30.610 --> 00:05:45.272
    <BLANKLINE>
    first section
    <BLANKLINE>
    00:05:45.272 --> 00:08:32.574
    <BLANKLINE>
    second section

    >>> data = '''90,610022  345,271874   first section
    ... 345,271874  512,573912'''
    >>> print(audacity_to_srt(data).strip())
    00:01:30.610 --> 00:05:45.272
    <BLANKLINE>
    first section
    <BLANKLINE>
    00:05:45.272 --> 00:08:32.574
    <BLANKLINE>
    second section
    """
    stack = []
    for line in data.splitlines():
        try:
            (start, end, body) = tuple(line.split(None, 2))
        except ValueError:
            try:
                # A marker without label
                (start, end) = tuple(line.split(None, 1))
                body = ""
            except ValueError:
                # A blank line? Get lost!
                break

        start = float(start.replace(',', '.'))
        end = float(end.replace(',', '.'))

        start = timecode_fromsecs(start, alwaysfract=True, 
                                  alwayshours=True, fractdelim='.')
        end = timecode_fromsecs(end, alwaysfract=True, 
                                alwayshours=True, fractdelim='.')

        # If the end time equals the start time we ommit it.
        if end == start:
            end = ""

        if not explicit:
            # Deletes previous end time if equal to actual start time
            if len(stack) and stack[-1]['end'] == start:
                stack[-1]['end'] = ""

        body = body.replace(r'\n', '\n')
        #print(unicode(body))

        stack.append({'start': start, 'end': end, 'body': body})

    template = "{e[start]} --> {e[end]}\n\n{e[body]}\n\n"
    return "".join([template.format(e=e) for e in stack])

def srt_to_audacity(data, force_endtime=False):
    """docstring for srt_to_audacity"""
    # FIXME: UnicodeDecodeError...
    import re
    from aacore.mdx.mdx_sectionedit import (TIMECODE_HEADER, spliterator)
    from timecode import timecode_tosecs
    pattern = re.compile(TIMECODE_HEADER, re.I | re.M | re.X)

    stack = []
    for t in spliterator(pattern, data, returnLeading=0):
        m = pattern.match(t[0]).groupdict()

        if force_endtime:
            if len(stack) and stack[-1]['end'] == '':
                stack[-1]['end'] = timecode_tosecs(m['start'])
            end = timecode_tosecs(m['end']) or ''
        else:
            end = timecode_tosecs(m['end']) or timecode_tosecs(m['start'])

        stack.append({
            'start': timecode_tosecs(m['start']),
            'end': end,
            'body': t[1].strip('\n'),
        })

    template = "{e[start]}\t{e[end]}\t{e[body]}\n"
    return "".join([template.format(e=e) for e in stack])


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    f = open('/tmp/bla.srt', 'r')
    data = f.read()
    f.close()
    #print(audacity_to_srt(data))
    print(srt_to_audacity(data))
