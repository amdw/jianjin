# -*- coding: utf-8 -*-

import copy
import json

from django.test import TestCase, Client
from django.test.utils import setup_test_environment

import models, serializers

USER = 'user'
PASSWORD = 'password'

class LoggedInJsonTest(TestCase):
    """
    Base class for use in tests which need to be logged in and which require JSON assertions.
    """
    fixtures = ['testdata.json']

    def setUp(self):
        setup_test_environment()
        self.assertTrue(self.client.login(username=USER, password=PASSWORD))

    def assert_successful_json(self, response):
        """
        Assert that the response was successful, and contains JSON content.
        Return the parsed content.
        """
        self.assertEqual(200, response.status_code,
                         msg="Got HTTP {0}, content: {1}".format(response.status_code,
                                                                 response.content))
        self.assertEqual('application/json', response['Content-Type'])
        return json.loads(response.content)

    def post_json(self, url, data):
        """Post data to URL as JSON string"""
        return self.client.post(url, content_type="application/json",
                                data=json.dumps(data), follow=True)

    def put_json(self, url, data):
        """PUT data to URL as JSON string"""
        return self.client.put(url, content_type="application/json",
                               data=json.dumps(data), follow=True)

class MiscJsonApiTest(LoggedInJsonTest):
    def test_get_tags(self):
        response = self.client.get('/words/tags/')
        json_response = self.assert_successful_json(response)
        self.assertEqual(sorted(["awesome", "funny"]), sorted([t['tag'] for t in json_response]))

    def test_tags_read_only(self):
        """Tags should only be updated via words, so posting directly should not work"""
        response = self.post_json('/words/tags/', {"tag": "wibble"})
        self.assertEqual(405, response.status_code)

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


class WordsApiTest(LoggedInJsonTest):
    """Test the words JSON API itself (the most complex part of the API)"""
    def __init__(self, *args, **kwargs):
        super(LoggedInJsonTest, self).__init__(*args, **kwargs)
        self.orig_word = {u'confidence': 10,
                          u'date_added': u'2014-06-14T11:25:53.081000+00:00',
                          u'definitions': [{u'definition': u'Hello!',
                                            u'example_sentences': [],
                                            u'id': 1,
                                            u'part_of_speech': u' '}],
                          u'id': 1,
                          u'last_modified': u'2014-06-14T14:29:15.857000+00:00',
                          u'notes': u'',
                          u'pinyin': u'ni3hao3',
                          u'related_words': [{u'id': 3,
                                              u'pinyin': u'wu1long2qiu2',
                                              u'word': u'\u4e4c\u9f99\u7403'}],
                          u'tags': [{u'tag': u'awesome'}],
                          u'user': u'user',
                          u'word': u'\u4f60\u597d'}
        self.word_url = '/words/words/{0}/'.format(self.orig_word['id'])
    
    def latest_word(self):
        """Load the latest version of the word from the database"""
        return models.Word.objects.get(pk=self.orig_word['id'])

    def test_get_words(self):
        response = self.client.get('/words/words/')
        json_response = self.assert_successful_json(response)
        self.assertEqual(sorted([u"你好", u"蛋白质", u"乌龙球", u"妇女"]),
                         sorted(w['word'] for w in json_response))

    def test_get_word(self):
        response = self.client.get(self.word_url, follow=True)
        word = self.assert_successful_json(response)
        self.maxDiff = None
        self.assertEqual(self.orig_word, word)

    def test_get_words_by_tag(self):
        response = self.client.get('/words/wordsbytag/awesome', follow=True)
        json_response = self.assert_successful_json(response)
        self.assertEqual(sorted([u'蛋白质', u'你好']), [w['word'] for w in json_response])

    def test_update_word(self):
        new_word = copy.deepcopy(self.orig_word)
        new_word['word'] = u'你是谁'
        response = self.put_json(self.word_url, new_word)
        json_response = self.assert_successful_json(response)
        #self.assertEqual({}, json_response)
        self.assertEqual(new_word['word'], self.latest_word().word)

    def test_add_and_remove_definition(self):
        new_word = copy.deepcopy(self.orig_word)
        new_def = {'definition': 'Hi there!',
                   'example_sentences': [{'sentence': u'你好小猫',
                                          'pinyin': u'ni3hao3 xiao3mao1',
                                          'translation': u'Hello kitty!'}],
                   'part_of_speech': ' '}
        new_word['definitions'].append(new_def)
        response = self.put_json(self.word_url, new_word)
        json_response = self.assert_successful_json(response)
        self.assertEqual(len(new_word['definitions']), len(self.latest_word().definitions.all()))
        self.assertEqual(len(new_word['definitions']), len(json_response['definitions']))
        new_word['definitions'].pop(1)
        response = self.put_json(self.word_url, new_word)
        json_response = self.assert_successful_json(response)
        self.assertEqual(new_word['definitions'], self.orig_word['definitions'])
        self.assertEqual(len(self.orig_word['definitions']),
                         len(self.latest_word().definitions.all()))
        self.assertEqual(len(self.orig_word['definitions']),
                         len(json_response['definitions']))
        self.assertEqual(self.orig_word['definitions'][0]['definition'],
                         self.latest_word().definitions.all()[0].definition)
        self.assertEqual(self.orig_word['definitions'][0]['definition'],
                         json_response['definitions'][0]['definition'])
        # Old definition and example sentence should be gone from the database
        self.assertEqual(0, len(models.Definition.objects.filter(definition=new_def['definition'])))
        self.assertEqual(0, len(models.ExampleSentence.objects.filter(sentence=new_def['example_sentences'][0]['sentence'])))

    def test_add_sentence(self):
        new_word = copy.deepcopy(self.orig_word)
        new_defs = new_word['definitions'][0]['example_sentences']
        new_defs.append({'sentence': '你好亲爱的!',
                         'pinyin': 'Ni3hao3 qin1ai4de!',
                         'translation': 'Hello dear!'})
        response = self.put_json(self.word_url, new_word)
        json_response = self.assert_successful_json(response)
        self.assertEqual(len(new_defs),
                         len(self.latest_word().definitions.all()[0].example_sentences.all()))
        self.assertEqual(len(new_defs),
                         len(json_response['definitions'][0]['example_sentences']))

    def test_add_tag(self):
        new_word = copy.deepcopy(self.orig_word)
        new_word['tags'].append({'tag': 'splendiferous'})
        response = self.put_json(self.word_url, new_word)
        json_response = self.assert_successful_json(response)
        self.assertTrue('splendiferous' in [t.tag for t in self.latest_word().tags.all()])
        self.assertTrue('splendiferous' in [t['tag'] for t in json_response['tags']])

    def test_add_duplicate_tag(self):
        """
        Adding words with duplicate tags should work fine, but it should not result
        in multiple tag objects in the database
        """
        new_word = copy.deepcopy(self.orig_word)
        existing_tag = new_word['tags'][0]
        new_word['tags'].append(existing_tag)
        response = self.put_json(self.word_url, new_word)
        json_response = self.assert_successful_json(response)
        self.assertEquals(1, len(models.Tag.objects.filter(tag=existing_tag['tag'])))
        self.assertEquals(len(self.orig_word['tags']), len(json_response['tags']))

    def test_remove_tag(self):
        """
        Add a tag at the end of the list and remove it again
        """
        new_word = copy.deepcopy(self.orig_word)
        new_tag = {"tag": "wibble"}
        new_word['tags'].append(new_tag)
        response = self.put_json(self.word_url, new_word)
        json_response = self.assert_successful_json(response)
        new_word['tags'].remove(new_tag)
        response = self.put_json(self.word_url, new_word)
        json_response = self.assert_successful_json(response)
        self.assertEquals(self.orig_word['tags'], json_response['tags'])
        self.assertEquals([t['tag'] for t in self.orig_word['tags']],
                          [t.tag for t in self.latest_word().tags.all()])
        # Tag should get deleted, as there are no words on it left
        self.assertEquals(0, len(models.Tag.objects.filter(tag=new_tag['tag'])))

    def test_add_remove_existing_related_word(self):
        new_word = copy.deepcopy(self.orig_word)
        related_word = {'word': u'蛋白质'}
        new_word['related_words'].append(related_word)
        response = self.put_json(self.word_url, new_word)
        json_response = self.assert_successful_json(response)
        expected_related_words = [u'蛋白质', u'乌龙球']
        self.assertEquals(sorted(expected_related_words),
                          sorted([w['word'] for w in json_response['related_words']]))
        self.assertEquals(sorted(expected_related_words),
                          sorted([w.word for w in self.latest_word().related_words.all()]))
        # Reverse relation should also be present
        self.assertTrue(self.orig_word['id'] in [w.id for w in models.Word.objects.get(word=related_word['word']).related_words.all()])

        # Try removing it again
        new_word['related_words'].remove(related_word)
        response = self.put_json(self.word_url, new_word)
        json_response = self.assert_successful_json(response)
        self.assertTrue(related_word['word'] not in [w.word for w in self.latest_word().related_words.all()])
        self.assertTrue(related_word['word'] not in [w['word'] for w in json_response['related_words']])
        # Reverse relation should also be gone
        self.assertTrue(self.orig_word['word'] not in [w.word for w in models.Word.objects.get(word=related_word['word']).related_words.all()])

    def test_add_new_related_word(self):
        """
        Test adding a new word as a related word to another word.
        """
        # TODO
        pass


class AuthorizationTest(LoggedInJsonTest):
    """
    Check that users cannot read or manipulate entities which don't belong to them
    """
    def test_read_anothers_word(self):
        response = self.client.get('/words/words/5/')
        # Shouldn't even tell them it exists
        self.assertEquals(404, response.status_code)
        self.assertEquals(self.client.get('/words/words/79/').content, response.content)

    def test_write_anothers_word(self):
        word = models.Word.objects.get(pk=5)
        serializer = serializers.WordSerializer()
        word_map = serializer.serialize(word)
        word_map['confidence'] += 1
        response = self.put_json('/words/words/5/', word_map)
        self.assertEquals(404, response.status_code,
                          msg="Expected 404, got {0}".format(response.content))
        self.assertEquals(self.put_json('/words/words/79/', word_map).content, response.content)

        # Shouldn't be able to do it through the confidence API either
        response = self.post_json('/words/confidence/5/', {"new": word_map['confidence']})
        self.assertEquals(404, response.status_code,
                          msg="Expected 404, got {0}".format(response.content))
        self.assertEquals(self.post_json('/words/confidence/79/', {"new": 0}).content,
                          response.content)

    def test_update_anothers_definition(self):
        """
        Make a sneaky attempt to update someone else's definition through one of your
        own words
        """
        word_url = '/words/words/1/'
        word_map = self.assert_successful_json(self.client.get(word_url))
        new_definition = {'id': 5,
                          'definition': 'Something completely different',
                          'example_sentences': [],
                          'part_of_speech': 'V'}
        word_map['definitions'].append(new_definition)
        response = self.put_json(word_url, word_map)
        self.assertEquals(404, response.status_code)
        self.assertEquals(self.client.get('/words/words/79/').content, response.content)
        self.assertEquals("Come on!",
                          models.Definition.objects.get(pk=new_definition['id']).definition)

    def test_update_anothers_example(self):
        """
        Make a sneaky attempt to update someone else's example sentence through one of
        your own words
        """
        word_url = '/words/words/1/'
        word_map = self.assert_successful_json(self.client.get(word_url))
        new_example_sentence = {'id': 5,
                                'sentence': 'Something utterly alien',
                                'pinyin': 'Yoink!',
                                'translation': "Wouldn't you like to know!"}
        word_map['definitions'][0]['example_sentences'].append(new_example_sentence)
        response = self.put_json(word_url, word_map)
        self.assertEquals(404, response.status_code)
        self.assertEquals(self.client.get('/words/words/79/').content, response.content)
        self.assertEquals("Come on! Come on!",
                          models.ExampleSentence.objects.get(pk=new_example_sentence['id']).translation)

    def test_relate_anothers_word(self):
        """
        Try to relate someone else's word to your own
        """
        word_url = '/words/words/1/'
        word_map = self.assert_successful_json(self.client.get(word_url))
        new_related_word = {'id': 5}
        word_map['related_words'].append(new_related_word)
        response = self.put_json(word_url, word_map)
        self.assertEquals(404, response.status_code)
        self.assertEquals(0, len(models.Word.objects.get(pk=new_related_word['id']).related_words.all()))

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
