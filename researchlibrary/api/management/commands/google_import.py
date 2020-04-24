"""Google import job

ACE has been maintaining the library in a Google Spreadsheet.
This job imports an enhanced version of this spreadsheet to the
database.
"""

import logging
import re

import gspread
from dateutil.parser import parse as parse_date
from django.core import management
from oauth2client.service_account import ServiceAccountCredentials

from ... import models_choices
from ...models import Category, Keyword, Person, Resource


logger = logging.getLogger(__name__)


class Command(management.base.BaseCommand):
    help = "Imports the research library spreadsheet"

    def add_arguments(self, parser):
        parser.add_argument("credentials", help="JSON file with credentials")
        parser.add_argument(
            "id",
            help=(
                "ID of Google Spreadsheet "
                "(you may have to create a copy and share it with the"
                " email address from the credentials)"
            ),
        )
        parser.add_argument("sheet", help="Title of the sheet")

    def process(self, row):
        (
            status,
            title,
            url,
            fulltext_url,
            author_names,
            published,
            category_names,
            resource_type,
            keyword_names,
            abstract,
            review,
            discussion,
            # editor_names,
            # publisher,
            # subtitle,
            # review,
            # journal,
            # volume,
            # number,
            # startpage,
            # endpage,
            # series,
            # edition,
            # sourcetype,
        ) = row[:12]
        if status != "Pending" or Resource.objects.filter(url=url).exists():
            logger.info("Skipping entry %r", title)
            return
        subtitle = ""
        if re.search(r" – |: ", title):
            title, subtitle = re.split(r" – |: ", title, 1)
        authors = [
            Person.objects.get_or_create(name=author_name.strip())[0]
            for author_name in author_names.split(";")
            if author_name.strip()
        ]
        keywords = [
            Keyword.objects.get_or_create(name=keyword_name.strip().lower())[0]
            for keyword_name in re.split(r",|;|\n|  ", keyword_names)
            if keyword_name.strip()
        ]
        categories = [
            Category.objects.get(name=category_name.strip())
            for category_name in re.split(r",|;|\n|  ", category_names)
            if (
                category_name.strip()
                and Category.objects.filter(name=category_name.strip()).exists()
            )
        ]
        if discussion.strip():
            review += "\n\nDiscussion: {}".format(discussion)
        resource_type = dict(
            {value.lower(): key for key, value in models_choices.RESOURCE_TYPE_CHOICES},
            **{
                "book": models_choices.BOOK,
                "industry publication": models_choices.RESEARCH_SUMMARY,
                "wikipedia entry": models_choices.ENCYCLOPEDIA_ARTICLE,
                "study report": models_choices.STUDY_REPORT,
                "other (chapter)": models_choices.OTHER,
                "other (proceedings)": models_choices.OTHER,
                "other—survey data": models_choices.OTHER,
                "": models_choices.OTHER,
            }
        )[resource_type.lower()]
        if not re.match(r"^\d{4}(-\d{2})?(-\d{2})?$", published):
            year = re.search(r"\d{4}", published)
            if year:
                published = year.group(0)
            else:
                published = None
        resource = Resource(
            published=published,
            title=title.strip(),
            subtitle=subtitle.strip(),
            url=url.strip(),
            fulltext_url=fulltext_url.strip(),
            resource_type=resource_type,
            abstract=abstract.strip(),
            review=review.strip(),
        )
        resource.save()
        resource.authors = authors
        resource.keywords = keywords
        resource.categories.add(*categories)
        resource.save()

    def handle(self, *args, **options):
        scope = ["https://spreadsheets.google.com/feeds"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            options["credentials"], scope
        )
        gc = gspread.authorize(credentials)
        doc = gc.open_by_key(options["id"])
        worksheet = doc.worksheet(options["sheet"]).get_all_values()
        for row in worksheet:
            if row[1] == "Author":
                continue
            if row[1] == "":
                break
            self.process(row)
