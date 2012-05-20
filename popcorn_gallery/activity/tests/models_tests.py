from django.contrib.auth.models import User
from django.test import TestCase

from nose.tools import ok_, eq_

from .fixtures import create_user, create_activity
from ..models import Activity


class ActivityTest(TestCase):

    def setUp(self):
        self.user = create_user('bob', with_profile=True)

    def tearDown(self):
        for model in [Activity, User]:
            model.objects.all().delete()

    def test_activity_creation(self):
        data = {
            'user': self.user,
            'body': 'has created a Category',
            }
        activity = Activity.objects.create(**data)
        ok_(activity.id)
        ok_(activity.created)

    def test_activity_manager(self):
        activity = create_activity(user=self.user)
        other_user = create_user('other')
        create_activity(user=other_user)
        eq_(Activity.objects.get_for_user(self.user).count(), 1)
        eq_(Activity.objects.all().count(), 2)
