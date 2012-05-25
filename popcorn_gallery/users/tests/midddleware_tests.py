from mock import MagicMock
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.test import TestCase
from test_utils import RequestFactory

from ..middleware import ProfileMiddleware
from ..models import Profile


complete_user = AnonymousUser()
complete_user.is_authenticated = MagicMock(return_value=True)
complete_user.get_profile = MagicMock(return_value=Profile(name='Mock name'))

incomplete_user = AnonymousUser()
incomplete_user.is_authenticated = MagicMock(return_value=True)
incomplete_user.get_profile = MagicMock(return_value=Profile())


class TestProfileMiddleware(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_safe_view_request(self):
        request = self.factory.get(reverse('users_edit'))
        middleware = ProfileMiddleware()
        response = middleware.process_request(request)
        self.assertFalse(response)

    def test_safe_path_request(self):
        request = self.factory.get('/admin/something/')
        middleware = ProfileMiddleware()
        response = middleware.process_request(request)
        self.assertFalse(response)

    def test_authed_user_request(self):
        request = self.factory.get(reverse('users_dashboard'))
        request.user = complete_user
        middleware = ProfileMiddleware()
        response = middleware.process_request(request)
        self.assertFalse(response)

    def test_anon_user_request(self):
        request = self.factory.get(reverse('users_dashboard'))
        request.user = incomplete_user
        middleware = ProfileMiddleware()
        response = middleware.process_request(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('users_edit'))
