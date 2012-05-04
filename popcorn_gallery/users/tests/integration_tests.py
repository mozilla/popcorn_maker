from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
#from django.utils.unittest import TestCase

from funfactory.middleware import LocaleURLMiddleware
from test_utils import TestCase
from mock import Mock, patch

from .fixtures import create_user
from ..forms import ProfileCreateForm, ProfileForm
from ..models import Profile

suppress_locale_middleware = patch.object(LocaleURLMiddleware,
                                          'process_request',
                                          lambda *args: None)


class ProfileDataAnonTests(TestCase):

    def tearDown(self):
        for model in [Profile, User]:
            model.objects.all().delete()

    def assertRedirectsLogin(self, response):
        self.assertEqual(response.status_code, 302)
        self.assertTrue('Location' in response)
        self.assertTrue('login' in response['Location'])

    @suppress_locale_middleware
    def test_profile_access(self):
        url = reverse('users_edit')
        response = self.client.get(url)
        self.assertRedirectsLogin(response)

    @suppress_locale_middleware
    def test_profile_detail(self):
        user = create_user('bob')
        url = reverse('users_profile', args=['bob'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(context['object'].user.username, 'bob')

    @suppress_locale_middleware
    def test_dashboard(self):
        url = reverse('users_dashboard')
        response = self.client.get(url)
        self.assertRedirectsLogin(response)

    @suppress_locale_middleware
    def test_signout(self):
        url = reverse('logout')
        response = self.client.get(url)
        self.assertRedirects(response, '/')

    @suppress_locale_middleware
    def test_delete_get(self):
        url = reverse('users_delete')
        response = self.client.get(url)
        self.assertRedirectsLogin(response)

    @suppress_locale_middleware
    def test_delete_post(self):
        url = reverse('users_delete')
        response = self.client.post(url, {})
        self.assertRedirectsLogin(response)


class ProfileDataTests(TestCase):

    def setUp(self):
        self.user = create_user('bob', use_hash=True)
        self.client.login(username=self.user.username, password='bob')

    def tearDown(self):
        self.client.logout()
        for model in [Profile, User]:
            model.objects.all().delete()

    def assertRedirectsLogin(self, response):
        self.assertEqual(response.status_code, 302)
        self.assertTrue('Location' in response)
        self.assertTrue('login' in response['Location'])

    @suppress_locale_middleware
    def test_profile_creation_get(self):
        url = reverse('users_edit')
        response = self.client.get(url)
        context = response.context
        self.assertEquals(response.status_code, 200)
        self.assertTrue('form' in context)
        self.assertTrue(isinstance(context['form'], ProfileCreateForm))
        self.assertEqual(context['page_mode'], 'create')

    @suppress_locale_middleware
    def test_profile_creation_post(self):
        url = reverse('users_edit')
        response = self.client.post(url, {'name': 'BOB', 'agreement': True})
        self.assertRedirects(response, reverse('users_profile',
                                               args=[self.user.username]))

    @suppress_locale_middleware
    def test_profile_creation_post_invalid(self):
        url = reverse('users_edit')
        response = self.client.post(url, {'name': 'BOB'})
        self.assertEquals(response.status_code, 200)
        context = response.context
        self.assertTrue('form' in context)
        self.assertTrue(isinstance(context['form'], ProfileCreateForm))
        self.assertEqual(context['page_mode'], 'create')

    @suppress_locale_middleware
    def test_dashboard(self):
        url = reverse('users_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(context['object'].user.username, self.user.username)

    @suppress_locale_middleware
    def test_signout(self):
        url = reverse('logout')
        response = self.client.get(url)
        self.assertRedirects(response, '/')

    @suppress_locale_middleware
    def test_delete_get(self):
        url = reverse('users_delete')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(context['object'].user.username, self.user.username)

    @suppress_locale_middleware
    def test_delete_post(self):
        url = reverse('users_delete')
        response = self.client.post(url, {})
        self.assertRedirects(response, '/')
        self.assertEquals(User.objects.all().count(), 0)


class ProfileDataUpdatesTests(TestCase):

    def setUp(self):
        self.user = create_user('bob')
        self.client.login(username='bob', password='bob')

    def tearDown(self):
        self.client.logout()
        for model in [Profile, User]:
            model.objects.all().delete()

    @suppress_locale_middleware
    def test_profile_update_get(self):
        url = reverse('users_edit')
        response = self.client.get(url)
        context = response.context
        self.assertEquals(response.status_code, 200)
        self.assertTrue('form' in context)
        self.assertTrue(isinstance(context['form'], ProfileForm))
        self.assertEqual(context['page_mode'], 'edit')

    @suppress_locale_middleware
    def test_profile_update_post(self):
        url = reverse('users_edit')
        response = self.client.post(url, {'name': 'BOB'})
        self.assertRedirects(response, reverse('users_profile',
                                               args=[self.user.username, ]))

    @suppress_locale_middleware
    def test_profile_update_post_invalid(self):
        url = reverse('users_edit')
        response = self.client.post(url, {})
        self.assertEquals(response.status_code, 200)
        context = response.context
        self.assertTrue('form' in context)
        self.assertTrue(isinstance(context['form'], ProfileForm))
        self.assertEqual(context['page_mode'], 'edit')

    @suppress_locale_middleware
    def test_dashboard(self):
        url = reverse('users_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(context['object'].user.username, self.user.username)

    @suppress_locale_middleware
    def test_delete_get(self):
        url = reverse('users_delete')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(context['object'].user.username, self.user.username)

    @suppress_locale_middleware
    def test_delete_post(self):
        url = reverse('users_delete')
        response = self.client.post(url, {})
        self.assertRedirects(response, '/')
        self.assertEquals(User.objects.all().count(), 0)
