from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    # (r'^docs/', include('sarmadocs.urls')),

    url(r'^openid/', include('django_openid_auth.urls')),
    url(r'^logout/', 'django.contrib.auth.views.logout_then_login', {}, 'logout'),

    (r'^flickr/', include('flickr.urls')),
    (r'^youtube/', include('youtube.urls')),
    (r'^ffmpeg/', include('ffmpeg.urls')),
    (r'^internetarchive/', include('internetarchive.urls')),
    (r'', include('aacore.urls')),

)

if settings.DEBUG:
    baseurlregex = r'^static/(?P<path>.*)$'
    urlpatterns += patterns('',
        (baseurlregex, 'django.views.static.serve',
        {'document_root':  settings.MEDIA_ROOT}),
    )

    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))

