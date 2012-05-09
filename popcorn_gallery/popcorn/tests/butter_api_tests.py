import json

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.utils.unittest import TestCase

from .fixtures import create_project, create_user, create_template
from ..models import Project, Template


class JSONClient(Client):

    def post(self, path, data={}, user=None, content_type='application/json',
             **extra):
        data = json.dumps(data)
        return super(JSONClient, self).post(path, data=data,
                                            content_type=content_type, **extra)

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
        url = reverse('project_add')
        response = self.client.post(url, self.valid_data)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'okay')
        self.assertTrue('_id' in response_data['project'])
        project = Project.objects.get()
        json.loads(project.metadata)

    def test_get_detail_project(self):
        project = create_project(author=self.user)
        url = reverse('project_detail', args=[project.uuid])
        response = self.client.get(url)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'okay')
        self.assertTrue(isinstance(response_data['project'], basestring))
        json.loads(response_data['project'])

    def test_post_detail_project(self):
        project = create_project(author=self.user)
        url = reverse('project_detail', args=[project.uuid])
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
        response = self.client.get(reverse('project_list'))
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'okay')
        self.assertEqual(len(response_data['projects']), 1)

    def test_publish_project_get(self):
        project = create_project(author=self.user)
        url = reverse('project_publish', args=[project.uuid])
        response = self.client.get(reverse('project_publish',
                                           args=[project.uuid]))
        self.assertEqual(response.status_code, 404)

    def test_publish_project(self):
        project = create_project(author=self.user)
        url = reverse('project_publish', args=[project.uuid])
        response = self.client.post(reverse('project_publish',
                                            args=[project.uuid]))
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'okay')
        self.assertTrue('url' in response_data)
