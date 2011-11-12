from django.conf.urls.defaults import *


urlpatterns = patterns('internetarchive.views',
    url(r'^asset/(?P<id>\d+)/$', 'asset', {}, name='aa-internetarchive-asset'),
)


