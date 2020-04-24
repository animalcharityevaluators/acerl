from datetime import datetime

import xmltodict
from django.utils.text import slugify
from django.core import management

from ...models import Category, Resource


def prune(dictionary, empty=(None, {}, [], "")):
    if not isinstance(dictionary, dict):
        return dictionary
    new_dictionary = {}
    for key, value in dictionary.items():
        new_value = prune(value, empty)
        if new_value not in empty:
            new_dictionary[key] = new_value
    return new_dictionary


class Command(management.base.BaseCommand):
    help = "Export the research library"

    def add_arguments(self, parser):
        parser.add_argument("path", help="Path for files")

    def format_resource(self, resource):
        return prune(
            {
                "ref-type": {"@name": resource.resource_type},
                "contributors": {
                    "authors": {
                        "author": [author.name for author in resource.authors.all()]
                        + [
                            {"role": "editor", "last-name": editor.name}
                            for editor in resource.editors.all()
                        ]
                    }
                },
                "titles": {"title": resource.title, "secondary-title": resource.subtitle},
                "periodical": {"full-title": resource.journal},
                "pages": (
                    f"{resource.startpage}-{resource.endpage}"
                    if resource.startpage and resource.endpage
                    else resource.startpage
                ),
                "volume": resource.volume,
                "number": resource.number,
                "edition": resource.edition,
                "dates": {"pub-dates": {"date": resource.published}},
                "urls": {
                    "web-urls": {"url": resource.url},
                    "pdf-urls": {"url": resource.fulltext_url},
                },
                "research-notes": resource.review,
            }
        )

    def format_resources(self, resources):
        database = {"xml": {"records": {"record": map(self.format_resource, resources)}}}
        return xmltodict.unparse(database, pretty=True)

    def handle(self, *args, **options):
        for category in Category.objects.all():
            resources = Resource.objects.filter(categories__id=category.id)
            if resources:
                filename = (
                    f"{options['path']}/{slugify(category.name)}"
                    f".{datetime.utcnow().isoformat('T')}.xml"
                )
                with open(filename, "w") as xmlfile:
                    xmlfile.write(self.format_resources(resources))
        resources = Resource.objects.filter(categories__isnull=True)
        if resources:
            filename = f"{options['path']}/no-category.{datetime.utcnow().isoformat('T')}.xml"
            with open(filename, "w") as xmlfile:
                xmlfile.write(self.format_resources(resources))
