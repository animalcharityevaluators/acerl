"""Acerl API serializers.

The Acerl API returns JSON data. The serializers define rules
for the conversion of query sets and search results to JSON.
"""

import datetime
from collections import OrderedDict

from rest_framework import serializers
from rest_framework.fields import SkipField

from .models import Resource


class NonNullSerializer(serializers.HyperlinkedModelSerializer):
    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = [field for field in self.fields.values() if not field.write_only]
        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue
            if attribute is not None:
                represenation = field.to_representation(attribute)
                if represenation in (None, "", []):
                    # Do not seralize empty objects
                    continue
                ret[field.field_name] = represenation
        return ret


class ResourceSerializer(NonNullSerializer):
    """
    Serializer for the Resource model.
    """

    authors = serializers.StringRelatedField(many=True)
    editors = serializers.StringRelatedField(many=True)

    class Meta:
        model = Resource
        fields = (
            "authors",
            "editors",
            "title",
            "subtitle",
            "abstract",
            "publisher",
            "journal",
            "published",
            "accessed",
            "volume",
            "number",
            "pages",
            "series",
            "edition",
            "url",
            "fulltext_url",
        )


class SearchSerializer(NonNullSerializer):
    """
    Serializer for search results.
    """

    authors = serializers.StringRelatedField(many=True)
    editors = serializers.StringRelatedField(many=True)
    categories = serializers.StringRelatedField(many=True)
    excerpt = serializers.SerializerMethodField("fetch_excerpt")

    def __init__(self, instance=None, data=serializers.empty, **kwargs):
        for entry in instance:
            if isinstance(entry.published, datetime.datetime):
                entry.published = entry.published.date()
        super().__init__(instance=instance, data=data, **kwargs)

    def fetch_excerpt(self, obj):
        try:
            return obj.highlighted["text"][0]
        except (TypeError, AttributeError):
            return ""

    class Meta:
        model = Resource
        fields = (
            "authors",
            "editors",
            "title",
            "subtitle",
            "abstract",
            "publisher",
            "journal",
            "published",
            "volume",
            "number",
            "pages",
            "series",
            "edition",
            "url",
            "fulltext_url",
            "resource_type",
            "categories",
            "excerpt",
            "review",
        )


class SuggestSerializer(serializers.Serializer):
    """
    Serializer for suggestions.
    """

    field = serializers.CharField()
    value = serializers.CharField()
