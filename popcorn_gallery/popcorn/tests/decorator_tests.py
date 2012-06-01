from mock import MagicMock
from nose import tools
from nose.tools import ok_, eq_

from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.models import User, AnonymousUser
from django.http import Http404, HttpResponseForbidden
from django.test import TestCase
from django.test.client import RequestFactory

from .fixtures import create_user, create_project
from ..models import Template, Project
from ..decorators import valid_user_project


anon_user = AnonymousUser()
anon_user.is_authenticated = MagicMock(return_value=False)


@valid_user_project(['username', 'shortcode'])
def view_mock(request, project):
    """Mock of a view"""
    return request, project

@valid_user_project(['uuid'])
def view_mock_uuid(request, project):
    """Mock of a view"""
    return request, project


class TestValidProjectDecorator(TestCase):

    def setUp(self):
        self.user = create_user('bob')
        self.factory = RequestFactory()

    def tearDown(self):
        for model in [Project, Template, User]:
            model.objects.all().delete()

    def assertMockResponse(self, shortcode, response, project):
        """Asserts the right response from the mock view"""
        ok_(isinstance(response, WSGIRequest))
        ok_(isinstance(project, Project))
        eq_(project.shortcode, shortcode)

    def test_published_project(self):
        project = create_project(author=self.user, status=Project.LIVE)
        request = self.factory.get('/')
        request.user = anon_user
        result = view_mock(request, username=self.user.username,
                           shortcode=project.shortcode)
        self.assertMockResponse(project.shortcode, *result)

    def test_published_project_uuid(self):
        project = create_project(author=self.user, status=Project.LIVE)
        request = self.factory.get('/')
        request.user = anon_user
        result = view_mock_uuid(request, uuid=project.uuid)
        self.assertMockResponse(project.shortcode, *result)

    @tools.raises(Http404)
    def test_unpublished_project(self):
        project = create_project(author=self.user, status=Project.HIDDEN)
        request = self.factory.get('/')
        request.user = anon_user
        response = view_mock(request, username=self.user.username,
                             shortcode=project.shortcode)
        ok_(isinstance(response, HttpResponseForbidden))

    @tools.raises(Http404)
    def test_removed_project(self):
        project = create_project(author=self.user, status=Project.REMOVED)
        request = self.factory.get('/')
        request.user = anon_user
        view_mock(request, username=self.user.username,
                  shortcode=project.shortcode)

    def test_unpublished_owner(self):
        project = create_project(author=self.user, status=Project.HIDDEN)
        request = self.factory.get('/')
        request.user = self.user
        result = view_mock(request, username=self.user.username,
                           shortcode=project.shortcode)
        self.assertMockResponse(project.shortcode, *result)

    @tools.raises(Http404)
    def test_unpublished_other_user(self):
        alex = create_user('alex')
        project = create_project(author=self.user, status=Project.HIDDEN)
        request = self.factory.get('/')
        request.user = alex
        view_mock(request, username=self.user.username,
                  shortcode=project.shortcode)
