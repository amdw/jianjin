from rest_framework import serializers

from models import Word, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag

class RelatedWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ('id', 'word')
        
class WordSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='username')
    tags = TagSerializer(many=True)
    related_words = RelatedWordSerializer(many=True)
    
    class Meta:
        model = Word

