import json

from django.test import TestCase, Client
from django.test.utils import setup_test_environment

USER = 'user'
PASSWORD = 'password'

class JsonApiTest(TestCase):
    fixtures = ['testdata.json']

    def setUp(self):
        setup_test_environment()

    def test_get_tags(self):
        client = Client()
        self.assertTrue(client.login(username=USER, password=PASSWORD))
        response = client.get('/words/tags/')
        self.assertEqual(200, response.status_code)
        self.assertEqual('application/json', response['Content-Type'])
        json_response = json.loads(response.content)
        self.assertEqual(sorted(["awesome", "funny"]), sorted([t['tag'] for t in json_response]))
