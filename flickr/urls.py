from django.conf.urls.defaults import *


urlpatterns = patterns('flickr.views',
    url(r'^photo/(?P<id>\d+)/$', 'photo', {}, name='aa-flickr-photo'),
)


