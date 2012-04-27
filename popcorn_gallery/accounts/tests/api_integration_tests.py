from django.contrib.auth.models import User
from django.utils import simplejson as json
from django.utils.unittest import TestCase
from ...popcorn.tests.utils import CustomClient


class AccountHTTPTestCase(TestCase):

    def setUp(self):
        self.client = CustomClient()

    def tearDown(self):
        User.objects.all().delete()

    def test_create_account(self):
        data = {'email': 'popcorn@mozillapopcorn.org'}
        response = self.client.post('/api/v1/account/', data)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertTrue('username' in data)
        self.assertTrue('apikey' in data)
        self.assertTrue('email' in data)

    def test_invalid_email(self):
        data = {'email': 'invalid@invalid'}
        response = self.client.post('/api/v1/account/', data)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('email' in data['account'])
