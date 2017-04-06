from django.contrib import admin
from words.models import Word, Definition, ExampleSentence, Tag, ComparisonGroup, ComparisonExample

class ExampleSentenceInline(admin.StackedInline):
    model = ExampleSentence
    extra = 3

class DefinitionAdmin(admin.ModelAdmin):
    inlines = [ExampleSentenceInline]

class DefinitionLinkInline(admin.TabularInline):
    model = Definition
    fields = ('definition', 'part_of_speech', 'changeform_link')
    readonly_fields = ('changeform_link',)
    extra = 3

class WordAdmin(admin.ModelAdmin):
    inlines = [DefinitionLinkInline]

admin.site.register(Definition, DefinitionAdmin)
admin.site.register(Word, WordAdmin)
admin.site.register(Tag)

class ComparisonInline(admin.StackedInline):
    model = ComparisonExample
    extra = 2

class ComparisonGroupAdmin(admin.ModelAdmin):
    inlines = [ComparisonInline]

admin.site.register(ComparisonGroup, ComparisonGroupAdmin)
