from django.conf.urls.defaults import *


urlpatterns = patterns('youtube.views',
    url(r'^video/(?P<id>\d+)/$', 'video', {}, name='aa-youtube-video'),
    url(r'^video/(?P<id>\d+)/embed/$', 'video_embed', {}, name='aa-youtube-video-embed'),
)

