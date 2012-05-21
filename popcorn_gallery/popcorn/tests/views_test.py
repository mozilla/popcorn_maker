from django.contrib.auth.models import User
from django.test import TestCase
from .fixtures import create_user, create_template
from ..models import Project, Template
from ..views.api import save_project


class PopcornViewsAPITest(TestCase):

    def tearDown(self):
        for model in [Project, User, Template]:
            model.objects.all().delete()

    def test_save_project(self):
        template = create_template()
        user = create_user('bob')
        data = {
            'name': 'Hello World!',
            'template': template.name,
            'data': {"foo": "foo"},
            'html': '<!DOCTYPE html>',
            }
        response = save_project(data, user)
        self.assertEqual(response['error'], 'okay')
        self.assertEqual(Project.objects.all().count(), 1)

    def test_failed_project(self):
        template = create_template()
        user = create_user('bob')
        data = {
            'name': 'Hello World!',
            'template': template.name,
            'html': '<!DOCTYPE html>',
            }
        response = save_project(data, user)
        self.assertEqual(response['error'], 'error')
        self.assertEqual(Project.objects.all().count(), 0)
