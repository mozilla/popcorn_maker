from django.conf.urls.defaults import patterns, url


project_pattern = '(?P<username>[-\w]+)/(?P<uuid>[-\w]+)'

urlpatterns = patterns(
    'popcorn_gallery.popcorn.views.projects',
    url(r'^%s/$' % project_pattern, 'user_project', name='user_project'),
    url(r'^%s/edit/$' % project_pattern, 'user_project_edit',
        name='user_project_edit'),
    url(r'^%s/meta/$' % project_pattern, 'user_project_meta',
        name='user_project_meta'),
    url(r'^%s/data/$' % project_pattern, 'user_project_data',
        name='user_project_data'),
    )
