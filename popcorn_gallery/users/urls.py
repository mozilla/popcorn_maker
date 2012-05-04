from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'popcorn_gallery.users.views',
    url(r'^edit/$', 'edit', name='users_edit'),
    url(r'^delete/$', 'delete_profile', name='users_delete'),
    url(r'^(?P<username>[\w-]+)/$', 'profile', name='users_profile'),
)
