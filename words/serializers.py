from rest_framework import serializers

from models import Definition, ExampleSentence, Tag, Word

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('tag',)

class RelatedWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ('id', 'word', 'pinyin')

class ExampleSentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleSentence
        exclude = ('definition',)
        
class DefinitionSerializer(serializers.ModelSerializer):
    example_sentences = ExampleSentenceSerializer(many=True, allow_add_remove=True)
    
    class Meta:
        model = Definition
        exclude = ('word',)

class WordSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='username')
    tags = TagSerializer(many=True, allow_add_remove=True)
    related_words = RelatedWordSerializer(many=True)
    definitions = DefinitionSerializer(many=True, allow_add_remove=True)
    
    def save(self, **kwargs):
        # This ugly hack is necessitated by a bug in Django Rest Framework in the handling
        # of adding and removing nested objects through many-to-many relationships.
        # Once it is fixed, this hack can be removed. Related pull request:
        # https://github.com/tomchristie/django-rest-framework/pull/1457
        m2m_data = getattr(self.object, '_m2m_data', None)
        if m2m_data and 'tags' in m2m_data:
            for tag in m2m_data['tags']:
                if not tag.id:
                    tag.save()

        super(WordSerializer, self).save(**kwargs)

    class Meta:
        model = Word

