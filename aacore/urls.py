from django.conf.urls.defaults import *

urlpatterns = patterns('aacore.views',
    url(r'^$', 'foo', {}, name='aa-foo'),
    url(r'^pages/$', 'foo', {}, name='aa-page-list'),
    url(r'^pages/(?P<slug>[-\w]+)/$', 'foo', {}, name='aa-foo'),
)
