from django.test import TestCase

from nose.tools import ok_, eq_
from ..models import Report


class ReportTest(TestCase):

    def tearDown(self):
        Report.objects.all().delete()

    def test_report_creation(self):
        data = {
            'url': 'http://mozillapopcorn.org',
            'description': 'Description of the report'
            }
        report = Report.objects.create(**data)
        ok_(report.id)
        ok_(report.created)
        eq_(report.is_reviewed, False)
