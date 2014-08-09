import random

from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response

from words.models import Word, Tag
from serializers import WordSerializer, TagSerializer

class TagsViewSet(viewsets.ModelViewSet):
    model = Tag
    serializer_class = TagSerializer

def load_words(request, tag_name=None):
    "Retrieve matching words for a particular HTTP request, with tag as an optional parameter"
    if not tag_name:
        tag_name = request.QUERY_PARAMS.get('tag', None)

    if tag_name:
        tag = get_object_or_404(Tag, tag=tag_name)
        words = tag.word_set.filter(user=request.user.id)
    else:
        words = Word.objects.filter(user=request.user.id)

    return words

class WordsViewSet(viewsets.ModelViewSet):
    model = Word
    serializer_class = WordSerializer

    def get_queryset(self):
        # Only return words which belong to the current user
        return Word.objects.filter(user=self.request.user.id)

@api_view(['GET'])
def words_by_tag(request, tag):
    """View function to load words for a particular tag"""
    words = load_words(request, tag)
    serializer = WordSerializer(words, many=True)
    return Response(serializer.data)

class FlashcardViewSet(viewsets.ViewSet):
    model = Word

    def list(self, request):
        words = load_words(request)
        word = random.choice(words)
        serializer = WordSerializer(word)
        return Response(serializer.data)
