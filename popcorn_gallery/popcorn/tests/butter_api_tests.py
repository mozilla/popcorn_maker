from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.utils.unittest import TestCase

from django_extensions.db.fields import json
from nose.tools import eq_, ok_
from .fixtures import create_project, create_user, create_template
from ..models import Project, Template


class JSONClient(Client):

    def get(self, path, **extra):
        extra.update({
            'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest',
            })
        return super(JSONClient, self).get(path, **extra)

    def post(self, path, data={}, content_type='application/json', **extra):
        data = json.dumps(data)
        extra.update({'data': data,
                      'content_type': content_type,
                      'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        return super(JSONClient, self).post(path, **extra)


VALID_DATA = {
    "name": "Rad Project!",
    "data": {"data": "foo"},
    "template": "basic",
    "html": "<!DOCTYPE html5>",
    }


class ButterIntegrationTestCase(TestCase):
    """We use harcoded urls because the API is coupled to them"""

    def setUp(self):
        self.user = create_user('bob')
        self.template = create_template(slug='base-template')
        self.client = JSONClient()
        self.client.login(username='bob', password='bob')

    def tearDown(self):
        self.client.logout()
        for model in [Project, Template, User]:
            model.objects.all().delete()

    def test_add_project(self):
        url = '/api/project/'
        response = self.client.post(url, VALID_DATA)
        eq_(response.status_code, 200)
        response_data = json.loads(response.content)
        eq_(response_data['error'], 'okay')
        ok_('_id' in response_data['project'])
        project = Project.objects.get()
        json.loads(project.metadata)

    def test_get_detail_project_hidden(self):
        project = create_project(author=self.user, status=Project.HIDDEN,
                                 template=self.template)
        url = '/api/project/%s' % project.uuid
        response = self.client.get(url)
        eq_(response.status_code, 200)
        response_data = json.loads(response.content)
        eq_(response_data['error'], 'okay')
        ok_(isinstance(response_data['project'], basestring))
        json.loads(response_data['project'])

    def test_get_detail_project(self):
        project = create_project(author=self.user, status=Project.LIVE,
                                 template=self.template)
        url = '/api/project/%s' % project.uuid
        response = self.client.get(url)
        eq_(response.status_code, 200)
        response_data = json.loads(response.content)
        eq_(response_data['error'], 'okay')
        ok_(isinstance(response_data['project'], basestring))
        json.loads(response_data['project'])

    def test_get_detail_project_removed(self):
        project = create_project(author=self.user, status=Project.REMOVED,
                                 template=self.template)
        url = '/api/project/%s' % project.uuid
        response = self.client.get(url)
        eq_(response.status_code, 404)

    def test_post_detail_project(self):
        project = create_project(author=self.user,
                                 template=self.template)
        url = '/api/project/%s' % project.uuid
        response = self.client.post(url, VALID_DATA)
        eq_(response.status_code, 200)
        response_data = json.loads(response.content)
        eq_(response_data['error'], 'okay')
        ok_('_id', response_data['project'])
        ok_('data', response_data['project'])

    def test_post_detail_project_invalid(self):
        project = create_project(author=self.user, template=self.template)
        url = '/api/project/%s' % project.uuid
        response = self.client.post(url, {'template': 'invalid'})
        eq_(response.status_code, 200)
        response_data = json.loads(response.content)
        eq_(response_data['error'], 'error')
        ok_('form_errors' in response_data)

    def test_list_projects(self):
        alex = create_user('alex')
        create_project(author=alex, template=self.template)
        create_project(author=self.user, template=self.template)
        response = self.client.get('/api/projects')
        eq_(response.status_code, 200)
        response_data = json.loads(response.content)
        eq_(response_data['error'], 'okay')
        eq_(len(response_data['projects']), 1)

    def test_list_project_removed(self):
        create_project(author=self.user, status=Project.REMOVED,
                       template=self.template)
        response = self.client.get('/api/projects')
        eq_(response.status_code, 200)
        response_data = json.loads(response.content)
        eq_(response_data['error'], 'okay')
        eq_(len(response_data['projects']), 0)

    def test_publish_project_get(self):
        project = create_project(author=self.user,
                                 template=self.template)
        url = '/api/publish/%s' % project.uuid
        response = self.client.get(url)
        eq_(response.status_code, 405)

    def test_publish_project(self):
        project = create_project(author=self.user, template=self.template)
        url = '/api/publish/%s' % project.uuid
        response = self.client.post(url, {})
        eq_(response.status_code, 200)
        response_data = json.loads(response.content)
        eq_(response_data['error'], 'okay')
        ok_('url' in response_data)

    def test_publish_project_removed(self):
        project = create_project(author=self.user, status=Project.REMOVED,
                                 template=self.template)
        url = '/api/publish/%s' % project.uuid
        response = self.client.post(url, {})
        eq_(response.status_code, 403)

    def test_whoami(self):
        response = self.client.get('/api/whoami')
        eq_(response.status_code, 200)
        response_data = json.loads(response.content)
        ok_(response_data['username'])
        ok_(response_data['name'])
        ok_(response_data['email'])


class ButterIntegrationTestCaseAnon(TestCase):

    def setUp(self):
        self.client = JSONClient()
        self.user = create_user('bob')

    def tearDown(self):
        self.client.logout()
        for model in [Project, Template, User]:
            model.objects.all().delete()

    def test_whoami(self):
        response = self.client.get('/api/whoami')
        eq_(response.status_code, 403)

    def test_get_detail_project(self):
        project = create_project(author=self.user)
        url = '/api/project/%s' % project.uuid
        response = self.client.get(url)
        eq_(response.status_code, 403)

    def test_post_detail_project(self):
        project = create_project(author=self.user)
        url = '/api/project/%s' % project.uuid
        response = self.client.post(url, VALID_DATA)
        eq_(response.status_code, 403)

    def test_get_detail_project_removed(self):
        project = create_project(author=self.user, status=Project.REMOVED)
        url = '/api/project/%s' % project.uuid
        response = self.client.get(url)
        eq_(response.status_code, 403)

    def test_publish_project(self):
        project = create_project(author=self.user)
        url = '/api/publish/%s' % project.uuid
        response = self.client.post(url, {})
        eq_(response.status_code, 403)


class ButterIntegrationTestCaseNotOwner(TestCase):

    def setUp(self):
        self.user = create_user('bob')
        self.other = create_user('x')
        self.template = create_template(slug='base-template')
        self.client = JSONClient()
        self.client.login(username='bob', password='bob')

    def tearDown(self):
        self.client.logout()
        for model in [Project, Template, User]:
            model.objects.all().delete()

    def test_get_project_unpublished(self):
        project = create_project(author=self.other, status=Project.HIDDEN,
                                 template=self.template)
        url = '/api/project/%s' % project.uuid
        response = self.client.get(url)
        eq_(response.status_code, 404)

    def test_post_project_unpublished(self):
        project = create_project(author=self.other, status=Project.HIDDEN,
                                 template=self.template)
        url = '/api/project/%s' % project.uuid
        response = self.client.post(url, VALID_DATA)
        eq_(response.status_code, 404)

    def test_get_detail_project(self):
        project = create_project(author=self.other, status=Project.LIVE,
                                 is_forkable=False, template=self.template)
        url = '/api/project/%s' % project.uuid
        response = self.client.get(url)
        eq_(response.status_code, 200)
        response_data = json.loads(response.content)
        eq_(response_data['error'], 'okay')
        ok_(isinstance(response_data['project'], basestring))
        json.loads(response_data['project'])

    def test_post_detail_project_not_forkable(self):
        project = create_project(author=self.other, status=Project.LIVE,
                                 is_forkable=False, template=self.template)
        url = '/api/project/%s' % project.uuid
        response = self.client.post(url, VALID_DATA)
        eq_(response.status_code, 403)

    def test_post_detail_project_forkable(self):
        project = create_project(author=self.other, status=Project.LIVE,
                                 is_forkable=True, template=self.template)
        url = '/api/project/%s' % project.uuid
        response = self.client.post(url, VALID_DATA)
        eq_(response.status_code, 200)
        response_data = json.loads(response.content)
        eq_(response_data['error'], 'okay')
        ok_('_id' in response_data['project'])
        json.loads(project.metadata)
        eq_(Project.objects.filter(author=self.user).count(), 1)
        eq_(Project.objects.filter(author=self.other).count(), 1)

