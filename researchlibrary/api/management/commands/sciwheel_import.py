import logging
import re
from dataclasses import dataclass
from datetime import datetime
from itertools import count

import requests
from dateutil.parser import parse as parse_date
from django.core import management
from oauth2client.service_account import ServiceAccountCredentials

from ... import models_choices
from ...fields import ApproximateDate
from ...models import Category, Keyword, Person, Resource

logger = logging.getLogger(__name__)
session = requests.Session()
session.headers["Authorization"] = "Bearer E3B47052BE53B29B9A397A10CFA12F4E"


@dataclass
class Project:
    id: str
    name: str


@dataclass
class Reference:
    id: int
    type: str
    pubMedId: int
    doi: str
    pmcId: str
    title: str
    abstractText: str
    publicationDate: str
    publishedYear: int
    volume: str
    issue: str
    pagination: str
    journalName: str
    journalAbbreviation: str
    authorsText: str
    fullTextLink: str
    pdfUrl: str
    pdfSize: int
    f1000Recommended: bool
    f1000Bookmarked: bool
    f1000Incomplete: bool
    f1000NotesCount: int
    f1000AddedBy: str
    f1000AddedDate: int
    f1000RecommendationsCount: int
    f1000Tags: list
    pubmedCitationsCount: int

    TYPES = {
        "BLOG_POST": models_choices.BLOG_ARTICLE,
        "BOOK": models_choices.BOOK,
        "BROADCAST": models_choices.BROADCAST,
        "CONFERENCE_PAPER": models_choices.CONFERENCE_ARTICLE,
        "CHAPTER": models_choices.CHAPTER,
        "F1000_ARTICLE": models_choices.JOURNAL_ARTICLE,
        "FILM": models_choices.FILM,
        "FORUM_POST": models_choices.OTHER,
        "LEGAL_CASE": models_choices.LEGAL_DOCUMENT,
        "MAGAZINE_ARTICLE": models_choices.MAGAZINE_ARTICLE,
        "MANUAL_ITEM_PDF": models_choices.OTHER,
        "MANUSCRIPT": models_choices.MANUSCRIPT,
        "MAP": models_choices.OTHER,
        "NEWSPAPER_ARTICLE": models_choices.NEWS_ARTICLE,
        "OTHER": models_choices.OTHER,
        "PATENT": models_choices.LEGAL_DOCUMENT,
        "PERSONAL_COMMUNICATION": models_choices.PERSONAL_COMMUNICATION,
        "PRESENTATION": models_choices.PRESENTATION,
        "REPORT_PAPER": models_choices.STUDY_REPORT,
        "RESEARCH_ARTICLE": models_choices.JOURNAL_ARTICLE,
        "SOFTWARE": models_choices.OTHER,
        "THESIS": models_choices.THESIS,
        "WEBSITE": models_choices.WEBSITE,
    }

    MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    def get_author_names(self):
        return self.authorsText.split(", ")

    def _get_title_and_subtitle(self):
        separators = re.compile(r" – |: ")
        title, subtitle = self.title, ""
        if separators.search(self.title):
            title, subtitle = separators.split(self.title, 1)
        return title, subtitle

    def get_title(self):
        title, _ = self._get_title_and_subtitle()
        return title

    def get_subtitle(self):
        _, subtitle = self._get_title_and_subtitle()
        return subtitle

    def get_published(self):
        segments = self.publicationDate.split(" ")
        year, month, day = segments + [None, None, None][len(segments) :]
        year = int(year) if year else None
        month = self.MONTHS.index(month) + 1 if month else None
        day = int(day) if day else None
        return ApproximateDate(year, month, day)

    def get_resource_type(self):
        return self.TYPES[self.type]

    def get_accessed(self):
        return datetime.fromtimestamp(self.f1000AddedDate / 1000)

    def get_url(self):
        return self.fullTextLink or ""

    def get_fulltext_url(self):
        return self.pdfUrl or ""

    def get_publisher(self):
        return self.journalName or ""

    def get_abstract(self):
        return self.abstractText or ""

    def get_volume(self):
        if self.volume:
            return int(self.volume)

    def get_number(self):
        if self.issue and self.issue.isnumeric():
            return int(self.issue)

    def get_startpage(self):
        if self.pagination:
            return self.pagination.split("-")[0]

    def get_endpage(self):
        if self.pagination and "-" in self.pagination:
            return self.pagination.split("-")[1]

    def get_remote_id(self):
        return self.id

    def get_misc(self):
        return {
            "pubMedId": self.pubMedId,
            "doi": self.doi,
            "pmcId": self.pmcId,
            "authorsText": self.authorsText,
            "f1000Recommended": self.f1000Recommended,
            "f1000Bookmarked": self.f1000Bookmarked,
            "f1000Incomplete": self.f1000Incomplete,
            "f1000NotesCount": self.f1000NotesCount,
            "f1000AddedBy": self.f1000AddedBy,
            "f1000AddedDate": self.f1000AddedDate,
            "f1000RecommendationsCount": self.f1000RecommendationsCount,
            "f1000Tags": self.f1000Tags,
            "pubmedCitationsCount": self.pubmedCitationsCount,
        }


def flatten(projects):
    for project in projects:
        yield Project(id=project["id"], name=project["name"])
        children = project.get("children", [])
        for child in flatten(children):
            yield child


class Command(management.base.BaseCommand):
    help = "Imports the research library spreadsheet"

    def add_arguments(self, parser):
        pass

    @staticmethod
    def depaginate(url):
        results = []
        separator = "&" if "?" in url else "?"  # TODO: Use urlunparse
        for page in count(1):
            page_url = f"{url}{separator}size=100&page={page}"
            response = session.get(page_url, timeout=10)
            response.raise_for_status()
            response_data = response.json()
            results.extend(response_data["results"])
            if response_data["totalPages"] <= page:
                break
        return results

    def sync_categories(self):
        logger.info("Syncing categories")
        projects = self.depaginate("https://sciwheel.com/extapi/work/projects")
        for project in flatten(projects):
            category = Category.objects.filter(remote_id=project.id).first()
            if category:
                category.name = project.name
                continue
            category = Category.objects.filter(name=project.name).first()
            if category:
                category.remote_id = project.id
                continue
            # New category
            Category.objects.create(remote_id=project.id, name=project.name)

    def update_resource(self, reference, category):
        resource = Resource.objects.filter(remote_id=reference.id).first()
        if not resource:
            matching_resources = [
                resource
                for resource in Resource.objects.prefetch_related("authors").filter(remote_id="")
                if resource.title.lower() in reference.title.lower()
            ]
            if len(matching_resources) > 1 and reference.authorsText:
                matching_resources = [
                    resource
                    for resource in matching_resources
                    if all(
                        author.last_name.lower() in reference.authorsText.lower()
                        for author in resource.authors.all()
                    )
                ]
            if len(matching_resources) > 1 and reference.publicationDate:
                matching_resources = [
                    resource
                    for resource in matching_resources
                    if resource.published.year == reference.get_published().year
                ]
            if len(matching_resources) == 1:
                [resource] = matching_resources
                logger.info("Found matching resource %s", resource)
            else:
                logger.warning("%s matching resources found", len(matching_resources))
                assert len(matching_resources) == 0
        if not resource:
            logger.info("Creating new resource")
            resource = Resource()
        resource.title = reference.get_title()
        resource.subtitle = reference.get_subtitle()
        resource.published = reference.get_published()
        resource.resource_type = reference.get_resource_type()
        resource.accessed = reference.get_accessed()
        resource.url = reference.get_url()
        resource.fulltext_url = reference.get_fulltext_url()
        resource.publisher = reference.get_publisher()
        resource.abstract = reference.get_abstract()
        resource.volume = reference.get_volume()
        resource.number = reference.get_number()
        resource.startpage = reference.get_startpage()
        resource.endpage = reference.get_endpage()
        resource.remote_id = reference.get_remote_id()
        resource.misc = reference.get_misc()
        resource.save()
        resource.categories.add(category)
        if not resource.id or not resource.authors.all():
            authors = []
            author_names = reference.get_author_names()
            for author_name in author_names:
                matching_authors = Person.objects.filter(name=author_name)
                if not matching_authors:
                    last_name, initials = author_name, ""
                    if " " in author_name:
                        last_name, initials = author_name.rsplit(" ", 1)
                    matching_authors = Person.objects.filter(name__contains=last_name)
                    for initial in initials:
                        if initial.isupper():
                            matching_authors = matching_authors.filter(name__contains=initial)
                if len(matching_authors) >= 1:
                    authors.append(matching_authors[0])
                else:
                    author = Person.objects.create(name=author_name)
                    authors.append(author)
            resource.authors.add(*authors)

    def sync_resources(self):
        logger.info("Syncing resources")
        for category in Category.objects.exclude(remote_id=""):
            references = self.depaginate(
                f"https://sciwheel.com/extapi/work/references"
                f"?projectId={category.remote_id}&sort=addedDate:desc"
            )
            references = [Reference(**reference) for reference in references]
            for reference in references:
                self.update_resource(reference, category)

    def handle(self, *args, **options):
        self.sync_categories()
        self.sync_resources()
