# This file is part of Active Archives.
# Copyright 2006-2010 the Active Archives contributors (see AUTHORS)
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
Thin wrapper functions to work with an RDF store based on the Redland C library
& Python bindings (librdf, python-librdf (python module name: RDF))

Requires: RDF
"""


import RDF
from urlparse import urlparse


def get_model (storage_name, storage_dir):
    """
    Opens/creates and return the default RDF Store (RDF.Model in bdb hashes
    format, contexts enabled).
        
        >>> STORAGE_NAME = 'mydb'
        >>> STORAGE_DIR = '/tmp/'
        >>> rdf_model = get_model(STORAGE_NAME, STORAGE_DIR)
        >>> print(rdf_model)
        <?xml version="1.0" encoding="utf-8"?>
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        </rdf:RDF>
        <BLANKLINE>
    """
    options = "hash-type='bdb', contexts='yes', dir='%s'" % storage_dir
    storage = RDF.HashStorage(storage_name, options=options)
    return RDF.Model(storage)


def groupby (results, groupbyvar, collectvar):
    """
    Reorganizes a SPARQL query result object to gather repeating values as a list of dictionaries.
    Returns a list of dictionaries d, in result order, such that d[collectvar] = [value, value, ...]
    NB: other keys in d only reflect the values of the first result/row with the new groupbyvar value.
    """
    ret = []
    last = None
    accum = None
    for r in results:
        cur = r.get(groupbyvar)
        if cur != last:
            last = cur
            accum = []
            item = {}
            for key in r.keys():
                if key != collectvar:
                    item[key] = r.get(key)
            item[collectvar] = accum
            ret.append(item)
        accum.append(r.get(collectvar))
    return ret


def rdfnode (n):
    """
    Unpeels an RDF.Node object to a displayable string
    """
    if n == None:
        return ""
    ret = n
    if type(n) == str or type(n) == unicode:
        return n
    if n.is_resource():
        ret = str(n.uri)
    elif n.is_literal():
        ret = n.literal_value.get("string")
    return ret


def query (q, rdfmodel, lang="sparql"):
    """
    Performs the Query q against the model rdfmodel, in the given language
    (basically just ensures that the query is encoded bytes as RDF.Query can't
    deal with unicode)

        >>> storage = RDF.HashStorage('dummy', options="new='yes', hash-type='memory', contexts='yes'")
        >>> model = RDF.Model(storage)
        >>> q = '''
        ... PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        ... SELECT *
        ... WHERE {
        ...     ?a ?b ?c .
        ... }'''
        >>> print(query(q, model))
        <?xml version="1.0" encoding="utf-8"?>
        <sparql xmlns="http://www.w3.org/2005/sparql-results#">
          <head>
            <variable name="a"/>
            <variable name="b"/>
            <variable name="c"/>
          </head>
          <results>
          </results>
        </sparql>
        <BLANKLINE>
    """
    if (type(q) == unicode):
        q = q.encode("utf-8")
    return RDF.Query(q, query_language=lang).execute(rdfmodel)


class BindingsIterator:
    """
    Convenience iterator for RDF.Query results as lists of bindings (not dictionaries)
    """
    def __init__(self, results):
        self.results = results
        self.bindings = []
        for i in range(results.get_bindings_count()):
            self.bindings.append(results.get_binding_name(i))
    def __iter__(self):
        return self
    def next(self):
        next = self.results.next()
        r = []
        for name in self.bindings:
            r.append(next.get(name))
        return r


def prep_uri (uri):
    """
    Turns a uri string (including raw file paths) into an RDF.Uri object.

        >>> print(prep_uri('bla'))
        file:///bla
        >>> print(prep_uri('http:bla'))
        http:///bla
        >>> print(prep_uri('http://stdin.fr'))
        http://stdin.fr
        >>> print(prep_uri('file:bla'))
        file:///bla
    """
    if (type(uri) == unicode):
        uri = uri.encode("utf-8")

    url_parts = urlparse(uri)

    if not url_parts.scheme:
        return RDF.Uri('file://%s' % url_parts.geturl())
    else:
        return RDF.Uri(url_parts.geturl())

        #o = list(url_parts)
        #o[0] = "file"
        #url_parts = urlparse(urlunparse(o))

    return RDF.Uri(url_parts.geturl())
    #if (type(uri) == unicode):
        #uri = uri.encode("utf-8")
    #if not uri.startswith("http") and not uri.startswith("file:"):
        #return RDF.Uri(string="file:" + uri)
    #else:
        #return RDF.Uri(uri)


def rdf_parse_into_model (model, uri, format=None, baseuri=None, context=None):
    """
    Parse the given URI into the default store.
    Format, baseuri, and context are all optional.
    (Default context is uri itself)
    Format = "rdfa", "rdfxml (default)", ... (other values supported by RDF)
    """
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

    stream = parser.parse_as_stream(uri, baseuri)
    model.context_remove_statements(context=context)
    model.add_statements(stream, context=context)
    # model.sync() # better not to do this


def rdf_context_remove_statements (model, context):
    """
    Remove all statements related to context in the default store
    """
    context = RDF.Node(prep_uri(context))
    model.context_remove_statements(context=context)


class SparqlQuery (object):
    """
    Thin SPARQL query builder, text only (not RDF specific)

    Example of use:

    #>>> q = SparqlQuery()
    #>>> q.prefix("dc:<http://purl.org/dc/elements/1.1/>")
    #>>> q.prefix("sarma:<http://sarma.be/terms/>")
    #>>> q.select("?value ?label ?doc")
    #>>> q.where("?doc <%s> ?value." % relurl)
    #>>> q.where("?value dc:title ?label.")
    #>>> q.orderby("?label ?value")
    #>>> querytext = q.render()
    #>>> # to actually perform the query using RDF:
    #>>> rdfquery = RDF.Query(querytext.encode("utf-8"), query_language="sparql")
    #>>> results = rdfquery.execute(rdfmodel)
    """
    def __init__(self):
        self._prefixes = ["rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>"]
        self._select = None
        self._wheres = []
        self._whereclauses = None
        self._orderby = None
        self._filters = []
        
    def prefix (self, val):
        if not val in self._prefixes:
            self._prefixes.append(val)

    def select (self, vals, distinct=False):
        self._select = vals
        self._selectdistinct = distinct
        
    def where (self, val):
        val = "  " + val
        self._wheres.append(val)

    def filter (self, val):
        self._filters.append(val)
        
    def orderby(self, val):
        self._orderby = val

    def where_clause(self, clause):
        if self._whereclauses == None:
            self._whereclauses = []
        clause = "    {%s}\n" % clause
        self._whereclauses.append(clause)

    def where_clause_end(self):
        self.where("{\n" + "    UNION\n".join(self._whereclauses) + "  }")
        self._whereclauses = None

    def render(self):
        ret = ""
        ret += "".join(["PREFIX %s\n" % x for x in self._prefixes])
        if self._select:
            if self._selectdistinct:
                ret += "SELECT DISTINCT %s\n" % self._select
            else:
                ret += "SELECT %s\n" % self._select
        if self._wheres:
            ret += "WHERE {\n"
            ret += "".join(["%s\n" % x for x in self._wheres])
            if self._filters:
                ret += "".join(["  FILTER %s\n" % x for x in self._filters])
            ret += "}\n"
        if self._orderby:
            ret += "ORDER BY %s\n" % self._orderby
        
        return ret


def load_links (model, context, uri=None, literal=None):
    """
    load all the relationship of a uri via the rdf model using SPARQL.
    """
    links_in = []
    links_out = []
    node_stats = []
    as_rel = None

    if literal:
        s = '"%s"' % literal
    else:
        s = "<%s>" % uri

    q = """
        SELECT DISTINCT ?relation ?object 
        WHERE {{ %s ?relation ?object . }} 
        ORDER BY ?relation
        """ % s

    for b in query(q, model):
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

    q = """
        SELECT DISTINCT ?subject ?relation 
        WHERE {{ ?subject ?relation %s . }} 
        ORDER BY ?relation
        """ % s

    for b in query(q, model):
        links_in.append(b)

    if not literal:
        q = """
            SELECT DISTINCT ?subject ?object 
            WHERE {{ ?subject %s ?object . }} 
            ORDER BY ?subject
            """ % s
        as_rel = [x for x in query(q, model)]
    else:
        as_rel = ()

    return (node_stats, links_out, links_in, as_rel)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
