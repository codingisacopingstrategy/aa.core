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
(1) Creates the "reindex_request" signal to:
    Allow Indexed Models or Delegates to request (re)indexing of their RDF,
(2) Watches indexed models/delegates post_delete signal to:
    Clear RDF index related to Delegate instances when deleted

NB: Delegates must themselves request reindexing by
sending the reindex_request signal, for example:

from aacore.signals import reindex_request
def some_method(self):
    ...
    reindex_request.send(sender=self.__class__, instance=self)
"""


import django.dispatch
import aacore.utils
from aacore import rdfutils
import RDF
from aacore import RDF_MODEL


reindex_request = django.dispatch.Signal(providing_args=[])

def indexing_reindex_item (item):
    full_url = aacore.utils.full_site_url(item.get_absolute_url())
    if hasattr(item, 'get_rdf_as_stream'):
        # in a way the URL here is the resource.url directly ?!
        stream = item.get_rdf_as_stream()
        context = RDF.Node(full_url)
        RDF_MODEL.context_remove_statements(context=context)
        RDF_MODEL.add_statements(stream, context=context)
    else:
#        # FOR DEBUGGING
#        resp = utils.direct_get_response(item.get_absolute_url())
#        page = resp.content
#        rdfaparser = RDF.Parser("rdfa")
#        furl = utils.full_site_url(item.get_absolute_url())
#        s = rdfaparser.parse_string_as_stream(page, furl)
#        print "RDFA:", (len(list(s))), "triples"

        aacore.utils.parse_localurl_into_model(RDF_MODEL, full_url, format="rdfa", baseuri=full_url, context=full_url)
    # RDF_MODEL.sync()

def indexing_drop_item (item):
    full_url = aacore.utils.full_site_url(item.get_absolute_url())
    rdfutils.rdf_context_remove_statements(RDF_MODEL, full_url)
    # RDF_MODEL.sync()

def indexing_post_delete(sender, instance, **kwargs):
    indexing_drop_item(instance)

def indexing_reindex(sender, instance, **kwargs):
    indexing_reindex_item(instance)

