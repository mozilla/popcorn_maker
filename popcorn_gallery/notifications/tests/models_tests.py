import datetime

from django.test import TestCase
from dateutil.relativedelta import relativedelta

from nose.tools import eq_, ok_
from .fixtures import create_notice
from ..models import Notice


class NoticeTest(TestCase):

    def tearDown(self):
        for model in [Notice]:
            model.objects.all().delete()

    def test_create_notice(self):
        data = {
            'title': 'Hello world!',
            'body': 'This is a Notice',
            }
        notice = Notice.objects.create(**data)
        ok_(notice.id, "Notice creation failed")
        ok_(notice.created, "Notice creation failed")
        eq_(notice.status, Notice.LIVE)

    def test_create_hidden_notice(self):
        data = {
            'title': 'Hello world!',
            'body': 'This is a Notice',
            'status': Notice.REMOVED,
            }
        notice = Notice.objects.create(**data)
        ok_(notice.id, "Notice creation failed")
        ok_(notice.created, "Notice creation failed")
        eq_(notice.status, Notice.REMOVED)

    def test_create_expiring_notice(self):
        data = {
            'title': 'Hello world!',
            'body': 'This is a Notice',
            'end_date': datetime.datetime.utcnow(),
            }
        notice = Notice.objects.create(**data)
        ok_(notice.id, "Notice creation failed")
        ok_(notice.created, "Notice creation failed")


class NoticeManagerTest(TestCase):

    def tearDown(self):
        for model in [Notice]:
            model.objects.all().delete()

    def test_live_manager(self):
        create_notice()
        create_notice(status=Notice.REMOVED)
        eq_(Notice.live.all().count(), 1)
        eq_(Notice.objects.all().count(), 2)

    def test_expired_notice(self):
        end_date = datetime.datetime.utcnow() - relativedelta(hours=1)
        notice = create_notice(end_date=end_date)
        eq_(notice.status, Notice.LIVE)
        eq_(Notice.live.all().count(), 0)
