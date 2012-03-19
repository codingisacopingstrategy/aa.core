from django.conf.urls.defaults import *


urlpatterns = patterns('aacore.views',
    ### BROWSER
    url(r'^browse/$', 'browse', {}, name='aa-browse'),
    url(r'^namespaces.css/$', 'namespaces_css', {}, name='aa-namespaces-css'),
    url(r'^resources/$', 'resources', {}, name='aa-resources'),
    url(r'^resources/(?P<id>\d+)/$', 'resource_sniff', {}, 'aa-resource-sniff'),
    url(r'^rdfdelegate/(?P<id>\d+)/$', 'rdf_delegate', {}, name='aa-rdf-source'),
)
urlpatterns += patterns('aacore.rdfviews',
    url(r'^reindex/$', 'reindex', {}, name='aa-rdf-reindex'),
    url(r'^dump/$', 'dump', {}, name='aa-rdf-dump'),
    url(r'^query/$', 'query', {}, name='aa-rdf-query'),
    #url(r'^browse/$', 'browse', {}, name='aa-rdf-browse'),
)
