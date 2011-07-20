from django.contrib import admin
from models import *


class ResourceAdmin(admin.ModelAdmin):
    list_display = ('url', )

admin.site.register(Resource, ResourceAdmin)


class RelationshipAdmin(admin.ModelAdmin):
    list_display = ('url', 'compacturl', '_type')
    list_editable = ('_type',)

admin.site.register(Relationship, RelationshipAdmin)


class RelationshipNamespaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')

admin.site.register(RelationshipNamespace, RelationshipNamespaceAdmin)
