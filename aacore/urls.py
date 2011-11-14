from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.views.generic.simple import direct_to_template


urlpatterns = patterns('aacore.views',
    ### RESOURCE ###
    url(r'^resource/(?P<id>\d+)/$', 'resource_sniff', {}, 'aa-resource-sniff'),
    url(r'^rdfsource/(?P<id>\d+)/$', 'rdf_source', {}, name='aa-rdf-source'),

    ### WIKI
    url(r'^$', redirect_to, {'url': '/pages/Index/'}),
    url(r'^pages/$', redirect_to, {'url': '/pages/Index/'}),
    url(r'^pages/(?P<slug>[^/]+)/$', 'page_detail', {}, name='aa-page-detail'),
    url(r'^pages/(?P<slug>[^/]+)/edit/$', 'page_edit', {}, name='aa-page-edit'),
    url(r'^pages/(?P<slug>[-\w]+)/history/$', 'page_history', {}, name='aa-page-history'),

    ### EMBED
    url(r'^embed.js$', 'embed_js', {}, name='aa-embed-js'),
    url(r'^embed/$', 'embed', {}, name='aa-embed'),
    url(r'^embed_jsonp.js$', 'embed_jsonp_js', {}, name='aa-embed-jsonp-js'),
    url(r'^embed_jsonp/$', 'embed_jsonp', {}, name='aa-embed-jsonp'),

    ### BROWSER
    url(r'^browse/$', 'browse', {}, name='aa-browse'),
    url(r'^resources/$', 'resources', {}, name='aa-resources'),
    url(r'^colors.css$', 'colors_css', {}, name='aa-colors-css'),

    ### SANDBOX
    url(r'^sandbox/$', 'sandbox', {}, name='aa-sandbox'),

    ### RDF ###
    (r'^rdf/', include('aacore.rdfviews')),
)
