"""Acerl API views.

The Acerl API is self-documenting. Call the API base URL in a
web browser for an overview of the available endpoints.
"""
import logging
from datetime import MAXYEAR

from haystack.inputs import Raw
from haystack.query import SearchQuerySet
from rest_framework import viewsets
from whoosh.sorting import FieldFacet, Count

from .models import Keyword, Category, Person, Resource
from .serializers import ResourceSerializer, SearchSerializer, SuggestSerializer

logger = logging.getLogger("debugging")


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

    queryset = SearchQuerySet()

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
        keyword_filters = request.GET.getlist("keyword")
        resource_type_filters = request.GET.getlist("type")
        min_year_filter = int(request.GET.get("minyear", 1000))
        max_year_filter = int(request.GET.get("maxyear", MAXYEAR))
        category_filters = request.GET.getlist("category")
        sorting = request.GET.get("sort", "")
        queryset = (
            self.queryset.models(Resource)
            .filter(content=Raw(query))
            .filter(published__year__range=[min_year_filter, max_year_filter])
            .highlight()
            .facet("categories")
            .facet("keywords")
        )
        if keyword_filters:
            queryset = queryset.filter(keywords__in=keyword_filters)
        if resource_type_filters:
            queryset = queryset.filter(resource_type__in=resource_type_filters)
        if category_filters:
            queryset = queryset.filter(categories__in=category_filters)
        if queryset and sorting.strip("-") in queryset[0]._additional_fields:
            queryset = queryset.order_by(sorting)
        return queryset

    @property
    def facet_fields(self):
        facet_names = ["resource_type", "year_published", "categories", "keywords"]
        return {name: FieldFacet(name, allow_overlap=True, maptype=Count) for name in facet_names}

    def _get_facets(self, queryset):
        whoosh = queryset.query.backend
        searcher = whoosh.index.searcher()
        query = whoosh.parser.parse(queryset.query.build_query())
        results = searcher.search(query, groupedby=self.facet_fields)
        facet_counts = {name: results.groups(name) for name in results.facet_names()}
        categories_tree = [
            self._format_categories_list(category, facet_counts["categories"])
            for category in Category.objects.filter(level=0)
        ]
        return {
            "categories_list": categories_tree,
            "resource_type_list": filter(bool, facet_counts["resource_type"].keys()),
            "published_list": filter(bool, facet_counts["year_published"].keys()),
            # Keywords are currently not displayed in the frontend anyway
            "keywords_list": [],  # filter(bool, facet_counts['keywords'].keys()),
        }

    def _format_categories_list(self, category, facet_counts):
        if category.is_leaf_node():
            return {
                "name": category.name,
                "children": [],
                "resource_count": facet_counts.get(category.name, 0),
            }
        children = [
            self._format_categories_list(child, facet_counts) for child in category.get_children()
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
            sq4 = [
                {"value": result.keyword, "field": "keyword"}
                for result in SearchQuerySet()
                .models(Keyword)
                .autocomplete(keyword_auto=search_text)
            ]
            results = sq1 + sq2 + sq3 + sq4
        else:
            results = []
        page = self.paginate_queryset(results)
        serializer = SuggestSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)
