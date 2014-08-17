import random

from django.http import HttpResponse, Http404
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

class WordsViewSet(viewsets.ViewSet):
    """
    Using ModelViewSet should work here, but unfortunately the DRF serializers are just too buggy
    right now in regard to their handling of many-to-many relationships. For example, see:
    https://github.com/tomchristie/django-rest-framework/labels/writable%20nested%20serializers

    Once these issues have been addressed, it should be possible to simplify this considerably.
    """
    model = Word

    def _get_serializer(self):
        return WordSerializer()

    def list(self, request):
        words = Word.objects.filter(user=request.user.id)
        serializer = self._get_serializer()
        return Response(serializer.serialize_many(words))

    def retrieve(self, request, pk=None):
        word = get_object_or_404(Word, pk=pk, user=request.user.id)
        serializer = self._get_serializer()
        return Response(serializer.serialize(word))

    def create(self, request):
        serializer = self._get_serializer()
        word = serializer.deserialize_and_update(request.DATA, request.user.id)
        return Response(serializer.serialize(word))

    def update(self, request, pk=None):
        serializer = self._get_serializer()
        word = serializer.deserialize_and_update(request.DATA, request.user.id, pk)
        return Response(serializer.serialize(word))

    def partial_update(self, request, pk=None):
        # Is this even needed?
        pass

    def destroy(self, request, pk=None):
        #TODO
        pass

@api_view(['GET'])
def words_by_tag(request, tag_name):
    """View function to load words for a particular tag"""
    words = load_words(request, tag_name)
    serializer = WordSerializer()
    return Response(serializer.serialize_many(words))

def random_choice_by_weight(choices, r=random):
    """
    Given a list of 2-tuples (choice, weight), return a random choice with the
    probabilities weighted so that for a particular choice X with weight W, the
    probability P(X) of returning X is W/sum(all weights).

    The optional argument r is to allow deterministic tests to be written.
    """
    if [w for (_, w) in choices if w < 0]:
        raise ArithmeticError("Negative weights are not allowed!")
    total_weights = sum([weight for (_, weight) in choices])
    weight_index = r.uniform(0, total_weights)
    weight_sum = 0
    for (choice, weight) in choices:
        weight_sum += weight
        if weight_sum > weight_index:
            return choice
    raise ArithmeticError("Weight selection algorithm failed")

def weights_for_words(words):
    """
    Calculate flashcard probability weights for a given set of words based on confidence
    """
    confidences = [w.confidence for w in words]
    # Shift all confidence scores so larger confidence means smaller weight and 1 is the minimum
    shift = -max(confidences)
    weights = [-c - shift + 1 for c in confidences]
    return weights

@api_view(['GET'])
def flashcard_word(request, tag_name=None):
    """View function to load random word for flashcard purposes"""
    words = load_words(request, tag_name)
    if not words:
        raise Http404
    weights = weights_for_words(words)
    word = random_choice_by_weight(zip(words, weights))
    serializer = WordSerializer()
    return Response(serializer.serialize(word))

@api_view(['POST'])
def confidence(request, word_id):
    """View function to allow direct adjustments of confidence"""
    word = get_object_or_404(Word, pk=int(word_id), user=request.user.id)
    if not 'new' in request.DATA:
        return Response({"error": "Must specify 'new' confidence value"},
                        status=status.HTTP_400_BAD_REQUEST)
    new_confidence = request.DATA['new']
    if isinstance(new_confidence, basestring) and not new_confidence.isdigit():
        return Response({"error": "New confidence value must be a number, not '{0}'".format(new_confidence)},
                        status=status.HTTP_400_BAD_REQUEST)
    word.confidence = int(new_confidence)
    word.save()
    return Response({"new": word.confidence})
