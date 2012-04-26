import httplib
import urllib
try:
    import json
except ImportError:
    import simplejson as json

from django.contrib.auth.models import User
from ...popcorn.tests.testcases import TestServerTestCase


class AccountHTTPTestCase(TestServerTestCase):

    def setUp(self):
        self.start_server(address='localhost', port=8001)

    def tearDown(self):
        self.stop_server()

    def get_connection(self):
        return httplib.HTTPConnection('localhost', 8001)

    def do_request(self, method, url, data=None):
        """Generates a request with the right headers"""
        connection = self.get_connection()
        headers = {'Accept': 'application/json'}
        if data:
            headers['Content-type'] = 'application/json'
        kwargs = {'headers': headers }
        if data:
            kwargs['body'] = json.dumps(data)
        connection.request(method, url, **kwargs)
        response = connection.getresponse()
        connection.close()
        return response

    def test_create_account(self):
        data = {'email': 'popcorn@mozillapopcorn.org'}
        response = self.do_request('POST', '/api/v1/account/', data)
        data = json.load(response)
        self.assertEqual(response.status, 201)
        self.assertTrue('username' in data)
        self.assertTrue('apikey' in data)
        self.assertTrue('email' in data)

    def test_invalid_email(self):
        data = {'email': 'invalid@invalid'}
        response = self.do_request('POST', '/api/v1/account/', data)
        data = json.load(response)
        self.assertEqual(response.status, 400)
        self.assertTrue('email' in data['account'])
