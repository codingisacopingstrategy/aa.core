from django.contrib import admin
from models import *

class AssetAdmin(admin.ModelAdmin):
    list_display = ("url", "title", "mediatype", "files_count")
    # list_display_links = ("flickrid", "name", "url")
    list_filter = ("license", "mediatype", )
admin.site.register(Asset, AssetAdmin)

class FileAdmin(admin.ModelAdmin):
    list_display = ("asset", "filename", "source", "size", "original", "format")
    # list_display_links = ("flickrid", "name", "url")
    list_filter = ("source", )
admin.site.register(File, FileAdmin)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ("asset", "reviewtitle", "reviewbody", "reviewer", "reviewdate", "stars", "editedby")
    # list_display_links = ("flickrid", "name", "url")
admin.site.register(Review, ReviewAdmin)

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "assets_count")
    # list_display_links = ("flickrid", "name", "url")
admin.site.register(User, UserAdmin)

class CollectionAdmin(admin.ModelAdmin):
    list_display = ("shortname", "fullname", "url", "assets_count")
    # list_display_links = ("flickrid", "name", "url")
admin.site.register(Collection, CollectionAdmin)

class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "assets_count")
    # list_display_links = ("flickrid", "name", "url")
admin.site.register(Subject, SubjectAdmin)

class MediaTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "assets_count")
    # list_display_links = ("flickrid", "name", "url")
admin.site.register(MediaType, MediaTypeAdmin)

