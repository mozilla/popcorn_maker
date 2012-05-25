from django.core import mail
from django.contrib.auth.models import User

from nose.tools import ok_, eq_
from test_utils import TestCase

from ..utils import notify_admins


class NotifyAdminTest(TestCase):

    def tearDown(self):
        User.objects.all().delete()

    def create_user(self, handle='x'):
        email = '%s@%s.com' % (handle, handle)
        user = User.objects.create_user(handle, email, handle)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

    def test_notify_admins(self):
        self.create_user()
        result = notify_admins('Hello!', 'How are you doing?')
        eq_(result, True)
        eq_(len(mail.outbox), 1)

    def test_notify_no_admins(self):
        result = notify_admins('Hello!', 'How are you doing?')
        eq_(result, False)
        eq_(len(mail.outbox), 0)
