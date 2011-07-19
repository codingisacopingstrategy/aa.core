# This file is part of Active Archives.
# Copyright 2006-2011 the Active Archives contributors (see AUTHORS)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Also add information on how to contact you by electronic and paper mail.

import django
from models import *
from utils import *

# from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, Http404, HttpResponseForbidden, HttpResponseNotAllowed

def page_list(request):
    """ A listing of All Pages (like MediaWiki Special:AllPages) """
    context = {}
    return django.shortcuts.render_to_response("aacore/page_list.html", context, context_instance = django.template.RequestContext(request))

def page_detail (request, slug):
    """ Main view of a page """
    context = {}
    name = dewikify(slug)
    page = django.shortcuts.get_object_or_404(Page, name=name)
    return django.shortcuts.render_to_response("aacore/page.html", context, context_instance = django.template.RequestContext(request))

import sniffer

def sniff (request):
    """
    Main URL sniffer view, collects all annotations from the sniffer plugins and displays them in a single page.
    Options: 'url' parameter
    Sniffing only displays information, it should not alter the database / create new resources
    """
    context = {}
    url = request.REQUEST.get('url', '')
    if url:
        data, annotations = sniffer.sniff(url)
        context['original_url'] = url
        context['data'] = data
        context['annotations'] = annotations    
        context['url'] = data.url
    return django.shortcuts.render_to_response("aacore/sniff.html", context, context_instance = django.template.RequestContext(request))

##### RDF VIEWS #################
import RDF
from rdfutils import *

def rdfdump (request):
    """ debug view to see the contents of the RDF store (in turtle/text format) """
    model = get_model()
    ser = RDF.Serializer(name="turtle")
    return django.http.HttpResponse(ser.serialize_model_to_string(model), mimetype="text/plain")

##### PIPELINE PROCESSING #########

# """ {{ http://www.jabberwocky.com/carroll/walrus.html | htmlcrop /html/body/p[2] }} """
import re, html5lib, lxml, urllib2, lxml.cssselect, urlparse

def pipeline_url (stdin, url):
    request = urllib2.Request(url)
    request.add_header("User-Agent", "Mozilla/5.0 (X11; U; Linux x86_64; fr; rv:1.9.1.5) Gecko/20091109 Ubuntu/9.10 (karmic) Firefox/3.5.5")
    return urllib2.urlopen(request)

def pipeline_xpath (stdin, xpath, url=None): 
    htmlparser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("lxml"), namespaceHTMLElements=False)
    page = htmlparser.parse(stdin)
    p = page.xpath(xpath)
    if p:
        return "\n".join([lxml.etree.tostring(absolutize_refs(url, item), encoding='unicode') for item in p])
#        if url:
#            return "\n".join([lxml.etree.tostring(absolutize_refs(url, item), encoding='unicode') for item in p])
#        else:
#            return "\n".join([lxml.etree.tostring(item, encoding='unicode') for item in p])
##        
#        p = p[0]
#        if url:
#            absolutize_refs(url, p)
#        return lxml.etree.tostring(p, encoding='unicode')
        # return "".join([t for t in p.itertext()])

def absolutize_refs (baseurl, lxmlnode):
    for elt in lxml.cssselect.CSSSelector("*[src]")(lxmlnode):
        elt.set('src', urlparse.urljoin(baseurl, elt.get("src")))
    return lxmlnode

def sandbox (request):
    """
    Sample page to test wikitext / embed processing. Unlike a real wiki sandbox, this page is always ephemeral (nothing is saved)
    Options: 
    This view does not alter the database / create new resources (?)
    """
    context = {}
    text = request.REQUEST.get("text", "")
    context['text'] = text

    if text:
        url = None
        def pipeline_process(content, part):
            global url
            if part.startswith("http"):
                url = part.strip()
                return pipeline_url(content, url)
            elif part.startswith ("xpath"):
                (cmd, xpath) = part.split(" ", 1)
                xpath = xpath.strip()
                return pipeline_xpath(content, xpath, url=url)

        def sub(m):
            d = m.groupdict()
            parts = d.get("content", "").strip().split("|")
            parts = [x.strip() for x in parts]
            content = ""
            for part in parts:
                content = pipeline_process(content, part)
            return content

        embed_pat = re.compile(r"\{\{(?P<content>.+)\}\}", re.I)
        context['result'] = embed_pat.sub(sub, text)

    return django.shortcuts.render_to_response("aacore/sandbox.html", context, context_instance = django.template.RequestContext(request))


