import logging

from whoosh.analysis import StemmingAnalyzer
from haystack.fields import CharField

logger = logging.getLogger(__name__)


class AnalyzerCharField(CharField):
    field_type = "string"

    def __init__(self, analyzer=None, **kwargs):
        self.analyzer = analyzer
        super().__init__(**kwargs)
