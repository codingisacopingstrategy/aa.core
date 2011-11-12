from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.views.generic.simple import direct_to_template


urlpatterns = patterns('aacore.views',
    ### SANDBOX
    url(r'^sandbox/$', 'sandbox', {}, name='aa-sandbox'),

    ### RDF ###
    (r'^rdf/', include('aacore.rdfviews')),
    url(r'^rel/(?P<id>\d+)/$', 'rel', {}, name='aa-rdf-relation'),
    url(r'^resource/(?P<id>\d+)/$', 'resource_sniff', {}, 'aa-resource-sniff'),
    url(r'^rdfsource/(?P<id>\d+)/$', 'rdf_source', {}, name='aa-rdf-source'),

    ### WIKI
    url(r'^$', redirect_to, {'url': '/pages/Index/'}),
    url(r'^pages/$', redirect_to, {'url': '/pages/Index/'}),
    url(r'^pages/(?P<slug>[^/]+)/$', 'page_detail', {}, name='aa-page-detail'),
    # url(r'^pages/(?P<slug>[^/]+)/$', 'page_sarma', {}, name='aa-page-detail'),
    url(r'^pages/(?P<slug>[^/]+)/edit/$', 'page_edit', {}, name='aa-page-edit'),

    url(r'^pages/(?P<slug>[^/]+)/table/$', 'tag_table', {}, name='aa-tag-table'),
    url(r'^pages/(?P<slug>[^/]+)/graph/(?P<relid>\d+)/$', 'link_graph', {}, name='aa-link-graph'),

    ### EMBED
    url(r'^embed.js$', 'embed_js', {}, name='aa-embed-js'),
    url(r'^embed/$', 'embed', {}, name='aa-embed'),
    url(r'^embed_jsonp.js$', 'embed_jsonp_js', {}, name='aa-embed-jsonp-js'),
    url(r'^embed_jsonp/$', 'embed_jsonp', {}, name='aa-embed-jsonp'),

    ### BROWSER
    url(r'^browse/$', 'browse', {}, name='aa-browse'),
    url(r'^resources/$', 'resources', {}, name='aa-resources'),
    url(r'^mini/$', 'mini', {}, name='aa-mini-browser'),
    url(r'^mini/r/(?P<id>\d+)/$', 'mini_res', {}, name='aa-mini-res'),

    url(r'^colors.css$', 'colors_css', {}, name='aa-colors-css'),

#    url(r'^browse/(?P<id>\d+)/$', 'resource', {}, 'aa-resource'),
#    url(r'^browse/(?P<url>\w.+)$', 'resource', {}, 'aa-resource'),
#    url(r'^browse/(?P<id>\d+)/detail/$', 'resource_meta', {}, 'aa-resource-meta'),
#    url(r'^browse/(?P<id>\d+)/export/$', 'resource_export', {}, 'aa-resource-export'),
#    url(r'^browse/(?P<id>\d+)/star/$', 'resource_star', {}, 'aa-resource-star'),
#    url(r'^browse/(?P<id>\d+)/addtocollection/$', 'resource_addtocollection', {}, 'aa-resource-addtocollection'),
#    url(r'^tags/$', 'tags', {}, 'aa-tags'),
#    url(r'^tags/(?P<id>\d+)/$', 'tag', {}, 'aa-tag'),
#    url(r'^starred/$', 'starred', {}, 'aa-starred'),
#    url(r'^collections/$', 'collections', {}, 'aa-collections'),
#    url(r'^collection/(?P<id>\d+)/$', 'collection', {}, 'aa-collection'),
#    url(r'^collection/(?P<id>\d+)/order/$', 'collection_order', {}, 'aa-collection-order'),
#    url(r'^collection/(?P<id>\d+)/delete/$', 'collection_delete', {}, 'aa-collection-delete'),
#    url(r'^users/$', 'users', {}, 'aa-users'),
#    url(r'^users/(?P<id>\d+)/$', 'user', {}, 'aa-user'),
#    url(r'^search/$', 'search', {}, 'aa-search'),

)


