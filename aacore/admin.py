from django.contrib import admin
from models import *


class RelationshipAdmin(admin.ModelAdmin):
    list_display = ('url', 'compacturl', '_type')
    list_editable = ('_type',)


class RelationshipNamespaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')


admin.site.register(Relationship, RelationshipAdmin)
admin.site.register(RelationshipNamespace, RelationshipNamespaceAdmin)
