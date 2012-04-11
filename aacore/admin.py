# This file is part of Active Archives.
# Copyright 2006-2011 the Active Archives contributors (see AUTHORS)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Also add information on how to contact you by electronic and paper mail.


"""
Active Archives aacore admin site.
"""


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
