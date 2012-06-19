from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'popcorn_gallery.tutorials.views',
    url(r'^(?P<slug>[\w-]+)/$', 'object_detail', name='object_detail'),
    url(r'^$', 'object_list', name='object_list'),
)
