from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import TestCase
from tastypie.http import HttpUnauthorized
from tastypie.models import ApiKey
from .fixtures import create_project
from ..auth import InternalApiKeyAuthentication
from ..models import Project, Template
from ...urls import v1_api


class PopcornApiTest(TestCase):

    def setUp(self):
        self.project = create_project()

    def tearDown(self):
        for model in [Project, User, Template]:
            model.objects.all().delete()

    def test_registered_models(self):
        keys = v1_api._registry.keys()
        keys.sort()
        self.assertEqual(keys, ['account', 'project', 'template'])


class PopcornApiIntegrationTest(TestCase):

    def tearDown(self):
        for model in [Project, User, Template]:
            model.objects.all().delete()

    def test_create_user_api_key(self):
        handle = 'bob'
        email = '%s@%s.com' % (handle, handle)
        user = User.objects.create_user(handle, email, handle)
        assert user.api_key, "API Key is missing"
        assert user.api_key.key, "API Key is missing"


class InternalApiKeyAuthenticationTestCase(TestCase):

    def setUp(self):
        handle = 'bob'
        email = '%s@%s.com' % (handle, handle)
        user = User.objects.create_user(handle, email, handle)
        self.auth_header = 'ApiKey %s:%s' % (user.username, user.api_key.key)

    def tearDown(self):
        for model in [ApiKey, User]:
            model.objects.all().delete()

    def test_invalid_ip_request(self):
        auth = InternalApiKeyAuthentication()
        request = HttpRequest()
        request.META['HTTP_AUTHORIZATION'] = self.auth_header
        request.META['HTTP_X_REAL_IP'] = '0.0.0.0'
        result = auth.is_authenticated(request)
        self.assertEqual(isinstance(result, HttpUnauthorized), True)

    def test_valid_ip_request(self):
        auth = InternalApiKeyAuthentication()
        request = HttpRequest()
        request.META['HTTP_AUTHORIZATION'] = self.auth_header
        request.META['HTTP_X_REAL_IP'] = '127.0.0.1'
        self.assertTrue(auth.is_authenticated(request))
