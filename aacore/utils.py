import urllib
import re
import string


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


def convert_line_endings(temp, mode):
        #modes:  0 - Unix, 1 - Mac, 2 - DOS
        if mode == 0:
            temp = string.replace(temp, '\r\n', '\n')
            temp = string.replace(temp, '\r', '\n')
        elif mode == 1:
            temp = string.replace(temp, '\r\n', '\r')
            temp = string.replace(temp, '\n', '\r')
        elif mode == 2:
            temp = re.sub("\r(?!\n)|(?<!\r)\n", "\r\n", temp)
        return temp


if __name__ == '__main__':
    import doctest
    doctest.testmod()
