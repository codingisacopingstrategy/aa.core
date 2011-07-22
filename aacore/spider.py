"""
docstring :)
"""

import urllib2, urlparse, lxml, lxml.cssselect, html5lib

from settings import USER_AGENT


def spider (url, levels=1):
    """
    Spiders the given url and returns a dictionnary containing all its links
    and images. Takes an optional depth as sucond argument (not implemented yet).
    """
    ret = {}

    request = urllib2.Request(url)
    request.add_header("User-Agent", USER_AGENT)
    f = urllib2.urlopen(request)
    parser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("lxml"), namespaceHTMLElements=False)
    page = parser.parse(f)

    seen = {}
    for elt in lxml.cssselect.CSSSelector('a[href]')(page):
        href = urlparse.urljoin(f.geturl(), elt.attrib['href'])
        if href.startswith('http'):
            if not href in seen:
                seen[href] = True
    ret['links'] = seen.keys()
    ret['links'].sort()

    seen = {}
    for elt in lxml.cssselect.CSSSelector('img[src]')(page):
        src = urlparse.urljoin(f.geturl(), elt.attrib['src'])
        if src.startswith('http'):
            if not src in seen:
                seen[src] = True
    ret['images'] = seen.keys()
    ret['images'].sort()

    return ret


if __name__ == "__main__":
    import sys, pprint
    pprint.pprint(spider(sys.argv[1]))
