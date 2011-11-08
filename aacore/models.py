import codecs
import os.path
from git import Repo, NoSuchPathError
import cStringIO
from ConfigParser import ConfigParser

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from utils import wikify
import aacore.templatetags.aatags
from settings import GIT_DIR

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
    """
    Resource is the main class of AA.
    In a nutshell: a resource is an (augmented) URL.
    """
    url = models.URLField(verify_exists=False)
    # pipeline = models.CharField(max_length=1024, blank=True)

    content_type = models.CharField(max_length=255, default="", blank=True)
    content_length = models.IntegerField(default=0)
    charset = models.CharField(max_length=64, default="", blank=True)
    last_modified = models.DateTimeField(null=True, blank=True)
    etag = models.CharField(max_length=255, default="", blank=True)

    status = models.CharField(max_length=255, choices=RESOURCE_STATUS, default="default")
    _type = models.CharField(max_length=255, choices=RESOURCE_TYPES, blank=True)

    def getLocalFile(self):
        """
        Returns: an absolute path to a local file (if available)
        Throws: AAWait when local file is not (yet) available
        """
        pass

    def getMetadata(self):
        """
        Returns: a dictionary of key-value pairs (where keys are RDF style URLs)
        Throws: AAWait when not yet available.
        """
        pass


############################
# PAGES
############################


class Page(models.Model):
    """
    This is the model class for Wiki pages.
    It might move away from aacore in the future.
    """
    name = models.CharField(max_length=255)
    content = models.TextField(blank=True)

    @property
    def slug(self):
        """
        Returns the wikified name of the page.
        """
        return wikify(self.name)

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
        return ("aa-page-history", (), {'slug': wikify(self.name)})

    @models.permalink
    def get_edit_url(self):
        return ("aa-page-edit", (), {'slug': wikify(self.name)})

    @models.permalink
    def get_absolute_url(self):
        return ("aa-page-detail", (), {'slug': wikify(self.name)})

    def __unicode__(self):
        return self.name


############################
# RELATIONSHIP
############################

RELTYPES = (
    ('uri', 'URI'),
    ('wikipage', 'WikiPage'),
    ('literal', 'Literal'),
    ('integer', 'Number (integer)'),
    ('float', 'Number (float)'),
    ('date', 'Date'),
    ('duration', 'Duration'),
    ('time', 'Time'),
    ('boolean', 'Boolean'),
)


class RelationshipNamespace (models.Model):
    """
    ...
    """
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Relationship (models.Model):
    """
    ...
    """
    url = models.CharField(max_length=255)
    _type = models.CharField(max_length=255, choices=RELTYPES, default="uri", blank=False)
    name = models.CharField(max_length=255, blank=True)
    name_plural = models.CharField(max_length=255, blank=True)
    reverse_name = models.CharField(max_length=255, blank=True)
    facet = models.BooleanField(default=False)

    class Meta:
        ordering = ("name",)

    @property
    def compacturl(self):
        return aacore.templatetags.aatags.compactnamespace(self.url)

    def __unicode__(self):
        return self.url
