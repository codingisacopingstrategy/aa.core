import html5lib, urllib2, lxml
import urlparse, xml.sax.saxutils, urllib, os.path

from django.template.defaultfilters import stringfilter
from django import template
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

from aacore.utils import pagename_for_url
from aacore.mdx import get_markdown, get_simple_markdown
from aacore.html5tidy import tidy
from aacore.models import *


register = template.Library()

@register.filter
@stringfilter
def aamarkdown (value):
    """ 
    markdown with aa extensions
    """
    md = get_markdown()
    return md.convert(value)
aamarkdown.is_safe = True

@register.filter
@stringfilter
def aasimplemarkdown (value):
    """ 
    markdown with aa extensions
    """
    md = get_simple_markdown()
    return md.convert(value)
aamarkdown.is_safe = True

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
        return "\n".join([lxml.etree.tostring(absolutize_refs(value, item), encoding='utf-8') for item in p])
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
    if arg is None or arg not in ['html5', 'html5audio']:
        arg = "html5"
    if arg == "html5":
        return """<video class="player" width="320" height="240" controls="controls" src="%s" type="video/ogg" preload="auto"/>
        Your browser does not support the video tag.
        </video>""" % value
    elif arg == "html5audio":
        return """<audio class="player" controls="controls" src="%s" type="audio/ogg" preload="auto"/>
        Your browser does not support the audio tag.
        </audio>""" % value
    else:
        return None
embed.is_safe = True


#@register.filter
#def crop(uri, size='200w'):
    #""" Takes an image ressource uri as input value and a size as argument
    #returns the url of the new image
    #usage:
        #{{ http://mysite.org/myimage.png | crop }}
    #"""
    #SCALE_WIDTH = 'w'
    #SCALE_HEIGHT = 'h'
    #SCALE_BOTH = 'both'

    #def scale(max_x, pair):
        #x, y = pair
        #new_y = (float(max_x) / x) * y
        #return (int(max_x), int(new_y))

    ## defining the size
    #if (size.lower().endswith('h')):
        #mode = 'h'
        #size = size[:-1]
        #height = int(size.strip())
        #width = ""
    #elif (size.lower().endswith('w')):
        #mode = 'w'
        #size = size[:-1]
        #width = int(size.strip())
        #height = ""
    #else:
        #mode = 'both'
        #size = size.split("x")
        #width = int(size[0].strip())
        #height = int(size[1].strip())
        
    ## defining the filename and the miniature filename
    #filehead, filetail = os.path.split(file.path)
    #basename, format = os.path.splitext(filetail)
    #miniature = basename + '_thumb_' + str(width) + str(height) + format
    #filename = file.path
    #miniature_filename = os.path.join(filehead, miniature)
    #filehead, filetail = os.path.split(file.url)
    #miniature_url = filehead + '/' + miniature

    #if os.path.exists(miniature_filename) and os.path.getmtime(filename)>os.path.getmtime(miniature_filename):
        #os.unlink(miniature_filename)

    ## if the image wasn't already resized, resize it
    #if not os.path.exists(miniature_filename):
        
        ## See http://redskiesatnight.com/2005/04/06/sharpening-using-image-magick/
        ## for unsharpening values
        #if mode == SCALE_HEIGHT:
            #cmd = 'convert %s -resize x%d -unsharp 0.5x0.5+0.75+0.05     %s' % (filename, height, miniature_filename)
        #elif mode == SCALE_WIDTH:
            #cmd = 'convert %s -resize %d -unsharp 0.5x0.5+0.75+0.05 %s' % (filename, width, miniature_filename)
        #elif mode == SCALE_BOTH:
            #cmd = 'convert %s -resize %dx%d -unsharp 0.5x0.5+0.75+0.05 %s' % (filename, width, height, miniature_filename)
        #else:
            #raise Exception("Thumbnail size must be in ##w, ##h, or ##x## format.")
        
        #os.system(cmd)   

    #return miniature_url


@register.filter
@stringfilter
def zoom (value):
    """ Takes a url as input value and an xpath as argument.
    Returns a collection of html elements
    usage:
        {{ "http://upload.wikimedia.org/wikipedia/commons/c/cd/Tympanum_central_mosaic_santa_Maria_del_Fiore_Florence.jpg"|zoom }}
    """
    from django.template.loader import render_to_string
    rendered = render_to_string('aacore/partials/zoom.html', { 'value': value })
    return rendered
    
zoom.is_safe = True

####################
## RDF


@register.filter
def browseurl(uri):
    return reverse('aa-browse') + "?" + urllib.urlencode({'uri': uri})

@register.filter
def rdfbrowselink (node):
    """ filter by aa-resource """
    if node.is_resource():
        uri = str(node.uri)
        return mark_safe('<a href="{0}" title="{2}">{1}</a>'.format(browseurl(uri), compacturl(uri), uri))
    elif node.is_literal():
        literal = node.literal_value.get("string")
#        return literal
        link = reverse('aa-browse') + "?" + urllib.urlencode({'uri': literal})
        return mark_safe('<a href="%s">%s</a>' % (link, literal))
    elif node.is_blank():
#        return "blank"+node.blank_identifier
        link = reverse('aa-browse') + "?" + urllib.urlencode({'uri': "blank:"+node.blank_identifier})
        return mark_safe('<a href="%s">%s</a>' % (link, "blank"+node.blank_identifier))
    else:
        return node

@register.filter
def rdfrellink (node):
    """ filter by aa-resource """
    if node.is_resource():
        uri = str(node.uri)
        link = reverse('aa-browse') + "?" + urllib.urlencode({'uri': uri})
        return mark_safe('<a href="{0}" title="{2}">{1}</a>'.format(link, compacturl(uri), uri))
    elif node.is_literal():
        literal = node.literal_value.get("string")
#        return literal
        link = reverse('aa-browse') + "?" + urllib.urlencode({'uri': literal})
        return mark_safe('<a href="%s">%s</a>' % (link, literal))
    elif node.is_blank():
#        return "blank"+node.blank_identifier
        link = reverse('aa-browse') + "?" + urllib.urlencode({'uri': "blank:"+node.blank_identifier})
        return mark_safe('<a href="%s">%s</a>' % (link, "blank"+node.blank_identifier))
    else:
        return node

@register.filter
def rdfrelnamespace (node):
    """ filter by aa-resource """
    uri = str(node.uri)

@register.filter
def rdfviewslink (node):
    """ filter used in rdfviews.browse (debug) """
    if node.is_resource():
        uri = str(node.uri)
        link = reverse('aa-rdf-browse') + "?" + urllib.urlencode({'uri': uri})
        return mark_safe('<a href="%s">%s</a>' % (link, compacturl(uri)))
    elif node.is_literal():
        literal = node.literal_value.get("string")
#        return literal
        link = reverse('aa-rdf-browse') + "?" + urllib.urlencode({'uri': literal})
        return mark_safe('<a href="%s">%s</a>' % (link, literal))
    elif node.is_blank():
#        return "blank"+node.blank_identifier
        link = reverse('aa-rdf-browse') + "?" + urllib.urlencode({'uri': "blank:"+node.blank_identifier})
        return mark_safe('<a href="%s">%s</a>' % (link, "blank"+node.blank_identifier))
    else:
        return node


@register.filter
@stringfilter
def compacturl (url):
    url = rdfnode(url)
    for ns in Namespace.objects.all():
        if url.startswith(ns.url):
            return ns.name + ":" + url[len(ns.url):]
    return url

@register.filter
@stringfilter
def namespace_for_url (url):
    url = rdfnode(url)
    for ns in Namespace.objects.all():
        if url.startswith(ns.url):
            return ns.name
    return url

@register.filter
@stringfilter
def url_filename (url):
    parts = urlparse.urlparse(url)
    if parts.path:
        d, p = os.path.split(parts.path.rstrip('/'))
        if p:
            return p
        else:
            return d
    else:
        return url

@register.filter
@stringfilter
def url_hostname (url):
    return urlparse.urlparse(url).netloc

@register.filter
@stringfilter
def html5tidy (src):
    return mark_safe(tidy(src, fragment=True))

@register.filter
@stringfilter
def xmlescape (src):
    return xml.sax.saxutils.escape(src)

@register.filter
def rdfnode (n):
    if n == None: return ""
    ret = n
    if type(n) == str or type(n) == unicode: return n
    if n.is_resource():
        ret = str(n.uri)
    elif n.is_literal():
        ret = n.literal_value.get("string")
    return ret

@register.filter
def rel_for_url (url):
    url = unicode(rdfnode(url))
    try:    
        return Relationship.objects.get(url=url)
    except Relationship.DoesNotExist:
        return None

@register.filter
def rel_name_for_url (url):
    rel = rel_for_url(url)
    if rel:
        return rel.name
    else:
        return url
        # (_, ret) = os.path.split(urlparse.urlparse(rel.url).path)

@register.filter
def rel_name_plural_for_url (url):
    rel = rel_for_url(url)
    if rel:
        return rel.name_plural
    else:
        return url
        # (_, ret) = os.path.split(urlparse.urlparse(rel.url).path)

@register.filter
def rdfnodedisplay (node):
    if node.is_resource():
        uri = str(node.uri)
        link = reverse('aacore.views.browse') + "?" + urllib.urlencode({'uri': uri})
        return mark_safe('<a href="%s">%s</a>' % (link, compacturl(uri)))
    elif node.is_literal():
        return node.literal_value.get("string")
    elif node.is_blank():
        return "blank" + node.blank_identifier
    else:
        return node

# ok this is a bit crappy here...
pageurlbase = "http://"+Site.objects.get_current().domain + "/pages/"

@register.filter
def rdfnode_fix_pagenames (url):
    url = rdfnode(url)
    if url.startswith(pageurlbase):
        return pagename_for_url(url)
    else:
        return url

import datetime

@register.filter
def iso8601_date (date):
    if type(date) == datetime.datetime:
        return "{0:04d}-{1:02d}-{2:02d}".format(date.year, date.month, date.day)
    else:
        return date

def page_list():
    """
    Returns an unordered list of all the wiki pages
    Usage:
        {% page_list %}
    """
    return {
        'page_list': aacore.models.Page.objects.all(),
    }
register.inclusion_tag('aacore/partials/page_list.html')(page_list)
