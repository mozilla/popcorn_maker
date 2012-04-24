import httplib
try:
    import json
except ImportError:
    import simplejson as json

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import TestCase
from tastypie.models import ApiKey
from .fixtures import create_project, create_template, create_user
from .testcases import TestServerTestCase
from ..models import Project, Template
from ...urls import v1_api


class PopcornApiTest(TestCase):

    def setUp(self):
        self.project = create_project()

    def tearDown(self):
        for model in [Project, User, Template]:
            model.objects.all().delete()

    def test_registered_models(self):
        self.assertEqual(v1_api._registry.keys(), ['project', 'template'])


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


class HTTPTestCase(TestServerTestCase):

    def setUp(self):
        self.start_server(address='localhost', port=8001)
        self.user = create_user('bob')
        self.template = create_template()
        self.project = create_project(user=self.user, template=self.template)
        self.auth = 'ApiKey %s:%s' % (self.user.username, self.user.api_key.key)

    def tearDown(self):
        self.stop_server()
        for model in [Project, User, Template]:
            model.objects.all().delete()

    def get_connection(self):
        return httplib.HTTPConnection('localhost', 8001)

    def do_request(self, method, url, is_authenticated=False):
        """Generates a request with the right headers"""
        connection = self.get_connection()
        headers = {'Accept': 'application/json'}
        if is_authenticated:
            headers['Authorization'] = self.auth
        connection.request(method, url, headers=headers)
        response = connection.getresponse()
        connection.close()
        return response

    def test_get_apis_json(self):
        response = self.do_request('GET', '/api/v1/')
        data = response.read()
        self.assertEqual(response.status, 200)
        self.assertEqual(data,'{"project": {"list_endpoint": "/api/v1/project/", "schema": "/api/v1/project/schema/"}, "template": {"list_endpoint": "/api/v1/template/", "schema": "/api/v1/template/schema/"}}')


class TemplateHttpTestCase(HTTPTestCase):

    def test_get_template_api_anon(self):
        response = self.do_request('GET', '/api/v1/template/')
        response.read()
        self.assertEqual(response.status, 401)

    def test_get_template_api_logged_in(self):
        response = self.do_request('GET', '/api/v1/template/', True)
        data = response.read()
        assert False, data
        self.assertEqual(response.status, 200)
