from django.conf.urls.defaults import *


urlpatterns = patterns('aacore.views',
    # url(r'^$', 'foo', {}, name='aa-foo'),
    url(r'^sniff/$', 'sniff', {}, name='aa-sniff'),
    url(r'^pages/$', 'page_list', {}, name='aa-page-list'),
    url(r'^pages/(?P<slug>[-\w]+)/$', 'page_detail', {}, name='aa-page-detail'),
    url(r'^sandbox/$', 'sandbox', {}, name='aa-sandbox'),
    url(r'^rdfdump/$', 'rdfdump', {}, name='aa-rdf-dump'),
    url(r'^import/$', '_import', {}, name='aa-import'),
)
