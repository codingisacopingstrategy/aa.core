import html5lib, urllib2, lxml

from django.template.defaultfilters import stringfilter
from django import template
import urlparse

register = template.Library()


@register.filter
@stringfilter
def xpath (value, arg):
    """ Takes a url as input value and an xpath as argument.
    Returns a collection of html elements
    usage:
        {{ "http://fr.wikipedia.org/wiki/Antonio_Ferrara"|xpath:"//h2" }}
    """
    def absolutize_refs (baseurl, lxmlnode):
        for elt in lxml.cssselect.CSSSelector("*[src]")(lxmlnode):
            elt.set('src', urlparse.urljoin(baseurl, elt.get("src")))
        return lxmlnode
    request = urllib2.Request(value)
    request.add_header("User-Agent", "Mozilla/5.0 (X11; U; Linux x86_64; fr; rv:1.9.1.5) Gecko/20091109 Ubuntu/9.10 (karmic) Firefox/3.5.5")
    stdin = urllib2.urlopen(request)
    htmlparser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("lxml"), namespaceHTMLElements=False)
    page = htmlparser.parse(stdin)
    p = page.xpath(arg)
    if p:
        return "\n".join([lxml.etree.tostring(absolutize_refs(value, item), encoding='unicode') for item in p])
    else:
        return None
xpath.is_safe = True

@register.filter
@stringfilter
def embed (value, arg):
    """ Takes an audio/video ressource uri as input value and a player type as argument.
    returns html
    usage:
        {{ "http://video.constantvzw.org/AAworkshop/MVI_1675.ogv"|embed:"html5" }}
    """
    if arg is None or arg not in ['html5']:
        arg = html5
    if arg == "html5":
        return """<video width="320" height="240" controls="controls">
        <source src="%s" type="video/ogg" />
        Your browser does not support the video tag.
        </video>""" % value
    else:
        return None
embed.is_safe = True
