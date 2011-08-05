from django.db import models
import aacore.templatetags.aatags
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
import time

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
    """ This exception is used when a resource is not yet available.
    The URL is a special "task-tracking" URL that can be used to poll until task is done.
    (Returns a JSON object with a "done" boolean value.)
    """
    def __init__ (self, url):
        self.url = url

class AANotAvailable (Exception):
    pass


class Resource (models.Model):
    """ Resource is the main class of AA. In a nutshell: a resource is an (augmented) URL """
    url = models.URLField(verify_exists=False)
    # pipeline = models.CharField(max_length=1024, blank=True)

    content_type = models.CharField(max_length=255, default="", blank=True)
    content_length = models.IntegerField(default=0)
    charset = models.CharField(max_length=64, default="", blank=True)
    last_modified = models.DateTimeField(null=True, blank=True)
    etag = models.CharField(max_length=255, default="", blank=True)

    status = models.CharField(max_length=255, choices=RESOURCE_STATUS, default="default")
    _type = models.CharField(max_length=255, choices=RESOURCE_TYPES, blank=True)

    def getLocalFile (self):
        """
        Return: an absolute path to a local file (if available)
        Throws: AAWait when local file is not (yet) available
        """
        pass

    def getMetadata (self):
        """
        Returns: a dictionary of key-value pairs (where keys are RDF style URLs)
        Throws: AAWait when not yet available.
        """
        pass

    def task (self):
        time.sleep(15)
        return "OK!"

import djangotasks
djangotasks.register_task(Resource.task, "Test task for resource")

############################
# PAGES 
############################

class Page(models.Model):
    """Wiki pages"""
    name = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('aa-page-detail')


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
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)

    def __unicode__ (self):
        return self.name


class Relationship (models.Model):
    url = models.CharField(max_length=255)
    _type = models.CharField(max_length=255, choices=RELTYPES, default="uri", blank=False)
    name = models.CharField(max_length=255, blank=True)
    name_plural = models.CharField(max_length=255, blank=True)
    reverse_name = models.CharField(max_length=255, blank=True)
    facet = models.BooleanField(default=False)

    class Meta:
        ordering = ("name", )

    @property
    def compacturl(self):
        return aacore.templatetags.aatags.compactnamespace(self.url)

    def __unicode__ (self):
        return self.url

