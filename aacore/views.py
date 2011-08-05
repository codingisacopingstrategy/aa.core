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


import html5lib, lxml, lxml.cssselect, RDF, re, urllib2, urlparse, markdown

from django.shortcuts import (render_to_response, get_object_or_404, redirect)
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, Template, Context
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from aacore.spider import spider
from plugins import sniffer
from models import *
from rdfutils import *
from utils import *


def page_list (request):
    """
    A listing of All Pages (like MediaWiki Special:AllPages)
    """
    context = {}
    return render_to_response("aacore/page_list.html", context, context_instance=RequestContext(request))

def page_detail (request, slug):
    """
    Displays a wiki page :model:`aacore.Page`.

    **Context**

    ``RequestContext``
        Request context

    ``page``
        An instance of :model:`aacore.Page`.

    **Template:**

    :template:`aacore/page.html`
    """
    context = {}
    name = dewikify(slug)
    try:
        page = Page.objects.get(name=name)
        context['page'] = page

        p = re.compile(r'(^# .*?)(?=^# )', re.MULTILINE|re.DOTALL)
        md_sections = p.split(page.content)
        
        html_sections = []

        for md_section in md_sections:
            if len(md_section) != 0:  # Avoids empty annotation boxes
                # This is a trick to use of django filter in the pages
                t = Template("{% load filters aatags %}" + md_section)
                c = Context({})
                md = markdown.Markdown(extensions=['extra', 'meta'])
                #html_section.append(md.convert(t.render(c)))
                fragment = """
                <div class="section">
                    <a class="edit" href="#">edit</a>
                    <div class="source">
                        <p>
                        <textarea>%s</textarea>
                        </p>
                        <p>
                        <button class="cancel">Cancel</button>
                        <button class="save">Save</button>
                        </p>
                    </div>
                    <div class="rendered">%s</div>
                </div>
                """ % (md_section, md.convert(t.render(c)))
                html_sections.append(fragment)

        # Wraps h2 sections
        #import wrap
        #import lxml.etree
        #doc = wrap.parser.parse(html)
        #wrap.treeSectionalize(doc, startLevel=1, stopLevel=2)
        #content = lxml.etree.tostring(doc, pretty_print=True, encoding="UTF-8", method="html")

        context['content'] = mark_safe("".join(html_sections))
        return render_to_response("aacore/page.html", context, context_instance=RequestContext(request))
    except Page.DoesNotExist:
        # Redirects to the edit page
        url = reverse('aa-page-edit', kwargs={'slug':slug})
        return redirect(url)

def page_edit (request, slug):
    """
    Page edition view

    template
        :template:`aacore/edit.html`
    """
    context = {}
    name = dewikify(slug)
    try:
        page = Page.objects.get(name=name)
        context['page'] = page
        context['content'] = page.content
    except Page.DoesNotExist:
        page = None
    if request.method == "POST":
        content = request.POST.get('content', '')
        if page:
            if content == "delete":
                page.delete()
            else:
                page.content = content 
                page.save()
        else:
            if content == "delete":
                pass
            else:
                page = Page(content=content, name=name)
                page.save()
        url = reverse('aa-page-detail', kwargs={'slug':slug})
        return redirect(url)
    return render_to_response("aacore/edit.html", context, context_instance=RequestContext(request))

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
    return render_to_response("aacore/sniff.html", context, context_instance=RequestContext(request))

##### RDF VIEWS #################
def rdfdump (request):
    """ debug view to see the contents of the RDF store (in turtle/text format) """
    model = get_model()
    ser = RDF.Serializer(name="turtle")
    return HttpResponse(ser.serialize_model_to_string(model), mimetype="text/plain")

def sandbox (request):
    """
    Sample page to test wikitext / embed processing. Unlike a real wiki
    sandbox, this page is always ephemeral (nothing is saved)
    Options: 
    This view does not alter the database / create new resources (?)
    """
    context = {}
    text = request.REQUEST.get("text", "")
    context['text'] = text

    if text:
        # This is a trick to use of django filter in the pages
        t = Template("{% load aatags %}{% load filters %}\n" + text)
        c = Context({})
        context['result'] = t.render(c)

    return render_to_response("aacore/sandbox.html", context, context_instance=RequestContext(request))

def _import (request):
    """
    Import view
    """
    context = {}

    url = request.REQUEST.get("url", "")
    context['url'] = url

    if url:
        context['spider'] = spider(url)

    if request.method == "POST":
        submit = request.REQUEST.get("_submit")
        if submit == "import":
            for importurl in request.REQUEST.getlist("importurl"):
                (res, created) = Resource.objects.get_or_create(url=importurl)
            return HttpResponse ("ok")
            
    return render_to_response("aacore/import.html", context, context_instance=RequestContext(request))

