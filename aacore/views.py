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


import RDF, urllib
try: import simplejson as json
except ImportError: import json
import feedparser

from django.shortcuts import (render_to_response, redirect, get_object_or_404)
from django.http import (HttpResponse, HttpResponseRedirect)
from django.template import (RequestContext, Template, Context)
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.conf import settings as projsettings
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site

from aacore.spider import spider
#from plugins import sniffer
from models import *
from utils import (get_rdf_model, full_site_url, dewikify, url_for_pagename, convert_line_endings, pagename_for_url, add_resource)
from mdx import get_markdown
from mdx.mdx_sectionedit import (sectionalize, sectionalize_replace)
import rdfutils
from forms import PageEditForm


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

def get_embeds (uri, model, request):
    """ UNSTABLE: Example get_embeds for basic HTML(5) types """

    # Is this suitable for a audio/video tag?
    q = """PREFIX dc:<http://purl.org/dc/elements/1.1/>
PREFIX aa:<http://activearchives.org/terms/>
PREFIX http:<http://www.w3.org/Protocols/rfc2616/>
PREFIX media:<http://search.yahoo.com/mrss/>

SELECT ?ctype ?format ?audiocodec ?videocodec
WHERE {{
  OPTIONAL {{ <{0}> http:content_type ?ctype . }}
  OPTIONAL {{ <{0}> dc:format ?format . }}
  OPTIONAL {{ <{0}> media:audio_codec ?audiocodec . }}
  OPTIONAL {{ <{0}> media:video_codec ?videocodec . }}
}}
""".strip().format(uri)

    b = {}
    for row in rdfutils.query(q, model):
        for name in row:
            b[name] = rdfutils.rdfnode(row.get(name))
        break

    ret = []

    # TODO: move to templates
    if b.get('ctype') in ("image/jpeg", "image/png", "image/gif"):
        ret.append('<img src="{0}" />'.format(uri))
    elif b.get('ctype') in ("video/ogg", "video/webm") or (b.get('videocodec') in ("theora", "vp8")):
        ret.append('<video class="player" controls src="{0}" />'.format(uri))
    elif b.get('ctype') in ("audio/ogg", ) or (b.get('audiocodec') == "vorbis" and (not b.get('videocodec'))):
        ret.append('<audio class="player" controls src="{0}" />'.format(uri))
    elif b.get('ctype') in ("application/rss+xml", "text/xml"):
        feed = feedparser.parse(uri)
        output = ""
        for entry in feed['entries'][:4]:
            output += '<div>'
            output += '<h3><a href="%s">%s</a></h3>' % (entry.link.encode(feed.encoding), entry.title.encode(feed.encoding))
            output += '<div>'
            output += entry.summary.encode(feed.encoding)
            output += '</div>'
            output += '</div>'
        ret.append(output)

    return ret

def embed (request):
    """
    Receives a request with parameters URL and filter.
    Returns a JSON containing content of the embed.
    """
    url = request.REQUEST.get("url")
    # ALLOW (authorized users) to trigger a resource to be added...
    model = get_rdf_model()
    if url.startswith("http"):
        # TODO: REQUIRE LOGIN TO ACTUALLY ADD...
        add_resource(url, model, request)

    ### APPLY FILTERS (if any)
    filterstr = request.REQUEST.get("filter", "").strip()
    if filterstr and not filterstr.startswith("http:"):
        filters = [x.strip() for x in filterstr.split("|")]
        rendered = ""
        for fcall in filters:
            if ":" in fcall:
                (fname, fargs) = fcall.split(":", 1) 
            else:
                fname = fcall.strip()
                fargs = ""
            f = get_filter_by_name(fname)
            if f:
                rendered = f(fargs, url, rendered, rdfmodel=model)
    else:
        embeds = get_embeds(url, model, request)
        if len(embeds):
            rendered = embeds[0]
        else:
            rendered = url

    browseurl = reverse("aa-browse") + "?" + urllib.urlencode({'uri': url})
    ret = """
<div class="aa_embed">
    <div class="links">
        <a class="directlink" href="{0[url]}">URL</a>
        <a class="browselink" target="browser" href="{0[browseurl]}">browse</a>
    </div>
    <div class="body">{0[embed]}</div>
</div>""".strip()

    content = ret.format({'url': url, 'browseurl': browseurl, 'embed': rendered})
    return HttpResponse(json.dumps({"ok": True, "content": content}), mimetype="application/json");


def browse (request):
    """ Main "browser" view """

    model = get_rdf_model()  # Open the RDF Store (the 4 redland databases)
    uri = request.REQUEST.get("uri", "")

    # Avoids browsing an internal URL
    if utils.is_local_url(uri):
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

def annotation_export(request, slug, section, _format="audacity"):
    context = {}
    name = dewikify(slug)
    page = Page.objects.get(name=name)

    sections = sectionalize(page.content)
    sectiondict = sections[int(section)]

    sections = sectionalize(sectiondict['header'] + sectiondict['body'])
    print sections

    context['sections'] = sections

    context['foo'] = []

    import re
    from aacore.mdx.mdx_sectionedit import (TIMECODE_HEADER, spliterator)
    pattern = re.compile(TIMECODE_HEADER, re.I | re.M | re.X)
    for header, body, start, end in spliterator(pattern, sectiondict['header'] + sectiondict['body'], returnLeading=0):
        p = r"((?P<hours>\d\d):)?(?P<minutes>\d\d):(?P<seconds>\d\d)(?P<milliseconds>[,.]\d{1,3})?"
        bar = re.search(p, header)
        hours = int(bar.groupdict()['hours'])
        minutes = int(bar.groupdict()['minutes'])
        seconds = int(bar.groupdict()['seconds'])
        print(hours, minutes, seconds)
        context['foo'].append({'start': start, 'end': end, 'body': body})
        


    c = RequestContext(request)
    return render_to_response("aacore/annotation_export.audacity", context, context_instance=RequestContext(request), mimetype="text/plain;charset=utf-8")

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
    context = {}
    context['namespaces'] = Namespace.objects.all()
    name = dewikify(slug)

    try:
        page = Page.objects.get(name=name)
    except Page.DoesNotExist:
        # Redirects to the edit page
        url = reverse('aa-page-edit', kwargs={'slug': slug})
        return redirect(url)

    context['page'] = page
    c = RequestContext(request)

    # TODO: Markdown extension for stylesheet embed
#    if 'css' in md.Meta:
#        context['extra_css'] = md.Meta['css']

    return render_to_response("aacore/page_detail.html", context, context_instance=RequestContext(request))


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
            context['form'] = PageEditForm(initial={"content": '# First section {: style="top: 30px; left: 30px;" }'})
        
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
                    if section == -1:
                        page.content = page.content.rstrip() + "\n\n" + content
                    else:
                        page.content = sectionalize_replace(page.content, section, content)
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

from django.template.loader import render_to_string

# USER_AGENT + MIME_TYPE

def embed_filter (fargs, res, cur, rdfmodel=None):
    contenttypes = res.get_metadata(rel="http://activearchives.org/terms/content_type")
    if "image/jpeg" in contenttypes:
        return render_to_string('aacore/embeds/image.html', { 'resource': res })
    return ""

def path_to_url (p):
    if p.startswith(projsettings.MEDIA_ROOT):
        return full_site_url(projsettings.MEDIA_URL + p[len(projsettings.MEDIA_ROOT):])
    return p

def thumbnail_filter (fargs, res, cur, rdfmodel=None):
    sizepat = re.compile(r"(?P<width>\d+)px", re.I)
    m = sizepat.search(fargs)
    if m:
        width = m.groupdict()['width']
        fpath = res.get_local_file()
        (dname, fname) = os.path.split(fpath)
        tpath = os.path.join(dname, "thumbnail_{}px.jpg".format(width))
        if not os.path.exists(tpath):
            cmd = 'convert -resize {0}x "{1}" "{2}"'.format(width, fpath, tpath)
            os.system(cmd)
        return '<img src="{}" />'.format(path_to_url(tpath))


import urlparse, html5lib, urllib2, lxml.cssselect

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

def get_filter_by_name (n):
    if n == "thumbnail":
        return thumbnail_filter
    elif n == "xpath":
        return xpath_filter
    elif n == "embed":
        return embed_filter
