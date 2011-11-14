from django.contrib import admin
from models import *

# from django.contrib.contenttypes.generic import GenericTabularInline, GenericStackedInline
from django.contrib.contenttypes import generic


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
    # search_fields = ("url", "name")
    # prepopulated_fields = {"slug": ("name",)}
    list_display_links = ("url", )
    list_editable = ("order", "facet", "autotag", "name", "name_plural", "sort_key")
admin.site.register(Relationship, RelationshipAdmin)


#def garbage_collect_tags (modeladmin, request, queryset):
#    """ warning, now works irregardless of queryset (selected items) """
#    modeladmin.model.objects.filter(refs=None).delete()
#garbage_collect_tags.short_description = "Delete unreferenced tags"

class PageAdmin(admin.ModelAdmin):
    list_display = ("name", "content", )
    search_fields = ("name", "content")

admin.site.register(Page, PageAdmin)

admin.site.register(ResourceDelegate)

class RDFSourceAdmin(admin.ModelAdmin):
    list_display = ("url", "format")
admin.site.register(RDFSource, RDFSourceAdmin)

