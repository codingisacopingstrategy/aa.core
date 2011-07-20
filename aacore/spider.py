import urllib2, urlparse, lxml, lxml.cssselect, html5lib

def spider (url, levels=1):
    ret = {}

    request = urllib2.Request(url)
    request.add_header("User-Agent", "Mozilla/5.0 (X11; U; Linux x86_64; fr; rv:1.9.1.5) Gecko/20091109 Ubuntu/9.10 (karmic) Firefox/3.5.5")
    f=urllib2.urlopen(request)
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


