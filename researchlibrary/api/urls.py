"""Acerl API endpoints.

The Acerl API is self-documenting. Call the API base URL in a
web browser for an overview of the available endpoints.
"""

from django.conf.urls import include, url
from django.views.generic import RedirectView
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'list', views.ResourceViewSet, base_name='list')
router.register(r'search', views.SearchViewSet, base_name='search')
router.register(r'suggest', views.SuggestViewSet, base_name='suggest')


urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name='api-root')),
    url(r'^v1/', include(router.urls)),
]
