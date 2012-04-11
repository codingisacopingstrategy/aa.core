from django.conf.urls.defaults import *


urlpatterns = patterns('aacore.views',
    ### BROWSER
    url(r'^browse/$', 'browse', {}, name='aa-browse'),
    url(r'^colors.css$', 'colors_css', {}, name='aa-colors-css'),
    url(r'^resources/$', 'resources', {}, name='aa-resources'),
    url(r'^resources/(?P<id>\d+)/$', 'resource_sniff', {}, 'aa-resource-sniff'),
    url(r'^rdfdelegate/(?P<id>\d+)/$', 'rdf_delegate', {}, name='aa-rdf-source'),
)
