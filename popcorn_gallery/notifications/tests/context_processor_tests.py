import datetime

from django.test import TestCase
from django.test.client import RequestFactory

from nose.tools import eq_, ok_
from .fixtures import create_notice
from ..models import Notice
from ..context_processors import notifications


class NoticeContextProcessorTest(TestCase):

    def setUp(self):
        self.notification = create_notice()
        self.factory = RequestFactory()

    def tearDown(self):
        Notice.objects.all().delete()

    def test_context_available(self):
        request = self.factory.get('/')
        data = notifications(request)
        ok_(data['notice_list'])
        eq_(len(data['notice_list']), 1)

    def test_context_available_order(self):
        new_notification = create_notice(title='second')
        request = self.factory.get('/')
        data = notifications(request)
        eq_(list(data['notice_list']), [new_notification, self.notification])

