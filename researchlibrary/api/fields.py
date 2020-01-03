import datetime
import re
from functools import total_ordering

from django.db import models
from django import forms
from django.forms import ValidationError
from django.utils import dateformat

approx_date_re = re.compile(r"^\d{4}(-\d{1,2})?(-\d{1,2})?$")


@total_ordering
class ApproximateDate(str):
    def __new__(cls, year, month=None, day=None):
        datetime.date(year, month or 1, day or 1)
        obj = str.__new__(cls, f"{year:04d}-{month or 0:02d}-{day or 0:02d}")
        obj.year = year
        obj.month = month
        obj.day = day
        return obj

    def __str__(self):
        return self.replace("-00", "")


class ApproximateDateField(models.CharField):
    description = "An approximate date"

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 10
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs

    def to_python(self, value):
        if isinstance(value, ApproximateDate):
            return value
        return self.from_db_value(value)

    def from_db_value(self, value, expression=None, connection=None, context=None):
        value = value.strip()
        if value in (None, ""):
            return ""
        if approx_date_re.search(value):
            value = value + "0000-00-00"[len(value) :]
        year, month, day = map(int, value.split("-"))
        try:
            return ApproximateDate(year, month, day)
        except ValueError as exception:
            raise ValidationError(f"Invalid date: {exception}")

    def get_prep_value(self, value):
        if value in (None, ""):
            return ""
        if isinstance(value, ApproximateDate):
            return str(value)
        if isinstance(value, datetime.date):
            return dateformat.format(value, "Y-m-d")
        if isinstance(value, str) and approx_date_re.search(value):
            return value
        raise ValidationError("Enter a valid date in YYYY-MM-DD, YYYY-MM, or YYYY format.")

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def formfield(self, **kwargs):
        defaults = {"form_class": ApproximateDateFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class ApproximateDateFormField(forms.fields.Field):
    def __init__(self, max_length=10, empty_value="", *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self, value):
        value = super().clean(value)
        value = value.strip()
        if not value:
            return ""
        if isinstance(value, ApproximateDate):
            return value
        if isinstance(value, str) and approx_date_re.search(value):
            value = value + "0000-00-00"[len(value) :]
            year, month, day = map(int, value.split("-"))
            try:
                return ApproximateDate(year, month, day)
            except ValueError as exception:
                raise ValidationError(f"Invalid date: {exception}")
        raise ValidationError("Please enter a valid date.")

