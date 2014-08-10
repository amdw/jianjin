import random

from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response

from words.models import Word, Tag
from serializers import WordSerializer, TagSerializer

class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Tags are only updated via words, so this is a read-only view set"""
    model = Tag
    serializer_class = TagSerializer

    def get_queryset(self):
        # Only return tags which the user has actually used
        return list(set(Tag.objects.filter(word__user=self.request.user.id)))

def load_words(request, tag_name):
    "Retrieve matching words for a particular HTTP request"
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
def words_by_tag(request, tag_name):
    """View function to load words for a particular tag"""
    words = load_words(request, tag_name)
    serializer = WordSerializer(words, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def flashcard_word(request, tag_name=None):
    """View function to load random word for flashcard purposes"""
    words = load_words(request, tag_name)
    word = random.choice(words)
    serializer = WordSerializer(word)
    return Response(serializer.data)

@api_view(['POST'])
def confidence(request, word_id):
    """View function to allow direct adjustments of confidence"""
    word = get_object_or_404(Word, pk=int(word_id))
    if not 'new' in request.DATA:
        return Response({"error": "Must specify 'new' confidence value"}, status=status.HTTP_400_BAD_REQUEST)
    new_confidence = request.DATA['new']
    if isinstance(new_confidence, basestring) and not new_confidence.isdigit():
        return Response({"error": "New confidence value must be a number, not '{0}'".format(new_confidence)},
                        status=status.HTTP_400_BAD_REQUEST)
    word.confidence = int(new_confidence)
    word.save()
    return Response({"new": word.confidence})
