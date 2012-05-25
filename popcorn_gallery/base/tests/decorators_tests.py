import json
import mock

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.test import TestCase
from django.test.client import RequestFactory

from nose.tools import eq_, ok_
from ..decorators import json_handler, login_required_ajax, throttle_view


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
        mocked = json_handler(view_mock)
        response = mocked(self.factory.get('/'))
        self.assertTrue(hasattr(response, 'JSON'))
        self.assertEqual(response.JSON, {})
        self.assertEqual(response.method, 'GET')
        self.assertFalse(response.is_json)

    def test_view_post(self):
        mocked = json_handler(view_mock)
        request = self.factory.post('/', {'foo': 'foo'})
        response = mocked(request)
        self.assertTrue(hasattr(response, 'JSON'))
        self.assertEqual(response.JSON, {})
        self.assertTrue('foo' in response.POST)
        self.assertEqual(response.method, 'POST')
        self.assertFalse(response.is_json)

    def test_json_get(self):
        mocked = json_handler(view_mock)
        request = self.factory.get('/', {}, CONTENT_TYPE='application/json')
        response = mocked(request)
        self.assertTrue(hasattr(response, 'JSON'))
        self.assertEqual(response.JSON, {})
        self.assertEqual(response.method, 'GET')
        self.assertTrue(response.is_json)

    def test_json_post(self):
        mocked = json_handler(view_mock)
        request = self.factory.post('/', json.dumps({'foo': 'foo'}),
                                    content_type='application/json',
                                    CONTENT_TYPE='application/json')
        response = mocked(request)
        self.assertTrue(hasattr(response, 'JSON'))
        self.assertEqual(response.JSON, {'foo': 'foo'})
        self.assertEqual(response.method, 'POST')
        self.assertTrue(response.is_json)

    def test_json_post_invalid(self):
        """Request is marked as application/json but the data is
        application/x-www-form-urlencoded"""
        mocked = json_handler(view_mock)
        request = self.factory.post('/', {'foo': 'foo'},
                                    CONTENT_TYPE='application/json')
        response = mocked(request)
        self.assertTrue(isinstance(response, HttpResponseBadRequest))

    def test_json_post_invalid_keys(self):
        """JSON sent is invalid"""
        mocked = json_handler(view_mock)
        request = self.factory.post('/', {0: 'foo'},
                                    CONTENT_TYPE='application/json')
        response = mocked(request)
        self.assertTrue(isinstance(response, HttpResponseBadRequest))

    def test_json_post_javascript_key(self):
        """JSON sent is invalid"""
        mocked = json_handler(view_mock)
        request = self.factory.post('/', {'<script>alert()</script>': 'foo'},
                                    CONTENT_TYPE='application/json')
        response = mocked(request)
        self.assertTrue(isinstance(response, HttpResponseBadRequest))


class TestLoginRequredAjaxDecorator(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_get_anon(self):
        mocked = login_required_ajax(view_mock)
        request = self.factory.get('/', {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = AnonymousUser()
        response = mocked(request)
        self.assertRaises(isinstance(response, HttpResponseForbidden))

    def test_get(self):
        mocked = login_required_ajax(view_mock)
        request = self.factory.get('/', {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = AuthedUser()
        response = mocked(request)
        self.assertEqual(response.method, 'GET')

    def test_post_anon(self):
        mocked = login_required_ajax(view_mock)
        request = self.factory.post('/', {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = AnonymousUser()
        response = mocked(request)
        self.assertRaises(isinstance(response, HttpResponseForbidden))

    def test_post(self):
        mocked = login_required_ajax(view_mock)
        request = self.factory.post('/', {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = AuthedUser()
        response = mocked(request)
        self.assertEqual(response.method, 'POST')


class ThottleDecoratorTest(TestCase):

    def setUp(self):
        # key is a mk5 key, determined between the remote ip and
        # path from the request
        self.key = '8243f83255259f10db07a5c781f7c3ab'
        self.factory = RequestFactory()
        kwargs = {'HTTP_X_FORWARDED_FOR': '127.0.0.1'}
        self.request = self.factory.get('/', **kwargs)

    @mock.patch('django.core.cache.cache.set', return_value=True)
    @mock.patch('django.core.cache.cache.get', return_value=False)
    def test_view_not_in_cache(self, cache_get, cache_set):
        mocked = throttle_view(view_mock, methods=['GET'], duration=30)
        response = mocked(self.request)
        cache_get.assert_called_with(self.key)
        cache_set.assert_called_with(self.key, True, 30)
        eq_(response, self.request)

    @mock.patch('django.core.cache.cache.set', return_value=True)
    @mock.patch('django.core.cache.cache.get', return_value=True)
    def test_view_in_cache(self, cache_get, cache_set):
        mocked = throttle_view(view_mock, methods=['GET'], duration=30)
        response = mocked(self.request)
        cache_get.assert_called_with(self.key)
        eq_(cache_get.called, False)
        eq_(response.status_code, 403)
        ok_(isinstance(response, HttpResponseForbidden))

    @mock.patch('django.core.cache.cache.set', return_value=True)
    @mock.patch('django.core.cache.cache.get', return_value=False)
    def test_other_method_not_in_cache(self, cache_get, cache_set):
        mocked = throttle_view(view_mock, methods=['POST', 'PUT'], duration=30)
        response = mocked(self.request)
        eq_(cache_get.called, False)
        eq_(cache_set.called, False)
        eq_(response, self.request)

    @mock.patch('django.core.cache.cache.set', return_value=True)
    @mock.patch('django.core.cache.cache.get', return_value=True)
    def test_other_method_in_cache(self, cache_get, cache_set):
        mocked = throttle_view(view_mock, methods=['POST', 'PUT'], duration=30)
        response = mocked(self.request)
        eq_(cache_get.called, False)
        eq_(cache_set.called, False)
        eq_(response, self.request)
