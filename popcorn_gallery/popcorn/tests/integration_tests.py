from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse

from django_extensions.db.fields import json
from funfactory.middleware import LocaleURLMiddleware
from test_utils import TestCase
from mock import patch
from nose.tools import ok_, eq_

from .fixtures import (create_user, create_project, create_project_category,
                       create_template, create_template_category,
                       create_external_project)
from ..forms import ProjectEditForm, ExternalProjectEditForm
from ..models import (Project, Template, TemplateCategory, ProjectCategory,
                      ProjectCategoryMembership)


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

    def assertContextMessage(self, context, message_status):
        ok_('messages' in context)
        for item in list(context['messages']):
            eq_(item.tags, message_status)


class ProjectIntegrationTest(PopcornIntegrationTestCase):

    def setUp(self):
        super(ProjectIntegrationTest, self).setUp()
        self.category = create_project_category(is_featured=True)

    def tearDown(self):
        super(ProjectIntegrationTest, self).tearDown()
        ProjectCategory.objects.all().delete()

    @suppress_locale_middleware
    def test_project_list(self):
        project = create_project(author=self.user, status=Project.LIVE,
                                 is_shared=True)
        project.categories.add(self.category)
        response = self.client.get(reverse('project_list'))
        context = response.context
        eq_(len(context['project_list']), 1)
        eq_(len(context['category_list']), 1)
        eq_(context['category'], None)

    @suppress_locale_middleware
    def test_project_list_category(self):
        project = create_project(author=self.user, status=Project.LIVE,
                                 is_shared=True)
        project.categories.add(self.category)
        response = self.client.get(reverse('project_list_category',
                                           args=[self.category.slug]))
        context = response.context
        eq_(len(context['project_list']), 1)
        eq_(len(context['category_list']), 1)
        eq_(context['category'], self.category)

    @suppress_locale_middleware
    def test_project_list_invalid_category(self):
        project = create_project(author=self.user)
        response = self.client.get(reverse('project_list_category',
                                           args=['invalid']))
        eq_(response.status_code, 404)


class DetailIntegrationTest(PopcornIntegrationTestCase):

    @suppress_locale_middleware
    def test_project_detail(self):
        project = create_project(author=self.user, status=Project.LIVE)
        url = self.get_url('user_project', self.user, project)
        response = self.client.get(url)
        eq_(response.status_code, 200)
        ok_('<!DOCTYPE html5>' in response.content)

    @suppress_locale_middleware
    def test_unpublished_project_anon(self):
        project = create_project(author=self.user, status=Project.HIDDEN)
        url = self.get_url('user_project', self.user, project)
        response = self.client.get(url)
        eq_(response.status_code, 404)

    @suppress_locale_middleware
    def test_unpublished_project_user(self):
        alex = create_user('alex', with_profile=True)
        project = create_project(author=self.user, status=Project.HIDDEN)
        url = self.get_url('user_project', self.user, project)
        self.client.login(username=alex.username, password='alex')
        response = self.client.get(url)
        eq_(response.status_code, 404)
        self.client.logout()

    @suppress_locale_middleware
    def test_unpublished_project_owner(self):
        project = create_project(author=self.user, status=Project.HIDDEN)
        url = self.get_url('user_project', self.user, project)
        self.client.login(username=self.user.username, password='bob')
        response = self.client.get(url)
        eq_(response.status_code, 200)
        ok_('<!DOCTYPE html5>' in response.content)
        self.client.logout()

    @suppress_locale_middleware
    def test_removed_project(self):
        project = create_project(author=self.user, status=Project.REMOVED)
        url = self.get_url('user_project', self.user, project)
        response = self.client.get(url)
        eq_(response.status_code, 404)


class EditIntegrationTest(PopcornIntegrationTestCase):

    valid_data = {
        'is_shared': False,
        'is_forkable': False,
        'name': 'Changed!',
        'status': Project.HIDDEN,
        'description': 'Description of the project',
        }

    @suppress_locale_middleware
    def test_edited_project_anon(self):
        project = create_project(author=self.user)
        url = self.get_url('user_project_edit', self.user, project)
        response = self.client.get(url)
        eq_(response.status_code, 302)

    @suppress_locale_middleware
    def test_edited_project_anon_post(self):
        project = create_project(author=self.user)
        url = self.get_url('user_project_edit', self.user, project)
        response = self.client.post(url, self.valid_data)
        eq_(response.status_code, 302)

    @suppress_locale_middleware
    def test_edited_project_user(self):
        project = create_project(author=self.user)
        alex = create_user('alex', with_profile=True)
        url = self.get_url('user_project_edit', self.user, project)
        self.client.login(username=alex.username, password='alex')
        response = self.client.get(url)
        eq_(response.status_code, 404)
        self.client.logout()

    @suppress_locale_middleware
    def test_edited_project_user_post(self):
        project = create_project(author=self.user)
        alex = create_user('alex', with_profile=True)
        url = self.get_url('user_project_edit', self.user, project)
        self.client.login(username=alex.username, password='alex')
        response = self.client.post(url, self.valid_data)
        eq_(response.status_code, 404)
        self.client.logout()

    @suppress_locale_middleware
    def test_edited_project_owner(self):
        project = create_project(author=self.user)
        url = self.get_url('user_project_edit', self.user, project)
        self.client.login(username=self.user.username, password='bob')
        response = self.client.get(url)
        eq_(response.status_code, 200)
        context = response.context
        eq_(context['project'], project)
        eq_(context['form'].instance, project)
        ok_(isinstance(context['form'], ProjectEditForm))
        self.client.logout()

    @suppress_locale_middleware
    def test_edited_project_owner_post(self):
        project = create_project(author=self.user)
        url = self.get_url('user_project_edit', self.user, project)
        self.client.login(username=self.user.username, password='bob')
        response = self.client.post(url, self.valid_data)
        self.assertRedirects(response, project.get_absolute_url())
        project = Project.objects.get()
        eq_(project.name, 'Changed!')


    @suppress_locale_middleware
    def test_edited_project_owner_post_removed(self):
        project = create_project(author=self.user, status=Project.REMOVED)
        url = self.get_url('user_project_edit', self.user, project)
        self.client.login(username=self.user.username, password='bob')
        response = self.client.post(url, self.valid_data)
        eq_(response.status_code, 404)


class EditProjectCategoryIntegrationTest(PopcornIntegrationTestCase):

    def setUp(self):
        super(EditProjectCategoryIntegrationTest, self).setUp()
        self.project = create_project(author=self.user, status=Project.LIVE)
        self.category = create_project_category()
        self.data = {
            'name': 'Awesome project!',
            'description': 'Hello world!',
            'status': Project.LIVE,
            'is_shared': True,
            'is_forkable': True,
            'categories': [self.category.pk]
            }
        self.client.login(username=self.user.username, password='bob')
        self.url = self.get_url('user_project_edit', self.user, self.project)

    def tearDown(self):
        super(EditProjectCategoryIntegrationTest, self).tearDown()
        for model in [ProjectCategoryMembership, ProjectCategory, User]:
            model.objects.all().delete()
        self.client.logout()

    def add_membership(self, status):
        data = {
            'user': self.user.profile,
            'project_category': self.category,
            'status': getattr(ProjectCategoryMembership, status)
            }
        return ProjectCategoryMembership.objects.create(**data)

    @suppress_locale_middleware
    def test_edit_project_category_get(self):
        self.add_membership('APPROVED')
        response = self.client.get(self.url)
        eq_(response.status_code, 200)
        ok_(response.context['form'].has_categories)

    @suppress_locale_middleware
    def test_edit_project_category_denied_get(self):
        self.add_membership('DENIED')
        response = self.client.get(self.url)
        eq_(response.status_code, 200)
        eq_(response.context['form'].has_categories, False)

    @suppress_locale_middleware
    def test_edit_project_category_pending_get(self):
        self.add_membership('PENDING')
        response = self.client.get(self.url)
        eq_(response.status_code, 200)
        eq_(response.context['form'].has_categories, False)

    @suppress_locale_middleware
    def test_edit_project_category_post(self):
        self.add_membership('APPROVED')
        response = self.client.post(self.url, self.data, follow=True)
        self.assertContextMessage(response.context, 'success')

    @suppress_locale_middleware
    def test_edit_project_category_denied_post(self):
        self.add_membership('DENIED')
        response = self.client.post(self.url, self.data)
        eq_(response.status_code, 200)
        ok_(response.context['form'].errors)

    @suppress_locale_middleware
    def test_edit_project_category_pending_post(self):
        self.add_membership('PENDING')
        response = self.client.post(self.url, self.data)
        eq_(response.status_code, 200)
        ok_(response.context['form'].errors)


class MetadataIntegrationTest(PopcornIntegrationTestCase):

    @suppress_locale_middleware
    def test_project_detail(self):
        project = create_project(author=self.user, status=Project.LIVE)
        url = self.get_url('user_project_meta', self.user, project)
        response = self.client.get(url)
        eq_(response.status_code, 200)
        data = json.loads(response.content)
        eq_(data['project'], project.name)

    @suppress_locale_middleware
    def test_unpublished_project_anon(self):
        project = create_project(author=self.user, status=Project.HIDDEN)
        url = self.get_url('user_project_meta', self.user, project)
        response = self.client.get(url)
        eq_(response.status_code, 404)

    @suppress_locale_middleware
    def test_unpublished_project_user(self):
        alex = create_user('alex', with_profile=True)
        project = create_project(author=self.user, status=Project.HIDDEN)
        url = self.get_url('user_project_meta', self.user, project)
        self.client.login(username=alex.username, password='alex')
        response = self.client.get(url)
        eq_(response.status_code, 404)
        self.client.logout()

    @suppress_locale_middleware
    def test_unpublished_project_owner(self):
        project = create_project(author=self.user, status=Project.HIDDEN)
        url = self.get_url('user_project_meta', self.user, project)
        self.client.login(username=self.user.username, password='bob')
        response = self.client.get(url)
        eq_(response.status_code, 200)
        data = json.loads(response.content)
        eq_(data['project'], project.name)
        self.client.logout()

    @suppress_locale_middleware
    def test_removed_project(self):
        project = create_project(author=self.user, status=Project.REMOVED)
        url = self.get_url('user_project_meta', self.user, project)
        response = self.client.get(url)
        eq_(response.status_code, 404)


class DataIntegrationTest(PopcornIntegrationTestCase):

    @suppress_locale_middleware
    def test_project_detail(self):
        project = create_project(author=self.user, status=Project.LIVE)
        url = self.get_url('user_project_data', self.user, project)
        response = self.client.get(url)
        eq_(response.status_code, 200)
        data = json.loads(response.content)
        ok_('data' in data)
        ok_(not 'projectID' in data)
        ok_(not 'name' in data)

    @suppress_locale_middleware
    def test_unpublished_project_anon(self):
        project = create_project(author=self.user, status=Project.HIDDEN)
        url = self.get_url('user_project_data', self.user, project)
        response = self.client.get(url)
        eq_(response.status_code, 404)

    @suppress_locale_middleware
    def test_unpublished_project_user(self):
        alex = create_user('alex', with_profile=True)
        project = create_project(author=self.user, status=Project.HIDDEN)
        url = self.get_url('user_project_data', self.user, project)
        self.client.login(username=alex.username, password='alex')
        response = self.client.get(url)
        eq_(response.status_code, 404)
        self.client.logout()

    @suppress_locale_middleware
    def test_unpublished_project_owner(self):
        project = create_project(author=self.user, status=Project.HIDDEN)
        url = self.get_url('user_project_data', self.user, project)
        self.client.login(username=self.user.username, password='bob')
        response = self.client.get(url)
        eq_(response.status_code, 200)
        data = json.loads(response.content)
        ok_('data' in data)
        ok_('projectID' in data)
        ok_('name' in data)
        self.client.logout()

    @suppress_locale_middleware
    def test_published_project_not_owner(self):
        other = create_user('other')
        project = create_project(author=other, status=Project.LIVE)
        url = self.get_url('user_project_data', other, project)
        self.client.login(username=self.user.username, password='bob')
        response = self.client.get(url)
        eq_(response.status_code, 200)
        data = json.loads(response.content)
        ok_('data' in data)
        ok_(not 'projectID' in data)
        ok_(not 'name' in data)
        self.client.logout()

    @suppress_locale_middleware
    def test_removed_project(self):
        project = create_project(author=self.user, status=Project.REMOVED)
        url = self.get_url('user_project_data', self.user, project)
        response = self.client.get(url)
        eq_(response.status_code, 404)


class DeleteIntegrationTest(PopcornIntegrationTestCase):

    def setUp(self):
        super(DeleteIntegrationTest, self).setUp()
        category = create_project_category(name='Special')
        self.project = create_project(author=self.user)
        self.project.categories.add(category)

    def tearDown(self):
        super(DeleteIntegrationTest, self).tearDown()
        ProjectCategory.objects.all().delete()
        self.client.logout()

    @suppress_locale_middleware
    def test_delete_get(self):
        url = self.get_url('user_project_delete', self.user, self.project)
        self.client.login(username=self.user.username, password='bob')
        response = self.client.get(url)
        eq_(response.status_code, 200)
        eq_(response.context['project'], self.project)

    @suppress_locale_middleware
    def test_delete_post(self):
        url = self.get_url('user_project_delete', self.user, self.project)
        self.client.login(username=self.user.username, password='bob')
        response = self.client.post(url, {})
        eq_(response.status_code, 302)
        ok_(reverse('users_dashboard'), response['Location'])
        eq_(Project.objects.all().count(), 0)
        eq_(ProjectCategory.objects.all().count(), 1)
        eq_(User.objects.filter(id=self.user.id).count(), 1)

    @suppress_locale_middleware
    def test_delete_not_owner_get(self):
        alex = create_user('alex', with_profile=True)
        url = self.get_url('user_project_delete', self.user, self.project)
        self.client.login(username=alex.username, password='alex')
        response = self.client.get(url)
        eq_(response.status_code, 404)

    @suppress_locale_middleware
    def test_delete_not_owner_post(self):
        alex = create_user('alex', with_profile=True)
        url = self.get_url('user_project_delete', self.user, self.project)
        self.client.login(username=alex.username, password='alex')
        response = self.client.post(url)
        eq_(response.status_code, 404)

    @suppress_locale_middleware
    def test_delete_anon_get(self):
        url = self.get_url('user_project_delete', self.user, self.project)
        response = self.client.get(url)
        # Redirects to login
        eq_(response.status_code, 302)

    @suppress_locale_middleware
    def test_delete_anon_post(self):
        url = self.get_url('user_project_delete', self.user, self.project)
        response = self.client.get(url)
        eq_(response.status_code, 302)


class CategoryIntegrationTest(TestCase):

    def setUp(self):
        self.category = create_project_category(is_featured=True)
        self.user = create_user('bob', with_profile=True)

    def tearDown(self):
        for model in [Project, User, Template, ProjectCategory]:
            model.objects.all().delete()

    @suppress_locale_middleware
    def test_project_category_detail(self):
        project = create_project(author=self.user, status=Project.LIVE,
                                 is_shared=True)
        project.categories.add(self.category)
        response = self.client.get(self.category.get_absolute_url())
        context = response.context
        eq_(context['category'], self.category)
        eq_(len(context['project_list']), 1)
        eq_(len(context['category_list']), 1)

    @suppress_locale_middleware
    def test_project_category_detail_non_shared(self):
        project = create_project(author=self.user, is_shared=False)
        project.categories.add(self.category)
        response = self.client.get(self.category.get_absolute_url())
        context = response.context
        eq_(context['category'], self.category)
        eq_(len(context['project_list']), 0)

    @suppress_locale_middleware
    def test_category_detail_removed(self):
        project = create_project(author=self.user, status=Project.REMOVED)
        project.categories.add(self.category)
        response = self.client.get(self.category.get_absolute_url())
        context = response.context
        eq_(context['category'], self.category)
        eq_(len(context['project_list']), 0)


class TemplateIntegrationTest(TestCase):

    def setUp(self):
        self.category = create_template_category(is_featured=True)

    def tearDown(self):
        for model in [Template, TemplateCategory]:
            model.objects.all().delete()

    @suppress_locale_middleware
    def test_template_list(self):
        template = create_template(is_featured=True)
        response = self.client.get(reverse('template_list'))
        context = response.context
        eq_(len(context['template_list']), 1)
        eq_(len(context['category_list']), 1)

    @suppress_locale_middleware
    def test_template_list_category(self):
        category = create_template_category()
        template = create_template(is_featured=True)
        template.categories.add(category)
        response = self.client.get(reverse('template_list_category',
                                           args=[category.slug]))
        context = response.context
        eq_(len(context['template_list']), 1)
        eq_(len(context['category_list']), 1)
        eq_(context['category'], category)

    @suppress_locale_middleware
    def test_template_list_hidden(self):
        template = create_template(status=Template.HIDDEN)
        response = self.client.get(reverse('template_list'))
        context = response.context
        eq_(len(context['template_list']), 0)
        eq_(len(context['category_list']), 1)

    @suppress_locale_middleware
    def test_template_list_category_hidden(self):
        category = create_template_category()
        template = create_template(status=Template.HIDDEN)
        template.categories.add(category)
        response = self.client.get(reverse('template_list_category',
                                           args=[category.slug]))
        context = response.context
        eq_(len(context['template_list']), 0)
        eq_(len(context['category_list']), 1)
        eq_(context['category'], category)

    @suppress_locale_middleware
    def test_template_detail_hidden(self):
        template = create_template(status=Template.HIDDEN)
        response = self.client.get(reverse('template_detail',
                                           args=[template.slug]))
        eq_(response.status_code, 404)

    @suppress_locale_middleware
    def test_template_detail(self):
        template = create_template()
        response = self.client.get(reverse('template_detail',
                                           args=[template.slug]))
        eq_(response.status_code, 200)
        ok_('<!DOCTYPE html5>' in response.content)

    @suppress_locale_middleware
    def test_template_summary_hidden(self):
        template = create_template(status=Template.HIDDEN)
        response = self.client.get(reverse('template_summary',
                                           args=[template.slug]))
        eq_(response.status_code, 404)

    @suppress_locale_middleware
    def test_template_summary(self):
        template = create_template()
        response = self.client.get(reverse('template_summary',
                                           args=[template.slug]))
        eq_(response.status_code, 200)
        eq_(response.context['template'], template)
        ok_('object' in response.context)
        ok_('project_list' in response.context)
        ok_('tag_list' in response.context)


    @suppress_locale_middleware
    def test_template_config_hidden(self):
        template = create_template(status=Template.HIDDEN)
        response = self.client.get(reverse('template_summary',
                                           args=[template.slug]))
        eq_(response.status_code, 404)

    @suppress_locale_middleware
    def test_template_config(self):
        template = create_template()
        response = self.client.get(reverse('template_summary',
                                           args=[template.slug]))
        eq_(response.status_code, 200)
        eq_(response.context['template'], template)


class TestCategoryMembershipIntegrationTest(TestCase):

    def setUp(self):
        self.category = create_project_category()
        self.user = create_user('bob', with_profile=True)
        self.client.login(username=self.user.username, password='bob')
        self.url = reverse('project_category_join', args=[self.category.slug])

    def tearDown(self):
        for model in [ProjectCategoryMembership, ProjectCategory, User]:
            model.objects.all().delete()
        self.client.logout()

    def assertContextMessage(self, context, message_status):
        ok_('messages' in context)
        for item in list(context['messages']):
            eq_(item.tags, message_status)

    @suppress_locale_middleware
    def test_membership_request_get(self):
        response = self.client.get(self.url)
        eq_(response.status_code, 200)
        eq_(response.context['category'], self.category)

    @suppress_locale_middleware
    def test_membership_request_post(self):
        response = self.client.post(self.url, {}, follow=True)
        self.assertContextMessage(response.context, 'success')

    @suppress_locale_middleware
    def test_membership_request_post_admin_notification(self):
        admin = create_user('admin', with_profile=True)
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()
        response = self.client.post(self.url, {}, follow=True)
        self.assertContextMessage(response.context, 'success')
        eq_(len(mail.outbox), 1)

    @suppress_locale_middleware
    def test_duplicate_membership_request_get(self):
        ProjectCategoryMembership.objects.create(user=self.user.profile,
                                                 project_category=self.category)
        response = self.client.get(self.url, follow=True)
        self.assertContextMessage(response.context, 'error')

    @suppress_locale_middleware
    def test_duplicate_membership_request_post(self):
        ProjectCategoryMembership.objects.create(user=self.user.profile,
                                                 project_category=self.category)
        response = self.client.post(self.url, {}, follow=True)
        self.assertContextMessage(response.context, 'error')


class TestExternalProjectIntegrationTest(PopcornIntegrationTestCase):

    def setUp(self):
        super(TestExternalProjectIntegrationTest, self).setUp()
        self.project = create_external_project(author=self.user,
                                               status=Project.LIVE)
        self.client.login(username=self.user.username, password='bob')

    def tearDown(self):
        super(TestExternalProjectIntegrationTest, self).tearDown()
        self.client.logout()

    @suppress_locale_middleware
    def test_detail_user_project(self):
        url = self.get_url('user_project', self.user, self.project)
        response = self.client.get(url)
        eq_(response.status_code, 404)

    @suppress_locale_middleware
    def test_detail_user_project_config(self):
        url = self.get_url('user_project_config', self.user, self.project)
        response = self.client.get(url)
        eq_(response.status_code, 404)

    @suppress_locale_middleware
    def test_detail_user_project_meta(self):
        url = self.get_url('user_project_meta', self.user, self.project)
        response = self.client.get(url)
        eq_(response.status_code, 404)

    @suppress_locale_middleware
    def test_detail_user_data(self):
        url = self.get_url('user_project_data', self.user, self.project)
        response = self.client.get(url)
        eq_(response.status_code, 404)

    @suppress_locale_middleware
    def test_detail_user_project_fork(self):
        url = self.get_url('user_project_fork', self.user, self.project)
        response = self.client.get(url)
        eq_(response.status_code, 404)

    @suppress_locale_middleware
    def test_detail_user_project_fork_post(self):
        url = self.get_url('user_project_fork', self.user, self.project)
        response = self.client.post(url, {})
        eq_(response.status_code, 404)

    @suppress_locale_middleware
    def test_edit_project_owner(self):
        url = self.get_url('user_project_edit', self.user, self.project)
        response = self.client.get(url)
        eq_(response.status_code, 200)
        context = response.context
        eq_(context['project'], self.project)
        eq_(context['form'].instance, self.project)
        ok_(isinstance(context['form'], ExternalProjectEditForm))
        self.client.logout()

    @suppress_locale_middleware
    def test_edit_project_owner_post(self):
        data = {
            'is_shared': False,
            'name': 'Changed!',
            'status': Project.HIDDEN,
            'description': 'Description of the project',
        }
        url = self.get_url('user_project_edit', self.user, self.project)
        response = self.client.post(url, data)
        self.assertRedirects(response, self.project.get_absolute_url())
        project = Project.objects.get()
        eq_(project.name, 'Changed!')

