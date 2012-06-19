from django.test import TestCase
from django.contrib.auth.models import User

from .fixtures import create_template, create_user, create_project_category
from ..models import Template, Project, ProjectCategoryMembership
from ..forms import ProjectForm, ProjectEditForm, ExternalProjectEditForm


class PopcornFormTests(TestCase):

    def setUp(self):
        create_template(slug='basic')

    def tearDown(self):
        Template.objects.all().delete()

    def test_project_form(self):
        data = {
            'name': 'Awesome project!',
            'data': {'foo': 'foo'},
            'html': '<!DOCTYPE html>',
            'template': 'basic',
            }
        form = ProjectForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['data'], '{"foo": "foo"}')

    def test_invalid_form(self):
        data = {
            'name': 'Awesome project!',
            'template': 'basic',
            }
        form = ProjectForm(data)
        self.assertFalse(form.is_valid())

    def test_invalid_json(self):
        data = {
            'name': 'Awesome project!',
            'template': 'basic',
            'data': 2 + 1j,
            }
        form = ProjectForm(data)
        self.assertFalse(form.is_valid())


class PopcornProjectEditFormTests(TestCase):

    def setUp(self):
        self.user = create_user('bob', with_profile=True)
        create_template(slug='basic')

    def tearDown(self):
        for model in [Template, User]:
            model.objects.all().delete()

    def test_project_edit_form(self):
        data = {
            'name': 'Awesome project!',
            'status': Project.LIVE,
            }
        form = ProjectEditForm(data, user=self.user.profile)
        self.assertTrue(form.is_valid())

    def test_project_edit_form_full(self):
        data = {
            'name': 'Awesome project!',
            'description': 'Hello world!',
            'status': Project.LIVE,
            'is_shared': True,
            'is_forkable': True
            }
        form = ProjectEditForm(data, user=self.user.profile)
        self.assertTrue(form.is_valid())

    def test_project_edit_form_invalid(self):
        data = {'name': ''}
        form = ProjectEditForm(data, user=self.user.profile)
        self.assertFalse(form.is_valid())


class PopcornExternalProjectEditFormTests(TestCase):

    def setUp(self):
        self.user = create_user('bob', with_profile=True)

    def tearDown(self):
        for model in [Template, User]:
            model.objects.all().delete()

    def test_project_edit_form(self):
        data = {
            'name': 'Awesome project!',
            'status': Project.LIVE,
            }
        form = ExternalProjectEditForm(data, user=self.user.profile)
        self.assertTrue(form.is_valid())

    def test_project_edit_form_full(self):
        data = {
            'name': 'Awesome project!',
            'description': 'Hello world!',
            'status': Project.LIVE,
            'is_shared': True,
            }
        form = ExternalProjectEditForm(data, user=self.user.profile)
        self.assertTrue(form.is_valid())

    def test_project_edit_form_invalid(self):
        data = {'name': ''}
        form = ProjectEditForm(data, user=self.user.profile)
        self.assertFalse(form.is_valid())


class PopcornFormEditCategoriesTests(TestCase):

    def setUp(self):
        self.user = create_user('bob', with_profile=True)
        self.category = create_project_category()
        self.template = create_template(slug='basic')
        self.data = {
            'name': 'Awesome project!',
            'description': 'Hello world!',
            'status': Project.LIVE,
            'is_shared': True,
            'is_forkable': True,
            'categories': [self.category.pk]
            }

    def tearDown(self):
        for model in [Template, User]:
            model.objects.all().delete()

    def add_membership(self, status):
        data = {
            'user': self.user.profile,
            'project_category': self.category,
            'status': getattr(ProjectCategoryMembership, status)
            }
        return ProjectCategoryMembership.objects.create(**data)

    def test_project_edit_form_category(self):
        self.add_membership('APPROVED')
        form = ProjectEditForm(self.data, user=self.user.profile)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.has_categories)

    def test_project_edit_form_category_denied(self):
        self.add_membership('DENIED')
        form = ProjectEditForm(self.data, user=self.user.profile)
        self.assertFalse(form.is_valid())
        self.assertFalse(form.has_categories)

    def test_project_edit_form_category_pending(self):
        self.add_membership('PENDING')
        form = ProjectEditForm(self.data, user=self.user.profile)
        self.assertFalse(form.is_valid())
        self.assertFalse(form.has_categories)

    def test_project_edit_form_category_no_membership(self):
        form = ProjectEditForm(self.data, user=self.user.profile)
        self.assertFalse(form.is_valid())
        self.assertFalse(form.has_categories)
