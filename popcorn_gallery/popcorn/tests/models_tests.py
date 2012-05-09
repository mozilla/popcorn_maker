from django.contrib.auth.models import User
from django.test import TestCase
from .fixtures import create_user, create_template, create_project
from ..models import Project, Template, Category


class PopcornTest(TestCase):

    def tearDown(self):
        for model in [Project, User, Template]:
            model.objects.all().delete()

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
        self.assertTrue(project.is_forkable)
        self.assertTrue(project.is_shared)
        self.assertFalse(project.is_removed)

    def test_butter_data(self):
        project = create_project()
        for attr in ['_id', 'name', 'template', 'data', 'created', 'modified']:
            self.assertTrue(attr in project.butter_data)

    def test_project_live_manager(self):
        project = create_project(status=Project.LIVE)
        self.assertEqual(Project.live.all().count(), 1)

    def test_project_live_manager_hidden(self):
        project = create_project(status=Project.HIDDEN)
        self.assertEqual(Project.live.all().count(), 0)
        self.assertEqual(Project.objects.all().count(), 1)


class TemplateTest(TestCase):

    def tearDown(self):
        Template.objects.all().delete()

    def test_template_creation(self):
        template = 'popcorn/templates/test/base.html'
        config = 'popcorn/templates/test/config.cfg'
        template = Template.objects.create(name='basic', slug='basic',
                                           template=template, config=config)
        assert template.id, "Template couldn't be created"


class CategoryTest(TestCase):

    def tearDown(self):
        Category.objects.all().delete()

    def test_category_creation(self):
        data = {'name': 'Special'}
        category = Category.objects.create(**data)
        assert category.id, 'Failed to create Category'
