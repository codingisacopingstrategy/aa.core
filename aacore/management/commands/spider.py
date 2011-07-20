from django.core.management.base import BaseCommand, CommandError
import urllib, urllib2, urlparse, html5lib, lxml, lxml.cssselect
from django.core.urlresolvers import reverse
import aacore
from settings import SITE_BASE_URL

class Command(BaseCommand):
    args = '<url ...>'
    help = 'url(s) to spider'

    def handle(self, *args, **options):
        links = {}
        for url in args:
            request = urllib2.Request(url)
            request.add_header("User-Agent", "Mozilla/5.0 (X11; U; Linux x86_64; fr; rv:1.9.1.5) Gecko/20091109 Ubuntu/9.10 (karmic) Firefox/3.5.5")
            f=urllib2.urlopen(request)
            parser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("lxml"), namespaceHTMLElements=False)
            page = parser.parse(f)
            for elt in lxml.cssselect.CSSSelector('a[href]')(page):
                href = urlparse.urljoin(f.geturl(), elt.attrib['href'])
                if href.split(':')[0] == 'http':
                    if not href in links:
                        links[href] = True
        links = links.keys()
        links.sort()

        for link in links:
            sniffurl = reverse("aacore.views.sniff", args=[]) + "?" + urllib.urlencode({"url": link})
            print link
            sniffurl = SITE_BASE_URL + sniffurl
            aacore.rdfutils.put_url(sniffurl)

