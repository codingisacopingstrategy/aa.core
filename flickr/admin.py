from django.contrib import admin
from models import *

class TagAdmin(admin.ModelAdmin):
    list_display = ("slug", "admin_count")
    search_fields = ("slug", )
admin.site.register(Tag, TagAdmin)

class UserAdmin(admin.ModelAdmin):
    list_display = ("flickrid", "path_alias", "username", "realname", "location", "ispro", "photos_count", "photos_first_date_taken")
admin.site.register(User, UserAdmin)

class PhotoAdmin(admin.ModelAdmin):
    list_display = ("wiki_reference", "admin_thumbnail", "page_url", "title", "date_taken", "date_posted", "description", "license")
    # filter_horizontal = ("tags", )
    raw_id_fields = ("owner", )
    date_hierarchy = "date_taken"
    list_display_links = ("wiki_reference", )
    list_filter = ("license", )
    search_fields = ("title", "description", )
admin.site.register(Photo, PhotoAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ("photo", "body")
admin.site.register(Comment, CommentAdmin)

#class ExifAdmin(admin.ModelAdmin):
#    list_display = ("photo", "tagspace", "tag", "content")
#    list_filter = ("tagspace", "tag", )
#    search_fields = ("tag", "content", "tagspace")
#admin.site.register(Exif, ExifAdmin)

class LicenseAdmin(admin.ModelAdmin):
    list_display = ("flickrid", "name", "url", "admin_count")
    list_display_links = ("flickrid", "name", "url")
admin.site.register(License, LicenseAdmin)

