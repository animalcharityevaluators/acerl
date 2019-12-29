import datetime
import logging
from collections import defaultdict

from haystack.backends.solr_backend import SolrEngine, SolrSearchBackend
from haystack.inputs import Raw
from rest_framework import viewsets

from .models import Keyword, NewCategory, Person, Resource
from .serializers import ResourceSerializer, SearchSerializer, SuggestSerializer

logger = logging.getLogger("debugging")


class CustomSolrSearchBackend(SolrSearchBackend):
    def build_search_kwargs(self, *args, **kwargs):
        kwargs = super().build_search_kwargs(*args, **kwargs)
        del kwargs['df']
        print(kwargs)
        return kwargs


class CustomSolrEngine(SolrEngine):
    backend = CustomSolrSearchBackend
