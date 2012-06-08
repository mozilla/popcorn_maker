from django.contrib.auth.models import User
from django.utils.unittest import TestCase

from .fixtures import create_user
from ..models import Profile
from ..forms import ProfileForm, ProfileCreateForm


class TestProfileForms(TestCase):

    def tearDown(self):
        for model in [Profile, User]:
            model.objects.all().delete()

    def test_valid_data_edit(self):
        user = create_user('bob', use_hash=True)
        data = {'name': 'BOB'}
        form = ProfileForm(data, instance=user.get_profile())
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(instance.name, 'BOB')

    def test_invalid_data_edit(self):
        user = create_user('bob', use_hash=True)
        data = {}
        form = ProfileForm(data, instance=user.get_profile())
        self.assertFalse(form.is_valid())

    def test_valid_data_create(self):
        user = create_user('bob')
        data = {'name': 'BOB',
                'agreement': True,
                'username': 'bob'}
        form = ProfileCreateForm(data, instance=user.get_profile())
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(instance.name, 'BOB')

    def test_duplicated_username(self):
        alex = create_user('alex')
        user = create_user('bob')
        data = {'name': 'BOB',
                'agreement': True,
                'username': 'alex'}
        form = ProfileCreateForm(data, instance=user.get_profile())
        self.assertFalse(form.is_valid())

    def test_blacklisted_username(self):
        user = create_user('bob')
        data = {'name': 'BOB',
                'agreement': True,
                'username': 'admin'}
        form = ProfileCreateForm(data, instance=user.get_profile())
        self.assertFalse(form.is_valid())

    def test_invalid_data_create(self):
        user = create_user('bob')
        data = {'name': 'BOB'}
        form = ProfileCreateForm(data, instance=user.get_profile())
        self.assertFalse(form.is_valid())

    def test_invalid_username_characters(self):
        user = create_user('bob')
        data = {'name': 'BOB',
                'agreement': True,
                'username': 'bob!'
                }
        form = ProfileCreateForm(data, instance=user.get_profile())
        self.assertFalse(form.is_valid())

