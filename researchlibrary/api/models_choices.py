"""Includes all Dropdown-choices used in models.py"""


# ResourceType choices

BLOG_ARTICLE = "BLOG_ARTICLE"
BOOK = "BOOK"
BROADCAST = "BROADCAST"
CATALOG = "CATALOG"
CHAPTER = "CHAPTER"
CONFERENCE_ARTICLE = "CONFERENCE_ARTICLE"
ENCYCLOPEDIA_ARTICLE = "ENCYCLOPEDIA_ARTICLE"
FILM = "FILM"
HISTORICAL_DOCUMENT = "HISTORICAL_DOCUMENT"
JOURNAL_ARTICLE = "JOURNAL_ARTICLE"
LEGAL_DOCUMENT = "LEGAL_DOCUMENT"
MAGAZINE_ARTICLE = "MAGAZINE_ARTICLE"
MANUSCRIPT = "MANUSCRIPT"
METASTUDY = "METASTUDY"
NEWS_ARTICLE = "NEWS_ARTICLE"
OPINION_PIECE = "OPINION_PIECE"
OTHER = "OTHER"
PERSONAL_COMMUNICATION = "PERSONAL_COMMUNICATION"
PRESENTATION = "PRESENTATION"
RESEARCH_SUMMARY = "RESEARCH_SUMMARY"
SCHOLARLY_BOOK = "SCHOLARLY_BOOK"
STUDY_REPORT = "STUDY_REPORT"
TEXTBOOK = "TEXTBOOK"
THESIS = "THESIS"
WEBSITE = "WEBSITE"
WORKING_PAPER = "WORKING_PAPER"


RESOURCE_TYPE_CHOICES = (
    (BLOG_ARTICLE, "Blog post"),
    (BOOK, "Book"),
    (BROADCAST, "Broadcast"),
    (CATALOG, "Database or catalog"),
    (CHAPTER, "Book chapter"),
    (CONFERENCE_ARTICLE, "Conference article"),
    (ENCYCLOPEDIA_ARTICLE, "Encyclopedia entry"),
    (FILM, "Film or documentary"),
    (HISTORICAL_DOCUMENT, "Historical document"),
    (JOURNAL_ARTICLE, "Journal article"),
    (LEGAL_DOCUMENT, "Government report or legal document"),
    (MAGAZINE_ARTICLE, "Magazine article"),
    (MANUSCRIPT, "Manuscript"),
    (METASTUDY, "Meta-analysis"),
    (NEWS_ARTICLE, "Newspaper article"),
    (OPINION_PIECE, "Opinion piece"),
    (OTHER, "Other"),
    (PERSONAL_COMMUNICATION, "Personal communication"),
    (PRESENTATION, "Presentation"),
    (RESEARCH_SUMMARY, "Literature review"),
    (SCHOLARLY_BOOK, "Scholarly book"),
    (STUDY_REPORT, "Project or study report"),
    (TEXTBOOK, "Textbook"),
    (THESIS, "Thesis or dissertation"),
    (WEBSITE, "Website"),
    (WORKING_PAPER, "Working paper"),
)


# SourceType choices

NEWSPAPER = "NEWSPAPER"
JOURNAL = "JOURNAL"
BOOK = "BOOK"
CONFERENCE = "CONFERENCE"
BLOG = "BLOG"

SOURCETYPE_CHOICES = (
    (NEWSPAPER, "Newspaper"),
    (JOURNAL, "Journal"),
    (BOOK, "Book"),
    (CONFERENCE, "Conference"),
    (BLOG, "Blog"),
    (OTHER, "Other"),
)


# Quasi-boolean choices

TRUE = "TRUE"
FALSE = "FALSE"
UNSET = "UNSET"

BOOLEAN_CHOICES = (
    (TRUE, "Yes"),
    (FALSE, "No"),
    (UNSET, "Unset"),
)
