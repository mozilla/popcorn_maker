from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from funfactory.middleware import LocaleURLMiddleware
from mock import patch
from nose.tools import ok_, eq_
from test_utils import TestCase

from ..models import Report


suppress_locale_middleware = patch.object(LocaleURLMiddleware,
                                          'process_request',
                                          lambda *args: None)


class ReportIntegrationTestCase(TestCase):

    def setUp(self):
        self.url = reverse('report')

    def tearDown(self):
        for model in [Report, User]:
            model.objects.all().delete()

    def assertContextMessage(self, context, message_status):
        ok_('messages' in context)
        for item in list(context['messages']):
            eq_(item.tags, message_status)

    def create_user(self, handle='x'):
        email = '%s@%s.com' % (handle, handle)
        user = User.objects.create_user(handle, email, handle)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

    @suppress_locale_middleware
    def test_report_form_get(self):
        response = self.client.get(self.url)
        eq_(response.status_code, 200)
        ok_('form' in response.context)

    @suppress_locale_middleware
    def test_report_form_post_invalid(self):
        data = {
            'url': 'invalid',
            }
        response = self.client.post(self.url, data)
        eq_(response.status_code, 200)
        ok_('form' in response.context)
        ok_(response.context['form'].errors)

    @suppress_locale_middleware
    def test_report_form_post_valid(self):
        self.create_user()
        data = {
            'url': 'http://mozillapopcorn.org',
            'description': 'Description of the report',
            }
        response = self.client.post(self.url, data, follow=True)
        self.assertContextMessage(response.context, 'success')
        eq_(len(mail.outbox), 1)
