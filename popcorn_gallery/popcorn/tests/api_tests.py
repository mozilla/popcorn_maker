from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import TestCase
from .fixtures import create_project
from ..models import Project, Template
from ...urls import v1_api


class PopcornApiTest(TestCase):

    def setUp(self):
        self.project = create_project()

    def tearDown(self):
        for model in [Project, User, Template]:
            model.objects.all().delete()

    def test_registered_models(self):
        self.assertEqual(v1_api._registry.keys(), ['project'])


class PopcornApiIntegrationTest(TestCase):

    def setUp(self):
        self.project = create_project()
        self.resource = v1_api.canonical_resource_for('project')

    def test_get_project(self):
        request = HttpRequest()
        project = self.resource.get_via_uri('/api/v1/project/1/', request=request)
        self.assertEqual(project.pk, self.project.pk)

    def test_create_project(self):
        pass
