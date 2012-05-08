from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    'popcorn_gallery.popcorn.views.api',
    url(r'^projects$', 'project_list', name='project_list'),
    url(r'^project/null$', 'project_add', name='project_add'),
    url(r'^project/(?P<uuid>[-\w]+)$', 'project_detail',
        name='project_detail'),
    url(r'^template/$', 'template_detail', name='template'),
    url(r'^config/default.conf$', 'template_config', name='template_config'),
    )
