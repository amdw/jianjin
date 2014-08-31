import re

from django.db import models
from django.core import urlresolvers
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

TAG_REGEX = "[a-z0-9]+"

class Tag(models.Model):
    tag = models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return self.tag

    def clean(self):
        if not re.match("^{0}$".format(TAG_REGEX), self.tag):
            raise ValidationError("Tag must match regular expression " + TAG_REGEX)

class Word(models.Model):
    word = models.CharField(max_length=10)
    pinyin = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    user = models.ForeignKey(User)
    tags = models.ManyToManyField(Tag, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    confidence = models.IntegerField(default=0)
    related_words = models.ManyToManyField("self", blank=True)

    def __unicode__(self):
        return self.word

    def username(self):
        return self.user.username

PART_CHOICES = (
    (' ', 'none'),
    ('N', 'noun'),
    ('V', 'verb'),
    ('ADJ', 'adjective'),
    ('ADV', 'adverb'),
    ('PREP', 'preposition'),
    ('MW', 'measure'),
)
    
class Definition(models.Model):
    word = models.ForeignKey(Word, related_name='definitions')
    definition = models.CharField(max_length=100)
    part_of_speech = models.CharField(max_length=10, choices=PART_CHOICES)

    def __unicode__(self):
        return self.definition

    def changeform_link(self):
        if self.id:
            changeform_url = urlresolvers.reverse('admin:words_definition_change', args=(self.id,))
            return '<a href="{0}" target="_blank">Details</a>'.format(changeform_url)
        return ""
    changeform_link.allow_tags = True
    changeform_link.short_description = ""

class ExampleSentence(models.Model):
    definition = models.ForeignKey(Definition, related_name='example_sentences')
    sentence = models.TextField()
    pinyin = models.TextField()
    translation = models.TextField()

    def __unicode__(self):
        return self.sentence

class ComparisonGroup(models.Model):
    name = models.CharField(max_length=20, blank=True)

    def __unicode__(self):
        return self.name

class ComparisonExample(models.Model):
    comparison_group = models.ForeignKey(ComparisonGroup)
    word = models.ForeignKey(Word)
    example = models.TextField()
    explanation = models.TextField()
