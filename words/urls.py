from django.conf.urls import patterns, url, include
from words import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'words', views.WordsViewSet)
router.register(r'flashcard', views.FlashcardViewSet)
router.register(r'tags', views.TagsViewSet)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^wordsbytag/([A-Za-z0-9]+)', views.words_by_tag),
)
