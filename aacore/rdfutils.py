import RDF
from settings import *

# if model is None: raise Exception("new RDF.model failed")

def put_url (theuri):
    storage = RDF.HashStorage(RDF_STORAGE_NAME, options="hash-type='bdb',contexts='yes',dir='"+RDF_STORAGE_DIR+"'") # dir='.'
    # if storage is None: raise Exception("open RDF.Storage failed")
    model = RDF.Model(storage)
    # open the url
    # parse as rdf(a)
    # push into the hashes store with context=url
    if not theuri.startswith("http") and not theuri.startswith("file:"):
        theuri = "file:" + theuri
    uri = RDF.Uri(theuri)
    parser=RDF.Parser('rdfa')
    # if parser is None: raise Exception("Failed to create RDF.Parser")
    stream = parser.parse_as_stream(uri,uri)  # 2nd is base uri
    cnode = RDF.Node(uri) 
    model.add_statements(stream, context=cnode)
    # model.sync() # not sure if this is necessary

def get_model ():
    storage = RDF.HashStorage(RDF_STORAGE_NAME, options="hash-type='bdb',contexts='yes',dir='"+RDF_STORAGE_DIR+"'") # dir='.'
    return RDF.Model(storage)


