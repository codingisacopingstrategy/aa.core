from django.contrib import admin
from models import *
import django

class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "admin_video_count" )
    search_fields = ("name", )
admin.site.register(Tag, TagAdmin)

class UserAdmin(admin.ModelAdmin):
    # list_display = ("admin_thumbnail", "username", "url", "related_url", "firstName", "lastName", "location", "age", "gender", "hobbies", "hometown", "subscriber_count", "view_count", "total_upload_views", "admin_video_count")
    list_display = ("admin_thumbnail", "username", "url", "location", "age", "gender", "subscriber_count", "view_count", "total_upload_views", "admin_video_count")
    search_files = ("username", "firstName", "lastName", "location")
admin.site.register(User, UserAdmin)

    
##################
class ThumbnailWidget(django.forms.Widget):
    def __init__(self, obj, attrs=None):
        self.object = obj
        super(ThumbnailWidget, self).__init__(attrs)
    
    def render(self, name, value, attrs=None):
        if self.object.url:
            return django.utils.safestring.mark_safe(u'<img src="%s" />' % (self.object.url))
        else:
            return django.utils.safestring.mark_safe(u'')

class VideoThumbnailForm(django.forms.ModelForm):
    thumbnail = django.forms.CharField(label='thumbnail', required=False)
    def __init__(self, *args, **kwargs):
        super(VideoThumbnailForm, self).__init__(*args, **kwargs)
        self.fields['thumbnail'].widget = ThumbnailWidget(self.instance)
##################

class VideoThumbnailInline(admin.TabularInline):
    form = VideoThumbnailForm
    model = VideoThumbnail
    extra = 0
    max_num = 0
    
class VideoAlternateFormatInline(admin.TabularInline):
    model = VideoAlternateFormat
    extra = 0
    max_num = 0

class VideoAdmin(admin.ModelAdmin):
    list_display = ("wiki_reference", "admin_thumbnail", "watch_url", "title", "duration", "published", "aspectRatio", "author", "license")
    filter_horizontal = ("tags", )
    raw_id_fields = ("author", "tags")
    date_hierarchy = "published"
    # list_display_links = ("youtubeid", "title")
    list_filter = ("license", )
    search_fields = ("title", )
    inlines = [VideoThumbnailInline, VideoAlternateFormatInline]

# admin.site.register(Video)
admin.site.register(Video, VideoAdmin)


