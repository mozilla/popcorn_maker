from django.test import TestCase

from nose.tools import ok_, eq_

from ..forms import ReportForm
from ..models import Report


class ReportFormTest(TestCase):

    def tearDown(self):
        Report.objects.all().delete()

    def test_invalid_data(self):
        data = {'url': 'random', 'description': 'Invalid'}
        form = ReportForm(data)
        eq_(form.is_valid(), False)

    def test_invalid_domain(self):
        data = {'url': 'http://invalid.mozillapopcorn.org/inappropriate/',
                'description': 'This is outrageous!'}
        form = ReportForm(data)
        eq_(form.is_valid(), False)

    def test_valid_data(self):
        data = {'url': 'http://test.mozillapopcorn.org/inappropriate/',
                'description': 'This is outrageous!'}
        form = ReportForm(data)
        ok_(form.is_valid())
