"""
Implements active archives models
"""


import re
import RDF
import os
import os.path
import urllib2
import django.dispatch
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_delete
from aacore.rdfutils import (rdfnode, prep_uri)
from aacore.settings import (CACHE_DIR, CACHE_URL)
import aacore.utils
import rdfutils
import resource_opener



class Resource (models.Model):
    """ Represents an (augmented) URL.

    Acts like a proxy to access to the associated RDF store but caches the
    last information of an URL for convenience.
    
    This is the main class of Active Archives. 

    """
    url = models.URLField(verify_exists=False)
    _filter = models.CharField(max_length=1024, blank=True)
    primary = models.BooleanField(default=True)
    redirect = models.ForeignKey('self', null=True, blank=True)

    # Misc cached information from the last connexion
    # Allows conditional GET
    content_type = models.CharField(max_length=255, default="", blank=True)
    content_length = models.IntegerField(default=0)
    charset = models.CharField(max_length=64, default="", blank=True)
    last_modified = models.DateTimeField(null=True, blank=True)
    etag = models.CharField(max_length=255, default="", blank=True)

    def __unicode__(self):
        return self.url

    @models.permalink
    def get_absolute_url(self):
        return ('aa-resource-sniff', (str(self.id), ))

    @classmethod
    def get_or_create_from_url(cls, url, reload=False):
        """ 
        Retrieves the resource, or creates it -- if possible (if matching)
        Returns object, created
        NB: Object may be None for non-matching URLs (in which case created will always be False)
        """
        try:
            # SHOULD MAYBE CONVERT URL to id,
            # then search on flickrid NOT page_url
            ret = cls.objects.get(url=url)
            if reload:
                ret.sync()
            return ret, False
        except cls.DoesNotExist:
            pass

        ret = Resource.objects.create(url=url)
        ret.sync()
        return ret, True

    def load_data(self):
        r = resource_opener.ResourceOpener(url=self.url)
        r.get()
        return r

    def sync(self, data=None):
        try:
            if data == None:
                data = self.load_data()
                data.file.close()  # ? better to do this here ?
            # data is an instance of ResourceOpener
            self.content_type = data.content_type
            self.charset = data.charset
            self.content_length = data.content_length
            self.last_modified = data.last_modified
            self.etag = data.etag
            self.status = data.status
            self.save()
        except urllib2.HTTPError, e:
            self.status = e.code
            self.save()
        # request reindex (via signal)
        reindex_request.send(sender=self.__class__, instance=self)

    def get_about_url(self):
        """ this gets used to do reverse lookup to resource """
        return self.url

    @staticmethod
    def get_url_from_local_path(path):
        # TODO: decide if it should be cached in a field or not
        # FIXME: make it more robust
        p = re.search(r"\d{6}", path)
        if p:
            return Resource.objects.get(id=p.group()).url
        else:
            return None

    @staticmethod
    def get_local_path_from_url(url):
        return os.path.join(settings.MEDIA_ROOT, url)

    def foo(self):
        return "%06d" % self.id
        
    def get_local_file(self, forcereload=False):
        """
        Returns: an absolute path to a local file (if available)
        Throws: AAWait when local file is not (yet) available
        """
        # local_dir = os.path.join(CACHE_DIR, "{:06d}".format(self.id))
        #import pdb; pdb.set_trace()
        local_dir = os.path.join(CACHE_DIR, "%06d" % self.id)
        try:
            os.makedirs(local_dir)
        except OSError:
            pass

        local_path = os.path.join(local_dir, "original" + os.path.splitext(self.url)[1])
        if forcereload or (not os.path.exists(local_path)):
            outfile = open(local_path, "wb")
            src = resource_opener.ResourceOpener(self.url)
            src.writeToFile(outfile)
        return local_path

    def get_local_url(self):
        self.get_local_file()  # Ugly hack to cache the file
        local_dir = os.path.join(CACHE_URL, "%06d" % self.id)
        local_url = os.path.join(local_dir, "original" + os.path.splitext(self.url)[1])
        return local_url

    def get_metadata(self, rel=None, rdfmodel=None):
        """
        Returns: a dictionary of key-value pairs (where keys are RDF style URLs)
        Throws: AAWait when not yet available.
        """
        if rdfmodel == None:
            rdfmodel = aacore.utils.get_rdf_model()
        if rel:
            query = """SELECT DISTINCT ?obj 
                    WHERE {{ <%s> <%s> ?obj. }} 
                    ORDER BY ?rel ?obj
                    """ % (self.url, rel)

            query = query.encode("utf-8")
            bindings = RDF.Query(query, query_language="sparql").execute(rdfmodel)
            ret = []
            for row in bindings:
                ret.append(rdfnode(row['obj']))
            return ret


class ResourceDelegate (models.Model):
    """
    Resources can be related to one or more delegates;
    Delegates are instances of a Model from an "AAPP" (plugin),
    providing content/tool-specific views & filters & scripts
    """
    resource = models.ForeignKey(Resource, related_name="delegates")
    delegate_type = models.ForeignKey(ContentType)
    delegate_id = models.PositiveIntegerField()
    delegate = generic.GenericForeignKey('delegate_type', 'delegate_id')


class Namespace (models.Model):
    """
    Defines RDF namespaces and assigns colors. 
    """
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    color = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.name


SORTKEY_CHOICES = (
    ("default", "default"),
    ("lastword", "last word (name)")
)


RDF_SOURCE_FORMAT_CHOICES = (
    ("rdfxml", "RDF/XML"),
    ("rdfa", "RDFA"),
)


class RDFDelegate (models.Model):
    """
    AA Delegate for a URL that itself directly contains RDF-encoded data (such
    as an RDF/XML file, or an HTML file with RDFA embedded within it).
    """

    url = models.URLField(verify_exists=False)
    format = models.CharField(max_length=255, choices=RDF_SOURCE_FORMAT_CHOICES)

    @models.permalink
    def get_absolute_url(self):
        return ('aa-rdf-source', (str(self.id), ))

    @classmethod
    def get_or_create_from_url(cls, url, request=None, reload=False):
        try:
            # normalize the url to strip off hash fragment
            ret = cls.objects.get(url=url)
            if reload:
                ret.sync()
            return ret, False
        except cls.DoesNotExist:
            r = resource_opener.ResourceOpener(url)
            try:
                r.get()
                r.file.close()
                if (r.content_type == "application/rdf+xml"):
                    ret = cls.objects.create(url=url, format="rdfxml")
                    return ret, True
            except urllib2.HTTPError:
                pass
            return None, False

    def sync(self):
        # request reindex (via signal)
        reindex_request.send(sender=self.__class__, instance=self)
        
    def get_rdf_as_stream(self):
        uri = prep_uri(self.url)
        parser = RDF.Parser(self.format.encode("utf-8"))
        # stream = parser.parse_as_stream(uri, uri)
        return parser.parse_as_stream(uri)

##############################################
# SIGNALS
##############################################
#
# (1) Creates the "reindex_request" signal to:
#     Allow Indexed Models or Delegates to request (re)indexing of their RDF,
# (2) Watches indexed models/delegates post_delete signal to:
#     Clear RDF index related to Delegate instances when deleted
#
# NB: Delegates must themselves request reindexing by
# sending the reindex_request signal, for example:
#
# from aacore.models import reindex_request
# def some_method(self):
#     ...
#     reindex_request.send(sender=self.__class__, instance=self)

reindex_request = django.dispatch.Signal(providing_args=[])

def indexing_reindex_item (item):
    rdfmodel = aacore.utils.get_rdf_model()
    full_url = aacore.utils.full_site_url(item.get_absolute_url())
    if hasattr(item, 'get_rdf_as_stream'):
        # in a way the URL here is the resource.url directly ?!
        stream = item.get_rdf_as_stream()
        context = RDF.Node(full_url)
        rdfmodel.context_remove_statements(context=context)
        rdfmodel.add_statements(stream, context=context)
    else:
#        # FOR DEBUGGING
#        resp = utils.direct_get_response(item.get_absolute_url())
#        page = resp.content
#        rdfaparser = RDF.Parser("rdfa")
#        furl = utils.full_site_url(item.get_absolute_url())
#        s = rdfaparser.parse_string_as_stream(page, furl)
#        print "RDFA:", (len(list(s))), "triples"

        aacore.utils.parse_localurl_into_model(rdfmodel, full_url, format="rdfa", baseuri=full_url, context=full_url)
    # rdfmodel.sync()

def indexing_drop_item (item):
    rdfmodel = aacore.utils.get_rdf_model()
    full_url = aacore.utils.full_site_url(item.get_absolute_url())
    rdfutils.rdf_context_remove_statements (rdfmodel, full_url)
    # rdfmodel.sync()

def indexing_post_delete(sender, instance, **kwargs):
    indexing_drop_item(instance)

def indexing_reindex(sender, instance, **kwargs):
    indexing_reindex_item(instance)

for model in aacore.utils.get_indexed_models():
    reindex_request.connect(indexing_reindex, sender=model, dispatch_uid="aa-indexer")
    post_delete.connect(indexing_post_delete, sender=model, dispatch_uid="aa-indexer")


