from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    'popcorn_gallery.reports.views',
    url(r'^$', 'report_form', name='report'),
    )

