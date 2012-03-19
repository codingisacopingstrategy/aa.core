#
# Generic RDF views useful for debugging / maintenance
#
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
#

import RDF
from django.conf.urls.defaults import *
from django.shortcuts import (render_to_response)
from django.http import (HttpResponse, HttpResponseRedirect)
from django.template import RequestContext
from aacore.models import *
from aacore.utils import full_site_url
import rdfutils
from aacore import RDF_MODEL



FORMAT_MIMETYPES = {
    "rdfxml":       "application/rdf+xml",
    "json":         "application/json",
    "json-triples": "application/json"
}

def reindex (request):
    url = request.REQUEST.get("url")
    url = full_site_url(url)
    format = request.REQUEST.get("format")
    rdfutils.rdf_parse_into_model(RDF_MODEL, url, format)
    return HttpResponseRedirect(url)

def dump (request):
    """
    url:    input url (optional, if not given displays the contents of the store)
    input:  format of input url if given
    format: output format (default ntriples), possible values include: ntriples, rdfxml, turtle, dot, json, json-triples
    """
    url = request.REQUEST.get("url", "")
    if not url:
        model = RDF_MODEL
    else:
        inputformat = request.REQUEST.get("input", "")
        # parser = RDF.Parser(name="rdfa")
        if inputformat:
            parser = RDF.Parser(name=inputformat)
        else:
            parser = RDF.Parser()
        model = RDF.Model()
        parser.parse_into_model(model, url, base_uri=url)

    format = str(request.REQUEST.get("output", "turtle"))
    ser = RDF.Serializer(name=format)

    for n in Namespace.objects.all():
        ser.set_namespace(n.name.encode("utf-8"), RDF.Uri(n.url.encode("utf-8") ))

    # dc: http://purl.org/dc/elements/1.1/
    # xmls: http://www.w3.org/2001/XMLSchema#

    mime = FORMAT_MIMETYPES.get(format, "text/plain")
    return HttpResponse(ser.serialize_model_to_string(model), mimetype=mime + ";charset=utf-8")

def query (request):
    context = {}
    q = request.REQUEST.get("query", "")
    context['query'] = q
    context['namespaces'] = Namespace.objects.all()
    if q and request.method == "POST":
        thequery = RDF.Query(q.encode("utf-8"), query_language="sparql")
        results = thequery.execute(RDF_MODEL)
        context['results'] = results.get_bindings_count()
        bindings = []
        for i in range(results.get_bindings_count()):
            bindings.append(results.get_binding_name(i))
        context['bindings'] = bindings

        rows = []
        for r in results:
            row = []
            for key in bindings:
                row.append(r.get(key))
            rows.append(row)
        context['rows'] = rows

    return render_to_response("rdfviews/query.html", context, 
                              context_instance=RequestContext(request))

def browse (request):
    uri = request.REQUEST.get("uri", "")
    submit = request.REQUEST.get("_submit", "")
    if submit == "goto":
        return HttpResponseRedirect(uri)

    literal = None
    if not uri.startswith("http:"):
        literal = uri

    context = {}
    context['namespaces'] = Namespace.objects.all()
    if literal:
        s = '"{0}"'.format(literal)
    else:
        s = "<{0}>".format(uri)

    context['uri'] = uri
    context['literal'] = literal

    q = "SELECT DISTINCT ?relation ?object WHERE {{ {0} ?relation ?object . }} ORDER BY ?relation".format(s)
    context['results_as_subject'] = rdfutils.query(q, RDF_MODEL)
    if not literal:
        q = "SELECT DISTINCT ?subject ?object WHERE {{ ?subject {0} ?object . }} ORDER BY ?subject".format(s)
        context['results_as_relation'] = rdfutils.query(q, RDF_MODEL)
    else:
        context['results_as_relation'] = ()
    q = "SELECT DISTINCT ?subject ?relation WHERE {{ ?subject ?relation {0} . }} ORDER BY ?relation".format(s)
    context['results_as_object'] = rdfutils.query(q, RDF_MODEL)

    return render_to_response("rdfviews/browse.html", context, 
                              context_instance=RequestContext(request))

