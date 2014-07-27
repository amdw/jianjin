from rest_framework import serializers

from models import Definition, ExampleSentence, Tag, Word

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag

class RelatedWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ('id', 'word', 'pinyin')

class ExampleSentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleSentence
        
class DefinitionSerializer(serializers.ModelSerializer):
    example_sentences = ExampleSentenceSerializer(many=True)
    
    class Meta:
        model = Definition

class WordSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='username')
    tags = serializers.SlugRelatedField(many=True, slug_field='tag')
    related_words = RelatedWordSerializer(many=True)
    definitions = DefinitionSerializer(many=True)
    
    class Meta:
        model = Word
