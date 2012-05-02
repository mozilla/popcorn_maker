from django.contrib.auth.models import User
from django.test import TestCase
from .fixtures import create_user, create_template, create_project
from ..models import Project, Template


class PopcornTest(TestCase):

    def tearDown(self):
        for model in [Project, User, Template]:
            model.objects.all().delete()

    def test_template_creation(self):
        template = Template.objects.create(name='basic')
        assert template.id, "Template couldn't be created"

    def test_project_creation(self):
        data = {
            'author': create_user('bob'),
            'name': 'Hello World!',
            'template': create_template(),
            'metadata': '{}',
            'html': '<!DOCTYPE html>',
            }
        project = Project.objects.create(**data)
        assert project.id, "Project couldn't be created"
        assert project.uuid, "Project UUID missing"
        self.assertEqual(project.status, Project.LIVE)

    def test_butter_data(self):
        project = create_project()
        for attr in ['_id', 'name', 'template', 'data', 'created', 'modified']:
            self.assertTrue(attr in project.butter_data)
