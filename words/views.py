import random

from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.response import Response

from words.models import Word, Tag
from serializers import WordSerializer

class WordsViewSet(viewsets.ModelViewSet):
    model = Word
    serializer_class = WordSerializer

    def get_queryset(self):
        # Only return words which belong to the current user
        return Word.objects.filter(user=self.request.user.id)

class FlashcardViewSet(viewsets.ViewSet):
    model = Word

    def list(self, request):
        tag_name = request.QUERY_PARAMS.get('tag', None)

        if tag_name:
            all_tags = Tag.objects.all()
            tag = get_object_or_404(all_tags, tag=tag_name)
            words = tag.word_set.filter(user=self.request.user.id)
        else:
            words = Word.objects.filter(user=self.request.user.id)

        word = random.choice(words)
        serializer = WordSerializer(word)

        return Response(serializer.data)
