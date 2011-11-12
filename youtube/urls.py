from django.conf.urls.defaults import *


urlpatterns = patterns('youtube.views',
    url(r'^video/(?P<id>\d+)/$', 'video', {}, name='aa-youtube-video'),
)

