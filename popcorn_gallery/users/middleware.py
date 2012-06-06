from django.contrib import messages
from django.core.urlresolvers import reverse, resolve, Resolver404
from django.http import HttpResponseRedirect

from tower import ugettext as _


class ProfileMiddleware(object):

    safe_views = ('users_edit', 'django.views.static.serve', 'users_signout',
                  'users_profile_add_link', 'users_profile_links',
                  'users_profile_delete_link', 'create_entry')

    safe_path = ('__debug__', '/admin/', '/api/', '/logout/', '/static/')

    def is_safe_view(self, path):
        try:
            match = resolve(path)
            return match.url_name in self.safe_views
        except Resolver404:
            return False

    def is_safe_path(self, path):
        for prefix in self.safe_path:
            if prefix in path:
                return True
        return False

    def is_safe(self, path):
        return self.is_safe_path(path) or self.is_safe_view(path)

    def process_request(self, request):
        if self.is_safe(request.path):
            return
        path = u'/%s' % ('/'.join(request.path.split('/')[2:]),)
        if self.is_safe(path):
            return
        if request.user.is_authenticated():
            profile = request.user.get_profile()
            if profile.name:
                return
            return HttpResponseRedirect(reverse('users_edit'))
