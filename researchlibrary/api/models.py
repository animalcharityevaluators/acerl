"""Acerl API model definitions"""

from datetime import date

from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models
from mptt.fields import TreeManyToManyField
from mptt.models import MPTTModel, TreeForeignKey

from .fields import ApproximateDateField
from .models_choices import RESOURCE_TYPE_CHOICES, SOURCETYPE_CHOICES


class Person(models.Model):
    """
    The person model serves a dual purpose as author and editor.
    The only property of persons are their names, so they can be
    created on the fly when resources are added.
    """

    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "people"

    @property
    def initials(self):
        print("Person name:", self.name)
        names = self.name.split(" ")
        first_names = names[:-1]
        return ".".join([name[0] for name in first_names]) + "."

    @property
    def last_name(self):
        print("Person name:", self.name)
        names = self.name.split(" ")
        return names[-1]

    @property
    def initials_and_last_name(self):
        return f"{self.initials} {self.last_name}"

    @property
    def initials_and_last_name_without_dots(self):
        return self.initials_and_last_name.replace(".", "")


class Category(MPTTModel):
    """
    The category of a resource, using mptt for tree management
    """

    name = models.CharField(max_length=50, unique=True)
    parent = TreeForeignKey("self", null=True, blank=True, related_name="children", db_index=True)
    remote_id = models.CharField(max_length=50, db_index=True, blank=True, default="")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"


class Keyword(models.Model):
    """
    The keywords associated with a resource.
    """

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Resource(models.Model):
    """
    The resource represents a paper, book, blog post, video, or any
    of many other things. The fields are inspired by the Bibtex format.

    Note that we prohibit the deletion of authors and editors so long as
    they are bound to any resources.
    """

    # Mandatory fields
    authors = models.ManyToManyField(Person, related_name="resources_authored")
    title = models.CharField(max_length=300)
    published = ApproximateDateField(
        "publication date", default="1000-01-01", help_text="Formats YYYY-MM-DD, YYYY-MM, and YYYY."
    )
    resource_type = models.CharField(max_length=30, choices=RESOURCE_TYPE_CHOICES, blank=True)

    # Optional fields
    subtitle = models.CharField(max_length=500, blank=True)
    accessed = models.DateField(
        "date accessed", help_text="ISO 8601 format, e.g., 1806-05-20.", null=True, blank=True
    )
    created = models.DateTimeField(auto_now_add=True)
    url = models.URLField(max_length=2000, blank=True, verbose_name="URL")
    fulltext_url = models.URLField(max_length=2000, blank=True, verbose_name="fulltext URL")
    categories = TreeManyToManyField(Category, related_name="resources", blank=True)
    keywords = models.ManyToManyField(Keyword, related_name="resources", blank=True)
    editors = models.ManyToManyField(Person, related_name="resources_edited", blank=True)
    publisher = models.CharField(max_length=300, blank=True)
    abstract = models.TextField(blank=True)
    fulltext = models.TextField(blank=True)
    review = models.TextField(blank=True)
    journal = models.CharField(max_length=300, blank=True)
    volume = models.IntegerField(blank=True, null=True)
    number = models.IntegerField(blank=True, null=True)
    startpage = models.IntegerField(blank=True, null=True)
    endpage = models.IntegerField(blank=True, null=True)
    series = models.CharField(max_length=300, blank=True)
    edition = models.CharField(max_length=300, blank=True)
    sourcetype = models.CharField(
        max_length=30,
        choices=SOURCETYPE_CHOICES,
        blank=True,
        help_text="The type of the source, e.g., “book” for a book chapter.",
    )
    remote_id = models.CharField(max_length=50, db_index=True, blank=True, default="")
    misc = JSONField(default=dict, blank=True)

    def clean(self):
        if self.published and self.published > date.today().isoformat():
            raise ValidationError("The entered publication date is invalid.")
        if self.startpage and self.endpage and self.startpage > self.endpage:
            raise ValidationError("The entered page numbers are invalid.")

    def __str__(self):
        return self.title

    def pages(self):
        if self.startpage and self.endpage:
            return "{}–{}".format(self.startpage, self.endpage)
        elif self.startpage or self.endpage:
            return str(self.startpage or self.endpage)

    def get_absolute_url(self):
        return "/resources/%i/" % self.id

    class Meta:
        ordering = ["-published", "title"]
        get_latest_by = "published"


Resource.authors.through.person.field.remote_field.on_delete = models.PROTECT
Resource.editors.through.person.field.remote_field.on_delete = models.PROTECT
