import json

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.test import TestCase
from django.test.client import RequestFactory

from ..decorators import json_handler, login_required_ajax


class AuthedUser(AnonymousUser):

    def is_authenticated(self):
        return True

def view_mock(request):
    """Mock of a view"""
    return request


class PopcornDecoratorTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_view_get(self):
        mock = json_handler(view_mock)
        response = mock(self.factory.get('/'))
        self.assertTrue(hasattr(response, 'JSON'))
        self.assertEqual(response.JSON, {})
        self.assertEqual(response.method, 'GET')
        self.assertFalse(response.is_json)

    def test_view_post(self):
        mock = json_handler(view_mock)
        request = self.factory.post('/', {'foo': 'foo'})
        response = mock(request)
        self.assertTrue(hasattr(response, 'JSON'))
        self.assertEqual(response.JSON, {})
        self.assertTrue('foo' in response.POST)
        self.assertEqual(response.method, 'POST')
        self.assertFalse(response.is_json)

    def test_json_get(self):
        mock = json_handler(view_mock)
        request = self.factory.get('/', {}, CONTENT_TYPE='application/json')
        response = mock(request)
        self.assertTrue(hasattr(response, 'JSON'))
        self.assertEqual(response.JSON, {})
        self.assertEqual(response.method, 'GET')
        self.assertTrue(response.is_json)

    def test_json_post(self):
        mock = json_handler(view_mock)
        request = self.factory.post('/', json.dumps({'foo': 'foo'}),
                                    content_type='application/json',
                                    CONTENT_TYPE='application/json')
        response = mock(request)
        self.assertTrue(hasattr(response, 'JSON'))
        self.assertEqual(response.JSON, {'foo': 'foo'})
        self.assertEqual(response.method, 'POST')
        self.assertTrue(response.is_json)

    def test_json_post_invalid(self):
        """Request is marked as application/json but the data is
        application/x-www-form-urlencoded"""
        mock = json_handler(view_mock)
        request = self.factory.post('/', {'foo': 'foo'},
                                    CONTENT_TYPE='application/json')
        response = mock(request)
        self.assertTrue(isinstance(response, HttpResponseBadRequest))

    def test_json_post_invalid_keys(self):
        """JSON sent is invalid"""
        mock = json_handler(view_mock)
        request = self.factory.post('/', {0: 'foo'},
                                    CONTENT_TYPE='application/json')
        response = mock(request)
        self.assertTrue(isinstance(response, HttpResponseBadRequest))

    def test_json_post_javascript_key(self):
        """JSON sent is invalid"""
        mock = json_handler(view_mock)
        request = self.factory.post('/', {'<script>alert()</script>': 'foo'},
                                    CONTENT_TYPE='application/json')
        response = mock(request)
        self.assertTrue(isinstance(response, HttpResponseBadRequest))


class TestLoginRequredAjaxDecorator(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_get_anon(self):
        mock = login_required_ajax(view_mock)
        request = self.factory.get('/', {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = AnonymousUser()
        response = mock(request)
        self.assertRaises(isinstance(response, HttpResponseForbidden))

    def test_get(self):
        mock = login_required_ajax(view_mock)
        request = self.factory.get('/', {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = AuthedUser()
        response = mock(request)
        self.assertEqual(response.method, 'GET')

    def test_post_anon(self):
        mock = login_required_ajax(view_mock)
        request = self.factory.post('/', {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = AnonymousUser()
        response = mock(request)
        self.assertRaises(isinstance(response, HttpResponseForbidden))

    def test_post(self):
        mock = login_required_ajax(view_mock)
        request = self.factory.post('/', {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = AuthedUser()
        response = mock(request)
        self.assertEqual(response.method, 'POST')
