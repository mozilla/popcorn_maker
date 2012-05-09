from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils import simplejson as json

from funfactory.middleware import LocaleURLMiddleware
from test_utils import TestCase
from mock import patch

from .fixtures import (create_user, create_project, create_category,
                       create_template)
from ..models import Project, Template, Category


suppress_locale_middleware = patch.object(LocaleURLMiddleware,
                                          'process_request',
                                          lambda *args: None)


class PopcornIntegrationTestCase(TestCase):
    def setUp(self):
        self.user = create_user('bob', with_profile=True)

    def tearDown(self):
        for model in [Project, User, Template]:
            model.objects.all().delete()

    def get_url(self, name, user, project):
        kwargs = {
            'username': user.username,
            'shortcode': project.shortcode
            }
        return reverse(name, kwargs=kwargs)


class DetailIntegrationTest(PopcornIntegrationTestCase):

    @suppress_locale_middleware
    def test_project_detail(self):
        project = create_project(author=self.user, status=Project.LIVE)
        url = self.get_url('user_project', self.user, project)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(context['object'], project)

    @suppress_locale_middleware
    def test_unpublished_project_anon(self):
        project = create_project(author=self.user, status=Project.HIDDEN)
        url = self.get_url('user_project', self.user, project)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @suppress_locale_middleware
    def test_unpublished_project_user(self):
        alex = create_user('alex', with_profile=True)
        project = create_project(author=self.user, status=Project.HIDDEN)
        url = self.get_url('user_project', self.user, project)
        self.client.login(username=alex.username, password='alex')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.client.logout()

    @suppress_locale_middleware
    def test_unpublished_project_owner(self):
        project = create_project(author=self.user, status=Project.HIDDEN)
        url = self.get_url('user_project', self.user, project)
        self.client.login(username=self.user.username, password='bob')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(context['object'], project)
        self.client.logout()

    @suppress_locale_middleware
    def test_removed_project(self):
        project = create_project(author=self.user, status=Project.LIVE,
                                 is_removed=True)
        url = self.get_url('user_project', self.user, project)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class EditIntegrationTest(PopcornIntegrationTestCase):

    valid_data = {
        'is_shared': False,
        'is_forkable': False,
        'name': 'Changed!',
        'status': Project.HIDDEN,
        }

    @suppress_locale_middleware
    def test_edited_project_anon(self):
        project = create_project(author=self.user)
        url = self.get_url('user_project_edit', self.user, project)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @suppress_locale_middleware
    def test_edited_project_anon_post(self):
        project = create_project(author=self.user)
        url = self.get_url('user_project_edit', self.user, project)
        response = self.client.post(url, self.valid_data)
        self.assertEqual(response.status_code, 404)

    @suppress_locale_middleware
    def test_edited_project_user(self):
        project = create_project(author=self.user)
        alex = create_user('alex', with_profile=True)
        url = self.get_url('user_project_edit', self.user, project)
        self.client.login(username=alex.username, password='alex')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.client.logout()

    @suppress_locale_middleware
    def test_edited_project_user_post(self):
        project = create_project(author=self.user)
        alex = create_user('alex', with_profile=True)
        url = self.get_url('user_project_edit', self.user, project)
        self.client.login(username=alex.username, password='alex')
        response = self.client.post(url, self.valid_data)
        self.assertEqual(response.status_code, 404)
        self.client.logout()

    @suppress_locale_middleware
    def test_edited_project_owner(self):
        project = create_project(author=self.user)
        url = self.get_url('user_project_edit', self.user, project)
        self.client.login(username=self.user.username, password='bob')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(context['object'], project)
        self.assertEqual(context['form'].instance, project)
        self.client.logout()

    @suppress_locale_middleware
    def test_edited_project_owner_post(self):
        project = create_project(author=self.user)
        url = self.get_url('user_project_edit', self.user, project)
        self.client.login(username=self.user.username, password='bob')
        response = self.client.post(url, self.valid_data)
        self.assertRedirects(response, project.get_absolute_url())
        project = Project.objects.get()
        self.assertEqual(project.name, 'Changed!')


class MetadataIntegrationTest(PopcornIntegrationTestCase):

    @suppress_locale_middleware
    def test_project_detail(self):
        project = create_project(author=self.user, status=Project.LIVE)
        url = self.get_url('user_project_meta', self.user, project)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['project'], project.name)

    @suppress_locale_middleware
    def test_unpublished_project_anon(self):
        project = create_project(author=self.user, status=Project.HIDDEN)
        url = self.get_url('user_project_meta', self.user, project)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @suppress_locale_middleware
    def test_unpublished_project_user(self):
        alex = create_user('alex', with_profile=True)
        project = create_project(author=self.user, status=Project.HIDDEN)
        url = self.get_url('user_project_meta', self.user, project)
        self.client.login(username=alex.username, password='alex')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.client.logout()

    @suppress_locale_middleware
    def test_unpublished_project_owner(self):
        project = create_project(author=self.user, status=Project.HIDDEN)
        url = self.get_url('user_project_meta', self.user, project)
        self.client.login(username=self.user.username, password='bob')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['project'], project.name)
        self.client.logout()

    @suppress_locale_middleware
    def test_removed_project(self):
        project = create_project(author=self.user, status=Project.LIVE,
                                 is_removed=True)
        url = self.get_url('user_project_meta', self.user, project)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class DataIntegrationTest(PopcornIntegrationTestCase):

    @suppress_locale_middleware
    def test_project_detail(self):
        project = create_project(author=self.user, status=Project.LIVE)
        url = self.get_url('user_project_data', self.user, project)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['project'], '{"data": "foo"}')

    @suppress_locale_middleware
    def test_unpublished_project_anon(self):
        project = create_project(author=self.user, status=Project.HIDDEN)
        url = self.get_url('user_project_data', self.user, project)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @suppress_locale_middleware
    def test_unpublished_project_user(self):
        alex = create_user('alex', with_profile=True)
        project = create_project(author=self.user, status=Project.HIDDEN)
        url = self.get_url('user_project_data', self.user, project)
        self.client.login(username=alex.username, password='alex')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.client.logout()

    @suppress_locale_middleware
    def test_unpublished_project_owner(self):
        project = create_project(author=self.user, status=Project.HIDDEN)
        url = self.get_url('user_project_data', self.user, project)
        self.client.login(username=self.user.username, password='bob')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['project'], '{"data": "foo"}')
        self.client.logout()

    @suppress_locale_middleware
    def test_removed_project(self):
        project = create_project(author=self.user, status=Project.LIVE,
                                 is_removed=True)
        url = self.get_url('user_project_data', self.user, project)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class CategoryIntegrationTest(TestCase):

    def setUp(self):
        self.category = create_category()
        self.user = create_user('bob', with_profile=True)

    def tearDown(self):
        for model in [Project, User, Template, Category]:
            model.objects.all().delete()

    @suppress_locale_middleware
    def test_category_detail(self):
        project = create_project(author=self.user)
        project.categories.add(self.category)
        response = self.client.get(self.category.get_absolute_url())
        context = response.context
        self.assertEqual(context['object'], self.category)
        self.assertEqual(len(context['project_list']), 1)

    @suppress_locale_middleware
    def test_category_detail_non_shared(self):
        project = create_project(author=self.user, is_shared=False)
        project.categories.add(self.category)
        response = self.client.get(self.category.get_absolute_url())
        context = response.context
        self.assertEqual(context['object'], self.category)
        self.assertEqual(len(context['project_list']), 0)

    @suppress_locale_middleware
    def test_category_detail_removed(self):
        project = create_project(author=self.user, is_removed=True)
        project.categories.add(self.category)
        response = self.client.get(self.category.get_absolute_url())
        context = response.context
        self.assertEqual(context['object'], self.category)
        self.assertEqual(len(context['project_list']), 0)


class TemplateIntegrationTest(TestCase):

    def tearDown(self):
        Template.objects.all().delete()

    @suppress_locale_middleware
    def test_template_detail(self):
        template = create_template()
        response = self.client.get(reverse('template_list'))
        context = response.context
        self.assertEqual(len(context['object_list']), 1)
