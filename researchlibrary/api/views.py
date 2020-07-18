"""Acerl API views.

The Acerl API is self-documenting. Call the API base URL in a
web browser for an overview of the available endpoints.
"""
import logging
from collections import Counter
from itertools import chain

from haystack.inputs import Raw
from haystack.query import SearchQuerySet
from rest_framework import viewsets
from whoosh.sorting import FieldFacet, Count

from .models import Category, Person, Resource
from .serializers import ResourceSerializer, SearchSerializer, SuggestSerializer

logger = logging.getLogger(__name__)

VALID_SORT_FIELDS = [
    "author",
    "authors",
    "categories",
    "edition",
    "editors",
    "fulltext_url",
    "journal",
    "keywords",
    "number",
    "pages",
    "published",
    "publisher",
    "resource_type",
    "series",
    "subtitle",
    "title",
    "url",
    "volume",
    "year_published",
]


class LengthlessSearchQuerySet(SearchQuerySet):
    def __len__(self):
        # Prevent this: https://stackoverflow.com/a/41475344/678861
        # Otherwise the query is run twice
        return 2048


class ResourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    The view of the /list endpoint of the API. For the API documentation
    call the endpoint in a browser.
    """

    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer


class SearchViewSet(viewsets.GenericViewSet):
    """
    The view of the /search endpoint of the API. For the API documentation
    call the endpoint in a browser.
    """

    queryset = LengthlessSearchQuerySet()

    def list(self, request, *args, **kwargs):
        """
        Return a paginated list of search hits filtered according to
        user-selected criteria.
        """

        # # This is found separately so that the counts per category are computed properly
        # queryset_no_categories = self._filtered_queryset_no_categories(request)

        queryset = self._filtered_queryset(request)
        page = self.paginate_queryset(queryset)
        serializer = SearchSerializer(page, many=True, context={"request": request})
        response = self.get_paginated_response(serializer.data)
        facets = self._get_facets(queryset)
        response.data.update(facets)
        return response

    def _filtered_queryset(self, request):
        query = request.GET.get("q") or ":"
        resource_type_filters = request.GET.getlist("type")
        min_year_filter = int(request.GET.get("minyear", 1000))
        max_year_filter = int(request.GET.get("maxyear", 3000)) + 1  # Off by one issue
        category_filters = set(request.GET.getlist("category"))
        sorting = request.GET.get("sort", "")
        queryset = (
            self.queryset.models(Resource)
            .filter(content=Raw(query))
            .filter(published__year__range=[min_year_filter, max_year_filter])
        )
        if resource_type_filters:
            queryset = queryset.filter(resource_type__in=resource_type_filters)
        if sorting.strip("-") in VALID_SORT_FIELDS:
            queryset = queryset.order_by(sorting)
        # Evaluate the queryset
        queryset = list(queryset)
        # These filters don’t work correctly because they return the resources all of whose
        # categories are in the filter categories, i.e. all resources whose categories are a subset
        # of the filter categories, e.g., if a resources has categories foo and bar, and I filter
        # for bar, it won’t be found. The filter we’d need is a filter that returns all that have a
        # nonempty intersection. That’s not supported, so we need to filter and facet manually.
        #
        # if category_filters:
        #     queryset = queryset.filter(categories__in=category_filters)
        if category_filters:
            queryset = [
                resource for resource in queryset if set(resource.categories) & category_filters
            ]
        return queryset

    @property
    def facet_fields(self):
        facet_names = ["resource_type", "year_published", "categories", "keywords"]
        return {name: FieldFacet(name, allow_overlap=True, maptype=Count) for name in facet_names}

    def _get_facets(self, queryset):
        category_counts = Counter(chain.from_iterable(resource.categories for resource in queryset))
        resource_type_counts = Counter(resource.resource_type for resource in queryset)
        year_published_counts = Counter(resource.year_published for resource in queryset)
        categories_tree = [
            self._format_categories_list(category, category_counts)
            for category in Category.objects.filter(level=0)
        ]
        # Filter empty top-level categories
        categories_tree = [category for category in categories_tree if category["resource_count"]]
        return {
            "categories_list": categories_tree,
            "resource_type_list": filter(bool, resource_type_counts.keys()),
            "published_list": filter(bool, year_published_counts.keys()),
            # Keywords are currently not displayed in the frontend anyway
            "keywords_list": [],
        }

    def _format_categories_list(self, category, counts):
        if category.is_leaf_node():
            return {
                "name": category.name,
                "children": [],
                "resource_count": counts.get(category.name, 0),
            }
        children = [
            self._format_categories_list(child, counts) for child in category.get_children()
        ]
        # Filter empty categories
        children = [child for child in children if child["resource_count"]]
        resource_count = sum(child["resource_count"] for child in children)
        return {"name": category.name, "children": children, "resource_count": resource_count}


class SuggestViewSet(viewsets.GenericViewSet):
    """
    The view of the /suggest endpoint of the API. For the API documentation
    call the endpoint in a browser.
    """

    queryset = SearchQuerySet()

    def list(self, request, *args, **kwargs):
        """
        Return a list of type-ahead suggestions based on what the user has
        already typed and four search fields, title, subtitle, author name,
        and keywords.
        """
        search_text = (request.GET.get("q", "")).strip()
        if search_text:
            sq1 = [
                {"value": result.title, "field": "title"}
                for result in SearchQuerySet().models(Resource).autocomplete(title_auto=search_text)
            ]
            sq2 = [
                {"value": result.subtitle, "field": "subtitle"}
                for result in SearchQuerySet()
                .models(Resource)
                .autocomplete(subtitle_auto=search_text)
            ]
            sq3 = [
                {"value": result.name, "field": "author"}
                for result in SearchQuerySet().models(Person).autocomplete(name_auto=search_text)
            ]
            results = sq1 + sq2 + sq3
        else:
            results = []
        page = self.paginate_queryset(results)
        serializer = SuggestSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)
