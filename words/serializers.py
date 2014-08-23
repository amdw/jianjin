from datetime import datetime

from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404

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
    example_sentences = ExampleSentenceSerializer(many=True, allow_add_remove=True, required=False)
    
    class Meta:
        model = Definition
        exclude = ('word',)

class WordSerializer:
    """
    It would be great to use ModelSerializer for words, but unfortunately there are too many
    bugs right now involving many-to-many relationships. For example, see:
    https://github.com/tomchristie/django-rest-framework/labels/writable%20nested%20serializers

    Once these are fixed, this code can be significantly simplified.
    """
    def serialize_many(self, words):
        """Serialize multiple words fit for JSON output"""
        return [self.serialize(word) for word in words]

    def serialize(self, word):
        """Serialize a single word fit for JSON output"""
        definitions = DefinitionSerializer(word.definitions.all(), many=True).data
        tags = TagSerializer(word.tags.all(), many=True).data
        related_words = RelatedWordSerializer(word.related_words.all(), many=True).data
        return {'id': word.id,
                'word': word.word,
                'pinyin': word.pinyin,
                'definitions': definitions,
                'notes': word.notes,
                'user': word.user.username,
                'tags': tags,
                'date_added': word.date_added.isoformat(),
                'last_modified': word.last_modified.isoformat(),
                'confidence': word.confidence,
                'related_words': related_words}

    def deserialize_and_update(self, obj, user_id, pk=None):
        """
        Given an incoming dictionary parsed from JSON, convert it into a model object,
        and create it in the database if it does not exist or update it if it does.
        """
        if pk:
            word = get_object_or_404(Word, pk=pk, user=user_id)
        elif 'id' in obj:
            word = get_object_or_404(Word, pk=obj['id'], user=user_id)
        else:
            word = Word.objects.create(user=get_object_or_404(User, pk=user_id))

        word.word = obj.get('word', word.word)
        word.pinyin = obj.get('pinyin', word.pinyin)
        word.notes = obj.get('notes', word.notes)
        # Don't allow updates to user or date_added, and ignore any user-provided last_modified
        word.last_modified = datetime.now()
        word.confidence = obj.get('confidence', word.confidence)

        word.save()

        if 'definitions' in obj:
            self._update_definitions(word, obj['definitions'], user_id)

        if 'tags' in obj:
            self._update_tags(word, obj['tags'])

        if 'related_words' in obj:
            self._update_related_words(word, obj['related_words'], user_id)

        return word

    def _update_tags(self, word, tag_maps):
        """
        Given a word and a list of tags, set the tag list for the word to these tags,
        creating any which don't already exist, and remove any tags which no longer have
        any associated words.
        """
        tags = self._get_tags(set([t['tag'] for t in tag_maps]))
        removed_tags = [t for t in word.tags.all() if not t in tags]
        word.tags.clear()
        word.tags.add(*tags)
        for tag in removed_tags:
            if not len(tag.word_set.all()):
                tag.delete()

    def _get_tags(self, tags):
        """
        Given a list of tag names, load them from the database if they exist,
        and create them otherwise
        """
        result = []
        for tag in tags:
            db_tags = Tag.objects.filter(tag=tag)
            if db_tags:
                result.append(db_tags[0]) # Guaranteed unique
            else:
                db_tag = Tag(tag=tag)
                db_tag.save()
                result.append(db_tag)
        return result

    def _update_definitions(self, word, def_maps, user_id):
        """
        Update the list of definitions for a word (create any new ones, delete any old ones,
        and update any existing ones).
        """
        new_def_ids = [d['id'] for d in def_maps if 'id' in d]
        removed_defs = [d for d in word.definitions.all() if d.id not in new_def_ids]
        for def_map in def_maps:
            if 'id' in def_map:
                existing_def = get_object_or_404(Definition, pk=def_map['id'])
                if existing_def.word.user.id != user_id:
                    raise Http404
            else:
                existing_def = word.definitions.create()
            # Test that people can't sneakily try to update each other's sentences
            if 'example_sentences' in def_map:
                for sentence in def_map['example_sentences']:
                    if 'id' in sentence:
                        existing_sentence = get_object_or_404(ExampleSentence, pk=sentence['id'])
                        if existing_sentence.definition.word.user.id != user_id:
                            raise Http404
            def_serializer = DefinitionSerializer(existing_def, data=def_map)
            if not def_serializer.is_valid():
                raise serializers.ValidationError("Invalid definitions: {0}".format(def_serializer.errors))
            def_serializer.save()

        for definition in removed_defs:
            definition.delete()

    def _update_related_words(self, word, related_word_maps, user_id):
        """
        Update the list of related words for a word
        """
        word.related_words.clear()
        related_words = []
        for word_map in related_word_maps:
            if 'id' in word_map:
                related_word = get_object_or_404(Word, pk=word_map['id'], user=user_id)
            else:
                if not 'word' in word_map:
                    raise serializers.ValidationError("Must specify 'word' or 'id' for related_words")
                related_word_list = Word.objects.filter(word=word_map['word'], user=user_id)
                if related_word_list:
                    # TODO Better handling of the case where multiple words come back
                    related_word = related_word_list[0]
                else:
                    # Create a new word to act as a placeholder
                    related_word = Word.objects.create(word=word_map['word'],
                                                       user=get_object_or_404(User, pk=user_id))
            related_words.append(related_word)
        word.related_words.add(*related_words)
