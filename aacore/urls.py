from django.conf.urls.defaults import (patterns, url)


urlpatterns = patterns('aacore.views',
    #url(r'^browse/$', 'browse', {}, name='aa-rdf-browse'),
    url(r'^browse/$', 'browse', {}, name='aa-browse'),
    url(r'^namespaces.css/$', 'namespaces_css', {}, name='aa-namespaces-css'),
    url(r'^resources/$', 'resources', {}, name='aa-resources'),
    url(r'^resources/(?P<id>\d+)/$', 'resource_sniff', {}, 'aa-resource-sniff'),
    url(r'^rdfdelegate/(?P<id>\d+)/$', 'rdf_delegate', {}, name='aa-rdf-source'),
    url(r'^reindex/$', 'reindex', {}, name='aa-rdf-reindex'),
    url(r'^dump/$', 'dump', {}, name='aa-rdf-dump'),
    url(r'^query/$', 'query', {}, name='aa-rdf-query'),
)
