"""Acerl API search indices.

The Acerl API allows indexed searches over the content of resources
(e.g., papers, books, blog posts) as well as several meta data. This
module defines the indices.
"""

from haystack import indexes
from whoosh.analysis import KeywordAnalyzer, IDTokenizer
from .fields import AnalyzerCharField
from ..models import Keyword, Person, Resource


class ResourceIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(
        document=True,
        use_template=True,
        template_name='search/indexes/api/resource_text.txt'
    )
    published = indexes.DateField(model_attr='published', null=True)
    abstract = indexes.CharField(model_attr='abstract', null=True, indexed=False)
    review = indexes.CharField(model_attr='review', null=True, indexed=False)
    publisher = AnalyzerCharField(model_attr='publisher', null=True, indexed=False, analyzer=IDTokenizer())
    journal = AnalyzerCharField(model_attr='journal', null=True, indexed=False, analyzer=IDTokenizer())
    volume = indexes.IntegerField(model_attr='volume', null=True, indexed=False)
    number = indexes.IntegerField(model_attr='number', null=True, indexed=False)
    pages = AnalyzerCharField(model_attr='pages', null=True, indexed=False, analyzer=IDTokenizer())
    series = AnalyzerCharField(model_attr='series', null=True, indexed=False, analyzer=IDTokenizer())
    edition = AnalyzerCharField(model_attr='edition', null=True, indexed=False, analyzer=IDTokenizer())
    url = AnalyzerCharField(model_attr='url', null=True, indexed=False, analyzer=IDTokenizer())
    fulltext_url = AnalyzerCharField(model_attr='fulltext_url', indexed=False, null=True, analyzer=IDTokenizer())
    resource_type = AnalyzerCharField(model_attr='resource_type', null=True, analyzer=IDTokenizer())
    categories = indexes.MultiValueField()
    newcategories = indexes.MultiValueField()
    authors = indexes.MultiValueField()
    editors = indexes.MultiValueField()
    keywords = indexes.MultiValueField()
    title = AnalyzerCharField(model_attr='title', null=True, indexed=False)
    subtitle = AnalyzerCharField(model_attr='subtitle', null=True, indexed=False)
    title_auto = indexes.EdgeNgramField(model_attr='title')
    subtitle_auto = indexes.EdgeNgramField(model_attr='subtitle')
    # A search with the author: prefix will search this field:
    author = AnalyzerCharField(null=True, analyzer=IDTokenizer())
    year_published = indexes.IntegerField(null=True)

    def get_model(self):
        return Resource

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def prepare_categories(self, obj):
        return list(obj.categories.all())

    def prepare_newcategories(self, obj):
        return list(obj.newcategories.all())

    def prepare_authors(self, obj):
        return list(obj.authors.all())

    def prepare_editors(self, obj):
        return list(obj.editors.all())

    def prepare_keywords(self, obj):
        return list(obj.keywords.all())

    def prepare_author(self, obj):
        return ' '.join([person.name for person in obj.authors.all() | obj.editors.all()])

    def prepare_resource_type(self, obj):
        return obj.get_resource_type_display()

    def prepare_year_published(self, obj):
        return obj.published.year if obj.published else None


class PersonIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=False)
    name = AnalyzerCharField(model_attr='name', analyzer=IDTokenizer())
    name_auto = indexes.EdgeNgramField(model_attr='name')

    def get_model(self):
        return Person

    def index_queryset(self, using=None):
        return self.get_model().objects.all()


class KeywordIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=False)
    keyword = AnalyzerCharField(model_attr='name', analyzer=IDTokenizer())
    keyword_auto = indexes.EdgeNgramField(model_attr='name')

    def get_model(self):
        return Keyword

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
