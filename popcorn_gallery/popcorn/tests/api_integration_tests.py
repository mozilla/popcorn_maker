import httplib
import urllib
try:
    import json
except ImportError:
    import simplejson as json

from django.contrib.auth.models import User
from .fixtures import create_project, create_template, create_user
from .testcases import TestServerTestCase
from ..models import Project, Template


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

    def do_request(self, method, url, is_authenticated=False, data=None):
        """Generates a request with the right headers"""
        connection = self.get_connection()
        headers = {'Accept': 'application/json'}
        if is_authenticated:
            headers['Authorization'] = self.auth
        kwargs = {'headers': headers }
        if data:
            kwargs['body'] = urllib.urlencode(data)
        connection.request(method, url, **kwargs)
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

    def test_get_template_api(self):
        response = self.do_request('GET', '/api/v1/template/', True)
        data = json.load(response)
        self.assertEqual(response.status, 200)
        self.assertEqual(data['meta']['total_count'], 1)
        self.assertEqual(len(data['objects']), 1)

    def test_post_template_api_anon(self):
        data = {'name': 'Sample'}
        response = self.do_request('POST', '/api/v1/template/', False, data)
        response.read()
        self.assertEqual(response.status, 405)

    def test_post_template_api(self):
        data = {'name': 'Sample'}
        response = self.do_request('POST', '/api/v1/template/', True, data)
        response.read()
        self.assertEqual(response.status, 405)

    def test_get_template_detail_anon(self):
        response = self.do_request('GET', '/api/v1/template/1/')
        response.read()
        self.assertEqual(response.status, 401)

    def test_get_template_detail(self):
        response = self.do_request('GET', '/api/v1/template/1/', True)
        data = json.load(response)
        self.assertEqual(response.status, 200)
        self.assertEqual(data['name'], 'basic')
        self.assertEqual(data['resource_uri'], '/api/v1/template/1/')

    def test_patch_template_detail_anon(self):
        data = {'name': 'Sample'}
        response = self.do_request('PATCH', '/api/v1/template/', False, data)
        response.read()
        self.assertEqual(response.status, 405)

    def test_patch_template_detail(self):
        data = {'name': 'Sample'}
        response = self.do_request('PATCH', '/api/v1/template/', True, data)
        response.read()
        self.assertEqual(response.status, 405)

