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
try: import simplejson as json
except ImportError: import json

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
from mdx_aa import get_aa_markdown
from mdx_fenced_style import FencedStyleExtension 
from mdx_timecodes import TimeCodesExtension


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
    md = get_aa_markdown()
    rendered = md.convert(page.content)
    t = Template("{% load filters aatags %}" + rendered)
    c = Context({})
    context['content'] = mark_safe(t.render(c))

    # Extracts the geometry information from markdown metadata geometry key
    #md.convert(page.content)


    ## Geometry entry pattern, eg. "#myheader 300 400 50 50"
    #GEOMETRY_RE = r'(?P<id>-?[_a-zA-Z]+[_a-zA-Z0-9-]*)\s(?P<width>\d+)\s(?P<height>\d+)\s(?P<top>\d+)\s(?P<left>\d+)'

    #try:
        ## Adds the geometry info to the context dictionnary so we can relayout using javascript.  
        #values = {}
        #for i in md.Meta['geometry']:
            ##tokens = i.split()
            ##values["#" + str(tokens[0])] = map(lambda x: int(x), tokens[1:])

            ## Makes sure the entry is properly formatted
            #m = re.search(GEOMETRY_RE, i)

            #if m:
                #d = m.groupdict()
                #values['#' + d['id']] = {
                    #'width': d['width'],
                    #'height': d['height'],
                    #'top': d['top'],
                    #'left': d['left'],
                #}
        #context['geometry'] = json.dumps(values)
    #except (KeyError, AttributeError):
        #pass

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

def page_edit_geometry (request, slug):
    """
    A view to set/update information about the geometry of a page annotation.
    Persistance is done in the markdown source itself thanks to the metadata
    information, so no database is involded.

    method
        :POST
    data
        :_id <str> eg. "#my_header"
        :width <str> eg. "200"
        :height <str> eg. "300"
        :top <str> eg. "50"
        :left <str> eg. "500"
        
        to be implemented:
        :z-index <str> eg.  "1078"
    """
    context = {}
    name = dewikify(slug)
    page = Page.objects.get(name=name)

    if request.method == "POST":
        # Parses the content of the page
        myext = FencedStyleExtension()  # Adds a markup to wrap content with a div of a given class
        md = markdown.Markdown(extensions=['extra', 'meta', myext])
        md.convert(page.content)

        new_content = ""  #

        # Retrieves POST data
        _id = request.POST.get('id', '')
        width = request.POST.get('width', '0')
        height = request.POST.get('height', 0)
        top = request.POST.get('top', 0)
        left = request.POST.get('left', 0)

        try:
            match = None
            # Updates the geometry key if older information about the element is present
            for i in xrange(len(md.Meta['geometry'])):
                if md.Meta['geometry'][i].split()[0] == _id:
                    md.Meta['geometry'][i] = "%s %s %s %s %s" % (_id, width, height, top, left)
                    match = True

            # Appends the element geometry information if it wasn't there yet
            if not match:
                md.Meta['geometry'].append("%s %s %s %s %s" % (_id, width, height, top, left))
        except KeyError:  # md.Meta['geometry'] doesn't exist yet
            md.Meta['geometry'] = []
            md.Meta['geometry'].append("%s %s %s %s %s" % (_id, width, height, top, left))

        # Rebuilds the markdown source with new the updated metadata
        for i in md.Meta:
            new_content += i + ": " + "\n    ".join(md.Meta[i]) + "\n"
        new_content += "\n\n" + "\n".join(md.lines)
        page.content = new_content
        page.save()

        # Geometry entry pattern, eg. "#myheader 300 400 50 50"
        GEOMETRY_RE = r'(?P<id>-?[_a-zA-Z]+[_a-zA-Z0-9-]*)\s(?P<width>\d+)\s(?P<height>\d+)\s(?P<top>\d+)\s(?P<left>\d+)'

        try:
            # Adds the geometry info to the context dictionnary so we can relayout using javascript.  
            values = {}
            for i in md.Meta['geometry']:
                #tokens = i.split()
                #values["#" + str(tokens[0])] = map(lambda x: int(x), tokens[1:])

                # Makes sure the entry is properly formatted
                m = re.search(GEOMETRY_RE, i)

                if m:
                    d = m.groupdict()
                    values['#' + d['id']] = {
                        'width': d['width'],
                        'height': d['height'],
                        'top': d['top'],
                        'left': d['left'],
                    }
            context['geometry'] = json.dumps(values)
            return HttpResponse(json.dumps(values))
        except KeyError:
            pass

        return HttpResponse("ok")
    return HttpResponse("not ok")

def page_edit_section (request, slug, id):
    """
    Annotation edition view

    template
        :template:`aacore/edit.html`
    """
    name = dewikify(slug)
    page = Page.objects.get(name=name)

    myext = FencedStyleExtension()  # Adds a markup to wrap content with a div of a given class
    md = markdown.Markdown(extensions=['extra', 'meta', myext])
    md.convert(page.content)

    if request.method == "POST":
        content = request.POST.get('content', '')
        new_content = []

        for i in md.Meta:
            new_content.append(i + ": " + "\n    ".join(md.Meta[i]) + "\n")
        new_content += "\n\n"

        i = 0
        for (url, header, lines) in parse_header_sections(md.lines):
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

        ### 
        sections = []  # Collects all the rendered sections

        i = 0
        for (url, header, lines) in parse_header_sections(content.splitlines()):
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

        # Finally joins every section/annotation
        return HttpResponse(mark_safe("".join(sections)))


    return HttpResponse("ok")

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

