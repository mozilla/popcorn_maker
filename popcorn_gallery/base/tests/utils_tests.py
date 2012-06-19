from django.core import mail
from django.contrib.auth.models import User

from nose.tools import ok_, eq_
from test_utils import TestCase

from ...popcorn.tests.fixtures import create_user
from ..utils import notify_admins


class NotifyAdminTest(TestCase):

    def tearDown(self):
        User.objects.all().delete()

    def test_notify_admins(self):
        user = create_user('x')
        user.is_superuser = True
        user.is_staff = True
        user.save()
        result = notify_admins('Hello!', 'How are you doing?')
        eq_(result, True)
        eq_(len(mail.outbox), 1)

    def test_notify_no_admins(self):
        result = notify_admins('Hello!', 'How are you doing?')
        eq_(result, False)
        eq_(len(mail.outbox), 0)
