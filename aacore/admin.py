from django.contrib import admin
from aacore.models import (Resource, ResourceDelegate, Namespace, RDFDelegate)


admin.site.register(ResourceDelegate)

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

class RDFDelegateAdmin(admin.ModelAdmin):
    list_display = ("url", "format")
admin.site.register(RDFDelegate, RDFDelegateAdmin)
