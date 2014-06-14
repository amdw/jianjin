from django.db import models

from django.db import models
from django.core import urlresolvers

class Tag(models.Model):
    tag = models.CharField(max_length=20)

    def __unicode__(self):
        return self.tag

class Word(models.Model):
    word = models.CharField(max_length=10)
    pinyin = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    user_id = models.CharField(max_length=20, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    confidence = models.IntegerField(default=0)
    related_words = models.ManyToManyField("self", blank=True)

    def __unicode__(self):
        return self.word

PART_CHOICES = (
    (' ', 'none'),
    ('N', 'noun'),
    ('V', 'verb'),
    ('ADJ', 'adjective'),
    ('ADV', 'adverb'),
    ('PREP', 'preposition'),
)
    
class Definition(models.Model):
    word = models.ForeignKey(Word)
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
    definition = models.ForeignKey(Definition)
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
