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


import RDF
import urlparse

import django
from django.contrib.sites.models import Site
from django.core.urlresolvers import resolve
from django.http import HttpRequest

import aacore.models
from aacore import (RDF_MODEL, get_indexed_models)
from aacore.rdfutils import (rdf_parse_into_model, prep_uri)


def full_site_url(url):
    """
    Returns the fully qualified URL (joined with
    Site.objects.get_current().domain) for a given URL path.
    
    Requires that the Site is properly setup in the admin!
    """
    return urlparse.urljoin("http://%s" % Site.objects.get_current().domain, url)


def is_local_url(url):
    """
    Returns True if the given URL belongs to the current :model:`Site.domain`
    """
    domain = Site.objects.get_current().domain
    url = urlparse.urlparse(url).netloc
    return (url == domain)


def reindex (item, rdf_model=RDF_MODEL):
    url = full_site_url(item.get_absolute_url())
    try:                
        rdf_parse_into_model(rdf_model, url, format="rdfa", baseuri=url, context=url)
        return True
    except RDF.RedlandError:
        return False


def add_resource (url, rdf_model=RDF_MODEL, request=None, reload=False):
    """
    This is what gets called when in the aa browser you type a URL.
    """
    ## TODO: DEAL WITH URL NORMALIZATION HERE ?!
    ## actually need to peek ahead in models for tips on normalizing ...
    ## and actually, should a resource be created if no model claims the URL?

    (resource, created) = aacore.models.Resource.get_or_create_from_url(url, reload=reload)
    if created or reload:
        # relink delegates
        resource.delegates.all().delete()
        for model in get_indexed_models():
            if model == aacore.models.Resource:
                continue
            try:
                (delegate, created) = model.get_or_create_from_url(url, reload=reload)
                # are they already linked?
                if delegate:
                    resource_delegate = aacore.models.ResourceDelegate(resource=resource, delegate=delegate)
                    resource_delegate.save()
            except AttributeError:
                pass
        aacore.models.reindex_request.send(sender=resource.__class__, instance=resource)


def direct_get_response (url, request=None):
    """ 
    Hack to load a view contents without going through the (local) server, work
    around for local (testing) server blockage when called form another request

    request is optional, but NB the default one is really minimal and may be
    missing many things a view may require (like a REQUEST object)... so better
    to pass a real request object

    Returns response object (resp.content is content in bytes)
    """
    if request == None:
        request = HttpRequest()
        request.user = django.contrib.auth.models.AnonymousUser()
        request.REQUEST = {}
        request.POST = {}
        request.GET = {}

    # de-absolutize the URL
    rurl = urlparse.urlparse(url).path
    (func, args, kwargs) = resolve(rurl)

    try:
        return func(request, *args, **kwargs)
    except Exception, e:
        print("aacore.utils.direct_get_response: Exception:", e)


def parse_localurl_into_model (model, uri, format=None, baseuri=None, 
                               context=None, request=None):

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


if __name__ == "__main__":
    import doctest
    doctest.testmod()
