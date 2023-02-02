import logging
import re
from dataclasses import dataclass
from datetime import datetime
from itertools import count

import requests
from django.apps import apps as django_apps
from django.conf import settings
from django.core import management
from django.db.models import Q
from django.forms.models import model_to_dict
from django.utils.text import slugify

from ... import models_choices
from ...fields import ApproximateDate
from ...models import Category, Person, Resource

logger = logging.getLogger(__name__)
session = requests.Session()
session.headers["Authorization"] = "Bearer " + settings.SCIWHEEL_API_KEY


CATEGORIES_FROM_TAGS = True
CATEGORIES_FROM_PROJECTS = False
ROOT_PROJECT = "528152"  # Research Library (public)


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
        title, subtitle = self.title or "", ""
        if separators.search(title):
            title, subtitle = separators.split(title, 1)
        return title.strip(), subtitle.strip()

    def get_title(self):
        title, _ = self._get_title_and_subtitle()
        return title

    def get_subtitle(self):
        _, subtitle = self._get_title_and_subtitle()
        return subtitle

    def get_published(self):
        if self.publicationDate:
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
        return (self.fullTextLink or "").strip()

    def get_fulltext_url(self):
        return (self.pdfUrl or "").strip()

    def get_journal(self):
        return (self.journalName or "").strip()

    def get_abstract(self):
        return (self.abstractText or "").strip()

    def get_volume(self):
        if self.volume and self.volume.isnumeric():
            return int(self.volume)

    def get_number(self):
        if self.issue and self.issue.isnumeric():
            return int(self.issue)

    def _get_start_and_end_page(self):
        start = end = None
        if self.pagination:
            if "-" in self.pagination:
                start, end = self.pagination.split("-", 1)
            else:
                start = self.pagination
        if start and start.isnumeric():
            start = int(start)
            if start not in range(-2**31, 2**31-1):
                # Postgres limit
                start = None
        else:
            start = None
        if end and end.isnumeric():
            end = int(end)
            if start not in range(-2**31, 2**31-1):
                # Postgres limit
                start = None
        else:
            end = None
        return start, end

    def get_startpage(self):
        start, _ = self._get_start_and_end_page()
        return start

    def get_endpage(self):
        _, end = self._get_start_and_end_page()
        return end

    def get_tags(self):
        return self.f1000Tags

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
        [root_project] = [project for project in projects if project["id"] == ROOT_PROJECT]
        for project in flatten([root_project]):
            logger.info("Adding or updating project/category %s", project)
            # Well-known category (update returns the number of updated rows)
            if Category.objects.filter(remote_id=project.id).update(name=project.name):
                continue
            # Existing but unmatched category
            if Category.objects.filter(name=project.name).update(remote_id=project.id):
                continue
            # New category
            Category.objects.create(remote_id=project.id, name=project.name)

    def update_resource(self, reference, category):
        # Perfect match
        matching_resources = Resource.objects.filter(remote_id=reference.id)
        # Should be fairly reliable
        if not matching_resources:
            matching_resources = Resource.objects.filter(
                Q(url=reference.fullTextLink) | Q(fulltext_url=reference.fullTextLink)
            )
        # Unreliable matching
        if not matching_resources:
            matching_resources = [
                resource
                for resource in Resource.objects.filter(remote_id="")
                if slugify(reference.title).startswith(slugify(resource.title))
                or slugify(resource.extended_title).startswith(slugify(reference.title))
            ]
        # Filter my year only if there are too many
        if len(matching_resources) > 1 and reference.publicationDate:
            matching_resources = [
                resource
                for resource in matching_resources
                if resource.published.year == reference.get_published().year
            ]
        # Filter my author only if there are too many
        if len(matching_resources) > 1 and reference.authorsText:
            matching_resources = [
                resource
                for resource in matching_resources
                if all(
                    author.last_name.lower() in reference.authorsText.lower()
                    for author in resource.authors.all()
                )
            ]
        if len(matching_resources) == 1:
            [resource] = matching_resources
            if not resource.remote_id:
                logger.info("Found new matching resource %s", resource)
        elif len(matching_resources) < 1:
            logger.info("Creating new resource for %s", reference)
            resource = Resource()
        else:  # Multiple matching resources
            logger.error("Reference: %s", reference)
            logger.error(
                "%s matching resources found: %s",
                len(matching_resources),
                [model_to_dict(resource) for resource in matching_resources],
            )
            return
        resource.title = reference.get_title() or resource.title
        resource.subtitle = reference.get_subtitle() or resource.subtitle
        resource.published = reference.get_published() or resource.published
        resource.resource_type = reference.get_resource_type() or resource.resource_type
        resource.accessed = reference.get_accessed() or resource.accessed
        resource.url = reference.get_url() or resource.url
        resource.fulltext_url = reference.get_fulltext_url() or resource.fulltext_url
        resource.journal = reference.get_journal() or resource.journal
        resource.abstract = reference.get_abstract() or resource.abstract
        resource.volume = reference.get_volume() or resource.volume
        resource.number = reference.get_number() or resource.number
        resource.startpage = reference.get_startpage() or resource.startpage
        resource.endpage = reference.get_endpage() or resource.endpage
        resource.remote_id = reference.get_remote_id() or resource.remote_id
        resource.misc = reference.get_misc() or resource.misc
        resource.save()
        if CATEGORIES_FROM_PROJECTS and category.remote_id != ROOT_PROJECT:
            resource.categories.add(category)
        if CATEGORIES_FROM_TAGS:
            for tag in reference.get_tags():
                categories = Category.objects.filter(name__startswith=tag)
                if not categories:
                    categories = [Category.objects.create(name=tag)]
                resource.categories.add(*categories)
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
            logger.info("Retrieving category %s", category.name)
            references = self.depaginate(
                f"https://sciwheel.com/extapi/work/references"
                f"?projectId={category.remote_id}&sort=addedDate:desc"
            )
            references = [Reference(**reference) for reference in references]
            for reference in references:
                self.update_resource(reference, category)

    def handle(self, *args, **options):
        # It’s more efficient to deactivate signals and run an update once in the end
        django_apps.app_configs["haystack"].signal_processor.teardown()
        self.sync_categories()
        self.sync_resources()
        # Rebuilding takes about 50 s atm., updating about 130 s
        management.call_command("rebuild_index", interactive=False)
