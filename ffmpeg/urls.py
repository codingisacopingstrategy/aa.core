from django.conf.urls.defaults import *


urlpatterns = patterns('ffmpeg.views',
    url(r'^media/(?P<id>\d+)/$', 'media', {}, name='aa-ffmpeg-media'),
)


