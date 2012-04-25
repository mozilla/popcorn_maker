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

    def tearDown(self):
        self.stop_server()
        for model in [Project, User, Template]:
            model.objects.all().delete()

    def get_connection(self):
        return httplib.HTTPConnection('localhost', 8001)

    def do_request(self, method, url, user=None, data=None):
        """Generates a request with the right headers"""
        connection = self.get_connection()
        headers = {'Accept': 'application/json'}
        if user:
            headers['Authorization'] = 'ApiKey %s:%s' % (user.username,
                                                         user.api_key.key)
        if data:
            headers['Content-type'] = 'application/json'
        kwargs = {'headers': headers }
        if data:
            kwargs['body'] = json.dumps(data)
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

    def test_get_template_anon(self):
        response = self.do_request('GET', '/api/v1/template/')
        response.read()
        self.assertEqual(response.status, 401)

    def test_get_template_api(self):
        response = self.do_request('GET', '/api/v1/template/', self.user)
        data = json.load(response)
        self.assertEqual(response.status, 200)
        self.assertEqual(data['meta']['total_count'], 1)
        self.assertEqual(len(data['objects']), 1)

    def test_post_template_anon(self):
        data = {'name': 'Sample'}
        response = self.do_request('POST', '/api/v1/template/', data=data)
        response.read()
        self.assertEqual(response.status, 405)

    def test_post_template(self):
        data = {'name': 'Sample'}
        response = self.do_request('POST', '/api/v1/template/', self.user, data)
        response.read()
        self.assertEqual(response.status, 405)

    def test_get_template_detail_anon(self):
        response = self.do_request('GET', '/api/v1/template/1/')
        response.read()
        self.assertEqual(response.status, 401)

    def test_get_template_detail(self):
        response = self.do_request('GET', '/api/v1/template/1/', self.user)
        data = json.load(response)
        self.assertEqual(response.status, 200)
        self.assertEqual(data['name'], 'basic')
        self.assertEqual(data['resource_uri'], '/api/v1/template/1/')

    def test_patch_template_detail_anon(self):
        data = {'name': 'Sample'}
        response = self.do_request('PATCH', '/api/v1/template/1/', data=data)
        response.read()
        self.assertEqual(response.status, 405)

    def test_patch_template_detail(self):
        data = {'name': 'Sample'}
        response = self.do_request('PATCH', '/api/v1/template/1/', self.user, data)
        data = response.read()
        self.assertEqual(response.status, 405)

    def test_put_template_detail_anon(self):
        data = {'name': 'Sample'}
        response = self.do_request('PUT', '/api/v1/template/1/', data=data)
        response.read()
        self.assertEqual(response.status, 405)

    def test_put_template_detail(self):
        data = {'name': 'Sample'}
        response = self.do_request('PUT', '/api/v1/template/1/', self.user, data)
        response.read()
        self.assertEqual(response.status, 405)


class ProjectHttpTestCase(HTTPTestCase):

    valid_data = {
        'name': 'I love popcorn!',
        'metadata': '{json: "true"}',
        'html': '<!DOCTYPE html>',
        'template': '/api/v1/template/1/',
        }

    def test_get_project_anon(self):
        response = self.do_request('GET', '/api/v1/project/')
        response.read()
        self.assertEqual(response.status, 401)

    def test_get_project(self):
        response = self.do_request('GET', '/api/v1/project/', self.user)
        data = json.load(response)
        self.assertEqual(response.status, 200)
        self.assertEqual(data['meta']['total_count'], 1)
        self.assertEqual(len(data['objects']), 1)
        for project in data['objects']:
            self.assertEqual(project['user']['username'], self.user.username)

    def test_post_project_anon(self):
        response = self.do_request('POST', '/api/v1/project/',
                                   data=self.valid_data)
        response.read()
        self.assertEqual(response.status, 401)

    def test_post_project(self):
        response = self.do_request('POST', '/api/v1/project/', self.user,
                                   self.valid_data)
        data = response.read()
        self.assertEqual(response.status, 201)
        self.assertEqual(dict(response.getheaders())['location'],
                         'http://localhost:8001/api/v1/project/2/')
        response = self.do_request('GET', '/api/v1/project/', self.user)
        data = json.load(response)
        self.assertEqual(data['meta']['total_count'], 2)

    def test_get_project_detail_anon(self):
        response = self.do_request('GET', '/api/v1/project/1/')
        response.read()
        self.assertEqual(response.status, 401)

    def test_get_project_detail(self):
        response = self.do_request('GET', '/api/v1/project/1/', self.user)
        data = json.load(response)
        self.assertEqual(response.status, 200)
        self.assertTrue('uuid' in data)
        self.assertEqual(data['resource_uri'], '/api/v1/project/1/')
        self.assertEqual(data['user']['username'], self.user.username)
        self.assertEqual(data['template']['name'], self.template.name)

    def test_patch_project_detail_anon(self):
        data = {'name': 'This is awesome'}
        response = self.do_request('PATCH', '/api/v1/project/1/', data=data)
        response.read()
        self.assertEqual(response.status, 401)

    def test_patch_project_detail(self):
        data = {'name': 'This is awesome'}
        response = self.do_request('PATCH', '/api/v1/project/1/', self.user, data)
        response.read()
        self.assertEqual(response.status, 202)
        detail_response = self.do_request('GET', '/api/v1/project/1/', self.user)
        detail_data = json.load(detail_response)
        self.assertEqual(detail_data['name'], data['name'])

    def test_put_project_detail_anon(self):
        data = {'name': 'This is awesome'}
        response = self.do_request('PUT', '/api/v1/project/1/', data=data)
        response.read()
        self.assertEqual(response.status, 405)

    def test_put_project_detail(self):
        data = {'name': 'This is awesome'}
        response = self.do_request('PUT', '/api/v1/project/1/', self.user, data)
        response.read()
        self.assertEqual(response.status, 405)


class ProjectHttpTestCaseNotOwner(HTTPTestCase):

    def setUp(self):
        super(ProjectHttpTestCaseNotOwner, self).setUp()
        self.alex = create_user('alex')

    def test_get_project(self):
        response = self.do_request('GET', '/api/v1/project/', self.alex)
        data = json.load(response)
        self.assertEqual(response.status, 200)
        self.assertEqual(data['meta']['total_count'], 0)
        self.assertEqual(len(data['objects']), 0)

    def test_patch_project_not_owned(self):
        data = {'name': 'This is awesome'}
        response = self.do_request('PATCH', '/api/v1/project/1/', self.alex, data)
        response.read()
        self.assertEqual(response.status, 404)
