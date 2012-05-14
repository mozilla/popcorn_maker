from django.test import TestCase

from .fixtures import create_template
from ..models import Template, Project
from ..forms import ProjectForm, ProjectEditForm


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

    def test_project_edit_form(self):
        data = {
            'name': 'Awesome project!',
            'status': Project.LIVE,
            }
        form = ProjectEditForm(data)
        self.assertTrue(form.is_valid())

    def test_project_edit_form_full(self):
        data = {
            'name': 'Awesome project!',
            'description': 'Hello world!',
            'status': Project.LIVE,
            'is_shared': True,
            'is_forkable': True
            }
        form = ProjectEditForm(data)
        self.assertTrue(form.is_valid())

    def test_project_edit_form_invalid(self):
        data = {'name': ''}
        form = ProjectEditForm(data)
        self.assertFalse(form.is_valid())
