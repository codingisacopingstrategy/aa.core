from django.contrib import admin
from models import *

class MediaAdmin(admin.ModelAdmin):
    list_display = ("url", "duration", "video_codec", "width", "height", "framerate", "audio_codec", "audio_bits", "audio_sampling_rate", "audio_channels", "audio_bitrate")
    # list_display_links = ("flickrid", "name", "url")
admin.site.register(Media, MediaAdmin)

