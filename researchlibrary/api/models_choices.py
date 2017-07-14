"""Includes all Dropdown-choices used in models.py"""


# ResourceType choices

CATALOG = 'CATALOG'
LEGAL_DOCUMENT = 'LEGAL_DOCUMENT'
MAGAZINE_ARTICLE = 'MAGAZINE_ARTICLE'
JOURNAL_ARTICLE = 'JOURNAL_ARTICLE'
PRESENTATION = 'PRESENTATION'
STUDY_REPORT = 'STUDY_REPORT'
SCHOLARLY_BOOK = 'SCHOLARLY_BOOK'
TEXTBOOK = 'TEXTBOOK'
THESIS = 'THESIS'
WEBSITE = 'WEBSITE'
WORKING_PAPER = 'WORKING_PAPER'
NEWS_ARTICLE = 'NEWS_ARTICLE'
BLOG_ARTICLE = 'BLOG_ARTICLE'
OPINION_PIECE = 'OPINION_PIECE'
HISTORICAL_DOCUMENT = 'HISTORICAL_DOCUMENT'
ENCYCLOPEDIA_ARTICLE = 'ENCYCLOPEDIA_ARTICLE'
RESEARCH_SUMMARY = 'RESEARCH_SUMMARY'
METASTUDY = 'METASTUDY'
BOOK = 'BOOK'
OTHER = 'OTHER'


RESOURCE_TYPE_CHOICES = (
    (CATALOG, 'Database or catalog'),
    (LEGAL_DOCUMENT, 'Government report or legal document'),
    (MAGAZINE_ARTICLE, 'Magazine article'),
    (JOURNAL_ARTICLE, 'Journal article'),
    (PRESENTATION, 'Presentation'),
    (STUDY_REPORT, 'Project or study report'),
    (SCHOLARLY_BOOK, 'Scholarly book'),
    (TEXTBOOK, 'Textbook'),
    (THESIS, 'Thesis or dissertation'),
    (WEBSITE, 'Website'),
    (WORKING_PAPER, 'Working paper'),
    (RESEARCH_SUMMARY, 'Literature review'),
    (METASTUDY, 'Meta-analysis'),
    (SYSTEMATIC_REVIEW, 'Systematic review'),
    (OPINION_PIECE, 'Opinion piece'),
    (HISTORICAL_DOCUMENT, 'Historical document'),
    (ENCYCLOPEDIA_ARTICLE, 'Encyclopedia entry'),
    (BOOK, 'Nonfiction book'),
    (NEWS_ARTICLE, 'Newspaper article'),
    (BLOG_ARTICLE, 'Blog post'),
    (OTHER, 'Other'),
)


# SourceType choices

NEWSPAPER = 'NEWSPAPER'
JOURNAL = 'JOURNAL'
BOOK = 'BOOK'
CONFERENCE = 'CONFERENCE'
BLOG = 'BLOG'

SOURCETYPE_CHOICES = (
    (NEWSPAPER, 'Newspaper'),
    (JOURNAL, 'Journal'),
    (BOOK, 'Book'),
    (CONFERENCE, 'Conference'),
    (BLOG, 'Blog'),
    (OTHER, 'Other'),
)
