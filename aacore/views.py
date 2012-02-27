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


from django.shortcuts import (render_to_response, get_object_or_404)
from django.http import HttpResponseRedirect
from django.template import RequestContext 
from aacore.models import *
from aacore.utils import (get_rdf_model, add_resource, is_local_url)
from aacore import rdfutils


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

def browse (request):
    """ Main "browser" view """

    model = get_rdf_model()  # Opens the RDF Store (the 4 redland databases)
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
        (node_stats, links_out, links_in, as_rel) = rdfutils.load_links(model, context, literal=uri)
    else:
        (node_stats, links_out, links_in, as_rel) = rdfutils.load_links(model, context, uri=uri)

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

    return render_to_response("aacore/browse.html", context, 
                              context_instance=RequestContext(request))

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
    return render_to_response("aacore/resource_sniff.html", context, 
                              context_instance=RequestContext(request))


