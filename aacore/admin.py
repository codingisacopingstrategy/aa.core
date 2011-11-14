from django.contrib import admin
from django.contrib.contenttypes import generic

from models import *


admin.site.register(ResourceDelegate)


class LicenseAdmin(admin.ModelAdmin):
    list_display = ("name", "url")
admin.site.register(License, LicenseAdmin)


class ResourceDelegateInline(admin.TabularInline):
    model = ResourceDelegate
    extra = 0
    max_num = 0


class ResourceAdmin(admin.ModelAdmin):
    list_display = ('url', 'content_type', 'charset', 'content_length', 'last_modified', 'etag')
    inlines = (ResourceDelegateInline, )
admin.site.register(Resource, ResourceAdmin)


class NamespaceAdmin(admin.ModelAdmin):
    ordering = ("name", )
    list_display = ("name", "url", "color")
    search_fields = ("name", "url")
    list_editable = ("color", )
admin.site.register(Namespace, NamespaceAdmin)


class RelationshipAdmin(admin.ModelAdmin):
    ordering = ("order", "name")
    list_display = ("order", "facet", "autotag", "name", "name_plural", "sort_key", "url")
    list_display_links = ("url", )
    list_editable = ("order", "facet", "autotag", "name", "name_plural", "sort_key")
admin.site.register(Relationship, RelationshipAdmin)


class PageAdmin(admin.ModelAdmin):
    list_display = ("name", "content", )
    search_fields = ("name", "content")
admin.site.register(Page, PageAdmin)


class RDFSourceAdmin(admin.ModelAdmin):
    list_display = ("url", "format")
admin.site.register(RDFSource, RDFSourceAdmin)
