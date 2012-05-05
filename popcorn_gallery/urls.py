from django.contrib import admin
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

from .users.views import AjaxVerify
from funfactory.monkeypatches import patch

patch()
admin.autodiscover()


urlpatterns = patterns(
    '',
    (r'^admin/', include(admin.site.urls)),
    (r'^profile/', include('popcorn_gallery.users.urls')),
    (r'^api/', include('popcorn_gallery.popcorn.urls')),
    url('^browserid/verify$', AjaxVerify.as_view(), name='browserid_verify'),
    url(r'^$', 'popcorn_gallery.popcorn.views.index', name='index'),
)


urlpatterns += patterns(
    'popcorn_gallery.users.views',
    url(r'^dashboard/$', 'dashboard', name='users_dashboard'),
    url(r'^logout/$', 'signout', name='logout'),
)


## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
