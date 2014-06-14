from django.conf.urls import patterns, url, include
from words import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'words', views.WordsViewSet)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
)
