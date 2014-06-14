from django.conf.urls import patterns, url
from words import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^word/(?P<word_id>\d+)', views.word, name='word'),
)
