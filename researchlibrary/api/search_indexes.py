"""Acerl API search indices.

The Acerl API allows indexed searches over the content of resources
(e.g. papers, books, blog posts) as well as several meta data. This
module defines the indices.
"""

from haystack import indexes
from .models import Resource, Keyword, Person


class ResourceIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    published = indexes.DateField(model_attr='published', null=True)
    abstract = indexes.CharField(model_attr='abstract', null=True)
    review = indexes.CharField(model_attr='review', null=True)
    publisher = indexes.CharField(model_attr='publisher', null=True)
    journal = indexes.CharField(model_attr='journal', null=True)
    volume = indexes.IntegerField(model_attr='volume', null=True)
    number = indexes.IntegerField(model_attr='number', null=True)
    pages = indexes.CharField(model_attr='pages', null=True)
    series = indexes.CharField(model_attr='series', null=True)
    edition = indexes.CharField(model_attr='edition', null=True)
    url = indexes.CharField(model_attr='url', null=True)
    fulltext_url = indexes.CharField(model_attr='fulltext_url', null=True)
    resource_type = indexes.CharField(model_attr='resource_type', null=True, faceted=True)
    categories = indexes.MultiValueField(indexed=True, stored=True)
    newcategories = indexes.MultiValueField(indexed=True, stored=True, faceted=True)
    authors = indexes.MultiValueField(indexed=True, stored=True)
    editors = indexes.MultiValueField(indexed=True, stored=True)
    keywords = indexes.MultiValueField(indexed=True, stored=True)
    title = indexes.CharField(model_attr='title', null=True)
    subtitle = indexes.CharField(model_attr='subtitle', null=True)
    title_auto = indexes.EdgeNgramField(model_attr='title')
    subtitle_auto = indexes.EdgeNgramField(model_attr='subtitle')
    # A search with the author: prefix will search this field:
    author = indexes.CharField(indexed=True, stored=True, null=True)

    def get_model(self):
        return Resource

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def prepare_categories(self, obj):
        return [c for c in obj.categories.all()]

    def prepare_newcategories(self, obj):
        return [c for c in obj.newcategories.all()]

    def prepare_authors(self, obj):
        return [a for a in obj.authors.all()]

    def prepare_editors(self, obj):
        return [e for e in obj.editors.all()]

    def prepare_keywords(self, obj):
        return [k for k in obj.keywords.all()]

    def prepare_author(self, obj):
        return (' '.join([a.name for a in obj.authors.all() | obj.editors.all()]))

    def prepare_resource_type(self, obj):
        return obj.get_resource_type_display()


class PersonIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=False)
    name = indexes.CharField(model_attr='name')
    name_auto = indexes.EdgeNgramField(model_attr='name')

    def get_model(self):
        return Person

    def index_queryset(self, using=None):
        return self.get_model().objects.all()


class KeywordIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=False)
    keyword = indexes.CharField(model_attr='name')
    keyword_auto = indexes.EdgeNgramField(model_attr='name')

    def get_model(self):
        return Keyword

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
