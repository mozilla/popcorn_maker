from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from .fixtures import (create_user, create_template, create_project,
                       create_project_category, create_external_project)
from ..models import (Project, Template, ProjectCategory, TemplateCategory,
                      ProjectCategoryMembership)


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
        self.assertEqual(project.status, Project.HIDDEN)
        self.assertFalse(project.is_forkable)
        self.assertFalse(project.is_shared)
        self.assertFalse(project.is_removed)
        self.assertFalse(project.is_published)
        self.assertFalse(project.is_external)

    def test_external_project_creation(self):
        data = {
            'author': create_user('bob'),
            'name': 'Hello World!',
            'url': 'http://mozillapopcorn.org',
            }
        project = Project.objects.create(**data)
        assert project.id, "Project couldn't be created"
        assert project.uuid, "Project UUID missing"
        self.assertEqual(project.status, Project.HIDDEN)
        self.assertFalse(project.is_forkable)
        self.assertFalse(project.is_shared)
        self.assertFalse(project.is_removed)
        self.assertFalse(project.is_published)
        self.assertTrue(project.is_external)

    def test_absolute_url(self):
        project = create_project()
        url = reverse('user_project_summary', args=[project.author.username,
                                                    project.shortcode])
        self.assertEqual(project.get_absolute_url(), url)

    def test_project_url(self):
        project = create_external_project()
        url = reverse('user_project', args=[project.author.username,
                                            project.shortcode])
        self.assertEqual(project.get_project_url(), url)

    def test_edit_url(self):
        project = create_external_project()
        url = reverse('user_project_edit', args=[project.author.username,
                                                 project.shortcode])
        self.assertEqual(project.get_edit_url(), url)

    def test_project_published(self):
        project = create_project(status=Project.LIVE)
        self.assertTrue(project.is_published)

    def test_hidden_project(self):
        project = create_project(status=Project.HIDDEN)
        self.assertFalse(project.is_removed)
        self.assertFalse(project.is_published)

    def test_removed_project(self):
        project = create_project(is_removed=True, status=Project.LIVE)
        self.assertEqual(project.status, project.LIVE)
        self.assertFalse(project.is_published)

    def test_butter_data(self):
        project = create_project()
        for attr in ['_id', 'name', 'template', 'data', 'created', 'modified']:
            self.assertTrue(attr in project.butter_data)


class TemplateTest(TestCase):

    def tearDown(self):
        Template.objects.all().delete()

    def test_template_creation(self):
        template = 'popcorn/templates/test/base.html'
        config = 'popcorn/templates/test/config.cfg'
        template = Template.objects.create(name='basic', slug='basic',
                                           template=template, config=config)
        assert template.id, "Template couldn't be created"
        self.assertEqual(template.status, Template.LIVE)
        self.assertEqual(template.is_featured, False)

    def test_template_live_manager(self):
        create_template(name='basic')
        self.assertEqual(Template.live.all().count(), 1)

    def test_template_live_manager_hidden(self):
        create_template(status=Template.HIDDEN)
        self.assertEqual(Template.live.all().count(), 0)
        self.assertEqual(Template.objects.all().count(), 1)


class ProjectCategoryTest(TestCase):

    def tearDown(self):
        ProjectCategory.objects.all().delete()

    def test_category_creation(self):
        data = {'name': 'Special'}
        category = ProjectCategory.objects.create(**data)
        assert category.id, 'Failed to create Category'


class TemplateCategoryTest(TestCase):

    def tearDown(self):
        TemplateCategory.objects.all().delete()

    def test_category_creation(self):
        data = {'name': 'Special'}
        category = TemplateCategory.objects.create(**data)
        assert category.id, 'Failed to create Category'


class ProjectCategoryMembershipTest(TestCase):

    def tearDown(self):
        for model in [ProjectCategoryMembership, ProjectCategory, User]:
            model.objects.all().delete()

    def test_membership_creation(self):
        user = create_user('bob', with_profile=True)
        data = {
            'user': user.profile,
            'project_category': create_project_category(),
            }
        membership = ProjectCategoryMembership.objects.create(**data)
        self.assertEqual(ProjectCategoryMembership.PENDING, membership.status)
        assert membership.created, "Missing created date"
