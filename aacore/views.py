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
from django.template.loader import get_template 
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from aacore.spider import spider
from plugins import sniffer
from models import *
from rdfutils import *
from utils import *
from mdx_fenced_style import FencedStyleExtension 


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
    except Page.DoesNotExist:
        # Redirects to the edit page
        url = reverse('aa-page-edit', kwargs={'slug':slug})
        return redirect(url) 

    context['page'] = page
    myext = FencedStyleExtension()  # Adds a markup to wrap content with a div of a given class
    md = markdown.Markdown(extensions=['extra', 'meta', myext])

    sections = []  # Collects all the rendered sections

    i = 0
    for (url, header, lines) in parse_header_sections(page.content.splitlines()):
        # Puts back the header with the rest of the section content
        if header:
            lines.insert(0, header)

        # Renders every times section
        timed_sections = []

        j = 0
        for (timecode, lines) in parse_timed_sections(lines):
            t = Template("{% load filters aatags %}" + "\n".join(lines))
            c = Context({})
            rendered = mark_safe(md.convert(t.render(c)))

            if timecode:
                # TODO: markup timecode
                t = get_template('aacore/partials/timed_section.html')
                c = Context({
                    'timecode': timecode,
                    'markdown': timecode + "\n" + "\n".join(lines),
                    'rendered': rendered,
                })
                timed_sections.append(t.render(c))
            else:
                timed_sections.append(rendered)

            j += 1

        print(timed_sections)

        # Renders the section content (determined by h1 headers)
        # Only articles, not source code form
        # 1. render django template tags
        # 2. converts to markdown
        # 3. mark_safe for next inclusion
        # 4. keeps rendered section in var rendered

        # This is a trick to use of django filter in the pages
        t = Template("{% load filters aatags %}" + "\n".join(lines))
        c = Context({})
        rendered = mark_safe(md.convert(t.render(c)))

        # Adds URL to reconstruct the source
        if url:
            lines.insert(0, url)

        if lines and header:  # Avoids empty annotation boxes
            # Renders the annotation box
            t = get_template('aacore/partials/annotation.html')
            c = Context({
                'rendered': mark_safe("\n".join(timed_sections)),
                'target': url,
                'post_url': reverse('aa-page-edit-section', kwargs={'slug': slug, 'id': i}),
                'source': "\n".join(lines)
            })
            annotation = t.render(c)

            i += 1

            sections.append(annotation)
        else:
            sections.append(rendered)


    context['content'] = mark_safe("".join(sections))
    return render_to_response("aacore/page.html", context, context_instance=RequestContext(request))

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

def page_edit_section (request, slug, id):
    """
    Annotation edition view

    template
        :template:`aacore/edit.html`
    """
    name = dewikify(slug)
    page = Page.objects.get(name=name)
    if request.method == "POST":
        content = request.POST.get('content', '')
        i = 0
        new_content = []
        for (url, header, lines) in parse_header_sections(page.content.splitlines()):
            if int(id) == i:
                new_content.append(content)
            else:
                if header:
                    lines.insert(0, header)
                if url:
                    lines.insert(0, url)
                new_content.append("\n".join(lines))
            i += 1
        page.content = "\n".join(new_content)
        page.save()
    return HttpResponse("ok")
    #url = reverse('aa-page-detail', kwargs={'slug': slug})
    #return redirect(url)


    #context = {}
    #name = dewikify(slug)
    #try:
        #page = Page.objects.get(name=name)
        #context['page'] = page
        #context['content'] = page.content
        #context['id'] = page._id
    #except Page.DoesNotExist:
        #page = None
    #if request.method == "POST":
        #content = request.POST.get('content', '')
        #if page:
            #if content == "delete":
                #page.delete()
            #else:
                #page.content = content 
                #page.save()
        #else:
            #if content == "delete":
                #pass
            #else:
                #page = Page(content=content, name=name)
                #page.save()
        #url = reverse('aa-page-detail', kwargs={'slug':slug})
        #return redirect(url)
    #return render_to_response("aacore/edit.html", context, context_instance=RequestContext(request))

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

