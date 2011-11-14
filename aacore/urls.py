from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.views.generic.simple import direct_to_template


urlpatterns = patterns('aacore.views',
    ### BROWSER
    url(r'^browse/$', 'browse', {}, name='aa-browse'),
    url(r'^colors.css$', 'colors_css', {}, name='aa-colors-css'),
    url(r'^resources/$', 'resources', {}, name='aa-resources'),
    url(r'^resources/(?P<id>\d+)/$', 'resource_sniff', {}, 'aa-resource-sniff'),
    url(r'^rdfdelegate/(?P<id>\d+)/$', 'rdf_delegate', {}, name='aa-rdf-source'),

    ### WIKI
    url(r'^$', redirect_to, {'url': '/pages/Index/'}),
    url(r'^pages/$', redirect_to, {'url': '/pages/Index/'}),
    url(r'^pages/(?P<slug>[^/]+)/$', 'page_detail', {}, name='aa-page-detail'),
    url(r'^pages/(?P<slug>[^/]+)/edit/$', 'page_edit', {}, name='aa-page-edit'),
    url(r'^pages/(?P<slug>[-\w]+)/history/$', 'page_history', {}, name='aa-page-history'),

    ### EMBED
    url(r'^embed/$', 'embed', {}, name='aa-embed'),

    ### SANDBOX
    url(r'^sandbox/$', 'sandbox', {}, name='aa-sandbox'),

    ### RDF ###
    (r'^rdf/', include('aacore.rdfviews')),
)
