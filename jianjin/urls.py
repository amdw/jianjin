from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import TemplateView

from django.contrib import admin
admin.autodiscover()

@method_decorator(ensure_csrf_cookie, name="dispatch")
class RootView(TemplateView):
    """
    Trivial template view with decorator to ensure CSRF cookie always sent.
    Strangely, this seems to be required for Firefox but not Chrome.
    """
    template_name = "main.html"

urlpatterns = [
    url(r'^$', login_required(RootView.as_view())),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', login, {'template_name': 'login.html'}, name="login"),
    url(r'^words/', include('words.urls')),
]
