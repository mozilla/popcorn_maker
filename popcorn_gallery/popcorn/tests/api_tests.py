from django.contrib.auth.models import User

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
