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
docstring please :)
"""

import RDF

from settings import *


# if model is None: raise Exception("new RDF.model failed")


def put_url(theuri):
    """
    docstring please :)
    """
    storage = RDF.HashStorage(RDF_STORAGE_NAME, options="hash-type='bdb',contexts='yes',dir='" + RDF_STORAGE_DIR + "'")  # dir='.'
    # if storage is None: raise Exception("open RDF.Storage failed")
    model = RDF.Model(storage)
    # open the url
    # parse as rdf(a)
    # push into the hashes store with context=url
    if not theuri.startswith("http") and not theuri.startswith("file:"):
        theuri = "file:" + theuri
    uri = RDF.Uri(theuri)
    parser = RDF.Parser('rdfa')
    # if parser is None: raise Exception("Failed to create RDF.Parser")
    stream = parser.parse_as_stream(uri, uri)  # 2nd is base uri
    cnode = RDF.Node(uri)
    model.add_statements(stream, context=cnode)
    # model.sync()  # not sure if this is necessary


def get_model():
    """
    docstring please :)
    """
    storage = RDF.HashStorage(RDF_STORAGE_NAME, options="hash-type='bdb',contexts='yes',dir='" + RDF_STORAGE_DIR + "'")  # dir='.'
    return RDF.Model(storage)
