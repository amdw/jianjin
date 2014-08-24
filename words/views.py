import random

from django.http import HttpResponse, Http404
from django.core import serializers
from django.core.paginator import Paginator, InvalidPage
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.templatetags.rest_framework import replace_query_param

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

def _get_page_size(request):
    """Get number of words per page from an HTTP request, and apply some validations"""
    page_size = int(request.QUERY_PARAMS.get('page_size', 10))
    if page_size > 100:
        raise ValueError("{0} is above max page size".format(page_size))
    if page_size <= 0:
        raise ValueError("Page size must be positive, found {0}".format(page_size))
    return page_size

def paginate_words(words, request):
    """Generate paginated output from a word query set"""
    try:
        page_size = _get_page_size(request)
        page_num = int(request.QUERY_PARAMS.get('page', 1))
        paginator = Paginator(words, page_size)
        page = paginator.page(page_num)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except InvalidPage as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    serializer = WordSerializer()
    response = {'count': paginator.count,
                'page_count': paginator.num_pages,
                'page': page_num,
                'results': serializer.serialize_many(page.object_list)}
    request_url = request.build_absolute_uri()
    if page.has_previous():
        response['previous'] = replace_query_param(request_url, 'page', page.previous_page_number())
    if page.has_next():
        response['next'] = replace_query_param(request_url, 'page', page.next_page_number())
    return Response(response)

class WordsViewSet(viewsets.ViewSet):
    """
    Main JSON view set for the manipulation of words.

    For more on why the implementation of this does not use ModelViewSet for the time being,
    see serializers.WordSerializer.
    """
    model = Word

    def list(self, request):
        words = Word.objects.filter(user=request.user.id).extra(order_by = ['word'])
        return paginate_words(words, request)

    def retrieve(self, request, pk=None):
        word = get_object_or_404(Word, pk=pk, user=request.user.id)
        serializer = WordSerializer()
        return Response(serializer.serialize(word))

    def create(self, request):
        serializer = WordSerializer()
        word = serializer.deserialize_and_update(request.DATA, request.user.id)
        return Response(serializer.serialize(word))

    def update(self, request, pk=None):
        serializer = WordSerializer()
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
    return paginate_words(words, request)

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
