from timecode import timecode_fromsecs


def audacity_to_srt(data):
    """
    >>> data = '''90,610022  90,610022   first section
    ... 345,271874  345,271874 second section'''
    >>> audacity_to_srt(data)
    """
    srt = ""
    for line in data.splitlines():
        (start, end, body) = tuple(line.split(None, 2))

        start = float(start.replace(',', '.'))
        end = float(end.replace(',', '.'))

        start = timecode_fromsecs(start, alwaysfract=True, 
                                  alwayshours=True, fractdelim='.')
        end = timecode_fromsecs(end, alwaysfract=True, 
                                alwayshours=True, fractdelim='.')

        # If the end time equals the start time we ommit it.
        if end == start:
            end = ""

        #body = body.decode('unicode-escape')
        body = body.replace(r'\n', '\n')

        srt += "{} --> {}\n\n{}\n\n".format(start, end, body)
    return srt


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    import codecs
    #f = codecs.open('/tmp/marqueurs.txt', mode='r', encoding='unicode-escape')
    f = open('/tmp/marqueurs.txt', 'r')
    data = f.read()
    f.close()
    #print(data)
    print(audacity_to_srt(data))
    #f = codecs.open('/tmp/marqueurs.srt', mode='w', encoding='utf-8')
    #f.write(audacity_to_srt(data))
    #f.close()
