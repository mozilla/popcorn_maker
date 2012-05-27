from django.contrib import admin
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from .users.views import AjaxVerify
from funfactory.monkeypatches import patch

patch()
admin.autodiscover()


urlpatterns = patterns(
    'popcorn_gallery.users.views',
    url(r'^dashboard/$', 'dashboard', name='users_dashboard'),
    url(r'^logout/$', 'signout', name='logout'),
    url('^login/$', 'login', name='login'),
    url('^login/failed/$', 'login', {'failed': True}, name='login_failed'),
)

# static pages
urlpatterns += patterns(
    'django.views.generic.simple',
    url('^about/$', 'direct_to_template', {'template': 'about.html'},
        name='about'),
    url('^help/$', 'direct_to_template', {'template': 'help.html'},
        name='help'),
    url('^legal/$', 'direct_to_template', {'template': 'legal.html'},
        name='legal'),
    )


urlpatterns += patterns(
    '',
    (r'^admin/', include(admin.site.urls)),
    (r'^profile/', include('popcorn_gallery.users.urls')),
    (r'^report/', include('popcorn_gallery.reports.urls')),
    (r'^api/', include('popcorn_gallery.popcorn.urls.api', namespace='api')),
    (r'', include('popcorn_gallery.popcorn.urls.projects')),
    url(r'^browserid/verify$', AjaxVerify.as_view(), name='browserid_verify'),
    url(r'^vote/(?P<model>project)/(?P<object_id>\d+)/(?P<direction>up|clear)/$',
        'popcorn_gallery.base.views.vote', name='vote'),
    url(r'^$', 'popcorn_gallery.base.views.homepage', name='homepage'),
    )

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
    urlpatterns += staticfiles_urlpatterns()
