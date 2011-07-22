import urllib


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
