import urlparse
import xml.sax.saxutils
import urllib
import os.path
import datetime
from django.template.defaultfilters import stringfilter
from django import template
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from aacore.html5tidy import tidy
from aacore.models import Namespace



register = template.Library()

####################
## RDF


@register.filter
def browseurl(uri):
    """
    Reverses the browse url of a resource or a litteral.
    """
    return reverse('aa-browse') + "?" + urllib.urlencode({'uri': uri})


@register.filter
def rdfbrowselink (node):
    """ filter by aa-resource """
    if node.is_resource():
        uri = str(node.uri)
        return mark_safe('<a href="%s" title="%s">%s</a>' % (browseurl(uri), uri, compacturl(uri)))
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
        return mark_safe('<a href="%s" title="%s">%s</a>' % (link, uri, compacturl(uri)))
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
    return str(node.uri)


@register.filter
def rdfviewslink (node):
    """ filter used in aacore.views.browse (debug) """
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
    """
    Returns the hostname of the given URL

    Usage format::

        <dl>
            <dt>Host name</dt>
            <dd property="http:hostname">{{ resource.url|url_hostname }}</dd>
        </dl>
    """
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
#pageurlbase = "http://"+Site.objects.get_current().domain + "/pages/"


#@register.filter
#def rdfnode_fix_pagenames (url):
    #url = rdfnode(url)
    #if url.startswith(pageurlbase):
        #return pagename_for_url(url)
    #else:
        #return url

@register.filter
def iso8601_date (date):
    """
    Renders the given datetime object to its iso8601 representations
    """
    if type(date) == datetime.datetime:
        return "%04d-%02d-%02d" % (date.year, date.month, date.day)
    else:
        return date

