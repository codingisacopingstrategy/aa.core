import RDF
import codecs
import os, os.path, urllib2
from git import Repo, NoSuchPathError
import cStringIO
from ConfigParser import ConfigParser

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

import utils
from rdfutils import rdfnode, prep_uri
from settings import CACHE_DIR
import resource_opener
from settings import GIT_DIR

############################
# License
############################

class License (models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(blank=True, verify_exists=False)
    redirect = models.ForeignKey('self', null=True, blank=True)

    def __unicode__(self):
        return self.name


############################
# RESOURCE
############################

RESOURCE_TYPES = (
    ('audio', 'audio'),
    ('video', 'video (no audio)'),
    ('audio/video', 'video'),
    ('image', 'image'),
    ('html', 'html'),
    ('text', 'text'),
    ('', '')
)

RESOURCE_STATUS = (
    ('active', 'active'),
    ('default', 'default'),
    ('inactive', 'inactive')
)


class AAWait (Exception):
    """
    This exception is used when a resource is not yet available.  The URL is a
    special "task-tracking" URL that can be used to poll until task is done.
    (Returns a JSON object with a "done" boolean value.)
    """
    def __init__(self, url):
        self.url = url


class AANotAvailable (Exception):
    pass

class Resource (models.Model):
    @classmethod
    def get_or_create_from_url(cls, url, reload=False):
        try:
            # SHOULD MAYBE CONVERT URL to id, then search on flickrid NOT page_url
            ret = cls.objects.get(url=url)
            if reload:
                ret.sync()
            return ret, False
        except cls.DoesNotExist:
            pass        

        ret = Resource.objects.create(url=url)
        ret.sync()
        return ret, True

    """
    Resource is the main class of AA.
    In a nutshell: a resource is an (augmented) URL.
    """
    url = models.URLField(verify_exists=False)
    _filter = models.CharField(max_length=1024, blank=True)
    primary = models.BooleanField(default=True)
    redirect = models.ForeignKey('self', null=True, blank=True)

    content_type = models.CharField(max_length=255, default="", blank=True)
    content_length = models.IntegerField(default=0)
    charset = models.CharField(max_length=64, default="", blank=True)
    last_modified = models.DateTimeField(null=True, blank=True)
    etag = models.CharField(max_length=255, default="", blank=True)

    status = models.CharField(max_length=255, choices=RESOURCE_STATUS, default="default")
    _type = models.CharField(max_length=255, choices=RESOURCE_TYPES, blank=True)

    def __unicode__(self):
        return self.url

    def load_data (self):
        r = resource_opener.ResourceOpener(url=self.url)
        r.get()
        return r

    def sync(self, data=None):
        try:
            if data == None:
                data = self.load_data()
                data.file.close() # ? better to do this here ?
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

    @models.permalink
    def get_absolute_url(self):
        return ('aa-resource-sniff', (str(self.id), ))

    def get_about_url(self):
        """ this gets used to do reverse lookup to resource """
        return self.url

    def getLocalFile(self, forcereload=False):
        """
        Returns: an absolute path to a local file (if available)
        Throws: AAWait when local file is not (yet) available
        """
        localdir = os.path.join(CACHE_DIR, "{:06d}".format(self.id))
        try:
            os.makedirs(localdir)
        except OSError:
            pass
        localpath = os.path.join(localdir, "original.data")
        if forcereload or (not os.path.exists(localpath)):
            outfile = open(localpath, "wb")
            src = resource_opener.ResourceOpener(self.url)
            src.writeToFile(outfile)
        return localpath

    def getMetadata(self, rel=None, rdfmodel=None):
        """
        Returns: a dictionary of key-value pairs (where keys are RDF style URLs)
        Throws: AAWait when not yet available.
        """
        if rdfmodel == None:
            rdfmodel = get_rdf_model()
        if rel:
            query = "SELECT DISTINCT ?obj WHERE {{ <{0}> <{1}> ?obj. }} ORDER BY ?rel ?obj".format(self.url, rel)
            query = query.encode("utf-8")
            bindings = RDF.Query(query, query_language="sparql").execute(rdfmodel)
            ret = []
            for row in bindings:
                ret.append(rdfnode(row['obj']))
            return ret

############################
# ResourceDelegate
############################

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


############################
# Collection
############################

class Collection (models.Model):
    """
    Collections are used by the gallery views to provide simple "star" and other named collections/playlists of resources
    Collection membership includes order, fragment, and text fields.
    """
    name = models.CharField(max_length=255)
    star = models.BooleanField(default=False)
    owner = models.ForeignKey(User, null=True, related_name="collections")
    resources = models.ManyToManyField(Resource, through='CollectionItem', related_name="collections")
    # items (provided by CollectionItem)

    db_created = models.DateTimeField(auto_now_add = True)
    db_lastmodified = models.DateTimeField(auto_now = True)

class CollectionItem (models.Model):
    class Meta:
        ordering = ("order", "db_created")

    collection = models.ForeignKey(Collection, related_name = "items")
    resource = models.ForeignKey(Resource, related_name = "collectionitems")
    author = models.ForeignKey(User, null=True)
    order = models.IntegerField(null=True, blank=True, default=1e10)
    fragment = models.CharField(max_length=255, blank=True)
    text = models.TextField()

    db_created = models.DateTimeField(auto_now_add = True)
    db_lastmodified = models.DateTimeField(auto_now = True)



############################
# PAGE
############################


class Page(models.Model):
    """
    This is the model class for Wiki pages.
    It might move away from core in the future.
    """
    name = models.CharField(max_length=255)
    content = models.TextField(blank=True)

    @property
    def slug(self):
        """
        Returns the wikified name of the page.
        """
        return utils.wikify(self.name)

    def get_repository(self):
        try:
            repo = Repo(GIT_DIR)
        except NoSuchPathError:
            repo = Repo.init(GIT_DIR)
        return repo 

    def iter_commits(self):
        repo = self.get_repository()
        return repo.iter_commits(paths=self.slug)

    def commit(self, message="No message", author="Anonymous <anonymous@127.0.0.1>", is_minor=False):
        """
        Commits page content and saves it it in the database.
        """
        # Makes sure the content ends with a newline
        if self.content[-1] != "\n":
            self.content += "\n"

        repo = self.get_repository()

        # Writes content to the CONTENT file
        path = os.path.join(GIT_DIR, self.slug)
        f = codecs.open(path, "w", "utf-8")
        f.write(self.content)
        f.close()

        # Adds the newly creates files and commits
        repo.index.add([self.slug,])
        repo.git.commit(message=message, author=author)

        # Add the commit metadata in a git note, formatted as
        # a .ini config file 
        config = ConfigParser()
        config.add_section('metadata')
        config.set('metadata','is_minor', is_minor)

        output = cStringIO.StringIO()
        config.write(output)
        repo.git.notes(["add", "--message=%s" % output.getvalue()], ref="metadata")

        self.save()


    @models.permalink
    def get_history_url(self):
        return ("aa-page-history", (), {'slug': utils.wikify(self.name)})

    @models.permalink
    def get_edit_url(self):
        return ("aa-page-edit", (), {'slug': utils.wikify(self.name)})

    @models.permalink
    def get_absolute_url(self):
        return ("aa-page-detail", (), {'slug': utils.wikify(self.name)})

    def __unicode__(self):
        return self.name

#from django.db.models.signals import post_save
#from django.dispatch import receiver
#from core.utils import get_rdf_model, reindex

#@receiver(post_save, sender=Page)
#def page_post_save(sender, instance, **kwargs):
#    rdfmodel = get_rdf_model()
#    reindex(instance, rdfmodel)


######################################
# NAMESPACE
######################################

class Namespace (models.Model):
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    color = models.CharField(max_length=255, blank=True)

    def __unicode__ (self):
        return self.name

######################################
# LANGUAGE
######################################

class Language (models.Model):
    class Meta:
        ordering = ("name",)
    name = models.CharField(max_length=255)
    def __unicode__ (self):
        return self.name

######################################
# RELATIONSHIP
######################################

SORTKEYS = (
    ("default", "default"),
    ("lastword", "last word (name)")
)

class Relationship (models.Model):
    class Meta:
        ordering = ("order", "name")
    url = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True)
    reverse_name = models.CharField(max_length=255, blank=True)
    name_plural = models.CharField(max_length=255, blank=True)
    facet = models.BooleanField(default=False)
    order = models.IntegerField(default=100)

    sort_key = models.CharField(max_length=255, default="default", choices=SORTKEYS)
    autotag = models.BooleanField(default=False)

    def parseValue (self, val):
        """ take a URL value and return an N3 representation ? """
        return ""

    def compact_url (self):
        for ns in Namespace.objects.all():
            if self.url.startswith(ns.url):
                return ns.name + ":" + self.url[len(ns.url):]
        return self.url

    @models.permalink
    def get_absolute_url(self):
        return ('core.views.rel', [self.id])


######################################
# RDFSource
######################################

RDF_SOURCE_FORMATS = (
    ("rdfxml", "RDF/XML"),
    ("rdfa", "RDFA"),
)

class RDFSource (models.Model):
    """
    An RDF Source represents a URL that itself directly contains RDF-encoded data 
    (such as an RDF/XML file, or an HTML file with RDFA embedded within it)
    """

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
            except urllib2.HTTPError, e:
                pass
            return None, False

    url = models.URLField(verify_exists=False)
    format = models.CharField(max_length=255, choices=RDF_SOURCE_FORMATS)

    @models.permalink
    def get_absolute_url(self):
        return ('aa-rdf-source', (str(self.id), ))

    def sync(self):
        pass

    def get_rdf_as_stream (self):
        uri = prep_uri(self.url)
        parser=RDF.Parser(self.format.encode("utf-8"))
        # stream = parser.parse_as_stream(uri, uri)
        return parser.parse_as_stream(uri)



######################################
# COMMAND
######################################

class Command (models.Model):   
    """ Commands represent a queue for batch actions to be preformed asynchronously
    ref: (optional) code to coordinate commands (ie possible prevent duplicate commands)
    """
    ref = models.CharField(max_length=255)
    text = models.TextField()
    creator = models.ForeignKey(User)
    started = models.DateTimeField(null=True, blank=True)
    completed = models.DateTimeField(null=True, blank=True)
    results = models.TextField()

