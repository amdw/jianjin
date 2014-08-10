import json

from django.test import TestCase, Client
from django.test.utils import setup_test_environment

USER = 'user'
PASSWORD = 'password'

class JsonApiTest(TestCase):
    fixtures = ['testdata.json']

    def setUp(self):
        setup_test_environment()
        self.client = Client()
        self.assertTrue(self.client.login(username=USER, password=PASSWORD))

    def test_get_tags(self):
        response = self.client.get('/words/tags/')
        self.assertEqual(200, response.status_code)
        self.assertEqual('application/json', response['Content-Type'])
        json_response = json.loads(response.content)
        self.assertEqual(sorted(["awesome", "funny"]), sorted([t['tag'] for t in json_response]))

class AuthenticationTest(TestCase):
    fixtures = ['testdata.json']

    def setUp(self):
        setup_test_environment()

    def test_html_redirect(self):
        """Test that unauthenticated HTML requests are redirected to the login page"""
        response = self.client.get('/', follow=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual([("http://testserver/accounts/login/?next=/", 302)], response.redirect_chain)
