from django.db import models
import aacore.templatetags.aatags
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

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
    class Meta:
        ordering = ("name", )
    url = models.CharField(max_length=255)
    _type = models.CharField(max_length=255, choices=RELTYPES, default="uri", blank=False)
    name = models.CharField(max_length=255, blank=True)
    name_plural = models.CharField(max_length=255, blank=True)
    reverse_name = models.CharField(max_length=255, blank=True)
    facet = models.BooleanField(default=False)

    @property
    def compacturl(self):
        return aacore.templatetags.aatags.compactnamespace(self.url)

    def __unicode__ (self):
        return self.url

#    order = models.IntegerField(default=100)
#    sort_key = models.CharField(max_length=255, default="default", choices=SORTKEYS)
#    autotag = models.BooleanField(default=False)

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

#class Resource (models.Model):
#    url = model.CharField(max_length=255)
#    status = models.CharField(max_length=16, choices=RESOURCE_STATUS, default="default")

#    url = models.URLField(verify_exists=False)
#    filename = models.CharField(max_length=255, blank=True)
#    hostname = models.CharField(max_length=255, blank=True)
#    content_type = models.CharField(max_length=255, default="", blank=True)
#    content_length = models.IntegerField(default=0)
#    charset = models.CharField(max_length=64, default="", blank=True)
#    last_modified_raw = models.CharField(max_length=255, default="", blank=True)
#    last_modified = models.DateTimeField(null=True, blank=True)
#    etag = models.CharField(max_length=255, default="", blank=True)
#    
#    object_type = models.ForeignKey(ContentType, null=True, blank=True)
#    object_id = models.PositiveIntegerField(null=True, blank=True)
#    content = generic.GenericForeignKey('object_type', 'object_id')

#    last_contact = models.DateTimeField(null=True, blank=True)
#    last_downloaded = models.DateTimeField(null=True, blank=True)

#    rtype = models.CharField(max_length=255, choices=RESOURCE_TYPES, blank=True)

#    top = models.IntegerField(default=0)
#    left = models.IntegerField(default=0)
#    width = models.IntegerField(default=320)
#    height = models.IntegerField(default=320)

#    db_creator = models.ForeignKey(User, null=True, blank=True, related_name="resources_as_creator")
#    db_created = models.DateTimeField(auto_now_add=True)
#    db_lastmodifier = models.ForeignKey(User, null=True, blank=True, related_name="resources_as_lastmodifier")
#    db_lastmodified = models.DateTimeField(auto_now=True)

#    def __unicode__ (self):
#        return self.url

