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


"""
Utilities specific to the core application
"""




import urlparse
import RDF

import django
from django.contrib.sites.models import Site
from django.core.urlresolvers import resolve
from django.conf import settings as projectsettings
from django.http import HttpRequest

from aacore.settings import (RDF_STORAGE_NAME, RDF_STORAGE_DIR, INDEXED_MODELS)
from aacore.rdfutils import (get_model, rdf_parse_into_model, prep_uri)
import aacore.models


def get_rdf_model ():
    """
    Opens the Active Archives RDF Store.
    """
    rdfmodel = get_model(RDF_STORAGE_NAME, RDF_STORAGE_DIR)
    return rdfmodel

def full_site_url(url):
    """
    Return a FULL absolute URL for a given URL, join with Site.objects.get_current().domain
    Requires: That the Site is properly setup in the admin!
    """
    try:
        base = projectsettings.SITE_URL
    except AttributeError:
        base = None

    base = base or "http://"+Site.objects.get_current().domain
    return urlparse.urljoin(base, url)

def is_local_url(url):
    """
    Returns True if url.startswith SITE_URL (or Site.domain)
    """
    try:
        base = projectsettings.SITE_URL
    except AttributeError:
        base = None
    base = base or "http://" + Site.objects.get_current().domain
    return url.startswith(base)

def reindex (item, rdfmodel=None):
    if rdfmodel == None:
        rdfmodel = get_rdf_model()
    url = full_site_url(item.get_absolute_url())
    try:                
        rdf_parse_into_model(rdfmodel, url, format="rdfa", baseuri=url, context=url)
        return True
    except RDF.RedlandError, e:
        return False
##################

# Multi-step resource ADD
# "Sniff" / "Add"
# Main Resource View -- allow "preview" of non-added resources

def add_resource (url, rdfmodel=None, request=None, reload=False):
    """
    This is what gets called when in the aa browser you type a URL.
    """
    if rdfmodel == None:
        rdfmodel = get_rdf_model()

    ## TODO: DEAL WITH URL NORMALIZATION HERE ?!
    ## actually need to peek ahead in models for tips on normalizing ...
    ## and actually, should a resource be created if no model claims the URL?

    (r, created) = aacore.models.Resource.get_or_create_from_url(url, reload=reload)
    if created or reload:
#        sniff_url = full_site_url(r.get_absolute_url())
#        parse_localurl_into_model(rdfmodel, sniff_url, format="rdfa", baseuri=sniff_url, context=sniff_url, request=request)

        # relink delegates
        r.delegates.all().delete()
        for model in get_indexed_models():
            if model == aacore.models.Resource:
                continue
            try:
                delegate, created = model.get_or_create_from_url(url, reload=reload)
                # are they already linked?
                if delegate:
#                    print "\tlinking to", delegate
                    rd = aacore.models.ResourceDelegate(resource=r, delegate=delegate)
                    rd.save()
#                    delegate_url = full_site_url(delegate.get_absolute_url())
#                    if hasattr(delegate, 'get_rdf_as_stream'):
#                        stream = delegate.get_rdf_as_stream()
#                        context = RDF.Node(delegate_url)
#                        rdfmodel.context_remove_statements(context=context)
#                        rdfmodel.add_statements(stream, context=context)
#                    else:
#                        parse_localurl_into_model(rdfmodel, delegate_url, format="rdfa", baseuri=delegate_url, context=delegate_url, request=request)
            except AttributeError:
                # print "attribute error in", model, "skipping."
                pass
        # Force Reindex of resource (to get delegate/sniffer links)        
        ## r.sync()
        aacore.models.reindex_request.send(sender=r.__class__, instance=r)


def get_indexed_models():
    modelnames = INDEXED_MODELS
    ret = []
    for modelname in modelnames:
        try:
            (modulename, classname) = modelname.rsplit(".", 1)
            module = __import__(modulename, fromlist=[classname])
            klass = getattr(module, classname)
            ret.append(klass)
        except ImportError:
            print "ERROR IMPORTING", modelname
    return ret

def direct_get_response (url, request=None):
    """ 
    Hack to load a view contents without going through the (local) server, work
    around for local (testing) server blockage when called form another request

    request is optional, but NB the default one is really minimal and may be
    missing many things a view may require (like a REQUEST object)... so better
    to pass a real request object

    Returns response object (resp.content is content in bytes)
    """
    # de-absolutize the URL
    if request == None:
        request = HttpRequest()
        request.user = django.contrib.auth.models.AnonymousUser()
        request.REQUEST = {}
        request.POST = {}
        request.GET = {}

    rurl = urlparse.urlparse(url).path
    func, args, kwargs = resolve(rurl)

    try:
        resp = func(request, *args, **kwargs)
        return resp
    except Exception, e:
        print "aacore.utils.direct_get_response: Exception:", e    

def parse_localurl_into_model (model, uri, format=None, baseuri=None, context=None, request=None):

    content = direct_get_response(uri, request).content
    # FIXME: html5tidy breaks the browse/sniff code.
    # When it is there, cliking on the browse button of the embeds does not
    # show anyting, even on reload...
    #content = html5tidy.tidy(content)
    uri = prep_uri(uri)

    if format:
        parser=RDF.Parser(format)
    else:
        parser=RDF.Parser()

    if baseuri != None:
        baseuri = prep_uri(baseuri)
    else:
        baseuri = uri

    if context != None:
        context = RDF.Node(prep_uri(context))
    else:
        context = RDF.Node(uri)

    stream = parser.parse_string_as_stream(content, baseuri)
    model.context_remove_statements(context=context)
    model.add_statements(stream, context=context)
