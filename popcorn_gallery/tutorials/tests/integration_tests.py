from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser, User

from funfactory.middleware import LocaleURLMiddleware
from mock import patch, MagicMock
from nose.tools import ok_, eq_
from test_utils import TestCase

from fixtures import create_tutorial, create_user
from ..models import Tutorial


suppress_locale_middleware = patch.object(LocaleURLMiddleware,
                                          'process_request',
                                          lambda *args: None)


class TutorialDetailIntegrationTest(TestCase):

    def tearDown(self):
        Tutorial.objects.all().delete()
        User.objects.all().delete()

    @suppress_locale_middleware
    def test_tutorial_detail(self):
        tutorial = create_tutorial(status=Tutorial.LIVE)
        response = self.client.get(tutorial.get_absolute_url())
        eq_(response.status_code, 200)
        eq_(response.context['tutorial'], tutorial)

    @suppress_locale_middleware
    def test_tutorial_detail_hidden(self):
        tutorial = create_tutorial(status=Tutorial.HIDDEN)
        response = self.client.get(tutorial.get_absolute_url())
        eq_(response.status_code, 404)


    @suppress_locale_middleware
    def test_tutorial_detail_superuser(self):
        user = create_user('bob', use_hash=False, with_profile=True)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        tutorial = create_tutorial(status=Tutorial.HIDDEN)
        self.client.login(username='bob', password='bob')
        response = self.client.get(tutorial.get_absolute_url())
        eq_(response.status_code, 200)
        eq_(response.context['tutorial'], tutorial)
        self.client.logout()


class TemplateListIntegrationTest(TestCase):

    def setUp(self):
        self.url = reverse('tutorial:object_list')

    def tearDown(self):
        Tutorial.objects.all().delete()
        User.objects.all().delete()

    @suppress_locale_middleware
    def test_tutorial_list(self):
        tutorial = create_tutorial(status=Tutorial.LIVE)
        response = self.client.get(self.url)
        eq_(response.status_code, 200)
