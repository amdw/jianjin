# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ComparisonExample',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('example', models.TextField()),
                ('explanation', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ComparisonGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=20, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Definition',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('definition', models.CharField(max_length=100)),
                ('part_of_speech', models.CharField(max_length=10, choices=[(' ', 'none'), ('N', 'noun'), ('V', 'verb'), ('ADJ', 'adjective'), ('ADV', 'adverb'), ('PREP', 'preposition'), ('MW', 'measure')])),
            ],
        ),
        migrations.CreateModel(
            name='ExampleSentence',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('sentence', models.TextField()),
                ('pinyin', models.TextField()),
                ('translation', models.TextField()),
                ('definition', models.ForeignKey(related_name='example_sentences', to='words.Definition')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('tag', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('word', models.CharField(max_length=10)),
                ('pinyin', models.CharField(max_length=50)),
                ('notes', models.TextField(blank=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('confidence', models.IntegerField(default=0)),
                ('related_words', models.ManyToManyField(related_name='related_words_rel_+', to='words.Word', blank=True)),
                ('tags', models.ManyToManyField(to='words.Tag', blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='definition',
            name='word',
            field=models.ForeignKey(related_name='definitions', to='words.Word'),
        ),
        migrations.AddField(
            model_name='comparisonexample',
            name='comparison_group',
            field=models.ForeignKey(to='words.ComparisonGroup'),
        ),
        migrations.AddField(
            model_name='comparisonexample',
            name='word',
            field=models.ForeignKey(to='words.Word'),
        ),
    ]
