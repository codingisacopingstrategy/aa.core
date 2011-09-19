from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to


urlpatterns = patterns('aacore.views',
    url(r'^$', redirect_to, {'url': '/pages/Index/'}),
    url(r'^pages/$', redirect_to, {'url': '/pages/Index/'}),
    url(r'^pages/(?P<slug>[-\w]+)/$', 'page_detail', {}, name='aa-page-detail'),
    url(r'^pages/(?P<slug>[-\w]+)/edit/$', 'page_edit', {}, name='aa-page-edit'),
    url(r'^sniff/$', 'sniff', {}, name='aa-sniff'),
    url(r'^sandbox/$', 'sandbox', {}, name='aa-sandbox'),
    url(r'^rdfdump/$', 'rdfdump', {}, name='aa-rdf-dump'),
    url(r'^import/$', '_import', {}, name='aa-import'),
)
