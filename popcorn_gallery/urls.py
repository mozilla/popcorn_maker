from django.contrib import admin
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from funfactory.monkeypatches import patch
from tastypie.api import Api
from .popcorn.api import ProjectResource, TemplateResource
from .accounts.api import AccountResource

patch()

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(TemplateResource())
v1_api.register(ProjectResource())
v1_api.register(AccountResource())


urlpatterns = patterns(
    '',
    (r'^admin/', include(admin.site.urls)),
    (r'^api/', include(v1_api.urls)),
    (r'^browserid/', include('django_browserid.urls')),
    url(r'^$', 'popcorn_gallery.popcorn.views.index', name='index'),
)

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
