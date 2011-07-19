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
