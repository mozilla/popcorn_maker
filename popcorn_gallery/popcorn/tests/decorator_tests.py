from mock import MagicMock
from nose import tools

from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.models import User, AnonymousUser
from django.http import Http404
from django.test import TestCase
from django.test.client import RequestFactory

from .fixtures import create_user, create_project
from ..models import Template, Project
from ..views.projects import valid_user_project


anon_user = AnonymousUser()
anon_user.is_authenticated = MagicMock(return_value=False)


def view_mock(request, project):
    """Mock of a view"""
    return request, project


class TestValidProjectDecorator(TestCase):

    def setUp(self):
        self.user = create_user('bob')
        self.factory = RequestFactory()

    def tearDown(self):
        for model in [Project, Template, User]:
            model.objects.all().delete()

    def assertMockResponse(self, uuid, response, project):
        """Asserts the right response from the mock view"""
        self.assertTrue(isinstance(response, WSGIRequest))
        self.assertTrue(isinstance(project, Project))
        self.assertEqual(project.uuid, uuid)

    def test_published_project(self):
        project = create_project(author=self.user)
        mock = valid_user_project(view_mock)
        request = self.factory.get('/')
        request.user = anon_user
        result = mock(request, username=self.user.username,
                      uuid=project.uuid)
        self.assertMockResponse(project.uuid, *result)

    @tools.raises(Http404)
    def test_unpublished_project(self):
        project = create_project(author=self.user, status=Project.HIDDEN)
        mock = valid_user_project(view_mock)
        request = self.factory.get('/')
        request.user = anon_user
        mock(request, username=self.user.username, uuid=project.uuid)

    @tools.raises(Http404)
    def test_removed_project(self):
        project = create_project(author=self.user, status=Project.LIVE,
                                 is_removed=True)
        mock = valid_user_project(view_mock)
        request = self.factory.get('/')
        request.user = anon_user
        mock(request, username=self.user.username, uuid=project.uuid)

    def test_unpublished_owner(self):
        project = create_project(author=self.user, status=Project.HIDDEN)
        mock = valid_user_project(view_mock)
        request = self.factory.get('/')
        request.user = self.user
        result = mock(request, username=self.user.username, uuid=project.uuid)

    @tools.raises(Http404)
    def test_unpublished_other_user(self):
        alex = create_user('alex')
        project = create_project(author=self.user, status=Project.HIDDEN)
        mock = valid_user_project(view_mock)
        request = self.factory.get('/')
        request.user = alex
        result = mock(request, username=self.user.username, uuid=project.uuid)

