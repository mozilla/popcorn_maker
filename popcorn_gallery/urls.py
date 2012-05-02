from django.contrib import admin
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

from .accounts.views import AjaxVerify
from funfactory.monkeypatches import patch



patch()
admin.autodiscover()


urlpatterns = patterns(
    '',
    (r'^admin/', include(admin.site.urls)),
    url('^browserid/verify$', AjaxVerify.as_view(), name='browserid_verify'),
    url(r'^$', 'popcorn_gallery.popcorn.views.index', name='index'),
)


# For the initial popcorn_gallery integration
urlpatterns += patterns(
    'popcorn_gallery.popcorn.views',
    url(r'^projects$', 'project_list', name='project_list'),
    url(r'^project/null$', 'project_add', name='project_add'),
    url(r'^project/(?P<uuid>[-\w]+)$', 'project_detail',
        name='project_detail'),
    url(r'^template/$', 'template_detail', name='template'),
    url(r'^config/default.conf$', 'template_config', name='template_config'),
    )

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
