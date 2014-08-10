# -*- coding: utf-8 -*-

import json

from django.test import TestCase, Client
from django.test.utils import setup_test_environment

USER = 'user'
PASSWORD = 'password'

class JsonApiTest(TestCase):
    fixtures = ['testdata.json']

    def setUp(self):
        setup_test_environment()
        self.assertTrue(self.client.login(username=USER, password=PASSWORD))

    def assert_successful_json(self, response):
        """Assert that the response was successful, and contains JSON content. Return the parsed content."""
        self.assertEqual(200, response.status_code)
        self.assertEqual('application/json', response['Content-Type'])
        return json.loads(response.content)

    def test_get_tags(self):
        response = self.client.get('/words/tags/')
        json_response = self.assert_successful_json(response)
        self.assertEqual(sorted(["awesome", "funny"]), sorted([t['tag'] for t in json_response]))

    def test_tags_read_only(self):
        """Tags should only be updated via words, so posting directly should not work"""
        response = self.client.post('/words/tags/', {"tag": "wibble"})
        self.assertEqual(405, response.status_code)

    def test_get_words(self):
        response = self.client.get('/words/words/')
        json_response = self.assert_successful_json(response)
        self.assertEqual(sorted([u"你好", u"蛋白质", u"乌龙球", u"妇女"]), sorted(w['word'] for w in json_response))

    def test_flashcard(self):
        response = self.client.get('/words/flashcard', follow=True)
        self.assert_successful_json(response)
        response = self.client.get('/words/flashcard/awesome', follow=True)
        self.assert_successful_json(response)

    def test_flashcard_errors(self):
        # Non-existent tag
        response = self.client.get('/words/flashcard/blah', follow=True)
        self.assertEqual(404, response.status_code)
        # Read-only API point
        response = self.client.post('/words/flashcard/', {"word": "blah"})
        self.assertEqual(405, response.status_code)

class AuthenticationTest(TestCase):
    fixtures = ['testdata.json']

    def setUp(self):
        setup_test_environment()

    def test_html_redirect(self):
        """Test that unauthenticated HTML requests are redirected to the login page"""
        response = self.client.get('/', follow=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual([("http://testserver/accounts/login/?next=/", 302)], response.redirect_chain)

    def test_json_auth(self):
        """Test that the JSON API cannot be accessed unless logged in"""
        response = self.client.get('/words/words/')
        self.assertEqual(403, response.status_code)
