from django.conf.urls import patterns, url, include
from words import views, models
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'words', views.WordsViewSet)
router.register(r'tags', views.TagsViewSet)
router.register(r'commontags', views.CommonTagsViewSet)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^flashcard/$', views.flashcard_word),
    url(r'^flashcard/({0})'.format(models.TAG_REGEX), views.flashcard_word),
    url(r'^wordsbytag/({0})'.format(models.TAG_REGEX), views.words_by_tag),
    url(r'^confidence/([0-9]+)', views.confidence),
    url(r'^searchexact/(.+)', views.search_exact),
    url(r'^search/(.+)', views.search_exact),
)
