from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    'popcorn_gallery.search.views',
    url(r'^$', 'search', name='search'),
    )
