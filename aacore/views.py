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


import RDF

from django.shortcuts import (render_to_response, redirect)
from django.http import HttpResponse
from django.template import (RequestContext, Template, Context)
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from aacore.spider import spider
from plugins import sniffer
from models import *
from rdfutils import get_model
from utils import (dewikify, convert_line_endings)
from mdx import get_markdown
from mdx.mdx_sectionedit import (sectionalize, sectionalize_replace)
from forms import PageEditForm


def page_detail(request, slug):
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
        url = reverse('aa-page-edit', kwargs={'slug': slug})
        return redirect(url)

    context['page'] = page
    md = get_markdown()
    rendered = md.convert(page.content)
    t = Template("{% load filters aatags %}" + rendered)
    c = RequestContext(request)
    if 'css' in md.Meta:
        context['extra_css'] = md.Meta['css']
    context['content'] = mark_safe(t.render(c))

    return render_to_response("aacore/page.html", context, context_instance=RequestContext(request))


def page_edit(request, slug):
    """
    Page edition view

    template
        :template:`aacore/edit.html`
    """
    context = {}
    name = dewikify(slug)

    section = int(request.REQUEST.get('section', 0))
    is_ajax = request.REQUEST.get('type') == 'ajax'

    try:
        page = Page.objects.get(name=name)
    except Page.DoesNotExist:
        page = None

    # Gets the edit form
    if request.method == "GET":
        if page:
            # Gets the whole content or just a section
            if section:
                sections = sectionalize(page.content)
                sectiondict = sections[section - 1]
                context['content'] = sectiondict['header'] + sectiondict['body']
                context['section'] = section
            else:
                context['content'] = page.content

            # Returns plain content in case of ajax editing 
            if is_ajax:
                return HttpResponse(context['content'])
            else:
                context['page'] = page  # So templates nows about what page we are editing
                context['form'] = PageEditForm(initial={"content": context['content']})
        else:
            context['name'] = name  # So templates nows about what page we are editing
            context['form'] = PageEditForm(initial={"content": '# My first section'})
        
        return render_to_response("aacore/edit.html", context, \
                context_instance=RequestContext(request))

    # Posts the edit form
    elif request.method == "POST":
        #import pdb; pdb.set_trace()

        is_cancelled = request.POST.get('cancel', None)
        if is_cancelled:
            print('is_cancelled')
            url = reverse('aa-page-detail', kwargs={'slug': slug})
            return redirect(url)

        form = PageEditForm(request.POST)

        if form.is_valid():  # Processes the content of the form
            # Retrieves and cleans the form values
            content = form.cleaned_data["content"]
            content = convert_line_endings(content, 0)  # Normalizes EOL
            message = form.cleaned_data["message"] or "<no messages>"
            is_minor = form.cleaned_data["is_minor"]
            author = "Anonymous <anonymous@%s>" % request.META['REMOTE_ADDR']

            if page:
                if section:  # section edit
                    page.content = sectionalize_replace(page.content, (section - 1), content)
                    page.commit(message=message, author=author, is_minor=is_minor)
                else:
                    if content == "delete":
                        page.delete()
                    else:
                        page.content = content
                        page.commit(message=message, author=author, is_minor=is_minor)
            else:
                if content == "delete":
                    pass
                else:
                    page = Page(content=content, name=name)
                    page.commit(message=message, author=author, is_minor=is_minor)

            if is_ajax:
                md = get_markdown()
                rendered = md.convert(content)
                t = Template("{% load filters aatags %}" + rendered)
                c = RequestContext(request)
                return HttpResponse(mark_safe(t.render(c)))

        else:  # Returns the invalid form for correction
            # TODO: factorize this chunk
            context['page'] = page  # So templates nows about what page we are editing
            context['name'] = name  # So templates nows about what page we are editing
            context['form'] = form
            return render_to_response("aacore/edit.html", context, \
                    context_instance=RequestContext(request))

        url = reverse('aa-page-detail', kwargs={'slug': slug})
        return redirect(url)


def page_history(request, slug): 
    """ """ 
    context = {} 
    name = dewikify(slug)

    try: 
        page = Page.objects.get(name=name) 
    except Page.DoesNotExist:
        # Redirects to the edit page
        url = reverse('aa-page-edit', kwargs={'slug': slug}) 
        return redirect(url)

    context['page'] = page

    return render_to_response("aacore/history.html", context,
            context_instance=RequestContext(request))


def page_diff(request, slug): 
    """Shows a single wiki page."""
    # Does the repo exist?
    context = {} 
    name = dewikify(slug)

    if request.method == "GET": # If the form has been submitted...
        try: 
            page = Page.objects.get(name=name)
        except Page.DoesNotExist:
            # Redirects to the edit page
            url = reverse('aa-page-edit', kwargs={'slug': slug}) 
            return redirect(url)

        context['page'] = page

        c1 = request.GET.get("c1", None)
        c2 = request.GET.get("c2", None)
        
        #if c1 is None or c2 is None:
            #raise Http404

        context['content'] = page.diff(c1, c2)

    return render_to_response("aacore/diff.html", context,
            context_instance=RequestContext(request))


def sniff(request):
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


def rdfdump(request):
    """ debug view to see the contents of the RDF store (in turtle/text format) """
    model = get_model()
    ser = RDF.Serializer(name="turtle")
    return HttpResponse(ser.serialize_model_to_string(model), mimetype="text/plain")


def sandbox(request):
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


def _import(request):
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
            return HttpResponse("ok")

    return render_to_response("aacore/import.html", context, context_instance=RequestContext(request))
