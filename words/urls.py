from django.conf.urls import patterns, url, include
from words import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'words', views.WordsViewSet)
router.register(r'tags', views.TagsViewSet)

tag_regex = "[A-Za-z0-9]+"

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^flashcard/$', views.flashcard_word),
    url(r'^flashcard/({0})'.format(tag_regex), views.flashcard_word),
    url(r'^wordsbytag/({0})'.format(tag_regex), views.words_by_tag),
)
