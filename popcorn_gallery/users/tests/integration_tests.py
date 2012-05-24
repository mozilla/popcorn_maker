from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from funfactory.middleware import LocaleURLMiddleware
from test_utils import TestCase
from mock import patch

from .fixtures import create_user
from ..forms import ProfileCreateForm, ProfileForm
from ..models import Profile
from ...popcorn.tests.fixtures import create_project, create_template
from ...popcorn.models import Project

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
        # self.assertTrue('login' in response['Location'])

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
        self.assertEqual(context['profile'].user.username, 'bob')
        self.assertTrue('activity_list' in context)
        self.assertTrue('project_list' in context)

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
        response = self.client.post(url, {'name': 'BOB',
                                          'agreement': True,
                                          'username': 'bob'})
        self.assertRedirects(response, reverse('users_profile',
                                               args=['bob']))

    @suppress_locale_middleware
    def test_profile_creation_existing_username(self):
        alex = create_user('alex')
        url = reverse('users_edit')
        response = self.client.post(url, {'name': 'BOB',
                                          'agreement': True,
                                          'username': 'alex'})
        self.assertEquals(response.status_code, 200)
        context = response.context
        self.assertTrue('form' in context)
        self.assertTrue(isinstance(context['form'], ProfileCreateForm))
        self.assertEqual(context['page_mode'], 'create')

    @suppress_locale_middleware
    def test_profile_creation_invalid_username(self):
        url = reverse('users_edit')
        response = self.client.post(url, {'name': 'BOB',
                                          'agreement': True,
                                          'username': 'admin'})
        self.assertEquals(response.status_code, 200)
        context = response.context
        self.assertTrue('form' in context)
        self.assertTrue(isinstance(context['form'], ProfileCreateForm))
        self.assertEqual(context['page_mode'], 'create')

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
        self.assertRedirects(response, reverse('users_edit'))

    @suppress_locale_middleware
    def test_signout(self):
        url = reverse('logout')
        response = self.client.get(url)
        self.assertRedirects(response, '/')

    @suppress_locale_middleware
    def test_delete_get(self):
        url = reverse('users_delete')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('users_edit'))

    @suppress_locale_middleware
    def test_delete_post(self):
        url = reverse('users_delete')
        response = self.client.post(url, {})
        self.assertRedirects(response, reverse('users_edit'))


class ProfileDataUpdatesTests(TestCase):

    def setUp(self):
        self.user = create_user('bob', with_profile=True)
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
        self.assertEqual(context['profile'].user.username, self.user.username)
        self.assertTrue('activity_list' in context)
        self.assertTrue('project_list' in context)

    @suppress_locale_middleware
    def test_delete_get(self):
        url = reverse('users_delete')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(context['profile'].user.username, self.user.username)

    @suppress_locale_middleware
    def test_delete_post(self):
        url = reverse('users_delete')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 302)
        self.assertEquals(User.objects.all().count(), 0)


class TestProfileProjects(TestCase):

    def setUp(self):
        self.user = create_user('bob', with_profile=True)
        self.client.login(username='bob', password='bob')
        template = create_template()
        self.project = create_project(name='Bob project', author=self.user,
                                      template=template, status=Project.LIVE,
                                      is_shared=True)
        self.alex = create_user('alex')
        self.alex_project = create_project(name='Alex project',
                                           author=self.alex, template=template,
                                           status=Project.LIVE, is_shared=True)

    def tearDown(self):
        self.client.logout()
        for model in [Profile, User, Project]:
            model.objects.all().delete()

    def assert_ownership(self, project_list, user):
        for project in project_list:
            self.assertEqual(project.author, user)

    @suppress_locale_middleware
    def test_user_dashboard(self):
        url = reverse('users_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        project_list = response.context['project_list']
        self.assertEqual(len(project_list), 1)
        self.assert_ownership(project_list, self.user)

    @suppress_locale_middleware
    def test_user_profile(self):
        url = reverse('users_profile', args=['alex'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        project_list = response.context['project_list']
        self.assertEqual(len(project_list), 1)
        self.assert_ownership(project_list, self.alex)

    @suppress_locale_middleware
    def test_hidden_projects_dashboard(self):
        self.project.status = Project.HIDDEN
        self.project.save()
        url = reverse('users_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        project_list = response.context['project_list']
        self.assertEqual(len(project_list), 1)
        self.assert_ownership(project_list, self.user)

    @suppress_locale_middleware
    def test_remove_projects_dashboard(self):
        self.project.is_removed = True
        self.project.save()
        url = reverse('users_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        project_list = response.context['project_list']
        self.assertEqual(len(project_list), 0)
        self.assert_ownership(project_list, self.user)

    @suppress_locale_middleware
    def test_hidden_projects_profile_owner(self):
        self.project.status = Project.HIDDEN
        self.project.save()
        url = reverse('users_profile', args=['bob'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        project_list = response.context['project_list']
        self.assertEqual(len(project_list), 1)
        self.assert_ownership(project_list, self.user)

    @suppress_locale_middleware
    def test_hidden_projects_profile(self):
        self.alex_project.status = Project.HIDDEN
        self.alex_project.save()
        url = reverse('users_profile', args=['alex'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        project_list = response.context['project_list']
        self.assertEqual(len(project_list), 0)
        self.assert_ownership(project_list, self.user)

    @suppress_locale_middleware
    def test_removed_projects_profile_owner(self):
        self.project.is_removed = True
        self.project.save()
        url = reverse('users_profile', args=['bob'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        project_list = response.context['project_list']
        self.assertEqual(len(project_list), 0)
        self.assert_ownership(project_list, self.user)

    @suppress_locale_middleware
    def test_removed_projects_profile(self):
        self.alex_project.is_removed = True
        self.alex_project.save()
        url = reverse('users_profile', args=['alex'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        project_list = response.context['project_list']
        self.assertEqual(len(project_list), 0)
        self.assert_ownership(project_list, self.user)
