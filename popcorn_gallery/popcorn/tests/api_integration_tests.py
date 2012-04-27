import httplib
import urllib

from django.contrib.auth.models import User
from django.utils import simplejson as json
from django.utils.unittest import TestCase
from tastypie.models import ApiKey
from .fixtures import create_project, create_template, create_user
from .utils import CustomClient
from ..models import Project, Template


class HTTPTestCase(TestCase):

    def setUp(self):
        self.user = create_user('bob')
        self.template = create_template()
        self.project = create_project(user=self.user, template=self.template)
        self.client = CustomClient()

    def tearDown(self):
        for model in [Project, ApiKey, User, Template]:
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
        response = self.client.get('/api/v1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '{"account": {"list_endpoint": "/api/v1/account/", "schema": "/api/v1/account/schema/"}, "project": {"list_endpoint": "/api/v1/project/", "schema": "/api/v1/project/schema/"}, "template": {"list_endpoint": "/api/v1/template/", "schema": "/api/v1/template/schema/"}}')


class TemplateHttpTestCase(HTTPTestCase):

    def test_get_template_anon(self):
        response = self.client.get('/api/v1/template/')
        self.assertEqual(response.status_code, 401)

    def test_get_template_api(self):
        response = self.client.get('/api/v1/template/', user=self.user)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['meta']['total_count'], 1)
        self.assertEqual(len(data['objects']), 1)

    def test_post_template_anon(self):
        data = {'name': 'Sample'}
        response = self.client.post('/api/v1/template/', data=data)
        self.assertEqual(response.status_code, 405)

    def test_post_template(self):
        data = {'name': 'Sample'}
        response = self.client.post('/api/v1/template/', user=self.user, data=data)
        self.assertEqual(response.status_code, 405)

    def test_get_template_detail_anon(self):
        url = '/api/v1/template/%s/' % self.template.pk
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_get_template_detail(self):
        url = '/api/v1/template/%s/' % self.template.pk
        response = self.client.get(url, user=self.user)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['name'], 'basic')
        self.assertEqual(data['resource_uri'], url)

    def test_patch_template_detail_anon(self):
        data = {'name': 'Sample'}
        url = '/api/v1/template/%s/' % self.template.pk
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, 405)

    def test_patch_template_detail(self):
        data = {'name': 'Sample'}
        url = '/api/v1/template/%s/' % self.template.pk
        response = self.client.patch(url, user=self.user, data=data)
        self.assertEqual(response.status_code, 405)

    def test_put_template_detail_anon(self):
        data = {'name': 'Sample'}
        url = '/api/v1/template/%s/' % self.template.pk
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, 405)

    def test_put_template_detail(self):
        data = {'name': 'Sample'}
        url = '/api/v1/template/%s/' % self.template.pk
        response = self.client.put(url, user=self.user, data=data)
        self.assertEqual(response.status_code, 405)


class ProjectHttpTestCase(HTTPTestCase):

    valid_data = {
        'name': 'I love popcorn!',
        'metadata': '{"json": true}',
        'html': '<!DOCTYPE html>',
        'template': '/api/v1/template/1/',
        }

    def test_get_project_anon(self):
        response = self.client.get('/api/v1/project/')
        self.assertEqual(response.status_code, 401)

    def test_get_project(self):
        response = self.client.get('/api/v1/project/', user=self.user)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['meta']['total_count'], 1)
        self.assertEqual(len(data['objects']), 1)
        for project in data['objects']:
            self.assertEqual(project['user']['username'], self.user.username)

    def test_post_project_anon(self):
        response = self.client.post('/api/v1/project/',
                                   data=self.valid_data)
        self.assertEqual(response.status_code, 401)

    def test_post_project(self):
        response = self.client.post('/api/v1/project/', data=self.valid_data,
                                    user=self.user)
        self.assertEqual(response.status_code, 201)
        self.assertTrue('location' in response)
        response = self.client.get('/api/v1/project/', user=self.user)
        data = json.loads(response.content)
        self.assertEqual(data['meta']['total_count'], 2)

    def test_get_project_detail_anon(self):
        url = '/api/v1/project/%s/' % self.project.pk
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_get_project_detail(self):
        url = '/api/v1/project/%s/' % self.project.pk
        response = self.client.get(url, user=self.user)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue('uuid' in data)
        self.assertEqual(data['resource_uri'], url)
        self.assertEqual(data['user']['username'], self.user.username)
        self.assertEqual(data['template']['name'], self.template.name)

    def test_patch_project_detail_anon(self):
        data = {'name': 'This is awesome'}
        response = self.client.patch('/api/v1/project/1/', data=data)
        self.assertEqual(response.status_code, 401)

    def test_patch_project_detail(self):
        initial_data = {'name': 'This is awesome'}
        url = '/api/v1/project/%s/' % self.project.pk
        response = self.client.patch(url, data=initial_data, user=self.user)
        self.assertEqual(response.status_code, 202)
        detail_response = self.client.get(url, user=self.user)
        detail_data = json.loads(detail_response.content)
        self.assertEqual(detail_data['name'], initial_data['name'])

    def test_put_project_detail_anon(self):
        data = {'name': 'This is awesome'}
        response = self.client.put('/api/v1/project/1/', data=data)
        self.assertEqual(response.status_code, 405)

    def test_put_project_detail(self):
        data = {'name': 'This is awesome'}
        url = '/api/v1/project/%s/' % self.project.pk
        response = self.client.put(url, user=self.user, data=data)
        self.assertEqual(response.status_code, 405)


class ProjectHttpTestCaseNotOwner(HTTPTestCase):

    def setUp(self):
        super(ProjectHttpTestCaseNotOwner, self).setUp()
        self.alex = create_user('alex')

    def test_get_project(self):
        response = self.client.get('/api/v1/project/', user=self.alex)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['meta']['total_count'], 0)
        self.assertEqual(len(data['objects']), 0)

    def test_patch_project_not_owned(self):
        data = {'name': 'This is awesome'}
        url = '/api/v1/project/%s/' % self.project.pk
        response = self.client.patch(url, data=data, user=self.alex)
        self.assertEqual(response.status_code, 404)
