"""Acerl API model definitions"""

import datetime

from django.core.exceptions import ValidationError
from django.db import models
from mptt.fields import TreeManyToManyField
from mptt.models import MPTTModel, TreeForeignKey

from .fields import ApproximateDate, ApproximateDateField
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


class Category(models.Model):
    """
    The category of a resource.
    """

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "category (old)"
        verbose_name_plural = "categories (old)"


class NewCategory(MPTTModel):
    """
    The category of a resource, using mptt for tree management
    """

    name = models.CharField(max_length=50, unique=True)
    parent = TreeForeignKey("self", null=True, blank=True, related_name="children", db_index=True)

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
    title = models.CharField(max_length=300, unique=True)
    published = ApproximateDateField(
        "publication date", default="1000-01-01", help_text="Formats YYYY-MM-DD, YYYY-MM, and YYYY."
    )
    resource_type = models.CharField(max_length=30, choices=RESOURCE_TYPE_CHOICES, blank=True)

    # Optional fields
    accessed = models.DateField(
        "date accessed", help_text="ISO 8601 format, e.g., 1806-05-20.", null=True, blank=True
    )
    url = models.URLField(max_length=2000, blank=True, verbose_name="URL")
    fulltext_url = models.URLField(max_length=2000, blank=True, verbose_name="fulltext URL")
    categories = models.ManyToManyField(Category, related_name="resources", blank=True)
    newcategories = TreeManyToManyField(NewCategory, related_name="resources", blank=True)
    keywords = models.ManyToManyField(Keyword, related_name="resources", blank=True)
    editors = models.ManyToManyField(Person, related_name="resources_edited", blank=True)
    publisher = models.CharField(max_length=300, blank=True)
    subtitle = models.CharField(max_length=500, blank=True)
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

    def clean(self):
        if self.published and self.published > datetime.date.today().isoformat():
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
