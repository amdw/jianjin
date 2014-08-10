# -*- coding: utf-8 -*-

import json

from django.test import TestCase, Client
from django.test.utils import setup_test_environment

import models

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

    def post_json(self, url, data):
        """Post data to URL as JSON string"""
        return self.client.post(url, content_type="application/json", data=json.dumps(data))

    def test_get_tags(self):
        response = self.client.get('/words/tags/')
        json_response = self.assert_successful_json(response)
        self.assertEqual(sorted(["awesome", "funny"]), sorted([t['tag'] for t in json_response]))

    def test_tags_read_only(self):
        """Tags should only be updated via words, so posting directly should not work"""
        response = self.post_json('/words/tags/', {"tag": "wibble"})
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
        response = self.post_json('/words/flashcard/', {"word": "blah"})
        self.assertEqual(405, response.status_code)

    def test_confidence(self):
        """Test API points to adjust confidence scores"""
        pk = 1

        def get_confidence():
            return models.Word.objects.get(pk=pk).confidence

        orig_confidence = get_confidence()
        url = '/words/confidence/{0}'.format(pk)

        response = self.post_json(url, {"new": orig_confidence + 1})
        self.assertEqual(200, response.status_code)
        self.assertEqual(orig_confidence + 1, get_confidence())
        response = self.post_json(url, {"new": orig_confidence - 1})
        self.assertEqual(200, response.status_code)
        self.assertEqual(orig_confidence - 1, get_confidence())
        # String also works
        response = self.post_json(url, {"new": str(orig_confidence + 2)})
        self.assertEqual(200, response.status_code)
        self.assertEqual(orig_confidence + 2, get_confidence())

        # Test erroneous input
        orig_confidence = get_confidence()
        response = self.post_json(url, {"nyew": orig_confidence - 14})
        self.assertEqual(400, response.status_code)
        self.assertEqual(orig_confidence, get_confidence())
        # Test non-existent word
        response = self.post_json('/words/confidence/77', {"new": -14})
        self.assertEqual(404, response.status_code)
        # Test non-integer
        response = self.post_json('/words/confidence/{0}'.format(pk), {"new": "12zzz"})
        self.assertEqual(400, response.status_code)
        self.assertEqual(orig_confidence, get_confidence())

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
