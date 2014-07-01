from django.http import HttpResponse
from django.core import serializers

from rest_framework import viewsets
from words.models import Word
from serializers import WordSerializer

class WordsViewSet(viewsets.ModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer
