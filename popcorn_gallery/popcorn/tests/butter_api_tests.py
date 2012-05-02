import json

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.utils.unittest import TestCase

from .fixtures import create_project, create_template, create_user
from ..models import Project, Template

class JSONClient(Client):

    def post(self, path, data={}, user=None, content_type='application/json',
             **extra):
        data = json.dumps(data)
        return super(JSONClient, self).post(path, data=data,
                                            content_type=content_type, **extra)


class ButterIntegrationTestCase(TestCase):

    def setUp(self):
        self.user = create_user('bob')
        self.client = JSONClient()
        self.client.login(username='bob', password='bob')

    def tearDown(self):
        self.client.logout()
        for model in [Project, Template, User]:
            model.objects.all().delete()

    def test_add_project(self):
        url = reverse('project_add')
        data = {
            "name": "Rad Project!",
            "data": {"data": "foo"},
            "template": "base-template",
            "html": "<!DOCTYPE html5>",
            }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'okay')
        self.assertTrue('project' in response_data)
        self.assertTrue('_id' in response_data['project'])
        project = Project.objects.get()
        assert False, project.metadata

    def test_detail_project(self):
        project = create_project(author=self.user)
        url = reverse('project_detail', args=[project.uuid])
        response = self.client.get(url)
        assert False, response
