from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

def index(request):
    return HttpResponse("This should show all the words!")

def word(request, word_id):
    word = get_object_or_404(Word, pk=word_id)
    output = serializers.serialize("json", [word])
    response = HttpResponse(output, content_type='application/json')
    return response
