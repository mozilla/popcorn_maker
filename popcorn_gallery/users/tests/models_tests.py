from django.contrib.auth.models import User
from django.test import TestCase

from .fixtures import create_user
from ..models import Profile


class UserProfileTest(TestCase):

    def tearDown(self):
        for model in [Profile, User]:
            model.objects.all().delete()

    def test_profile_creation(self):
        user = create_user('bob', use_hash=True)
        profile = user.get_profile()
        assert profile, "Profile wasn't created"
        assert profile.get_absolute_url(), "absolute URL couldn't be generated"
        self.assertFalse(profile.has_chosen_identifier)

    def test_valid_identifier(self):
        user = create_user('bob', use_hash=True)
        profile = user.get_profile()
        self.assertFalse(profile.has_chosen_identifier)
        user.username = 'hello'
        user.save()
        profile = user.get_profile()
        self.assertTrue(profile.has_chosen_identifier)
