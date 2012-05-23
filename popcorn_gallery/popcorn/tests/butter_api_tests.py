import json

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.utils.unittest import TestCase

from nose.tools import eq_, ok_
from .fixtures import create_project, create_user, create_template
from ..models import Project, Template


class JSONClient(Client):

    def get(self, path, **extra):
        extra.update({
            'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest',
            })
        return super(JSONClient, self).get(path, **extra)

    def post(self, path, data={}, content_type='application/json', **extra):
        data = json.dumps(data)
        extra.update({'data': data,
                      'content_type': content_type,
                      'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        return super(JSONClient, self).post(path, **extra)


class ButterIntegrationTestCase(TestCase):

    valid_data = {
        "name": "Rad Project!",
        "data": {"data": "foo"},
        "template": "base-template",
        "html": "<!DOCTYPE html5>",
        }

    def setUp(self):
        self.user = create_user('bob')
        self.template = create_template(slug='base-template')
        self.client = JSONClient()
        self.client.login(username='bob', password='bob')

    def tearDown(self):
        self.client.logout()
        for model in [Project, Template, User]:
            model.objects.all().delete()

    def test_add_project(self):
        url = reverse('api:project_add')
        response = self.client.post(url, self.valid_data)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'okay')
        self.assertTrue('_id' in response_data['project'])
        project = Project.objects.get()
        json.loads(project.metadata)

    def test_get_detail_project(self):
        project = create_project(author=self.user)
        url = reverse('api:project_detail', args=[project.uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'okay')
        self.assertTrue(isinstance(response_data['project'], basestring))
        json.loads(response_data['project'])

    def test_post_detail_project(self):
        project = create_project(author=self.user)
        url = reverse('api:project_detail', args=[project.uuid])
        response = self.client.post(url, self.valid_data)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'okay')
        self.assertTrue('_id', response_data['project'])
        self.assertTrue('data', response_data['project'])

    def test_list_projects(self):
        alex = create_user('alex')
        template = create_template()
        project_a = create_project(author=alex, template=template)
        project_b = create_project(author=self.user, template=template)
        response = self.client.get(reverse('api:project_list'))
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'okay')
        self.assertEqual(len(response_data['projects']), 1)

    def test_publish_project_get(self):
        project = create_project(author=self.user)
        url = reverse('api:project_publish', args=[project.uuid])
        response = self.client.get(reverse('api:project_publish',
                                           args=[project.uuid]))
        self.assertEqual(response.status_code, 404)

    def test_publish_project(self):
        project = create_project(author=self.user)
        url = reverse('api:project_publish', args=[project.uuid])
        response = self.client.post(reverse('api:project_publish',
                                            args=[project.uuid]))
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'okay')
        self.assertTrue('url' in response_data)

    def test_whoami(self):
        response = self.client.get(reverse('api:user_details'))
        eq_(response.status_code, 200)
        response_data = json.loads(response.content)
        ok_(response_data['username'])
        ok_(response_data['name'])
        ok_(response_data['email'])


class ButterIntegrationTestCaseAnon(TestCase):

    def setUp(self):
        self.client = JSONClient()

    def test_whoami(self):
        response = self.client.get(reverse('api:user_details'))
        eq_(response.status_code, 403)
