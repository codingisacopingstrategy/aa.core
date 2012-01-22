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


import urllib
import urlparse, html5lib, urllib2, lxml.cssselect

try: import simplejson as json
except ImportError: import json

from django.shortcuts import (render_to_response, redirect, get_object_or_404)
from django.http import (HttpResponse, HttpResponseRedirect)
from django.template import RequestContext 
from django.template.loader import (render_to_string, get_template)
from django.core.urlresolvers import reverse
from django.conf import settings as projsettings
from django.contrib.auth.decorators import login_required

from aacore.filters import *
from aacore.models import *
from aacore.utils import (get_rdf_model, full_site_url, dewikify,
                          convert_line_endings, add_resource, is_local_url)
from mdx import get_markdown
from mdx.mdx_sectionedit import (sectionalize, sectionalize_replace)
import rdfutils
from forms import (PageEditForm, AnnotationImportForm)
from audacity import audacity_to_srt
import re
from aacore.mdx.mdx_sectionedit import (TIMECODE_HEADER, spliterator)
from timecode import timecode_tosecs
import lxml.cssselect


def index (request):
    """ The 'index' view redirects to the Index page view """
    url = reverse("aa-page-detail", args=["Index"])
    return HttpResponseRedirect(url)

#### RDFSource
def rdf_delegate(request, id):
    """
    RDF Delegate view
    """
    context = {}
    source = get_object_or_404(RDFSource, pk=id)
    context['source'] = source
    return render_to_response("aacore/rdf_source.html", context, context_instance=RequestContext(request))

def colors_css (request):
    """
    Generates a stylesheet with the namespace colors
    """
    context = {}
    context['namespaces'] = Namespace.objects.all()
    return render_to_response("aacore/colors.css", context, context_instance=RequestContext(request), mimetype="text/css")

def resources (request):
    """
    Temporary view to dump a list of all the resources and links to browser view.
    """
    context = {}
    context['resources'] = Resource.objects.all()
    return render_to_response("aacore/resources.html", context, context_instance = RequestContext(request))

def embed (request):
    """
    Receives a request with parameters URL and filter.
    Returns a JSON containing content of the embed.
    """
    url = request.REQUEST.get("url")
    # ALLOW (authorized users) to trigger a resource to be added...
    model = get_rdf_model()
    if url.startswith("http://"):
        # TODO: REQUIRE LOGIN TO ACTUALLY ADD...
        add_resource(url, model, request)

    ### APPLY FILTERS (if any)
    pipeline = request.REQUEST.get("filter", "embed").strip()
    filters = {}

    for filter_ in AAFilter.__subclasses__():
        filters[filter_.name] = filter_

    stdin = {
        'original_url': url,
        'local_url': Resource.objects.get(url=url).get_local_url(),
        'local_path': Resource.objects.get(url=url).get_local_file(),
        'output': 'None',
        'extra_css': [],
        'extra_js': [],
        'script': "",
    }

    for command in [x.strip() for x in pipeline.split("|")]:
        if ":" in command:
            (filter_, arguments) = command.split(":", 1)
            filter_.strip()
            command.strip()
        else:
            (filter_, arguments) = (command.strip(), None)
        try:
            stdin = filters[filter_](arguments, stdin).stdout
        except KeyError:
            stdin['output'] = """The "%s" filter doesn't exist""" % filter_
            break
    
    browseurl = reverse("aa-browse") + "?" + urllib.urlencode({'uri': url})
    ret = """
<div class="aa_embed">
    <div class="links">
        <a class="directlink" href="%(url)s">URL</a>
        <a class="browselink" target="browser" href="%(browseurl)s">browse</a>
    </div>
    <div class="body">%(embed)s</div>
</div>""".strip()

    content = ret % {'url': url, 'browseurl': browseurl, 'embed': stdin['output']}
    return HttpResponse(json.dumps({"ok": True, "content": content, 'extra_css': stdin['extra_css'], 
                        'extra_js': stdin['extra_js'], 'script': stdin['script']}), 
                        mimetype="application/json");


def browse (request):
    """ Main "browser" view """

    model = get_rdf_model()  # Open the RDF Store (the 4 redland databases)
    uri = request.REQUEST.get("uri", "")

    # Avoids browsing an internal URL
    if is_local_url(uri):
        return HttpResponseRedirect(uri)

    submit = request.REQUEST.get("_submit", "")

    if submit == "reload":
        add_resource(uri, model, request, reload=True)
    else:
        # force every (http) resource to be added
        if uri.startswith("http"):
            # TODO: REQUIRE LOGIN TO ACTUALLY ADD...
            add_resource(uri, model, request)

    # RDF distinguishes URI and literals...
    literal = None
    if not uri.startswith("http:"):
        literal = uri

    context = {}
    context['namespaces'] = Namespace.objects.all()
    context['uri'] = uri
    context['literal'] = literal

    if literal:
        node_stats, links_out, links_in, as_rel = rdfutils.load_links(model, context, literal=uri)
    else:
        node_stats, links_out, links_in, as_rel = rdfutils.load_links(model, context, uri=uri)

    context['node_stats'] = node_stats
    context['links_out'] = links_out
    context['links_in'] = links_in
    context['links_as_rel'] = as_rel

    if not literal:
        try:
            resource = Resource.objects.get(url=uri)
            context['resource'] = resource
        except Resource.DoesNotExist:
            pass

    return render_to_response("aacore/browse.html", context, context_instance = RequestContext(request))

####################################
### Resource Main Sniff Page (http)

def resource_sniff (request, id):
    """
    This is the generic sniff view for Resources,
    it provides the basic resource data (from HTTP, etc) data as RDFa for indexing
    """
    context = {}
    context['namespaces'] = Namespace.objects.all()
    context['resource'] = get_object_or_404(Resource, pk=id)
    return render_to_response("aacore/resource_sniff.html", context, context_instance = RequestContext(request))


############################################################
# WIKI

@login_required
def annotation_import(request, slug, section):
    """
    Saves the file directly from the request object.
    Disclaimer:  This is code is just an example, and should
    not be used on a real website.  It does not validate
    file uploaded:  it could be used to execute an
    arbitrary script on the server.
    """
    context = {}
    name = dewikify(slug)
    page = Page.objects.get(name=name)

    if request.method == 'POST':
        form = AnnotationImportForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            data = ""
            for chunk in f.chunks():
                data += chunk

            srt = unicode(audacity_to_srt(data).decode('utf-8'))

            # Preserves the old header, because audacity only keeps timed section.
            # TODO: decide wether it should be handled here or in sectionalize_replace
            section = int(section)
            header = sectionalize(page.content)[section]['header'] + "\n\n"

            context = {'content': header + srt, 'section': section, 'page': page}
            return render_to_response("aacore/annotation_import_confirm.html", context, 
                                      context_instance=RequestContext(request))
    else:
        form = AnnotationImportForm()
        context['form'] = form
        return render_to_response("aacore/annotation_import.html", context, 
                                  context_instance=RequestContext(request))


def annotation_export(request, slug, section, _format="audacity",
                      force_endtime=False):
    context = {}
    name = dewikify(slug)
    page = Page.objects.get(name=name)

    section = sectionalize(page.content)[int(section)]
    pattern = re.compile(TIMECODE_HEADER, re.I | re.M | re.X)

    stack = []
    for t in spliterator(pattern, section['header'] + section['body'], 
                         returnLeading=0):
        m = pattern.match(t[0]).groupdict()

        if force_endtime:
            if len(stack) and stack[-1]['end'] == '':
                stack[-1]['end'] = timecode_tosecs(m['start'])
            end = timecode_tosecs(m['end']) or ''
        else:
            end = timecode_tosecs(m['end']) or timecode_tosecs(m['start'])

        stack.append({
            'start': timecode_tosecs(m['start']),
            'end': end,
            'body': t[1].strip('\n'),
        })

    context = {'sections': stack}

    return render_to_response("aacore/annotation_export.audacity", context, 
                              context_instance=RequestContext(request), 
                              mimetype="text/plain;charset=utf-8")


def page_detail(request, slug):
    """
    Displays a :model:`aacore.Page`.

    **Context**

    ``RequestContext``
        Request context
    ``page``
        An instance of :model:`aacore.Page`.
    ``namespaces``
        An list of all the instances of :model:`aacore.Namespace`.

    **Template:**

    :template:`aacore/page_detail.html`

    """
    context = RequestContext(request)
    context['namespaces'] = Namespace.objects.all()
    name = dewikify(slug)

    try:
        page = Page.objects.get(name=name)
    except Page.DoesNotExist:
        # Redirects to the edit page
        url = reverse('aa-page-edit', kwargs={'slug': slug})
        return redirect(url)

    revision = request.REQUEST.get('rev')
    if revision:
        content = page.read(revision)
    else:
        content = page.content

    context['page'] = page
    context['content'] = content

    t = get_template('aacore/page_detail.html')

    response = HttpResponse(t.render(context))

    # Forces the page to reload
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Expires'] = '-1'
    response['Pragma'] = 'no-cache'

    return response

    # TODO: Markdown extension for stylesheet embed

    #return render_to_response("aacore/page_detail.html", context)


@login_required
def page_flag(request, slug):
    """
    Flags the last commit the edit of a :model:`aacore.Page` as a major one

    Returns "OK"
    """
    name = dewikify(slug)
    page = Page.objects.get(name=name)
    message = request.REQUEST.get('message', None)
    page.commit(amend=True, message=message)
    return HttpResponse("Seems like it worked!")


@login_required
def page_edit(request, slug):
    """
    Displays the edit form for :model:`aacore.Page`

    **methods**
    ``GET``
        Either the edit form, OR provides Markdown source via AJAX call
    ``POST``
        Receives/commits edits on POST (either via form or AJAX)

    **parameters**
    ``section``
        Optional. Limits the scope of edition to the given section.

    **template**
        :template:`aacore/page_edit.html`
    """
    context = {}
    name = dewikify(slug)

    section = int(request.REQUEST.get('section', 0))
    is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

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
                sectiondict = sections[section]
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
            rendered = render_to_string("aacore/partials/initial_page_content.md", context)
            context['form'] = PageEditForm(initial={"content": rendered, "message": '/* Created a new page "%s" */' % name, })
        
        return render_to_response("aacore/page_edit.html", context, \
                context_instance=RequestContext(request))

    elif request.method == "POST":
        content = request.POST.get('content', '')
        content = convert_line_endings(content, 0)  # Normalizes EOL
        content = content.strip() + "\n\n" # Normalize whitespace around the markdown

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
            content = content.strip() + "\n\n" # Normalize whitespace around the markdown
            message = form.cleaned_data["message"] or "<no messages>"
            is_minor = form.cleaned_data["is_minor"]
            author = "Anonymous <anonymous@%s>" % request.META['REMOTE_ADDR']

            if page:
                old_content = page.content
                if section:  # section edit
                    keep_header = bool(request.REQUEST.get('keep_header'))
                    print(keep_header)
                    if section == -1:
                        page.content = page.content.rstrip() + "\n\n" + content
                    else:
                        page.content = sectionalize_replace(page.content, section, content, keep_header=keep_header)
                    if page.content != old_content:
                        page.commit(message=message, author=author, is_minor=is_minor)
                else:
                    if content == "delete":
                        page.delete()
                    else:
                        page.content = content
                        if page.content != old_content:
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
                return HttpResponse(rendered)

        else:  # Returns the invalid form for correction
            # TODO: factorize this chunk
            context['page'] = page  # So templates nows about what page we are editing
            context['name'] = name  # So templates nows about what page we are editing
            context['form'] = form
            return render_to_response("aacore/page_edit.html", context, \
                    context_instance=RequestContext(request))

        url = reverse('aa-page-detail', kwargs={'slug': slug})
        return redirect(url)


def page_history(request, slug): 
    """
    Displays the commit list of the Git repository associated to
    :model:`aacore.Page`.

    **Context**

    ``RequestContext``
        Request context
    ``page``
        An instance of :model:`aacore.Page`.

    **Template:**

    :template:`aacore/page_history.html`

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

    return render_to_response("aacore/page_history.html", context,
            context_instance=RequestContext(request))


def page_diff(request, slug): 
    """
    Displays a comparision of two revisions of a :model:`aacore.Page`.

    **Context**

    ``RequestContext``
        Request context
    ``page``
        An instance of :model:`aacore.Page`.
    ``content``
        The diff rendered in HTML.

    **Template:**

    :template:`aacore/page_diff.html`

    """
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

    return render_to_response("aacore/page_diff.html", context,
            context_instance=RequestContext(request))


def sandbox(request):
    """
    Sample page to test wikitext / embed processing. Unlike a real wiki
    sandbox, this page is always ephemeral (nothing is saved)
    Options:
    This view does not alter the database / create new resources (?)
    """
    context = {}
    context['content'] = request.REQUEST.get("content", "")
    return render_to_response("aacore/sandbox.html", context, context_instance=RequestContext(request))


############################################################
# UNSTABLE
############################################################

# map filter args to template context...


def path_to_url (p):
    if p.startswith(projsettings.MEDIA_ROOT):
        return full_site_url(projsettings.MEDIA_URL + p[len(projsettings.MEDIA_ROOT):])
    return p

def xpath_filter (fargs, url, cur, rdfmodel=None):
    """ Takes a url as input value and an xpath as argument.
    Returns a collection of html elements
    usage:
        {{ "http://fr.wikipedia.org/wiki/Antonio_Ferrara"|xpath:"//h2" }}
    """
    def absolutize_refs (baseurl, lxmlnode):
        for elt in lxml.cssselect.CSSSelector("*[src]")(lxmlnode):
            elt.set('src', urlparse.urljoin(baseurl, elt.get("src")))
        return lxmlnode
    request = urllib2.Request(url)
    request.add_header("User-Agent", "Mozilla/5.0 (X11; U; Linux x86_64; fr; rv:1.9.1.5) Gecko/20091109 Ubuntu/9.10 (karmic) Firefox/3.5.5")
    stdin = urllib2.urlopen(request)
    htmlparser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("lxml"), namespaceHTMLElements=False)
    page = htmlparser.parse(stdin)
    p = page.xpath(fargs)
    if p:
        return "\n".join([lxml.etree.tostring(absolutize_refs(url, item), encoding='utf-8') for item in p])
    else:
        return None

