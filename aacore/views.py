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
def rdf_source (request, id):
    context = {}
    source = get_object_or_404(RDFSource, pk=id)
    context['source'] = source
    # context['namespaces'] = Namespace.objects.all()
    return render_to_response("aacore/rdf_source.html", context, context_instance=RequestContext(request))

def colors_css (request):
    context = {}
    context['namespaces'] = Namespace.objects.all()
    return render_to_response("aacore/colors.css", context, context_instance=RequestContext(request), mimetype="text/css")

def resources (request):
    context = {}
    context['resources'] = Resource.objects.all()
    return render_to_response("aacore/resources.html", context, context_instance = RequestContext(request))

def get_embeds (uri, model, request):
    """ Example get_embeds for basic HTML(5) types """

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

    if b.get('ctype') in ("image/jpeg", "image/png", "image/gif"):
        ret.append('<img src="{0}" />'.format(uri))
    elif b.get('ctype') in ("video/ogg", "video/webm") or (b.get('videocodec') in ("theora", "vp8")):
        ret.append('<video class="player" controls src="{0}" />'.format(uri))
    elif b.get('ctype') in ("audio/ogg", ) or (b.get('audiocodec') == "vorbis" and (not b.get('videocodec'))):
        ret.append('<audio class="player" controls src="{0}" />'.format(uri))

    return ret

def embed_js (request):
    context = {}
    context['embed_url'] = full_site_url(reverse("aa-embed"))
    return render_to_response("aacore/embed.js", context, context_instance = RequestContext(request), mimetype="application/javascript")

def embed (request):
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
    this = "http://" + Site.objects.get_current().domain
    if uri.startswith(this):
        return HttpResponseRedirect(uri)

    submit = request.REQUEST.get("_submit", "")

    if submit == "direct":
        return HttpResponseRedirect(uri)
    elif submit == "remove":
        return HttpResponse('not implemented')
    elif submit == "reload":
        add_resource(uri, model, request, reload=True)
#    elif submit == "sniff":
#        add_resource(uri, model, request)
    else:
        # force every (http) resource to be added
        if uri.startswith("http"):
            # TODO: REQUIRE LOGIN TO ACTUALLY ADD...
            add_resource(uri, model, request)

    literal = None
    if not uri.startswith("http:"):
        literal = uri

    context = {}
    context['embeds'] = [] # get_embeds(uri, model, request)
    context['namespaces'] = Namespace.objects.all()

    context['uri'] = uri
    context['literal'] = literal

    if literal:
        node_stats, links_out, links_in, as_rel = load_links(model, context, literal=uri)
    else:
        node_stats, links_out, links_in, as_rel = load_links(model, context, uri=uri)

    context['node_stats'] = node_stats
    context['links_out'] = links_out
    context['links_in'] = links_in
    context['links_as_rel'] = as_rel

    # literals (by rel, by context)
    # links in/out (left/right) (by rel, by context)

    ###
    # is this resource starred by the current user
    if request.user:
        pass

    ###
    if not literal:
        try:
            resource = Resource.objects.get(url=uri)
            context['resource'] = resource
        except Resource.DoesNotExist:
            pass

    return render_to_response("aacore/browse.html", context, context_instance = RequestContext(request))

def load_links (model, context, uri=None, literal=None):
    """ load all the relationship of a uri via the rdf model """
    links_in = []
    links_out = []
    node_stats = []
    as_rel = None

    if literal:
        s = '"{0}"'.format(literal)
    else:
        s = "<{0}>".format(uri)

    q = "SELECT DISTINCT ?relation ?object WHERE {{ {0} ?relation ?object . }} ORDER BY ?relation".format(s)
    for b in rdfutils.query(q, model):
        if b['relation'].is_resource() and str(b['relation'].uri) == "http://purl.org/dc/elements/1.1/title":
            context['title'] = b['object'].literal_value.get("string")
        elif b['relation'].is_resource() and str(b['relation'].uri) == "http://purl.org/dc/elements/1.1/description":
            context['description'] = b['object'].literal_value.get("string")
        elif b['relation'].is_resource() and str(b['relation'].uri) == "http://xmlns.com/foaf/0.1/thumbnail":
            context['thumbnail'] = str(b['object'].uri)
        elif b['object'].is_resource():
            links_out.append(b)
        else:
            node_stats.append(b)

    q = "SELECT DISTINCT ?subject ?relation WHERE {{ ?subject ?relation {0} . }} ORDER BY ?relation".format(s)
    for b in rdfutils.query(q, model):
        links_in.append(b)

    if not literal:
        q = "SELECT DISTINCT ?subject ?object WHERE {{ ?subject {0} ?object . }} ORDER BY ?subject".format(s)
        as_rel = [x for x in rdfutils.query(q, model)]
    else:
        as_rel = ()

    return node_stats, links_out, links_in, as_rel


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
#    if 'css' in md.Meta:
#        context['extra_css'] = md.Meta['css']

    return render_to_response("aacore/page.html", context, context_instance=RequestContext(request))


def page_edit(request, slug):
    """
    Page edit

    GET: Either the edit form, OR provides Markdown source via AJAX call
    POST: Receives/commits edits on POST (either via form or AJAX)

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
            context['form'] = PageEditForm(initial={"content": '# My first section'})
        
        return render_to_response("aacore/edit.html", context, \
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
            message = form.cleaned_data["message"] or "<no messages>"
            is_minor = form.cleaned_data["is_minor"]
            author = "Anonymous <anonymous@%s>" % request.META['REMOTE_ADDR']

            if page:
                if section:  # section edit
                    page.content = sectionalize_replace(page.content, section, content)
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
                return HttpResponse(rendered)

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
        t = Template("{% load aatags %}\n" + text)
        c = Context({})
        context['result'] = t.render(c)

    return render_to_response("aacore/sandbox.html", context, context_instance=RequestContext(request))

############################################################

def getLinks (rdfmodel, url, norels=None):
    """ formerly getTag """
    q = """PREFIX dc:<http://purl.org/dc/elements/1.1/>
SELECT DISTINCT ?rel ?doc ?title ?author ?date
WHERE {
?doc dc:title ?title .
?doc ?rel <%s> .
OPTIONAL { ?doc dc:creator ?author }
OPTIONAL { ?doc dc:date ?date }
}
ORDER BY ?rel ?title""".strip() % url
    return rdfutils.query(q, rdfmodel)

def getLinksFaceted (rdfmodel, url):
    q = """
PREFIX dc:<http://purl.org/dc/elements/1.1/>
PREFIX sarma:<http://sarma.be/terms/>

SELECT ?doc ?rel ?tag
WHERE {
  ?doc ?rel ?tag .
  ?doc ?tagrel <%s> .
}
ORDER BY ?doc ?rel
""".strip() % url
    # groupby(res, "doc", "rel")
    links = rdfutils.query(q, rdfmodel)
    curdoc = None
    doc = None
    docs = []
    for rec in links:
        if curdoc != rec['doc']:
            curdoc = rec['doc']
            doc = {'doc': rdfnode(rec['doc']), 'tagsbyrel' : {}}
            docs.append(doc)
        rel = rdfnode(rec['rel'])
        if not rel in doc['tagsbyrel']:
            doc['tagsbyrel'][rel] = []
        doc['tagsbyrel'][rel].append(rdfnode(rec['tag']))
    return docs


############################################################
# Embed
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

def embed_jsonp_js (request):
    context = {}
    context['embed_url'] = full_site_url(reverse("aa-embed-jsonp"))
    return render_to_response("aacore/embed_jsonp.js", context, context_instance = RequestContext(request), mimetype="application/javascript")

# embed could always return a dictionary with content + an eventual polling url
# or test returned content that itself triggers polling (better?)

def embed_jsonp (request):
    url = request.REQUEST.get("url")
    # ALLOW (authorized users) to trigger a resource to be added...
    rdfmodel = get_rdf_model()
    try:
        res = Resource.objects.get(url=url)
    except Resource.DoesNotExist:
        add_resource(url, rdfmodel=rdfmodel)
        res = get_object_or_404(Resource, url=url)

    filterstr = request.REQUEST.get("filter", "embed").strip()
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
            rendered = f(fargs, res, rendered, rdfmodel=rdfmodel)

    callback = request.REQUEST.get("callback", "callback")
    response = callback + "(" + json.dumps(rendered) + ");"

    return HttpResponse(response, mimetype="application/javascript")

############################################################
# BROWSE
############################################################

#def resource (request, id=None, url=None):
#    if id:
#        resource = get_object_or_404(Resource, pk=id)
#    else:
#        try:    
#            resource = Resource.objects.get(url=url)
#        except Resource.DoesNotExist:
#            return HttpResponseRedirect(reverse("aa-404", (), url=url))

#    context = {}
#    context['resource'] = resource
#    context['collections'] = resource.collections.exclude(star=True)

#    # check if resource is starred by this user
#    try:
#        collection = Collection.objects.get(star=True, owner=request.user)
#        try:
#            citem = collection.items.get(asset=asset)
#            context['star'] = True
#        except CollectionItem.DoesNotExist:
#            pass
#    except Collection.DoesNotExist:
#        pass

#    ### LOAD ALL METADATA
#    model = get_rdf_model()
#    uri = resource.url
#    context['namespaces'] = Namespace.objects.all()
#    context['uri'] = uri
#    q = "SELECT DISTINCT ?relation ?object WHERE { <%s> ?relation ?object . } ORDER BY ?relation" % uri
#    context['results_as_subject'] = rdfutils.query(q, model)
#    q = "SELECT DISTINCT ?subject ?object WHERE { ?subject <%s> ?object . } ORDER BY ?subject" % uri
#    context['results_as_relation'] = rdfutils.query(q, model)
#    q = "SELECT DISTINCT ?subject ?relation WHERE { ?subject ?relation <%s> . } ORDER BY ?relation" % uri
#    context['results_as_object'] = rdfutils.query(q, model)


#    return render_to_response("aacore/browse_resource.html", context, context_instance = RequestContext(request))

@login_required
def resource_meta (request, id):
    context = {}
    context['resource'] = get_object_or_404(Resource, pk=id)
    return render_to_response("resource_meta.html", context, context_instance = RequestContext(request))

@login_required
def resource_export (request, id):
    context = {}
    context['resource'] = get_object_or_404(Resource, pk=id)
    return render_to_response("resource_export.html", context, context_instance = RequestContext(request))

@login_required
def resource_star (request, id):
    context = {}
    resource = get_object_or_404(Resource, pk=id)
    context['resource'] = resource
    if request.method == "POST":
        if request.POST.get("star") == "true":
            # Add this resource to this users starred resources
            (collection, created) = Collection.objects.get_or_create(star=True, owner=request.user)
            try:
                citem = collection.items.get(resource=resource)
            except CollectionItem.DoesNotExist:
                citem = CollectionItem(collection=collection, resource=resource, author=request.user)
                citem.save()
                return HttpResponse(json.dumps({'star': True}));
        else:
            # Remove this resource from users starred resources
            try:
                collection = Collection.objects.get(star=True, owner=request.user)
                item = collection.items.get(resource=resource)
                item.delete()
            except Collection.DoesNotExist:
                pass
            except CollectionItem.DoesNotExist:
                pass

            return HttpResponse(json.dumps({'star': False}));

from django import forms
class AddToCollectionForm (forms.Form):
    name = forms.CharField(max_length=255, required=True, label="Name of collection")

def resource_addtocollection (request, id):
    resource = get_object_or_404(Resource, pk=id)
    context = {}
    context['resource'] = resource
    context['form'] = AddToCollectionForm()
    collections = Collection.objects.filter(owner=request.user).exclude(star=True).order_by("name")
    
    if request.method == "POST":
        form = AddToCollectionForm(request.POST)
        if form.is_valid():
            cname = form.cleaned_data.get('name').strip()
            if cname:
                (collection, created) = Collection.objects.get_or_create(owner=request.user, name=cname)
                (citem, created) = CollectionItem.objects.get_or_create(collection=collection, asset=asset)
                next = reverse('asset', args=[asset.id])
                return HttpResponseRedirect(next)
    else:
        form = AddToCollectionForm()

    context['form'] = form        
    context['collections'] = collections
    return render_to_response("resource_addtocollection.html", context, context_instance = RequestContext(request))

@login_required
def starred (request):
    context={}
    context['star'] = True
    try:
        c = Collection.objects.get(owner=request.user, star=True)
        context['collection'] = c
        context['items'] = c.items.all()
    except Collection.DoesNotExist:
        pass
    return render_to_response("star.html", context, context_instance = RequestContext(request))

@login_required
def collections (request):
    context={}
    context['collections'] = Collection.objects.filter(owner=request.user).exclude(star=True)
    context['allcollections'] = Collection.objects.exclude(owner=request.user).exclude(star=True)
    return render_to_response("collections.html", context, context_instance = RequestContext(request))

@login_required
def collection (request, id):
    context={}
    c = get_object_or_404(Collection, pk=id)
    context['collection'] = c
    context['items'] = c.items.all()
    return render_to_response("collection.html", context, context_instance = RequestContext(request))

@login_required
def collection_order (request, id):
    context={}
    c = get_object_or_404(Collection, pk=id)
    if request.method == "POST":
        ordered_ids = request.POST.getlist("citem[]")
        for x, citem_id in enumerate(ordered_ids):
            citem = CollectionItem.objects.get(pk=citem_id)
            if citem.collection == c:
                citem.order = x
                citem.save()
        return HttpResponse(json.dumps({'result': True}));
    return HttpResponseNotAllowed(['POST'])

@login_required
def collection_delete (request, id):
    context={}
    c = get_object_or_404(Collection, pk=id)
    context['collection'] = c
    if request.method == "POST":
        if request.POST.get("_submit", "").lower() == "cancel":
            return HttpResponseRedirect(reverse('collection', args=[c.id]))
        c.delete()
        return HttpResponseRedirect(reverse('collections'))
    return render_to_response("collection_delete.html", context, context_instance = RequestContext(request))

@login_required
def tags (request):
    context={}
    context['tags'] = Tag.objects.all()
    return render_to_response("tags.html", context, context_instance = RequestContext(request))

@login_required
def tag (request, id):
    context={}
    tag = get_object_or_404(Tag, pk=id)
    context['tag'] = tag
    context['resources'] = tag.assets.all()
    return render_to_response("tag.html", context, context_instance = RequestContext(request))

@login_required
def users (request):
    context={}
    context['users'] = User.objects.filter(is_active=True)
    return render_to_response("users.html", context, context_instance = RequestContext(request))

@login_required
def user (request, id):
    context={}
    u = get_object_or_404(User, pk=id)
    context['user'] = u
    context['assets'] = [] # u.assets.all()
    context['collections'] = u.collections.exclude(favorites=True)
    return render_to_response("user.html", context, context_instance = RequestContext(request))

@login_required
def search (request, id):
    context={}
    return render_to_response("search.html", context, context_instance = RequestContext(request))


