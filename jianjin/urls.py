from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from django.contrib import admin
admin.autodiscover()

# TODO: Is there a way to make the root URL point to a static file, instead of using a no-op template view?
urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="main.html")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^words/', include('words.urls')),
)
